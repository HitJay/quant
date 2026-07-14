"""炸板科普 · 6 页小红书卡片 (matplotlib 版, 复用 xhs_card_template)

题材: 2026-07-14 涨停81只 炸板21只 — 封板率74%, 教育向科普
数据: output/hotspot/20260714/summary.json
渲染: xhs_card_template.XHSCard
"""
from __future__ import annotations

from pathlib import Path
import json
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

ROOT = Path("/das/user/QYJI/quant")
sys.path.insert(0, str(ROOT))
from xhs_card_template import XHSCard, COLORS, Metric

DATE = "20260714"
DAY_HUM = "2026-07-14"
TOPIC = "zhaban_edu"
VERSION = "v1"
OUT = ROOT / f"output/hotspot/{DATE}/xhs_{TOPIC}_{VERSION}"
OUT.mkdir(parents=True, exist_ok=True)

CARD = XHSCard(total_pages=6, brand="复旦杰伦", source="东方财富/雪球")

# 加载数据
with open(ROOT / f"output/hotspot/{DATE}/summary.json") as f:
    S = json.load(f)

ZT_COUNT = S["zt_count"]
ZB_COUNT = S["zb_count"]
SEAL_RATE = round((ZT_COUNT - ZB_COUNT) / ZT_COUNT * 100) if ZT_COUNT else 0
MAX_BOARD = S["zt_max_board"]
ZB_LIST = S["zb_top5"]

DATE_TAG = f"{DAY_HUM} 收盘复盘"


# ───────────────────────── P1 封面 ─────────────────────────
def page_1():
    fig, ax = CARD.canvas()
    CARD.title(ax, DATE_TAG, "炸板", "是怎么回事?", accent="red", y1=0.86, size1=40, size2=56)

    ax.text(0.5, 0.66, "涨停没封住 = 炸板 · 今天 21 只中招",
            ha="center", va="center", fontsize=23, color=COLORS["muted"],
            transform=ax.transAxes)

    CARD.metrics_row(ax, [
        Metric(f"{ZT_COUNT}只", "涨停", "red"),
        Metric(f"{ZB_COUNT}只", "炸板", "orange"),
        Metric(f"{SEAL_RATE}%", "封板率", "purple"),
    ], y=0.46)

    CARD.insight_box(
        ax,
        "有人涨停数钱, 有人炸板吃面",
        "今天国际连炸3次 — 追板的散户是怎么被埋的?",
        bottom=0.08, height=0.15, edge="red",
    )
    CARD.footer(ax, 1)
    return fig


# ───────────────────────── P2 什么是炸板 ─────────────────────────
def page_2():
    fig, ax = CARD.canvas()
    CARD.header(ax, "科普", "涨停没封住 = 炸板", "2分钟看懂追板踩坑机制")

    # 三个步骤卡片
    steps = [
        {"num": "01", "title": "涨停封板", "desc": "买盘压倒卖盘\n股价顶到涨停价\n买单排起长队等成交",
         "color": "red", "y": 0.72},
        {"num": "02", "title": "板上撤单", "desc": "大单突然撤走\n买盘塌方 封单消失\n排队散户被晾在板上",
         "color": "orange", "y": 0.48},
        {"num": "03", "title": "炸板回落", "desc": "卖盘涌出 价格跳水\n板上成交的散户\n当天就被套牢",
         "color": "green", "y": 0.24},
    ]
    for s in steps:
        y = s["y"]
        CARD.panel(ax, 0.07, y, 0.86, 0.195, edge=s["color"])
        CARD.pill(ax, 0.16, y + 0.09, s["num"], s["color"], 18)
        ax.text(0.31, y + 0.09, s["title"], ha="left", va="center",
                fontsize=20, fontweight="bold", color=COLORS[s["color"]],
                transform=ax.transAxes)
        ax.text(0.31, y + 0.055, s["desc"], ha="left", va="center",
                fontsize=14, color=COLORS["text"], transform=ax.transAxes,
                linespacing=1.6)

    CARD.footer(ax, 2)
    return fig


# ───────────────────────── P3 今天炸板案例 ─────────────────────────
def page_3():
    fig, ax = CARD.canvas()
    CARD.header(ax, "今日案例", "今天炸了 21 只", "炸板次数最多的 5 只, 你看过哪只?")

    zb_colors = ["red", "orange", "orange", "gold", "gold"]
    for i, (item, color) in enumerate(zip(ZB_LIST, zb_colors)):
        y = 0.72 - i * 0.12
        code = item["代码"]
        name = item["名称"]
        industry = item["所属行业"]
        cnt = item["炸板次数"]

        tag = f"炸{cnt}次!" if cnt >= 3 else f"炸{cnt}次"
        CARD.pill(ax, 0.12, y + 0.03, tag, color, 13)

        ax.text(0.22, y + 0.04, name, ha="left", va="center",
                fontsize=24, fontweight="bold", color=COLORS["text"],
                transform=ax.transAxes)
        ax.text(0.22, y - 0.02, f"{code} · {industry}", ha="left", va="center",
                fontsize=13, color=COLORS["muted"], transform=ax.transAxes)
        ax.axhline(y - 0.045, xmin=0.07, xmax=0.93, color=COLORS["border"],
                   lw=0.5, alpha=0.4)

    CARD.footer(ax, 3)
    return fig


