"""医药逆势涨停潮 · 7 页小红书卡片 (matplotlib 版, 复用 xhs_card_template)

题材: 2026-07-13 弱市抱团, 医药(化学制药/化学制品/中药)逆势涨停
数据: output/hotspot/20260713/summary.json + 东财午评新闻流
渲染: src/quant/... 的 xhs_card_template.XHSCard (项目自带暗色模板, 无需浏览器)
"""
from __future__ import annotations

from pathlib import Path

import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path("/das/user/QYJI/quant")
sys.path.insert(0, str(ROOT))
from xhs_card_template import XHSCard, COLORS, Metric
DATE = "20260713"
DAY_HUM = "2026-07-13"
TOPIC = "pharma_rally"
VERSION = "v1"
OUT = ROOT / f"output/hotspot/{DATE}/xhs_{TOPIC}_{VERSION}"
OUT.mkdir(parents=True, exist_ok=True)

CARD = XHSCard(total_pages=7, brand="复旦杰伦", source="东方财富/雪球")

DATE_TAG = f"{DAY_HUM} 弱市抱团"


# ───────────────────────── P1 封面 ─────────────────────────
def page_1():
    fig, ax = CARD.canvas()
    CARD.title(ax, DATE_TAG, "医药逆势", "涨停潮", accent="red", y1=0.86, size1=40, size2=56)
    ax.text(0.5, 0.66, "大盘暴跌 -1.54%, 唯独医药在涨", ha="center", va="center",
            fontsize=23, color=COLORS["muted"], transform=ax.transAxes)
    CARD.metrics_row(ax, [
        Metric("-1.54%", "沪指", "green"),
        Metric("24只", "涨停", "red"),
        Metric("8只", "医药系涨停", "gold"),
    ], y=0.46)
    CARD.insight_box(
        ax,
        "普跌日, 中药 / 化学制药 / 医药商业逆势走强",
        "化学制药·化学制品·中药 包揽涨停行业前三 — 弱市抱团主线",
        bottom=0.10, height=0.13, edge="gold",
    )
    CARD.footer(ax, 1)
    return fig


# ───────────────────────── P2 涨停天梯 ─────────────────────────
def page_2():
    fig, ax = CARD.canvas()
    CARD.title(ax, "涨停天梯", "医药系", "逆势封板", accent="red", y1=0.86, size1=40, size2=54)
    cards = [
        {"tag": "3连板", "name": "立方制药", "value": "+9.98%", "note": "化学制药", "color": "red"},
        {"tag": "2连板", "name": "哈药股份", "value": "+10.09%", "note": "化学制药", "color": "red"},
        {"tag": "20cm", "name": "日科化学", "value": "+20.00%", "note": "化学制品", "color": "red"},
        {"tag": "2只", "name": "中药Ⅱ", "value": "涨停", "note": "中药细分", "color": "gold"},
    ]
    CARD.stock_grid(ax, cards, top=0.66, bottom=0.30)
    ax.text(0.06, 0.235, "3 连板天梯里, 医药独占 2 席 (立方制药 / 哈药股份)",
            fontsize=18, color=COLORS["text"], transform=ax.transAxes)
    CARD.insight_box(
        ax,
        "化学制药 + 化学制品 + 中药 = 8 只医药系涨停",
        "占全天 24 只涨停约 1/3, 弱市里最整齐的连板梯队",
        bottom=0.09, height=0.13, edge="red",
    )
    CARD.footer(ax, 2)
    return fig


# ───────────────────────── P3 行业涨停分布 ─────────────────────────
def page_3():
    fig, ax = CARD.canvas()
    CARD.title(ax, "涨停地图", "涨停行业", "分布", accent="gold", y1=0.86, size1=40, size2=54)
    rows = [
        ("化学制药", 3, "red"),
        ("化学制品", 3, "red"),
        ("中药Ⅱ", 2, "gold"),
        ("燃气Ⅱ", 2, "muted"),
        ("通用设备", 2, "muted"),
    ]
    maxc = max(r[1] for r in rows)
    y0 = 0.66
    for i, (name, cnt, color) in enumerate(rows):
        y = y0 - i * 0.085
        ax.text(0.08, y, name, ha="left", va="center", fontsize=21,
                color=COLORS["text"], transform=ax.transAxes)
        w = 0.30 * cnt / maxc
        ax.add_patch(plt.Rectangle((0.34, y - 0.018), w, 0.030,
                     fc=COLORS[color], alpha=0.30, ec="none", transform=ax.transAxes))
        ax.add_patch(plt.Rectangle((0.34, y - 0.018), w, 0.030,
                     fill=False, ec=COLORS[color], lw=1.4, transform=ax.transAxes))
        ax.text(0.34 + w + 0.012, y, f"{cnt} 只", ha="left", va="center",
                fontsize=21, fontweight="bold", color=COLORS[color], transform=ax.transAxes)
    ax.text(0.08, 0.235, "医药系 (化学制药 + 化学制品 + 中药) 占涨停行业前三",
            fontsize=18, color=COLORS["text"], transform=ax.transAxes)
    CARD.insight_box(
        ax,
        "防御 + 低位 = 弱市避险首选",
        "中药 / 医药商业同列逆势走强, 资金抱团医药链",
        bottom=0.09, height=0.13, edge="gold",
    )
    CARD.footer(ax, 3)
    return fig


