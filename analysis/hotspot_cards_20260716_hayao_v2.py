"""哈药5连板 · 30年首次 — 6页深度量化卡片.

量化角度:
- 哈药30年历史首次5连板 (最高4×3次, 其后T+5跌20%)
- 当前位置: 距ATH -61.8%, 52周新高
- 封板率82.8%, 全产业链四线联动

数据源: output/hotspot/20260716/summary.json + akshare 新浪日线
"""

from __future__ import annotations
import akshare as ak
import pandas as pd
import numpy as np
import json
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path("/das/user/QYJI/quant")
DATE = "20260716"
DAY_HUM = "2026-07-16"
SUMMARY = json.loads((ROOT / f"output/hotspot/{DATE}/summary.json").read_text())
OUT = ROOT / f"output/hotspot/{DATE}/xhs_hayao_v2"
OUT.mkdir(parents=True, exist_ok=True)

# ─── 调色板 ───────────────────────────────
C = {
    "bg": "#0d1117", "card": "#161b22", "border": "#30363d",
    "text": "#c9d1d9", "muted": "#8b949e",
    "blue": "#58a6ff", "green": "#3fb950", "red": "#f85149",
    "orange": "#d2991d", "purple": "#bc8cff", "gold": "#f0c040",
    "cyan": "#56d4dd", "rose": "#ff7b72",
    "up": "#f85149", "down": "#3fb950",
}
CARD_W, CARD_H, DPI = 7.2, 9.6, 200

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "Droid Sans Fallback", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def new_card():
    fig, ax = plt.subplots(figsize=(CARD_W, CARD_H), facecolor=C["bg"])
    ax.set_facecolor(C["bg"])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    return fig, ax


def add_footer(ax, page, total=6):
    ax.text(0.5, 0.025, "* 数据来源: 东方财富/雪球/新浪 · 历史不代表未来 · 不构成投资建议",
            ha="center", va="center", fontsize=9, color=C["muted"], transform=ax.transAxes)
    ax.text(0.95, 0.025, f"{page}/{total}", ha="right", va="center",
            fontsize=10, color=C["muted"], transform=ax.transAxes)


def pill(ax, x, y, txt, fc, fs=11):
    ax.text(x, y, txt, ha="center", va="center", fontsize=fs, fontweight="bold",
            color=C["bg"],
            bbox=dict(boxstyle="round,pad=0.4", fc=fc, ec="none"),
            transform=ax.transAxes)


def card_bg(ax, cx, cy, w, h):
    p = FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                        boxstyle="round,pad=0.01", fc=C["card"], ec=C["border"], lw=0.8)
    ax.add_patch(p)


def save(fig, page):
    p = OUT / f"page_{page}.png"
    fig.savefig(p, dpi=DPI, bbox_inches=None, pad_inches=0,
                facecolor=C["bg"], edgecolor="none")
    plt.close(fig)
    print(f"  ✓ saved {p}")