# ───────────────────────── P4 为什么散户最容易被埋 ─────────────────────────
def page_4():
    fig, ax = CARD.canvas()
    CARD.header(ax, "散户心理", "追涨停 = 刀尖舔血", "三个致命陷阱, 你中了哪条?")

    traps = [
        {"tag": "陷阱1", "title": "排板买不到, 买到就炸",
         "body": "封板时买盘排队几十万手, 你以为排到了就能赚 — 但能让你买到的, 往往是封单已经开始撤了",
         "color": "red", "y": 0.69},
        {"tag": "陷阱2", "title": "涨停板 = 最高价买入",
         "body": "涨停价买入意味着成本是当日最高价。一炸板, 当天浮亏可能 5-10%, 第二天低开再亏一轮",
         "color": "orange", "y": 0.45},
        {"tag": "陷阱3", "title": "炸板恐慌 = 踩踏式卖出",
         "body": "炸板后散户争先逃跑, 卖盘涌出没有对手盘。你想止损都止不掉, 越是小票越容易锁死",
         "color": "green", "y": 0.21},
    ]
    for t in traps:
        y = t["y"]
        CARD.panel(ax, 0.07, y, 0.86, 0.195, edge=t["color"])
        CARD.pill(ax, 0.15, y + 0.09, t["tag"], t["color"], 15)
        ax.text(0.30, y + 0.09, t["title"], ha="left", va="center",
                fontsize=19, fontweight="bold", color=COLORS[t["color"]],
                transform=ax.transAxes)
        ax.text(0.30, y + 0.05, t["body"], ha="left", va="center",
                fontsize=13, color=COLORS["text"], transform=ax.transAxes,
                linespacing=1.7)

    CARD.footer(ax, 4)
    return fig


# ───────────────────────── P5 封板率看市场温度 ─────────────────────────
def page_5():
    fig, ax = CARD.canvas()
    CARD.header(ax, "数据视角", "封板率 = 市场温度计", "一个数字看穿今天是牛市还是熊市")

    # 三个档位
    tiers = [
        {"label": "高封板率 ≥85%", "sub": "牛市信号 · 资金充裕",
         "desc": "涨停票几乎都封住了\n追板成功率较高\n但警惕过热追高风险",
         "color": "red", "y": 0.66},
        {"label": "中封板率 70-85%", "sub": "震荡市 · 分化明显",
         "desc": "有人吃肉有人吃面\n选股能力决定成败\n龙头封得住, 跟风容易炸",
         "color": "gold", "y": 0.38},
    ]
    tier3_y = 0.10

    for t in tiers:
        y = t["y"]
        CARD.panel(ax, 0.07, y, 0.86, 0.225, edge=t["color"])
        ax.text(0.5, y + 0.17, t["label"], ha="center", va="center",
                fontsize=21, fontweight="bold", color=COLORS[t["color"]],
                transform=ax.transAxes)
        ax.text(0.5, y + 0.10, t["sub"], ha="center", va="center",
                fontsize=14, color=COLORS["muted"], transform=ax.transAxes)
        ax.text(0.5, y + 0.055, t["desc"], ha="center", va="center",
                fontsize=13, color=COLORS["text"], transform=ax.transAxes,
                linespacing=1.7)

    # 低封板率特殊标注
    CARD.panel(ax, 0.07, tier3_y, 0.86, 0.22, edge="green")
    ax.text(0.5, tier3_y + 0.17, "低封板率 <70%", ha="center", va="center",
            fontsize=21, fontweight="bold", color=COLORS["green"],
            transform=ax.transAxes)
    ax.text(0.5, tier3_y + 0.10, "熊市/恐慌信号 · 追板≈送钱",
            ha="center", va="center", fontsize=14, color=COLORS["muted"],
            transform=ax.transAxes)
    ax.text(0.5, tier3_y + 0.058, "涨停大部分封不住 · 炸板率飙升\n散户打板的绞肉机模式", ha="center", va="center",
            fontsize=13, color=COLORS["text"], transform=ax.transAxes,
            linespacing=1.7)

    CARD.footer(ax, 5)
    return fig


# ───────────────────────── P6 总结 + CTA ─────────────────────────
def page_6():
    fig, ax = CARD.canvas()
    CARD.header(ax, "总结", "炸板不是运气差", "三句话记牢, 少交学费")

    points = [
        ("01", "涨停买到就是赚?  错 — 能让你买到的, 往往是封单在撤", "red"),
        ("02", "追板先看封板率 — 低于 70% 的天, 不打板就是赚钱", "orange"),
        ("03", f"今天{ZT_COUNT}只涨停 / {ZB_COUNT}只炸板 — 每 4 只涨停就炸 1 只", "gold"),
    ]
    for i, (num, text, color) in enumerate(points):
        y = 0.70 - i * 0.14
        CARD.pill(ax, 0.09, y + 0.025, num, color, 16)
        ax.text(0.20, y + 0.025, text, ha="left", va="center",
                fontsize=18, color=COLORS["text"], transform=ax.transAxes)

    # 分隔线
    ax.axhline(0.35, xmin=0.07, xmax=0.93, color=COLORS["border"], lw=0.5, alpha=0.5)

    # 风险提示
    CARD.pill(ax, 0.5, 0.27, " 风险提示 ", "orange", 13)
    ax.text(0.5, 0.20, "涨停板是 A 股最锋利的双刃剑\n历史封板率不等于未来 · 追板前先问自己能否接受当日套牢",
            ha="center", va="center", fontsize=14, color=COLORS["muted"],
            transform=ax.transAxes, linespacing=1.6)

    CARD.cta(ax, "评论区聊聊: 你被炸过最惨的一次是什么票?", y=0.08, color="cyan")

    CARD.footer(ax, 6)
    return fig


# ───────────────────────── 渲染 ─────────────────────────
PAGES = [page_1, page_2, page_3, page_4, page_5, page_6]

if __name__ == "__main__":
    for fn in PAGES:
        fig = fn()
        page_num = PAGES.index(fn) + 1
        path = CARD.save(fig, OUT, page_num)
        print(f"  ✓ page_{page_num:02d}.png")

    print(f"\n产出目录: {OUT}")
    print("完成!")