# ───────────────────────── P4 避险逻辑 ─────────────────────────
def page_4():
    fig, ax = CARD.canvas()
    CARD.title(ax, "避险逻辑", "弱市为什么", "抱医药?", accent="cyan", y1=0.84, size1=36, size2=50)
    CARD.metrics_row(ax, [
        Metric("4573", "下跌", "green"),
        Metric("892", "上涨", "red"),
        Metric("24只", "涨停", "red"),
    ], y=0.63)
    CARD.contrast_boxes(
        ax,
        {"title": "逆势走强", "value": "医药链", "note": "中药·化学制药·医药商业·红利·燃气", "color": "green"},
        {"title": "集体领跌", "value": "科技链", "note": "商业航天·算力PCB·MLCC·军工电子", "color": "red"},
        y=0.27, h=0.22,
    )
    CARD.insight_box(
        ax,
        "全市场 4573 只绿, 唯医药在涨",
        "跌的是高位科技, 涨的是低位防御 — 资金切防御",
        bottom=0.09, height=0.13, edge="cyan",
    )
    CARD.footer(ax, 4)
    return fig


# ───────────────────────── P5 风险警示 ─────────────────────────
def page_5():
    fig, ax = CARD.canvas()
    CARD.title(ax, "风险提示", "追高之前", "看一眼风险", accent="orange", y1=0.84, size1=34, size2=48)
    ax.text(0.5, 0.65, "炸板率 54%   ·   13 只炸板   ·   星网锐捷炸板 3 次",
            ha="center", va="center", fontsize=22, fontweight="bold",
            color=COLORS["orange"], transform=ax.transAxes)
    cards = [
        {"tag": "退市", "name": "国华退", "value": "3连板", "note": "末日轮·极高风险", "color": "orange"},
        {"tag": "炸板", "name": "星网锐捷", "value": "炸板3次", "note": "通信设备", "color": "orange"},
        {"tag": "炸板", "name": "杭氧股份", "value": "炸板", "note": "化学制品", "color": "orange"},
        {"tag": "炸板", "name": "凯美特气", "value": "炸板", "note": "化学制品", "color": "orange"},
    ]
    CARD.stock_grid(ax, cards, top=0.58, bottom=0.24)
    CARD.insight_box(
        ax,
        "3 连板里混进退市股, 炸板率高达 54%",
        "连板越高越危险, 炸板 = 追高被套",
        bottom=0.08, height=0.13, edge="orange",
    )
    CARD.footer(ax, 5)
    return fig


# ───────────────────────── P6 情绪照妖镜 ─────────────────────────
def page_6():
    fig, ax = CARD.canvas()
    CARD.title(ax, "情绪照妖镜", "真主线 vs", "假热度", accent="purple", y1=0.84, size1=36, size2=50)
    CARD.metrics_row(ax, [
        Metric("-8.17%", "京东方A", "green"),
        Metric("-8.17%", "兆易创新", "green"),
        Metric("#3", "赛力斯讨论", "gold"),
    ], y=0.63)
    CARD.contrast_boxes(
        ax,
        {"title": "真主线·医药", "value": "逆势涨停", "note": "没人聊却天天涨, 资金用脚投票", "color": "red"},
        {"title": "假热度·半导体", "value": "人气霸榜却跌", "note": "东财人气前10清一色半导体, 今日集体 -8%", "color": "green"},
        y=0.27, h=0.22,
    )
    CARD.insight_box(
        ax,
        "人气高 ≠ 会涨, 逆势涨停才是真主线",
        "赛力斯突冲雪球讨论第3 — 新热点值得盯",
        bottom=0.09, height=0.13, edge="purple",
    )
    CARD.footer(ax, 6)
    return fig


# ───────────────────────── P7 操作三档 + CTA ─────────────────────────
def page_7():
    fig, ax = CARD.canvas()
    CARD.title(ax, "操作指南", "三档", "怎么上?", accent="green", y1=0.86, size1=42, size2=54)
    tiers = [
        ("激进", "red", "已持有 → 看立方制药/哈药封单能否延续, 断板减仓"),
        ("稳健", "orange", "未持有 → 别追高, 等回踩 MA20 确认再上车"),
        ("长线", "cyan", "定投医药/中药 ETF, 防御属性 + 低位性价比"),
    ]
    y = 0.64
    for t, c, b in tiers:
        CARD.panel(ax, 0.06, y - 0.075, 0.88, 0.075, edge=c, face="panel", lw=1.2)
        ax.text(0.10, y - 0.037, t, ha="center", va="center", fontsize=22, fontweight="bold",
                color=COLORS[c], transform=ax.transAxes)
        ax.text(0.26, y - 0.037, b, ha="left", va="center", fontsize=19,
                color=COLORS["text"], transform=ax.transAxes)
        y -= 0.105
    CARD.cta(ax, "点关注 + 收藏, 明早 9:15 递盘前情报", y=0.27, color="cyan", size=20)
    CARD.insight_box(
        ax,
        "弱市抱团有持续性, 但连板高位需控仓",
        "医药是主线, 节奏比方向更重要",
        bottom=0.09, height=0.13, edge="green",
    )
    CARD.footer(ax, 7)
    return fig


PAGES = [page_1, page_2, page_3, page_4, page_5, page_6, page_7]


def main():
    for i, gen in enumerate(PAGES, 1):
        fig = gen()
        path = CARD.save(fig, OUT, i)
        print(f"  saved {path.name} ({path.stat().st_size/1024:.0f}KB)")
    print(f"\n✅ 7 页卡片 → {OUT}")


if __name__ == "__main__":
    main()