# ═══════════════════════════════════════════════
# P1 — 封面: 哈药5连板 · 30年首次
# ═══════════════════════════════════════════════
def page1():
    fig, ax = new_card()
    pill(ax, 0.5, 0.95, f"  {DAY_HUM} · 盘中深度  ", C["gold"])

    # 主标
    ax.text(0.5, 0.82, "哈药股份", ha="center", fontsize=48, fontweight="bold",
            color=C["up"], transform=ax.transAxes)
    ax.text(0.5, 0.74, "5 连板", ha="center", fontsize=46, fontweight="bold",
            color=C["up"], transform=ax.transAxes)
    ax.text(0.5, 0.66, "30年历史首次", ha="center", fontsize=22, fontweight="bold",
            color=C["orange"], transform=ax.transAxes)

    # 三大数字
    zt, zb = SUMMARY["zt_count"], SUMMARY["zb_count"]
    seal_rate = zt / (zt + zb) * 100
    nums = [
        (zt, "涨停", C["up"]),
        (SUMMARY["zt_max_board"], f"连板(30年首见)", C["orange"]),
        (f"{seal_rate:.0f}%", "封板率", C["cyan"]),
    ]
    for i, (n, lbl, col) in enumerate(nums):
        x = [0.18, 0.50, 0.82][i]
        ax.text(x, 0.53, str(n), ha="center", fontsize=50, fontweight="bold",
                color=col, transform=ax.transAxes)
        ax.text(x, 0.445, lbl, ha="center", fontsize=12,
                color=C["muted"], transform=ax.transAxes)

    # 深度钩子 — 紧凑上移
    ax.text(0.5, 0.40, "↓ 30年3次4连板后都发生了什么? ↓", ha="center",
            fontsize=11, color=C["muted"], transform=ax.transAxes)

    # 历史4连板对比迷你表
    history_data = [
        ("1994-08", "4连板", "次日-18.6%", "T+5 +1.7%", C["down"]),
        ("2020-02", "4连板(疫情)", "次日+2.0%", "T+5 -20.7%", C["down"]),
        ("2026-07", "5连板!", "今日进行中", "历史首次", C["up"]),
    ]
    cols_w = [0.14, 0.20, 0.22, 0.22]
    headers = ["日期", "连板", "T+1", "T+5"]
    for ci, (hdr, cw) in enumerate(zip(headers, cols_w)):
        x_pos = 0.08 + sum(cols_w[:ci]) + cw/2
        ax.text(x_pos, 0.36, hdr, ha="center", fontsize=9, fontweight="bold",
                color=C["muted"], transform=ax.transAxes)
    for ri, (date, board, t1, t5, col) in enumerate(history_data):
        y = 0.33 - ri * 0.030
        vals = [date, board, t1, t5]
        for ci, (v, cw) in enumerate(zip(vals, cols_w)):
            x_pos = 0.08 + sum(cols_w[:ci]) + cw/2
            ax.text(x_pos, y, v, ha="center", fontsize=8.5,
                    color=col if ci >= 2 else C["text"], transform=ax.transAxes)

    # 翻页
    ax.text(0.5, 0.07, "翻到下一页 → 看连板股的历史生存率",
            ha="center", fontsize=11, color=C["muted"], style="italic",
            transform=ax.transAxes)

    add_footer(ax, 1)
    save(fig, 1)


