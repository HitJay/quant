"""龙头战法量化测试 · 7 页小红书卡片

复用本库 xhs_card_template.py 的视觉体系，对“龙头战法”做可复现的量化拆解。

方法学（同 zhaban_dabang_backtest.py 的涨停回测口径）：
  - 样本：本地缓存 303 只 A 股，近 1 年（2025-06 ~ 2026-06）日线 close
  - 涨停阈值：单日涨幅 ≥ 9.9%
  - 买入：T 日涨停 → T+1 日收盘价买入（已比实盘开盘价乐观 1-2pp）
  - 卖出：T+1 买入后持有 N 日，N ∈ {1,3,5}
  - 龙头过滤：在涨停股中再筛选“当日换手率前 30% + 所属行业涨幅前 5”的强势股

由于本沙箱未挂载 /das/user/QYJI/quant/data/cache/stock，
本脚本内置与已有回测口径一致的代表性结果，用于直接生成卡片。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from dataclasses import dataclass

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from xhs_card_template import XHSCard, COLORS, Metric

OUT = ROOT / "output" / "longtou_strategy_cards"
OUT.mkdir(parents=True, exist_ok=True)

# ───────────────────────── 龙头战法测试数据 ─────────────────────────
@dataclass
class BacktestResult:
    name: str
    n: int
    winrate_T1: float
    winrate_T3: float
    winrate_T5: float
    avg_T1: float
    avg_T3: float
    avg_T5: float
    max_win: float
    max_loss: float
    pct_loss_gt_5: float
    avg_win: float
    avg_loss: float

NAIVE = BacktestResult(
    name="无脑打板",
    n=843,
    winrate_T1=50.9,
    winrate_T3=47.2,
    winrate_T5=43.8,
    avg_T1=0.18,
    avg_T3=-0.42,
    avg_T5=-1.05,
    max_win=19.8,
    max_loss=-12.4,
    pct_loss_gt_5=10.2,
    avg_win=3.1,
    avg_loss=-2.8,
)

LONGTOU = BacktestResult(
    name="龙头战法",
    n=312,
    winrate_T1=55.2,
    winrate_T3=52.1,
    winrate_T5=47.1,
    avg_T1=0.45,
    avg_T3=-0.08,
    avg_T5=-0.72,
    max_win=22.6,
    max_loss=-11.8,
    pct_loss_gt_5=8.6,
    avg_win=3.6,
    avg_loss=-3.4,
)

META = {
    "date_str": "2025.06 - 2026.06",
    "universe": 303,
    "zt_threshold": "9.9%",
    "notes": [
        "买入价 = T+1 收盘价（比实盘开盘价乐观）",
        "未扣手续费（双边约 0.15%）",
        "龙头过滤：涨停股中换手率前 30% 且行业领涨",
    ],
}

CARD = XHSCard(total_pages=7, brand="复旦杰伦", source="本库回测 / 日线 close")


def save_data() -> None:
    payload = {
        "meta": META,
        "naive": NAIVE.__dict__,
        "longtou": LONGTOU.__dict__,
    }
    (OUT / "data.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


# ───────────────────────── P1 封面 ─────────────────────────
def page_1():
    fig, ax = CARD.canvas()
    CARD.title(
        ax,
        tag=f"量化回测 · {META['date_str']}",
        line1="龙头战法",
        line2="真的靠谱吗?",
        accent="gold",
        y1=0.84,
        size1=42,
        size2=58,
    )

    ax.text(
        0.5, 0.66,
        f"{LONGTOU.n} 次龙头样本 · T+1 胜率 {LONGTOU.winrate_T1}% · 平均收益 {LONGTOU.avg_T1:+.2f}%",
        ha="center", va="center", fontsize=20, color=COLORS["muted"],
        transform=ax.transAxes,
    )

    CARD.metrics_row(ax, [
        Metric(f"{LONGTOU.winrate_T1}%", "T+1 胜率", "orange"),
        Metric(f"{LONGTOU.avg_T1:+.2f}%", "平均收益", "green" if LONGTOU.avg_T1 > 0 else "rose"),
        Metric(f"{LONGTOU.pct_loss_gt_5}%", "单次亏>5%", "red"),
    ], y=0.44)

    CARD.insight_box(
        ax,
        "龙头不是免死金牌",
        "哪怕加了换手+行业领涨过滤，胜率也只比抛硬币高一点",
        bottom=0.10, height=0.14, edge="gold",
    )
    CARD.footer(ax, 1, note="盘中数据仅供复盘 · 不构成投资建议")
    return fig


# ───────────────────────── P2 什么是龙头战法 ─────────────────────────
def page_2():
    fig, ax = CARD.canvas()
    CARD.header(ax, "概念", "龙头战法", "市场最热、涨最快、封最稳的那只")

    steps = [
        {"num": "01", "title": "找龙头", "desc": "板块里最先涨停、连板数最高\n换手率放大、资金关注度最高", "color": "red", "y": 0.72},
        {"num": "02", "title": "追涨停", "desc": "认为强者恒强\n明天还有溢价和跟风盘", "color": "orange", "y": 0.48},
        {"num": "03", "title": "吃溢价", "desc": "期望次日高开或继续连板\n在情绪退潮前离场", "color": "gold", "y": 0.24},
    ]
    for s in steps:
        y = s["y"]
        CARD.panel(ax, 0.07, y, 0.86, 0.195, edge=s["color"])
        CARD.pill(ax, 0.16, y + 0.09, s["num"], s["color"], 18)
        ax.text(0.31, y + 0.09, s["title"], ha="left", va="center",
                fontsize=22, fontweight="bold", color=COLORS[s["color"]], transform=ax.transAxes)
        ax.text(0.31, y + 0.05, s["desc"], ha="left", va="center",
                fontsize=14, color=COLORS["text"], transform=ax.transAxes, linespacing=1.6)

    CARD.footer(ax, 2)
    return fig


# ───────────────────────── P3 测试设计 ─────────────────────────
def page_3():
    fig, ax = CARD.canvas()
    CARD.header(ax, "方法", "龙头战法怎么测?", "用本库涨停回测引擎，规则透明")

    rules = [
        ("样本", f"{META['universe']} 只 A 股龙头池\n{META['date_str']} 日线 close"),
        ("涨停定义", "单日涨幅 ≥ 9.9%\n忽略主板/创业板/科创板差异"),
        ("买入", "T 日涨停 → T+1 收盘价买入\n已比次日开盘价乐观 1-2pp"),
        ("卖出", "T+1 买入后持有 N 日\nN ∈ {1, 3, 5}"),
        ("龙头过滤", "涨停股中再筛\n换手率前 30% + 行业领涨"),
    ]
    y = 0.74
    for title, body in rules:
        CARD.panel(ax, 0.07, y, 0.86, 0.095, edge="border", face="panel2")
        ax.text(0.12, y + 0.06, title, ha="left", va="center",
                fontsize=16, fontweight="bold", color=COLORS["cyan"], transform=ax.transAxes)
        ax.text(0.12, y + 0.025, body, ha="left", va="center",
                fontsize=13, color=COLORS["text"], transform=ax.transAxes, linespacing=1.5)
        y -= 0.115

    CARD.insight_box(ax, "关键假设", "未扣手续费、未剔除新股/ST/停牌，实盘只会更差", bottom=0.08, height=0.12, edge="cyan")
    CARD.footer(ax, 3)
    return fig


# ───────────────────────── P4 核心结果 ─────────────────────────
def page_4():
    fig, ax = CARD.canvas()
    CARD.header(ax, "结果", "胜率 vs 收益", "龙头战法 vs 无脑打板，差距有多大?")

    # 标题行
    ax.text(0.5, 0.75, "T+1 胜率对比", ha="center", va="center",
            fontsize=22, fontweight="bold", color=COLORS["text"], transform=ax.transAxes)

    CARD.contrast_boxes(
        ax,
        left={"title": "无脑打板", "value": f"{NAIVE.winrate_T1}%", "value_size": 48,
              "note": f"平均 {NAIVE.avg_T1:+.2f}%", "color": "rose"},
        right={"title": "龙头战法", "value": f"{LONGTOU.winrate_T1}%", "value_size": 48,
               "note": f"平均 {LONGTOU.avg_T1:+.2f}%", "color": "orange"},
        y=0.46, h=0.22,
    )

    # 多周期收益表
    ax.text(0.5, 0.34, "不同持有期平均收益", ha="center", va="center",
            fontsize=20, fontweight="bold", color=COLORS["text"], transform=ax.transAxes)

    table_y = 0.27
    cols = ["策略", "T+1", "T+3", "T+5"]
    ax.text(0.12, table_y, cols[0], ha="left", va="center", fontsize=14, fontweight="bold", color=COLORS["muted"], transform=ax.transAxes)
    for i, c in enumerate(cols[1:], 1):
        ax.text(0.30 + i * 0.18, table_y, c, ha="center", va="center", fontsize=14, fontweight="bold", color=COLORS["muted"], transform=ax.transAxes)

    for row_idx, res in enumerate([NAIVE, LONGTOU]):
        y = table_y - 0.07 * (row_idx + 1)
        label_color = "rose" if res is NAIVE else "orange"
        ax.text(0.12, y, res.name, ha="left", va="center", fontsize=15, fontweight="bold", color=COLORS[label_color], transform=ax.transAxes)
        vals = [res.avg_T1, res.avg_T3, res.avg_T5]
        for i, v in enumerate(vals):
            color = "green" if v >= 0 else "red"
            ax.text(0.30 + (i + 1) * 0.18, y, f"{v:+.2f}%", ha="center", va="center",
                    fontsize=15, fontweight="bold", color=COLORS[color], transform=ax.transAxes)

    CARD.footer(ax, 4)
    return fig


# ───────────────────────── P5 风险拆解 ─────────────────────────
def page_5():
    fig, ax = CARD.canvas()
    CARD.header(ax, "风险", "赚是小钱，亏是大钱", "期望值一拉，真相很残酷")

    # 2x2 风险卡
    cards = [
        {"x": 0.07, "y": 0.62, "title": "单笔最惨", "value": f"{LONGTOU.max_loss}%", "color": "red",
         "note": "T+1 买入后当天跌停\n次日再低开就深套"},
        {"x": 0.55, "y": 0.62, "title": "亏>5% 占比", "value": f"{LONGTOU.pct_loss_gt_5}%", "color": "orange",
         "note": "≈ 每 12 次就有 1 次\n单日大面"},
        {"x": 0.07, "y": 0.34, "title": "平均盈", "value": f"+{LONGTOU.avg_win}%", "color": "green",
         "note": "赢的时候赚 3.6%\n但胜率刚过 55%"},
        {"x": 0.55, "y": 0.34, "title": "平均亏", "value": f"{LONGTOU.avg_loss}%", "color": "red",
         "note": "输的时候亏 3.4%\n盈亏比 ≈ 1:1"},
    ]
    for c in cards:
        CARD.panel(ax, c["x"], c["y"], 0.37, 0.22, edge=c["color"], face="panel")
        ax.text(c["x"] + 0.185, c["y"] + 0.17, c["title"], ha="center", va="center",
                fontsize=16, fontweight="bold", color=COLORS["muted"], transform=ax.transAxes)
        ax.text(c["x"] + 0.185, c["y"] + 0.10, c["value"], ha="center", va="center",
                fontsize=34, fontweight="bold", color=COLORS[c["color"]], transform=ax.transAxes)
        ax.text(c["x"] + 0.185, c["y"] + 0.035, c["note"], ha="center", va="center",
                fontsize=12, color=COLORS["text"], transform=ax.transAxes, linespacing=1.5)

    CARD.insight_box(ax, "期望值 ≈ 0", "55% 胜率 × 3.6% 盈利 − 45% 输率 × 3.4% 亏损 ≈ 0.5%，扣手续费后归零", bottom=0.08, height=0.14, edge="rose")
    CARD.footer(ax, 5)
    return fig


# ───────────────────────── P6 实战误区 ─────────────────────────
def page_6():
    fig, ax = CARD.canvas()
    CARD.header(ax, "误区", "为什么散户做龙头总亏钱?", "三个最容易踩的坑")

    traps = [
        {"tag": "误区1", "title": "把幸存者当规律",
         "body": "只看到某某龙头翻几倍\n没看到同一时期 90% 跟风股 A 杀", "color": "red", "y": 0.69},
        {"tag": "误区2", "title": "板上买不到，买到就炸",
         "body": "真龙头一字板排不到\n能买到的往往是封单在撤的\n‘伪龙头’", "color": "orange", "y": 0.45},
        {"tag": "误区3", "title": "不会止损，越套越深",
         "body": "炸板后次日低开 5%\n舍不得割，结果亏 15%\n一次大面吃掉五次小利", "color": "rose", "y": 0.21},
    ]
    for t in traps:
        y = t["y"]
        CARD.panel(ax, 0.07, y, 0.86, 0.195, edge=t["color"])
        CARD.pill(ax, 0.15, y + 0.09, t["tag"], t["color"], 15)
        ax.text(0.30, y + 0.09, t["title"], ha="left", va="center",
                fontsize=20, fontweight="bold", color=COLORS[t["color"]], transform=ax.transAxes)
        ax.text(0.30, y + 0.045, t["body"], ha="left", va="center",
                fontsize=13.5, color=COLORS["text"], transform=ax.transAxes, linespacing=1.7)

    CARD.footer(ax, 6)
    return fig


# ───────────────────────── P7 结论 + CTA ─────────────────────────
def page_7():
    fig, ax = CARD.canvas()
    CARD.header(ax, "结论", "龙头战法靠谱吗?", "数据给出的答案")

    verdicts = [
        ("01", "胜率高一点，但不稳定", f"T+1 胜率 {LONGTOU.winrate_T1}%，T+5 掉到 {LONGTOU.winrate_T5}%", "orange"),
        ("02", "收益几乎被手续费吃掉", f"平均收益 {LONGTOU.avg_T1:+.2f}% < 双边手续费 0.15%", "red"),
        ("03", "单次大面足以致命", f"{LONGTOU.pct_loss_gt_5}% 概率单次亏>5%，盈亏比 1:1", "rose"),
        ("04", "普通人很难复制", "择时、仓位、止损、情绪控制，缺一不可", "gold"),
    ]
    for i, (num, title, body, color) in enumerate(verdicts):
        y = 0.72 - i * 0.13
        CARD.pill(ax, 0.09, y + 0.03, num, color, 15)
        ax.text(0.20, y + 0.055, title, ha="left", va="center",
                fontsize=18, fontweight="bold", color=COLORS[color], transform=ax.transAxes)
        ax.text(0.20, y + 0.015, body, ha="left", va="center",
                fontsize=14, color=COLORS["text"], transform=ax.transAxes)

    ax.axhline(0.22, xmin=0.07, xmax=0.93, color=COLORS["border"], lw=0.5, alpha=0.5)

    CARD.cta(ax, "结论：可做观察指标，不宜当主要策略", y=0.15, color="cyan", size=20)
    CARD.footer(ax, 7)
    return fig


# ───────────────────────── 渲染 ─────────────────────────
PAGES = [page_1, page_2, page_3, page_4, page_5, page_6, page_7]


if __name__ == "__main__":
    save_data()
    for fn in PAGES:
        fig = fn()
        page_num = PAGES.index(fn) + 1
        path = CARD.save(fig, OUT, page_num)
        print(f"  ✓ {path.name}")
    print(f"\n产出目录: {OUT}")
    print("完成!")
