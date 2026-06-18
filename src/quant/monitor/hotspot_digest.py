"""散户热点数据 → 小红书选题素材 digest

把 HotspotFetcher 的原始数据汇总成可读报告 + 自动生成选题候选。

输出三个层次:
  1. summary_dict: 结构化数据 (给下游程序/给我做选题用)
  2. markdown:    人读简报 (你早上扫一眼)
  3. topics:      选题候选 (我帮你挑题用的素材池)
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

import pandas as pd


# ───────── 数据汇总 ─────────

def summarize(data: dict[str, pd.DataFrame], date: str) -> dict:
    """把原始 fetcher 字典汇总成结构化 summary"""
    summary: dict = {"date": date, "generated_at": datetime.now().isoformat(timespec="seconds")}

    # 1. 涨停天梯 (按连板数排)
    zt = data.get("zt_pool", pd.DataFrame())
    if len(zt):
        zt_sorted = zt.copy()
        zt_sorted["连板数"] = pd.to_numeric(zt_sorted.get("连板数"), errors="coerce").fillna(0).astype(int)
        zt_sorted = zt_sorted.sort_values("连板数", ascending=False)
        summary["zt_count"] = len(zt_sorted)
        summary["zt_max_board"] = int(zt_sorted["连板数"].max()) if len(zt_sorted) else 0
        summary["zt_top10"] = zt_sorted.head(10)[["代码", "名称", "连板数", "所属行业", "涨跌幅"]].to_dict("records")
        # 行业分布
        if "所属行业" in zt_sorted.columns:
            top_ind = zt_sorted["所属行业"].value_counts().head(5)
            summary["zt_top_industries"] = [{"行业": i, "涨停数": int(c)} for i, c in top_ind.items()]
    else:
        summary.update({"zt_count": 0, "zt_max_board": 0, "zt_top10": [], "zt_top_industries": []})

    # 2. 炸板情绪
    zb = data.get("zt_zbgc", pd.DataFrame())
    summary["zb_count"] = len(zb)
    if len(zb):
        summary["zb_top5"] = zb.head(5)[["代码", "名称", "所属行业", "炸板次数"]].to_dict("records")
    else:
        summary["zb_top5"] = []

    # 3. 雪球散户在聊
    xq_t = data.get("xueqiu_tweet", pd.DataFrame())
    if len(xq_t):
        summary["xueqiu_tweet_top10"] = xq_t.head(10)[["股票代码", "股票简称", "关注", "最新价"]].to_dict("records")
    else:
        summary["xueqiu_tweet_top10"] = []

    xq_f = data.get("xueqiu_follow", pd.DataFrame())
    if len(xq_f):
        summary["xueqiu_follow_top10"] = xq_f.head(10)[["股票代码", "股票简称", "关注", "最新价"]].to_dict("records")
    else:
        summary["xueqiu_follow_top10"] = []

    # 4. 东财人气
    em = data.get("em_hot_rank", pd.DataFrame())
    if len(em):
        summary["em_hot_top10"] = em.head(10)[["当前排名", "代码", "股票名称", "最新价", "涨跌幅"]].to_dict("records")
    else:
        summary["em_hot_top10"] = []

    # 5. 概念/行业板块涨跌
    cb = data.get("concept_board", pd.DataFrame())
    if len(cb):
        summary["concept_top5"] = cb.head(5).to_dict("records")
        summary["concept_bottom5"] = cb.tail(5).iloc[::-1].to_dict("records")
    else:
        summary["concept_top5"] = []
        summary["concept_bottom5"] = []

    ib = data.get("industry_board", pd.DataFrame())
    if len(ib):
        summary["industry_top5"] = ib.head(5).to_dict("records")
        summary["industry_bottom5"] = ib.tail(5).iloc[::-1].to_dict("records")
    else:
        summary["industry_top5"] = []
        summary["industry_bottom5"] = []

    # 6. 龙虎榜
    lhb = data.get("lhb", pd.DataFrame())
    if len(lhb):
        # 净买额排序 — 游资抢筹标的
        lhb_sorted = lhb.copy()
        if "龙虎榜净买额" in lhb_sorted.columns:
            lhb_sorted["龙虎榜净买额"] = pd.to_numeric(lhb_sorted["龙虎榜净买额"], errors="coerce")
            lhb_sorted = lhb_sorted.sort_values("龙虎榜净买额", ascending=False)
        keep = [c for c in ["代码", "名称", "解读", "涨跌幅", "龙虎榜净买额", "上榜原因"] if c in lhb_sorted.columns]
        summary["lhb_top10_buy"] = lhb_sorted.head(10)[keep].to_dict("records")
        summary["lhb_top5_sell"] = lhb_sorted.tail(5).iloc[::-1][keep].to_dict("records")
    else:
        summary["lhb_top10_buy"] = []
        summary["lhb_top5_sell"] = []

    # 7. 新闻流（最近 30 条）
    news = data.get("em_global_news", pd.DataFrame())
    if len(news):
        n = news.head(30).copy()
        if "发布时间" in n.columns:
            n["发布时间"] = n["发布时间"].astype(str)
        summary["news_recent30"] = n[["发布时间", "标题", "摘要"]].to_dict("records")
    else:
        summary["news_recent30"] = []

    return summary


# ───────── 选题候选生成 ─────────

def _fmt_money(x) -> str:
    try:
        x = float(x)
    except (TypeError, ValueError):
        return str(x)
    if abs(x) >= 1e8:
        return f"{x/1e8:.2f}亿"
    if abs(x) >= 1e4:
        return f"{x/1e4:.0f}万"
    return f"{x:.0f}"


def generate_topics(summary: dict) -> list[dict]:
    """基于汇总数据生成小红书选题候选

    每条选题: {angle, hook, evidence, kind}
      - angle: 复盘/八卦/科普/教育
      - hook : 标题钩子（小红书风格）
      - evidence: 支撑数据点
      - kind : 主线对象（ticker / 行业 / 概念 / 事件）
    """
    topics: list[dict] = []
    date = summary.get("date", "")

    # ── 复盘类 ──

    if summary.get("zt_max_board", 0) >= 4:
        top = summary["zt_top10"][0]
        topics.append({
            "angle": "复盘",
            "hook": f"{top['名称']} {top['连板数']}连板！{date} 涨停天梯一览",
            "evidence": f"全市场{summary['zt_count']}只涨停，最高{summary['zt_max_board']}连板，行业:{top.get('所属行业','—')}",
            "kind": f"ticker:{top['代码']}",
        })

    if summary.get("zt_top_industries"):
        top_ind = summary["zt_top_industries"][0]
        if top_ind["涨停数"] >= 3:
            topics.append({
                "angle": "复盘",
                "hook": f"{date} 涨停潮锁定【{top_ind['行业']}】，{top_ind['涨停数']}只齐刷刷封板",
                "evidence": f"行业涨停分布TOP5: " + ", ".join(f"{i['行业']}({i['涨停数']})" for i in summary["zt_top_industries"]),
                "kind": f"industry:{top_ind['行业']}",
            })

    if summary.get("concept_top5"):
        c = summary["concept_top5"][0]
        if c.get("pct_chg", 0) >= 3:
            topics.append({
                "angle": "复盘",
                "hook": f"今日最强概念【{c['name']}】涨{c['pct_chg']:.2f}%，领涨{c.get('leader_name','')}",
                "evidence": f"主力净流入{_fmt_money(c.get('main_net_in', 0))}，上涨{c.get('up_count','')}/下跌{c.get('down_count','')}",
                "kind": f"concept:{c['name']}",
            })

    if summary.get("industry_bottom5"):
        bot = summary["industry_bottom5"][0]
        if bot.get("pct_chg", 0) <= -2:
            topics.append({
                "angle": "复盘",
                "hook": f"⚠️【{bot['name']}】跌{bot['pct_chg']:.2f}%居首，{date}最惨行业",
                "evidence": f"主力净流出{_fmt_money(abs(bot.get('main_net_in', 0)))}",
                "kind": f"industry:{bot['name']}",
            })

    # ── 八卦类 ──

    if summary.get("zb_count", 0) >= 20:
        topics.append({
            "angle": "八卦",
            "hook": f"{date}炸板{summary['zb_count']}只！抓涨停的散户今天有多惨",
            "evidence": "炸板代表: " + ", ".join(f"{x['名称']}({x.get('所属行业','')})" for x in summary["zb_top5"][:3]),
            "kind": "event:zhaban",
        })

    if summary.get("lhb_top10_buy"):
        lhb_top = summary["lhb_top10_buy"][0]
        topics.append({
            "angle": "八卦",
            "hook": f"龙虎榜｜{lhb_top['名称']} 净买{_fmt_money(lhb_top.get('龙虎榜净买额', 0))}，{lhb_top.get('解读','')}",
            "evidence": f"上榜原因: {lhb_top.get('上榜原因','—')}",
            "kind": f"ticker:{lhb_top['代码']}",
        })

    if summary.get("xueqiu_tweet_top10") and summary.get("xueqiu_follow_top10"):
        # 找一只在讨论榜上但不在关注榜TOP10的"新热点"
        follow_codes = {x["股票代码"] for x in summary["xueqiu_follow_top10"]}
        new_buzz = [x for x in summary["xueqiu_tweet_top10"] if x["股票代码"] not in follow_codes]
        if new_buzz:
            top = new_buzz[0]
            topics.append({
                "angle": "八卦",
                "hook": f"雪球今天突然在聊【{top['股票简称']}】，发生啥了？",
                "evidence": f"讨论量飙至全市场前10，但长期关注榜外，最新价{top.get('最新价','—')}",
                "kind": f"ticker:{top['股票代码']}",
            })

    # ── 科普/教育类 ──

    if summary.get("zt_max_board", 0) >= 3:
        topics.append({
            "angle": "科普",
            "hook": f"{summary['zt_max_board']}连板是怎么回事？聊聊\"涨停天梯\"和\"高位股\"风险",
            "evidence": f"今日{summary['zt_count']}只涨停，最高{summary['zt_max_board']}连板",
            "kind": "edu:连板",
        })

    if summary.get("lhb_top10_buy"):
        topics.append({
            "angle": "教育",
            "hook": "龙虎榜怎么看？教你3分钟读懂\"机构席位\"和\"游资席位\"",
            "evidence": f"今日{date}龙虎榜上榜{len(summary['lhb_top10_buy']) + len(summary['lhb_top5_sell'])}只起",
            "kind": "edu:龙虎榜",
        })

    if summary.get("zb_count", 0) >= 15:
        topics.append({
            "angle": "教育",
            "hook": "炸板是啥？为什么追涨停的散户最容易被埋",
            "evidence": f"今天炸板{summary['zb_count']}只，足够当反面教材",
            "kind": "edu:炸板",
        })

    # ── 新闻钩子（取最近 5 条标题）──
    for item in summary.get("news_recent30", [])[:5]:
        title = item.get("标题", "")
        if len(title) < 8:
            continue
        topics.append({
            "angle": "复盘",
            "hook": f"📰 {title}",
            "evidence": (item.get("摘要", "") or "")[:80],
            "kind": "news",
        })

    return topics


# ───────── Markdown 渲染 ─────────

def to_markdown(summary: dict, topics: list[dict]) -> str:
    """生成人读简报"""
    lines: list[str] = []
    date = summary.get("date", "")
    lines.append(f"# 📊 {date} 散户热点速览")
    lines.append(f"_生成时间: {summary.get('generated_at', '')}_")
    lines.append("")

    # ── 涨停板 ──
    lines.append("## 🔥 涨停板情绪")
    lines.append(f"- 涨停 **{summary.get('zt_count', 0)}** 只 / 最高 **{summary.get('zt_max_board', 0)}** 连板 / 炸板 **{summary.get('zb_count', 0)}** 只")
    if summary.get("zt_top_industries"):
        lines.append("- 涨停行业TOP5: " + " | ".join(f"{x['行业']}({x['涨停数']})" for x in summary["zt_top_industries"]))
    if summary.get("zt_top10"):
        lines.append("\n**连板天梯 TOP10**")
        lines.append("| 代码 | 名称 | 连板 | 行业 | 涨幅 |")
        lines.append("|---|---|---|---|---|")
        for x in summary["zt_top10"]:
            pct = x.get("涨跌幅", 0)
            try: pct = f"{float(pct):.2f}%"
            except: pct = str(pct)
            lines.append(f"| {x['代码']} | {x['名称']} | {x['连板数']} | {x.get('所属行业','')} | {pct} |")
    if summary.get("zb_top5"):
        lines.append("\n**炸板代表 TOP5**")
        for x in summary["zb_top5"]:
            lines.append(f"- {x['名称']} ({x['代码']}) — {x.get('所属行业','')} 炸板{x.get('炸板次数','?')}次")

    # ── 板块 ──
    lines.append("\n## 📈 板块涨跌")
    if summary.get("industry_top5"):
        lines.append("**行业涨幅TOP5**")
        for x in summary["industry_top5"]:
            lines.append(f"- {x['name']} +{x['pct_chg']:.2f}% — 领涨 {x.get('leader_name','')} (主力净流入 {_fmt_money(x.get('main_net_in', 0))})")
    if summary.get("industry_bottom5"):
        lines.append("\n**行业跌幅TOP5**")
        for x in summary["industry_bottom5"]:
            lines.append(f"- {x['name']} {x['pct_chg']:+.2f}% — 主力净流出 {_fmt_money(abs(x.get('main_net_in', 0)))}")
    if summary.get("concept_top5"):
        lines.append("\n**概念涨幅TOP5**")
        for x in summary["concept_top5"]:
            lines.append(f"- {x['name']} +{x['pct_chg']:.2f}% — 领涨 {x.get('leader_name','')}")

    # ── 散户关注 ──
    lines.append("\n## 💬 散户关注度")
    if summary.get("xueqiu_tweet_top10"):
        lines.append("**雪球讨论榜 TOP10**（今天散户在聊）")
        for x in summary["xueqiu_tweet_top10"]:
            lines.append(f"- {x['股票简称']} ({x['股票代码']}) — 讨论量 {x['关注']}, 价 {x['最新价']}")
    if summary.get("em_hot_top10"):
        lines.append("\n**东财人气榜 TOP10**")
        for x in summary["em_hot_top10"]:
            pct = x.get("涨跌幅", 0)
            try: pct = f"{float(pct):.2f}%"
            except: pct = str(pct)
            lines.append(f"- #{x['当前排名']} {x['股票名称']} ({x['代码']}) — 价 {x['最新价']}, 涨幅 {pct}")

    # ── 龙虎榜 ──
    if summary.get("lhb_top10_buy"):
        lines.append("\n## 🐉 龙虎榜（净买入TOP10）")
        for x in summary["lhb_top10_buy"]:
            net = _fmt_money(x.get("龙虎榜净买额", 0))
            pct = x.get("涨跌幅", 0)
            try: pct = f"{float(pct):.2f}%"
            except: pct = str(pct)
            lines.append(f"- {x.get('名称','')} ({x.get('代码','')}) — 净买 {net} | {pct} | {x.get('解读','')}")
            if x.get("上榜原因"):
                lines.append(f"    > {x['上榜原因']}")

    # ── 新闻 ──
    if summary.get("news_recent30"):
        lines.append("\n## 📰 新闻流（最近10条）")
        for x in summary["news_recent30"][:10]:
            t = x.get("发布时间", "")
            lines.append(f"- `{t}` {x.get('标题','')}")

    # ── 选题候选 ──
    lines.append("\n## 🎯 小红书选题候选")
    by_angle: dict[str, list[dict]] = {}
    for t in topics:
        by_angle.setdefault(t["angle"], []).append(t)
    for angle, items in by_angle.items():
        lines.append(f"\n### {angle} ({len(items)})")
        for i, t in enumerate(items, 1):
            lines.append(f"{i}. **{t['hook']}**")
            lines.append(f"   - 素材: {t['evidence']}")
            lines.append(f"   - 主线: {t['kind']}")

    return "\n".join(lines)