# ═══════════════════════════════════════════════
# P2 — 涨停全景 + 连板股生存率
# ═══════════════════════════════════════════════
def page2():
    fig, ax = new_card()
    pill(ax, 0.5, 0.95, "  涨停天梯 + 历史胜率  ", C["up"])
    ax.text(0.5, 0.89, f"今日 {SUMMARY['zt_count']} 只涨停 · 封板率 {SUMMARY['zt_count']/(SUMMARY['zt_count']+SUMMARY['zb_count'])*100:.0f}%",
            ha="center", fontsize=14, color=C["text"], transform=ax.transAxes)

    # 连板天梯 TOP6
    for i, stk in enumerate(SUMMARY["zt_top10"][:6]):
        y = 0.805 - i * 0.095
        board = stk["连板数"]
        bc = C["up"] if board >= 4 else (C["orange"] if board >= 3 else C["gold"])
        ax.text(0.06, y, f"{board}", ha="center", fontsize=26, fontweight="bold",
                color=bc, transform=ax.transAxes)
        ax.text(0.06, y - 0.045, "连板", ha="center", fontsize=8,
                color=C["muted"], transform=ax.transAxes)
        ax.text(0.16, y + 0.008, stk["名称"], ha="left", fontsize=14, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        ax.text(0.16, y - 0.032, f"{stk['代码']} · {stk['所属行业']}", ha="left",
                fontsize=9, color=C["muted"], transform=ax.transAxes)
        pct = float(stk.get("涨跌幅", 0))
        ax.text(0.93, y, f"+{pct:.2f}%", ha="right", fontsize=12, fontweight="bold",
                color=C["up"], transform=ax.transAxes)
        if i < 5:
            ax.plot([0.06, 0.93], [y - 0.072, y - 0.072],
                    color=C["border"], lw=0.5, transform=ax.transAxes)

    # 行业分布
    ax.plot([0.06, 0.93], [0.29, 0.29], color=C["border"], lw=0.8, transform=ax.transAxes)
    ax.text(0.5, 0.32, "涨停最密集行业", ha="center", fontsize=12,
            fontweight="bold", color=C["text"], transform=ax.transAxes)
    for i, ind in enumerate(SUMMARY["zt_top_industries"]):
        x = 0.10 + i * 0.20
        ax.text(x, 0.285, ind["行业"][:5], ha="center", fontsize=10,
                color=C["muted"], transform=ax.transAxes)
        ax.text(x, 0.255, f"{ind['涨停数']}", ha="center", fontsize=22, fontweight="bold",
                color=C["orange"], transform=ax.transAxes)
        ax.text(x, 0.230, "只", ha="center", fontsize=9,
                color=C["muted"], transform=ax.transAxes)

    # 连板股历史胜率洞察
    ax.text(0.5, 0.19, "连板股历史数据", ha="center", fontsize=12,
            fontweight="bold", color=C["text"], transform=ax.transAxes)

    insight = [
        ("4连板以上", "哈药30年仅3次4连板, 本次首次达5连板"),
        ("T+1表现", "2020年4连板后次日+2.0%, 1994年-18.6%"),
        ("T+5表现", "2020年4连板后T+5暴跌-20.7%, 高位接盘代价大"),
    ]
    for i, (label, desc) in enumerate(insight):
        y = 0.155 - i * 0.033
        ax.text(0.10, y, label, ha="left", fontsize=9, fontweight="bold",
                color=C["orange"], transform=ax.transAxes)
        ax.text(0.32, y, desc, ha="left", fontsize=9,
                color=C["muted"], transform=ax.transAxes)

    add_footer(ax, 2)
    save(fig, 2)


# ═══════════════════════════════════════════════
# P3 — 医药链四线深度 + 资金流向
# ═══════════════════════════════════════════════
def page3():
    fig, ax = new_card()
    pill(ax, 0.5, 0.95, "  医药链深度  ", C["up"])
    ax.text(0.5, 0.89, "四条子线 · 全产业链资金共识", ha="center",
            fontsize=18, fontweight="bold", color=C["text"], transform=ax.transAxes)

    # 四线卡片 (含涨幅+涨停数+领涨)
    lines = [
        ("化学制药", "+10.02%/哈药5板/永安2板", 3, "涨停天梯最高", C["up"]),
        ("生物疫苗", "+1.79%/贤丰3板", 3, "概念板块联动", C["up"]),
        ("医疗器械", "+10.00%/九安3板", 3, "疫情记忆激活", C["orange"]),
        ("医疗服务", "+9.99%/南华2板", 3, "CRO昭衍+8.49%", C["orange"]),
    ]

    for i, (name, detail, cnt, note, col) in enumerate(lines):
        y = 0.76 - i * 0.115
        card_bg(ax, 0.50, y, 0.88, 0.10)
        pill(ax, 0.10, y + 0.02, f"  {name}  ", col, fs=10)
        ax.text(0.24, y + 0.02, detail, ha="left", fontsize=10.5,
                color=C["text"], transform=ax.transAxes)
        ax.text(0.24, y - 0.025, note, ha="left", fontsize=9,
                color=C["cyan"], transform=ax.transAxes)
        ax.text(0.88, y, f"{cnt}只", ha="center", fontsize=16, fontweight="bold",
                color=C["up"], transform=ax.transAxes)

    # 当前位置指标
    ax.text(0.5, 0.26, "当前位置·量化信号", ha="center", fontsize=13,
            fontweight="bold", color=C["text"], transform=ax.transAxes)

    signals = [
        ("哈药距历史最高", "-61.8%", "2015年11.76元 → 现在4.49元", C["down"]),
        ("52周位置", "52周新高", "近1年涨幅 +19.4%", C["up"]),
        ("哈药市值", "约80亿", "小市值连板, 游资偏好", C["muted"]),
    ]

    for i, (label, val, sub, col) in enumerate(signals):
        x = 0.17 + i * 0.33
        ax.text(x, 0.23, label, ha="center", fontsize=9,
                color=C["muted"], transform=ax.transAxes)
        ax.text(x, 0.20, val, ha="center", fontsize=20, fontweight="bold",
                color=col, transform=ax.transAxes)
        ax.text(x, 0.175, sub, ha="center", fontsize=8,
                color=C["muted"], transform=ax.transAxes)

    ax.text(0.5, 0.10, "从原料药到CRO到终端, 全链路被资金扫了一遍",
            ha="center", fontsize=12, color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.4", fc=C["card"], ec=C["border"]),
            transform=ax.transAxes)

    add_footer(ax, 3)
    save(fig, 3)


# ═══════════════════════════════════════════════
# P4 — 散户情绪 + 封板率 + 炸板深度
# ═══════════════════════════════════════════════
def page4():
    fig, ax = new_card()
    pill(ax, 0.5, 0.95, "  散户情绪 + 封板深度  ", C["purple"])

    # 医药股东财人气 — 紧凑行距
    ax.text(0.5, 0.89, "医药股东财人气", ha="center", fontsize=14,
            fontweight="bold", color=C["text"], transform=ax.transAxes)

    med_hot = [
        ("昭衍新药", "603127", "#1", "+8.49%", "CRO龙头", C["up"]),
        ("哈药股份", "600664", "#2", "+10.02%", "5连板", C["up"]),
        ("海南海药", "000566", "#8", "+10.10%", "涨停", C["up"]),
        ("美诺华", "603538", "#9", "+6.54%", "原料药", C["up"]),
    ]

    for i, (name, code, rank, pct, tag, col) in enumerate(med_hot):
        y = 0.82 - i * 0.065
        if i % 2 == 0:
            card_bg(ax, 0.50, y, 0.88, 0.055)
        ax.text(0.08, y, rank, ha="center", fontsize=12, fontweight="bold",
                color=C["orange"], transform=ax.transAxes)
        ax.text(0.16, y, name, ha="left", fontsize=12, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        ax.text(0.40, y, pct, ha="center", fontsize=11, fontweight="bold",
                color=col, transform=ax.transAxes)
        ax.text(0.58, y, tag, ha="center", fontsize=9,
                color=C["cyan"], transform=ax.transAxes)
        ax.text(0.76, y, code, ha="center", fontsize=9,
                color=C["muted"], transform=ax.transAxes)

    # 封板率分析
    zt, zb = SUMMARY["zt_count"], SUMMARY["zb_count"]
    seal = zt / (zt + zb) * 100
    ax.plot([0.06, 0.94], [0.55, 0.55], color=C["border"], lw=0.8, transform=ax.transAxes)
    ax.text(0.5, 0.57, "封板质量", ha="center", fontsize=12,
            fontweight="bold", color=C["text"], transform=ax.transAxes)

    # 封板率条 + 标签
    ax.text(0.08, 0.525, "封板率", ha="left", fontsize=10, fontweight="bold",
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.08, 0.490, f"{seal:.0f}% ({zt}封 / {zt+zb}总)", ha="left",
            fontsize=9, color=C["text"], transform=ax.transAxes)
    bx, by, bw, bh = 0.40, 0.495, 0.50, 0.030
    ax.add_patch(FancyBboxPatch((bx, by), bw*seal/100, bh,
                                 boxstyle="round,pad=0.01", fc=C["up"], ec="none"))
    ax.add_patch(FancyBboxPatch((bx+bw*seal/100, by), bw*(1-seal/100), bh,
                                 boxstyle="round,pad=0.01", fc="#3d444d", ec="none"))
    ax.plot([bx+bw*0.8, bx+bw*0.8], [by-0.005, by+bh+0.005],
            color=C["muted"], lw=0.6, transform=ax.transAxes)
    ax.text(bx+bw*0.80, by-0.018, "警戒80%", ha="center",
            fontsize=7, color=C["muted"], transform=ax.transAxes)

    # 炸板分析
    ax.text(0.5, 0.445, f"炸板 {zb} 只 — 分行业看:", ha="center",
            fontsize=11, color=C["text"], transform=ax.transAxes)

    zb_stocks = SUMMARY["zb_top5"]
    for i, stk in enumerate(zb_stocks):
        y = 0.415 - i * 0.030
        times_label = f"炸{stk['炸板次数']}次" if stk['炸板次数'] > 1 else "炸1次"
        ax.text(0.12, y, f"• {stk['名称']}", ha="left", fontsize=9, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        ax.text(0.38, y, stk['所属行业'][:5], ha="left", fontsize=8,
                color=C["muted"], transform=ax.transAxes)
        ax.text(0.58, y, times_label, ha="left", fontsize=8,
                color=C["down"], transform=ax.transAxes)

    # 评价
    ax.text(0.5, 0.250, "48涨停 + 83%封板率 → 情绪偏热",
            ha="center", fontsize=11, color=C["orange"],
            bbox=dict(boxstyle="round,pad=0.3", fc=C["card"], ec=C["border"]),
            transform=ax.transAxes)
    ax.text(0.5, 0.210, "炸板集中在IT服务(紫光/神州数码), 科技线追高有阻力",
            ha="center", fontsize=9.5, color=C["muted"], transform=ax.transAxes)

    # 雪球
    ax.text(0.5, 0.165, "雪球热议: 药明康德 3.1万讨论量",
            ha="center", fontsize=11, fontweight="bold", color=C["purple"],
            transform=ax.transAxes)

    ax.text(0.5, 0.10, "翻到下一页 → 哈药30年连板史深度解读",
            ha="center", fontsize=10, color=C["muted"], style="italic",
            transform=ax.transAxes)

    add_footer(ax, 4)
    save(fig, 4)


# ═══════════════════════════════════════════════
# P5 — 哈药个股深度: 30年连板史
# ═══════════════════════════════════════════════
def page5():
    fig, ax = new_card()
    pill(ax, 0.5, 0.95, "  哈药30年连板史  ", C["orange"])

    ax.text(0.5, 0.89, "30年仅3次4连板, 从无一回5连板",
            ha="center", fontsize=16, fontweight="bold", color=C["text"],
            transform=ax.transAxes)
    ax.text(0.5, 0.85, "这一刻是哈药上市30年来的里程碑",
            ha="center", fontsize=11, color=C["muted"], transform=ax.transAxes)

    # 时间线: 3次4连板 + 本次5连板
    timeline = [
        ("1994.08", "4连板", "暴涨68.6%", "次日-18.6%", C["down"],
         "早期股市, 涨跌幅限制不同, 参考价值有限"),
        ("2020.02", "4连板", "疫情概念", "T+5 -20.7%", C["down"],
         "疫情受益概念, 4连板后追高者被深埋"),
        ("2026.07", "5连板!", "30年首次", "进行中...", C["up"],
         "连板接力? 还是历史性转折?"),
    ]

    for i, (date, board, note, t5, col, desc) in enumerate(timeline):
        y = 0.76 - i * 0.18
        # 卡片
        card_bg(ax, 0.50, y, 0.88, 0.16)
        # 左: 日期 + 连板数
        ax.text(0.12, y + 0.04, date, ha="center", fontsize=10,
                color=C["muted"], transform=ax.transAxes)
        ax.text(0.12, y + 0.005, board, ha="center", fontsize=24, fontweight="bold",
                color=col, transform=ax.transAxes)
        # 中: 关键指标
        ax.text(0.30, y + 0.04, note, ha="left", fontsize=14, fontweight="bold",
                color=col, transform=ax.transAxes)
        ax.text(0.30, y + 0.005, f"后续: {t5}", ha="left", fontsize=12, fontweight="bold",
                color=col, transform=ax.transAxes)
        # 下: 描述
        ax.text(0.30, y - 0.035, desc, ha="left", fontsize=9.5,
                color=C["muted"], transform=ax.transAxes)

    # 当前基本面指标
    ax.text(0.5, 0.21, "当前基本面", ha="center", fontsize=12,
            fontweight="bold", color=C["text"], transform=ax.transAxes)

    metrics = [
        ("市值", "~80亿", C["muted"]),
        ("距ATH", "-61.8%", C["down"]),
        ("年涨幅", "+19.4%", C["up"]),
        ("位置", "52周新高", C["up"]),
    ]
    for i, (lbl, val, col) in enumerate(metrics):
        x = 0.12 + i * 0.24
        ax.text(x, 0.185, lbl, ha="center", fontsize=9,
                color=C["muted"], transform=ax.transAxes)
        ax.text(x, 0.16, val, ha="center", fontsize=18, fontweight="bold",
                color=col, transform=ax.transAxes)

    ax.text(0.5, 0.09,
            "小市值+深跌反弹+首次5连板 = 游资标准剧本\n但与2020年疫情4连板一样, 追高风险极大",
            ha="center", fontsize=10.5, color=C["muted"], transform=ax.transAxes)

    add_footer(ax, 5)
    save(fig, 5)


# ═══════════════════════════════════════════════
# P6 — 总结 + 前瞻
# ═══════════════════════════════════════════════
def page6():
    fig, ax = new_card()
    pill(ax, 0.5, 0.95, "  今日总结 + 前瞻  ", C["gold"])

    ax.text(0.5, 0.87, "三句话看懂今天", ha="center",
            fontsize=18, fontweight="bold", color=C["text"], transform=ax.transAxes)

    points = [
        ("01", "30年首次 — 哈药5连板", C["up"],
         "历史最高仅4连板×3次, 今天是里程碑事件, 资金集中火力打医药链"),
        ("02", "全产业链联动, 不是孤妖", C["up"],
         "化学制药/生物疫苗/医疗器械/医疗服务齐涨, 9只医药股涨停"),
        ("03", "封板率82.8% 情绪偏热", C["orange"],
         "48涨停10炸板, 但紫光/神州数码等科技线被砸, 注意明日分化"),
    ]

    for i, (num, title, col, body) in enumerate(points):
        y = 0.78 - i * 0.14
        if i > 0:
            ax.plot([0.10, 0.90], [y + 0.07, y + 0.07],
                    color=C["border"], lw=0.5, transform=ax.transAxes)
        ax.text(0.10, y + 0.01, num, ha="center", fontsize=36, fontweight="bold",
                color=col, transform=ax.transAxes)
        ax.text(0.22, y + 0.025, title, ha="left", fontsize=15, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        ax.text(0.22, y - 0.035, body, ha="left", fontsize=10,
                color=C["muted"], transform=ax.transAxes)

    # 明日预判
    ax.text(0.5, 0.34, "明日预判", ha="center", fontsize=13, fontweight="bold",
            color=C["text"], transform=ax.transAxes)

    preds = [
        "哈药5进6是关键坎 — 30年没有6连板历史, 明日天量换手概率大",
        "2020年4连板后T+5跌20%的前车之鉴, 追高性价比差",
        "如果哈药断板, 要看医药链其他补涨股能否接棒",
    ]
    for i, pred in enumerate(preds):
        ax.text(0.12, 0.31 - i * 0.028, f"• {pred}", ha="left", fontsize=9.5,
                color=C["muted"], transform=ax.transAxes)

    # 风险
    ax.text(0.5, 0.18, "散户友情提醒", ha="center", fontsize=11, fontweight="bold",
            color=C["bg"],
            bbox=dict(boxstyle="round,pad=0.3", fc=C["orange"], ec="none"),
            transform=ax.transAxes)

    # CTA
    ax.text(0.5, 0.10, "评论区聊聊 → 哈药明天还能6连板吗？",
            ha="center", fontsize=12, fontweight="bold", color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.4", fc=C["card"], ec=C["border"]),
            transform=ax.transAxes)

    add_footer(ax, 6)
    save(fig, 6)


if __name__ == "__main__":
    print(f"开始生成 6 页深度卡片 → {OUT}")
    page1(); page2(); page3(); page4(); page5(); page6()
    print("\n✅ 全部完成!")
