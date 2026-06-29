"""2026-06-29 医药热点 7 页小红书卡片 — FCF 排版风格."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from xhs_card_template import COLORS as C, XHSCard, money_text, wrap_text  # noqa: E402

DATE = "20260629"
DAY_HUMAN = "2026-06-29"
OUT = ROOT / "output/2026-06-29/today-hotspots/cards"
SUMMARY = json.loads((ROOT / f"output/hotspot/{DATE}/summary.json").read_text(encoding="utf-8"))
PERSISTENCE = json.loads((ROOT / "output/2026-06-29/today-hotspots/pharma_persistence_summary.json").read_text(encoding="utf-8"))
ZT_POOL = pd.read_parquet(ROOT / f"output/hotspot/{DATE}/raw/zt_pool.parquet")
SNAPSHOT_TIME = (SUMMARY.get("generated_at", "").split("T")[-1][:5] or "盘后")
PHARMA = next((item for item in SUMMARY["industry_top5"] if item["name"] == "医药生物"), SUMMARY["industry_top5"][0])
WORST = SUMMARY["industry_bottom5"][0]
COMPONENT = next((item for item in SUMMARY["industry_bottom5"] if item["name"] == "元件"), WORST)
PHARMA_UP = sum(item["up_count"] for item in SUMMARY["industry_top5"] if item["name"] in {"生物制品", "医疗服务", "化学制药", "医药生物", "中药Ⅱ"})
PHARMA_DOWN = sum(item["down_count"] for item in SUMMARY["industry_top5"] if item["name"] in {"生物制品", "医疗服务", "化学制药", "医药生物", "中药Ⅱ"})
PHARMA_BREADTH = PHARMA_UP / max(PHARMA_UP + PHARMA_DOWN, 1)
PHARMA_ZT = next((item["涨停数"] for item in SUMMARY["zt_top_industries"] if item["行业"] == "化学制药"), 0)
ZHABAN_RATE = SUMMARY["zb_count"] / max(SUMMARY["zt_count"] + SUMMARY["zb_count"], 1)
REL_STRENGTH = PHARMA["pct_chg"] - COMPONENT["pct_chg"]
PHARMA_NET = PHARMA.get("main_net_in", 0)
COMPONENT_NET = COMPONENT.get("main_net_in", 0)

card = XHSCard(total_pages=7, brand="复旦杰伦")


def pct_text(value: float) -> str:
    return f"{value:+.2f}%"


def limit_up_names(industry: str, n: int = 8) -> list[str]:
    stocks = ZT_POOL.loc[ZT_POOL["所属行业"].eq(industry), "名称"].head(n)
    return [str(item) for item in stocks]


def save(fig, page: int) -> None:
    print(card.save(fig, OUT, page))


def persist_row(code: str, horizon: int, threshold: float = 0.04) -> dict:
    for row in PERSISTENCE["rows"]:
        if row["code"] == code and row["threshold"] == threshold and row["horizon"] == horizon:
            return row
    raise KeyError((code, threshold, horizon))


def pct0(value: float) -> str:
    return f"{value:.0%}"


def signed_pct1(value: float) -> str:
    return f"{value:+.1%}"


def page_1() -> None:
    fig, ax = card.canvas()
    ax.text(0.06, 0.94, "热点复盘 · 医药主线真相", fontsize=14, color=C["red"], transform=ax.transAxes, fontweight="bold")
    ax.text(0.5, 0.83, "医药爆了", fontsize=46, color=C["text"], transform=ax.transAxes, ha="center", fontweight="bold")
    ax.text(0.5, 0.755, "但不是闭眼冲", fontsize=37, color=C["red"], transform=ax.transAxes, ha="center", fontweight="bold")
    ax.text(0.5, 0.700, "行业集体冲高 · 短线炸板也很多", fontsize=15.5, color=C["muted"], transform=ax.transAxes, ha="center")

    card.panel(ax, 0.07, 0.42, 0.41, 0.21, face="panel2")
    ax.text(0.275, 0.605, PHARMA["name"], fontsize=15, color=C["muted"], transform=ax.transAxes, ha="center")
    ax.text(0.275, 0.555, "行业涨幅", fontsize=13, color=C["muted"], transform=ax.transAxes, ha="center")
    ax.text(0.275, 0.475, pct_text(PHARMA["pct_chg"]), fontsize=38, color=C["red"], transform=ax.transAxes, ha="center", fontweight="bold")

    card.panel(ax, 0.52, 0.42, 0.41, 0.21, face="panel2")
    ax.text(0.725, 0.605, COMPONENT["name"], fontsize=15, color=C["muted"], transform=ax.transAxes, ha="center")
    ax.text(0.725, 0.555, f"{SNAPSHOT_TIME} 快照跌幅", fontsize=13, color=C["muted"], transform=ax.transAxes, ha="center")
    ax.text(0.725, 0.475, pct_text(COMPONENT["pct_chg"]), fontsize=38, color=C["down"], transform=ax.transAxes, ha="center", fontweight="bold")
    ax.text(0.5, 0.475, "->", fontsize=22, color=C["muted"], transform=ax.transAxes, ha="center")
    ax.text(0.5, 0.385, f"强弱差 {PHARMA['pct_chg'] - COMPONENT['pct_chg']:.1f} 个百分点", fontsize=15.5, color=C["gold"], transform=ax.transAxes, ha="center", fontweight="bold")

    ax.text(0.06, 0.330, "TL;DR · 今天先记住 3 件事", fontsize=14, color=C["text"], transform=ax.transAxes, fontweight="bold")
    tldr = [
        ("01", "生物制品 / 化学制药 / 医疗服务 / 中药一起进涨幅榜", C["red"]),
        ("02", "化学制药 13 只涨停, 是今天最集中的药味来源", C["orange"]),
        ("03", f"{SUMMARY['zt_count']} 只涨停同时有 {SUMMARY['zb_count']} 只炸板, 热闹不等于好追", C["gold"]),
    ]
    y = 0.270
    for number, text, color in tldr:
        ax.text(0.085, y, number, fontsize=22, color=color, transform=ax.transAxes, fontweight="bold")
        ax.text(0.155, y + 0.005, text, fontsize=13, color=C["text"], transform=ax.transAxes)
        y -= 0.060
    ax.text(0.5, 0.075, f"数据截至 {DAY_HUMAN} {SNAPSHOT_TIME} 快照 · 共 7 页盘中复盘", fontsize=11.5, color=C["muted"], transform=ax.transAxes, ha="center")
    card.footer(ax, 1)
    save(fig, 1)


def page_2() -> None:
    fig, ax = card.canvas()
    card.header(ax, "PAGE 02 · 行业横向对比", "今天钱往哪搬", "涨幅榜几乎被医药占满, 硬件链在另一边承压")
    top = SUMMARY["industry_top5"]
    y_top, y_bot = 0.74, 0.36
    y_step = (y_top - y_bot) / 4
    max_abs = max(abs(x["pct_chg"]) for x in top + SUMMARY["industry_bottom5"])
    ax.text(0.56, 0.805, "行业涨跌幅", fontsize=13, color=C["muted"], transform=ax.transAxes, ha="center", fontweight="bold")
    for i, item in enumerate(top):
        y = y_top - i * y_step
        ax.text(0.06, y + 0.014, item["name"], fontsize=15, color=C["text"], transform=ax.transAxes, fontweight="bold")
        ax.text(0.06, y - 0.018, f"领涨 {item.get('leader_name', '')}", fontsize=11, color=C["muted"], transform=ax.transAxes)
        width = abs(item["pct_chg"]) / max_abs * 0.24
        ax.add_patch(Rectangle((0.36, y - 0.014), width, 0.028, fc=C["red"], ec="none", transform=ax.transAxes))
        ax.text(0.64, y, pct_text(item["pct_chg"]), fontsize=15, color=C["red"], transform=ax.transAxes, va="center", ha="left", fontweight="bold")
        ax.text(0.80, y, money_text(item.get("main_net_in", 0)), fontsize=11, color=C["muted"], transform=ax.transAxes, va="center", ha="left")
    card.insight_box(ax, "结论: 不是单只龙头行情", "医药 5 个细分进涨幅榜, 更像板块扩散而不是孤立脉冲", bottom=0.16, height=0.13, edge="gold")
    losers = " / ".join(f"{x['name']} {pct_text(x['pct_chg'])}" for x in SUMMARY["industry_bottom5"][:3])
    ax.text(0.5, 0.112, f"{SNAPSHOT_TIME} 对照组: {losers}", fontsize=11.5, color=C["down"], transform=ax.transAxes, ha="center")
    card.footer(ax, 2)
    save(fig, 2)


def page_3() -> None:
    fig, ax = card.canvas()
    card.header(ax, "PAGE 03 · 涨停池真相", "药味从哪里来", "化学制药最集中, 中药和医疗服务跟着扩散")
    rows = [("化学制药", "13", limit_up_names("化学制药"), C["red"]), ("中药II", "5", limit_up_names("中药Ⅱ"), C["orange"]), ("医疗服务", "3", limit_up_names("医疗服务"), C["cyan"])]
    y_top, card_h, gap = 0.67, 0.145, 0.035
    for i, (title, count, names, color) in enumerate(rows):
        y = y_top - i * (card_h + gap)
        card.panel(ax, 0.06, y, 0.88, card_h, face="panel2")
        ax.text(0.10, y + 0.080, count, fontsize=34, color=color, transform=ax.transAxes, fontweight="bold", va="center")
        ax.text(0.23, y + 0.095, title, fontsize=16, color=C["text"], transform=ax.transAxes, fontweight="bold")
        ax.text(0.23, y + 0.055, wrap_text(" / ".join(names), 32), fontsize=11, color=C["muted"], transform=ax.transAxes, va="center", linespacing=1.2)
    card.insight_box(ax, "三个持仓式结论", "① 化学制药是主线  ② 中药有扩散  ③ 医疗服务/CXO 给了第二层叙事", bottom=0.10, height=0.11, edge="red", face="panel")
    card.footer(ax, 3)
    save(fig, 3)


def page_4() -> None:
    fig, ax = card.canvas()
    card.header(ax, "PAGE 04 · 新闻锚", "创新药为什么有故事", "医保目录窗口, 给了市场一个想象力入口")
    card.panel(ax, 0.06, 0.665, 0.88, 0.12, edge="purple", face="panel")
    ax.text(0.10, 0.745, "今日新闻锚", fontsize=13, color=C["purple"], transform=ax.transAxes, fontweight="bold")
    ax.text(0.10, 0.705, "7 款已在商保目录的创新药, 寻求进入新一轮基本医保目录", fontsize=14, color=C["text"], transform=ax.transAxes, fontweight="bold")
    cards = [("BUZZ", "药明康德", "雪球讨论 3.1w", "医药 + CXO 双修", C["cyan"]), ("REAL", "海思科", "化学制药领涨", "行业一号信号", C["red"]), ("REAL", "万邦医药", "医疗服务领涨", "服务端扩散", C["red"]), ("WATCH", "恒瑞医药", "老牌医药坐标", "关注榜仍在", C["gold"])]
    positions = [(0.06, 0.45), (0.53, 0.45), (0.06, 0.25), (0.53, 0.25)]
    for (x, y), (tag, name, value, note, color) in zip(positions, cards):
        card.panel(ax, x, y, 0.41, 0.15, face="panel2")
        ax.text(x + 0.03, y + 0.112, tag, fontsize=8.5, color=C["ink"], fontweight="bold", bbox=dict(boxstyle="round,pad=0.22", fc=color, ec="none"), transform=ax.transAxes)
        ax.text(x + 0.205, y + 0.105, name, fontsize=17, color=C["text"], transform=ax.transAxes, ha="center", fontweight="bold")
        ax.text(x + 0.205, y + 0.065, value, fontsize=13.5, color=color, transform=ax.transAxes, ha="center", fontweight="bold")
        ax.text(x + 0.205, y + 0.028, note, fontsize=10.5, color=C["muted"], transform=ax.transAxes, ha="center")
    card.insight_box(ax, "别把医保窗口写成无脑利好", "进目录 = 放量想象 + 价格谈判, 更适合写预期交易", bottom=0.09, height=0.11, edge="gold")
    card.footer(ax, 4)
    save(fig, 4)


def page_5() -> None:
    fig, ax = card.canvas()
    card.header(ax, "PAGE 05 · 老登股雷达", "老登股也没退场", "它们不一定最猛, 但一直是散户情绪锚")
    items = [("01", "贵州茅台", "雪球讨论 9.8w · 长期关注第 1", C["red"]), ("02", "格力电器", "雪球讨论 4.0w · 长期关注第 4", C["blue"]), ("03", "招商银行", "雪球讨论 3.2w · 长期关注第 3", C["gold"]), ("04", "恒瑞医药", "医药老牌核心 · 关注榜仍在", C["green"]), ("05", "比亚迪", "雪球讨论 10.1w · 新能源车情绪锚", C["cyan"])]
    for i, (num, title, body, color) in enumerate(items):
        y = 0.72 - i * 0.112
        ax.text(0.08, y, num, fontsize=28, color=color, transform=ax.transAxes, fontweight="bold", va="center")
        ax.text(0.19, y + 0.016, title, fontsize=16, color=C["text"], transform=ax.transAxes, fontweight="bold")
        ax.text(0.19, y - 0.016, body, fontsize=11.5, color=C["muted"], transform=ax.transAxes)
        if i < len(items) - 1:
            ax.plot([0.08, 0.92], [y - 0.055, y - 0.055], color=C["border"], lw=0.4, alpha=0.5, transform=ax.transAxes)
    card.insight_box(ax, "复旦杰伦短评", "市场不想玩纯题材时, 老登股会重新变成估值和现金流的比较坐标", bottom=0.08, height=0.10, edge="cyan")
    card.footer(ax, 5)
    save(fig, 5)


def page_6() -> None:
    fig, ax = card.canvas()
    card.header(ax, "PAGE 06 · 量化风险", "三个客观信号", "热闹是真热闹, 但追高也是真难")
    signals = [("信号 1 · 涨停热度", str(SUMMARY["zt_count"]), "今日涨停数", "HOT", C["red"], f"化学制药 {PHARMA_ZT} 只涨停\n医药主线够亮"), ("信号 2 · 炸板率", f"{ZHABAN_RATE:.0%}", "炸板 / (涨停+炸板)", "RISK", C["orange"], f"{SUMMARY['zb_count']} 只炸板\n短线容错率不高"), ("信号 3 · 高度未开", f"{SUMMARY['zt_max_board']}板", "最高连板", "WAIT", C["gold"], "题材有热度\n但高度还没打开")]
    for i, (title, value, note, pill, color, expl) in enumerate(signals):
        y = 0.66 - i * 0.185
        card.panel(ax, 0.06, y, 0.88, 0.16, face="panel2")
        ax.text(0.10, y + 0.130, title, fontsize=14, color=C["muted"], transform=ax.transAxes, fontweight="bold")
        ax.text(0.83, y + 0.130, pill, ha="center", va="center", fontsize=11.5, color=C["ink"], fontweight="bold", bbox=dict(boxstyle="round,pad=0.35", fc=color, ec="none"), transform=ax.transAxes)
        ax.text(0.10, y + 0.045, value, fontsize=34, color=color, transform=ax.transAxes, fontweight="bold")
        ax.text(0.10, y + 0.020, note, fontsize=11.5, color=C["muted"], transform=ax.transAxes)
        for j, line in enumerate(expl.split("\n")):
            ax.text(0.60, y + 0.085 - j * 0.025, line, fontsize=13, color=C["text"], transform=ax.transAxes)
    card.insight_box(ax, "结论: 可以复盘, 不要把复盘写成喊单", "主线和买点是两件事", bottom=0.07, height=0.10, edge="gold")
    card.footer(ax, 6)
    save(fig, 6)


def page_7() -> None:
    fig, ax = card.canvas()
    card.header(ax, "PAGE 07 · 持久度回测", "这波能不能多走几天", "历史大涨日后, 5/10/20 日表现")
    med5 = persist_row("159929", 5)
    med10 = persist_row("159929", 10)
    med20 = persist_row("159929", 20)
    inno10 = persist_row("159992", 10)
    latest_med = PERSISTENCE["latest"]["159929"]
    latest_inno = PERSISTENCE["latest"]["159992"]
    metrics = [
        ("01", "今日触发", signed_pct1(latest_med["latest_ret"]), f"159929 医药长序列ETF当日涨幅; 创新药ETF {signed_pct1(latest_inno['latest_ret'])}", C["red"]),
        ("02", "5日延续", pct0(med5["win_rate"]), f">=4%大涨日样本 n={med5['n']}; 5日中位收益 {signed_pct1(med5['median_ret'])}", C["orange"]),
        ("03", "10日持久", pct0(med10["win_rate"]), f"10日中位收益 {signed_pct1(med10['median_ret'])}; 不是强持续信号", C["gold"]),
        ("04", "20日余温", pct0(med20["win_rate"]), f"20日中位收益 {signed_pct1(med20['median_ret'])}; 胜率略过半", C["cyan"]),
        ("05", "创新药弹性", pct0(inno10["win_rate"]), f"159992 >=4%后10日中位 {signed_pct1(inno10['median_ret'])}; 短弹强于宽基", C["green"]),
    ]
    for i, (num, title, value, body, color) in enumerate(metrics):
        y = 0.705 - i * 0.116
        card.panel(ax, 0.06, y - 0.050, 0.88, 0.086, face="panel2", edge="border", lw=0.7)
        ax.text(0.095, y - 0.006, num, fontsize=23, color=color, transform=ax.transAxes, fontweight="bold", va="center")
        ax.text(0.20, y + 0.012, title, fontsize=14.8, color=C["text"], transform=ax.transAxes, fontweight="bold", va="center")
        ax.text(0.20, y - 0.024, body, fontsize=10.6, color=C["muted"], transform=ax.transAxes, va="center")
        ax.text(0.86, y - 0.002, value, fontsize=22, color=color, transform=ax.transAxes, fontweight="bold", ha="right", va="center")
    card.insight_box(ax, "持久度结论", "历史样本说: 这类大涨日短线容易震荡, 10-20日才略有延续胜率", bottom=0.07, height=0.095, edge="gold")
    card.footer(ax, 7)
    save(fig, 7)


def main() -> None:
    for func in (page_1, page_2, page_3, page_4, page_5, page_6, page_7):
        func()


if __name__ == "__main__":
    main()