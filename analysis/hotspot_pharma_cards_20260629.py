"""2026-06-29 医药热点 7 页小红书卡片 — FCF 排版风格."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import pandas as pd
from matplotlib.patches import Rectangle


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from xhs_card_template import COLORS as C, XHSCard, money_text, wrap_text  # noqa: E402


DATE = "20260629"
DAY_HUMAN = "2026-06-29"
OUT = ROOT / "output/2026-06-29/today-hotspots/cards"
SUMMARY = json.loads((ROOT / f"output/hotspot/{DATE}/summary.json").read_text(encoding="utf-8"))
ZT_POOL = pd.read_parquet(ROOT / f"output/hotspot/{DATE}/raw/zt_pool.parquet")

card = XHSCard(total_pages=7, brand="复旦杰伦")


def pct_text(value: float) -> str:
    return f"{value:+.2f}%"


def limit_up_names(industry: str, n: int = 8) -> list[str]:
    stocks = ZT_POOL.loc[ZT_POOL["所属行业"].eq(industry), "名称"].head(n)
    return [str(item) for item in stocks]


def save(fig, page: int) -> None:
    print(card.save(fig, OUT, page))


def data_note(ax, text: str, y: float = 0.075) -> None:
    ax.text(0.5, y, text, fontsize=11.5, color=C["muted"], transform=ax.transAxes, ha="center")


def page_1() -> None:
    fig, ax = card.canvas()
    ax.text(0.06, 0.94, "热点复盘 · 医药主线真相", fontsize=14, color=C["red"],
            transform=ax.transAxes, fontweight="bold")
    ax.text(0.5, 0.83, "医药爆了", fontsize=46, color=C["text"],
            transform=ax.transAxes, ha="center", fontweight="bold")
    ax.text(0.5, 0.755, "但不是闭眼冲", fontsize=37, color=C["red"],
            transform=ax.transAxes, ha="center", fontweight="bold")
    ax.text(0.5, 0.700, "行业集体冲高 · 短线炸板也很多", fontsize=15.5,
            color=C["muted"], transform=ax.transAxes, ha="center")

    card.panel(ax, 0.07, 0.42, 0.41, 0.21, face="panel2")
    ax.text(0.275, 0.605, "医药生物", fontsize=15, color=C["muted"], transform=ax.transAxes, ha="center")
    ax.text(0.275, 0.555, "行业涨幅", fontsize=13, color=C["muted"], transform=ax.transAxes, ha="center")
    ax.text(0.275, 0.475, "+4.63%", fontsize=38, color=C["red"],
            transform=ax.transAxes, ha="center", fontweight="bold")

    card.panel(ax, 0.52, 0.42, 0.41, 0.21, face="panel2")
    ax.text(0.725, 0.605, "元件", fontsize=15, color=C["muted"], transform=ax.transAxes, ha="center")
    ax.text(0.725, 0.555, "行业跌幅", fontsize=13, color=C["muted"], transform=ax.transAxes, ha="center")
    ax.text(0.725, 0.475, "-5.81%", fontsize=38, color=C["down"],
            transform=ax.transAxes, ha="center", fontweight="bold")
    ax.text(0.5, 0.475, "→", fontsize=26, color=C["muted"], transform=ax.transAxes, ha="center")
    ax.text(0.5, 0.385, "强弱差 10.4 个百分点", fontsize=15.5, color=C["gold"],
            transform=ax.transAxes, ha="center", fontweight="bold")

    ax.text(0.06, 0.330, "TL;DR · 今天先记住 3 件事", fontsize=14, color=C["text"],
            transform=ax.transAxes, fontweight="bold")
    tldr = [
        ("01", "生物制品 / 化学制药 / 医疗服务 / 中药一起进涨幅榜", C["red"]),
        ("02", "化学制药 13 只涨停, 是今天最集中的药味来源", C["orange"]),
        ("03", "79 只涨停同时有 43 只炸板, 热闹不等于好追", C["gold"]),
    ]
    y = 0.270
    for number, text, color in tldr:
        ax.text(0.085, y, number, fontsize=22, color=color, transform=ax.transAxes, fontweight="bold")
        ax.text(0.155, y + 0.005, text, fontsize=13, color=C["text"], transform=ax.transAxes)
        y -= 0.060

    data_note(ax, f"数据截至 {DAY_HUMAN} 13:08 · 共 7 页盘中复盘")
    card.footer(ax, 1)
    save(fig, 1)


def page_2() -> None:
    fig, ax = card.canvas()
    card.header(ax, "PAGE 02 · 行业横向对比", "今天钱往哪搬", "涨幅榜几乎被医药占满, 硬件链在另一边承压")

    top = SUMMARY["industry_top5"]
    y_top, y_bot = 0.74, 0.36
    y_step = (y_top - y_bot) / 4
    max_abs = max(abs(x["pct_chg"]) for x in top + SUMMARY["industry_bottom5"])
    bar_max_w = 0.24

    ax.text(0.56, 0.805, "行业涨跌幅", fontsize=13, color=C["muted"],
            transform=ax.transAxes, ha="center", fontweight="bold")
    for i, item in enumerate(top):
        y = y_top - i * y_step
        ax.text(0.06, y + 0.014, item["name"], fontsize=15, color=C["text"],
                transform=ax.transAxes, fontweight="bold")
        ax.text(0.06, y - 0.018, f"领涨 {item.get('leader_name', '')}", fontsize=11,
                color=C["muted"], transform=ax.transAxes)
        width = abs(item["pct_chg"]) / max_abs * bar_max_w
        ax.add_patch(Rectangle((0.36, y - 0.014), width, 0.028, fc=C["red"], ec="none", transform=ax.transAxes))
        ax.text(0.64, y, pct_text(item["pct_chg"]), fontsize=15, color=C["red"],
                transform=ax.transAxes, va="center", ha="left", fontweight="bold")
        ax.text(0.80, y, money_text(item.get("main_net_in", 0)), fontsize=11, color=C["muted"],
                transform=ax.transAxes, va="center", ha="left")

    card.insight_box(
        ax,
        "结论: 不是单只龙头行情",
        "医药 5 个细分进涨幅榜, 更像板块扩散而不是孤立脉冲",
        bottom=0.16,
        height=0.13,
        edge="gold",
    )
    ax.text(0.5, 0.112, "对照组: 元件 -5.81% / 消费电子 -4.79% / 通信设备 -4.63%", fontsize=11.5,
            color=C["down"], transform=ax.transAxes, ha="center")
    card.footer(ax, 2)
    save(fig, 2)


def page_3() -> None:
    fig, ax = card.canvas()
    card.header(ax, "PAGE 03 · 涨停池真相", "药味从哪里来", "化学制药最集中, 中药和医疗服务跟着扩散")

    rows = [
        ("化学制药", "13", limit_up_names("化学制药"), C["red"]),
        ("中药II", "5", limit_up_names("中药Ⅱ"), C["orange"]),
        ("医疗服务", "3", limit_up_names("医疗服务"), C["cyan"]),
    ]
    y_top, card_h, gap = 0.67, 0.145, 0.035
    for i, (title, count, names, color) in enumerate(rows):
        y = y_top - i * (card_h + gap)
        card.panel(ax, 0.06, y, 0.88, card_h, face="panel2")
        ax.text(0.10, y + 0.080, count, fontsize=34, color=color, transform=ax.transAxes,
                fontweight="bold", va="center")
        ax.text(0.23, y + 0.095, title, fontsize=16, color=C["text"],
                transform=ax.transAxes, fontweight="bold")
        ax.text(0.23, y + 0.055, wrap_text(" / ".join(names), 32), fontsize=11,
                color=C["muted"], transform=ax.transAxes, va="center", linespacing=1.2)

    card.insight_box(
        ax,
        "三个持仓式结论",
        "① 化学制药是主线  ② 中药有扩散  ③ 医疗服务/CXO 给了第二层叙事",
        bottom=0.10,
        height=0.11,
        edge="red",
        face="panel",
    )
    card.footer(ax, 3)
    save(fig, 3)


def page_4() -> None:
    fig, ax = card.canvas()
    card.header(ax, "PAGE 04 · 新闻锚", "创新药为什么有故事", "医保目录窗口, 给了市场一个想象力入口")

    card.panel(ax, 0.06, 0.665, 0.88, 0.12, edge="purple", face="panel")
    ax.text(0.10, 0.745, "今日新闻锚", fontsize=13, color=C["purple"],
            transform=ax.transAxes, fontweight="bold")
    ax.text(0.10, 0.705, "7 款已在商保目录的创新药, 寻求进入新一轮基本医保目录",
            fontsize=14, color=C["text"], transform=ax.transAxes, fontweight="bold")

    cards = [
        ("BUZZ", "药明康德", "雪球讨论 3.1w", "医药 + CXO 双修", C["cyan"]),
        ("REAL", "海思科", "化学制药领涨", "行业一号信号", C["red"]),
        ("REAL", "万邦医药", "医疗服务领涨", "服务端扩散", C["red"]),
        ("WATCH", "恒瑞医药", "老牌医药坐标", "关注榜仍在", C["gold"]),
    ]
    positions = [(0.06, 0.45), (0.53, 0.45), (0.06, 0.25), (0.53, 0.25)]
    for (x, y), (tag, name, value, note, color) in zip(positions, cards):
        card.panel(ax, x, y, 0.41, 0.15, face="panel2")
        ax.text(x + 0.03, y + 0.112, tag, fontsize=8.5, color=C["ink"], fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.22", fc=color, ec="none"), transform=ax.transAxes)
        ax.text(x + 0.205, y + 0.105, name, fontsize=17, color=C["text"],
                transform=ax.transAxes, ha="center", fontweight="bold")
        ax.text(x + 0.205, y + 0.065, value, fontsize=13.5, color=color,
                transform=ax.transAxes, ha="center", fontweight="bold")
        ax.text(x + 0.205, y + 0.028, note, fontsize=10.5, color=C["muted"],
                transform=ax.transAxes, ha="center")

    card.insight_box(ax, "别把医保窗口写成无脑利好", "进目录 = 放量想象 + 价格谈判, 更适合写预期交易", bottom=0.09, height=0.11, edge="gold")
    card.footer(ax, 4)
    save(fig, 4)


def page_5() -> None:
    fig, ax = card.canvas()
    card.header(ax, "PAGE 05 · 老登股雷达", "老登股也没退场", "它们不一定最猛, 但一直是散户情绪锚")

    items = [
        ("01", "贵州茅台", "雪球讨论 9.8w · 长期关注第 1", C["red"]),
        ("02", "格力电器", "雪球讨论 4.0w · 长期关注第 4", C["blue"]),
        ("03", "招商银行", "雪球讨论 3.2w · 长期关注第 3", C["gold"]),
        ("04", "恒瑞医药", "医药老牌核心 · 关注榜仍在", C["green"]),
        ("05", "比亚迪", "雪球讨论 10.1w · 新能源车情绪锚", C["cyan"]),
    ]
    y_top, y_step = 0.72, 0.112
    for i, (num, title, body, color) in enumerate(items):
        y = y_top - i * y_step
        ax.text(0.08, y, num, fontsize=28, color=color, transform=ax.transAxes,
                fontweight="bold", va="center")
        ax.text(0.19, y + 0.016, title, fontsize=16, color=C["text"],
                transform=ax.transAxes, fontweight="bold")
        ax.text(0.19, y - 0.016, body, fontsize=11.5, color=C["muted"], transform=ax.transAxes)
        if i < len(items) - 1:
            ax.plot([0.08, 0.92], [y - 0.055, y - 0.055], color=C["border"], lw=0.4,
                    alpha=0.5, transform=ax.transAxes)

    card.insight_box(
        ax,
        "复旦杰伦短评",
        "市场不想玩纯题材时, 老登股会重新变成估值和现金流的比较坐标",
        bottom=0.08,
        height=0.10,
        edge="cyan",
    )
    card.footer(ax, 5)
    save(fig, 5)


def page_6() -> None:
    fig, ax = card.canvas()
    card.header(ax, "PAGE 06 · 现在该追吗", "三个客观信号", "热闹是真热闹, 但追高也是真难")

    signals = [
        {"title": "信号 1 · 涨停热度", "val": str(SUMMARY["zt_count"]), "note": "今日涨停数", "pill": "HOT", "color": C["red"], "expl": "场子很热\n医药主线够亮"},
        {"title": "信号 2 · 炸板风险", "val": str(SUMMARY["zb_count"]), "note": "今日炸板数", "pill": "RISK", "color": C["orange"], "expl": "追板容易坐过山车\n短线容错率不高"},
        {"title": "信号 3 · 高度未开", "val": f"{SUMMARY['zt_max_board']}板", "note": "最高连板", "pill": "WAIT", "color": C["gold"], "expl": "题材有热度\n但高度还没打开"},
    ]

    y_top, card_h, gap = 0.66, 0.16, 0.025
    for i, sig in enumerate(signals):
        y = y_top - i * (card_h + gap)
        card.panel(ax, 0.06, y, 0.88, card_h, face="panel2")
        ax.text(0.10, y + card_h - 0.030, sig["title"], fontsize=14, color=C["muted"],
                transform=ax.transAxes, fontweight="bold")
        ax.text(0.83, y + card_h - 0.030, sig["pill"], ha="center", va="center",
                fontsize=11.5, color=C["ink"], fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.35", fc=sig["color"], ec="none"),
                transform=ax.transAxes)
        ax.text(0.10, y + 0.045, sig["val"], fontsize=34, color=sig["color"],
                transform=ax.transAxes, fontweight="bold")
        ax.text(0.10, y + 0.020, sig["note"], fontsize=11.5, color=C["muted"], transform=ax.transAxes)
        for j, line in enumerate(sig["expl"].split("\n")):
            ax.text(0.60, y + card_h - 0.075 - j * 0.025, line, fontsize=13,
                    color=C["text"], transform=ax.transAxes)

    card.insight_box(ax, "结论: 可以复盘, 不要把复盘写成喊单", "主线和买点是两件事", bottom=0.07, height=0.10, edge="gold")
    card.footer(ax, 6)
    save(fig, 6)


def page_7() -> None:
    fig, ax = card.canvas()
    card.header(ax, "PAGE 07 · 怎么发", "买之前先认清你写的是什么", "5 句话把今天这条内容立住")

    strategies = [
        ("01", "主标题", "创新药又爆了: 今天医药为什么突然成主线?", C["red"]),
        ("02", "第一段", "先讲行业扩散: 生物制品/化学制药/医疗服务/中药一起冲", C["blue"]),
        ("03", "副线", "老登股没退场: 市场在重新找确定性", C["gold"]),
        ("04", "风险刹车", "79 只涨停背后, 还有 43 只炸板", C["orange"]),
        ("05", "收盘后补充", "等龙虎榜出来, 再看医药是不是机构真买", C["green"]),
    ]
    y_top, y_step = 0.76, 0.124
    for i, (num, title, body, color) in enumerate(strategies):
        y = y_top - i * y_step
        ax.text(0.08, y + 0.020, num, fontsize=28, color=color,
                transform=ax.transAxes, fontweight="bold", va="center")
        ax.text(0.18, y + 0.040, title, fontsize=14.5, color=C["text"],
                transform=ax.transAxes, fontweight="bold")
        ax.text(0.18, y + 0.010, wrap_text(body, 30), fontsize=11.5, color=C["muted"],
                transform=ax.transAxes, va="top")
        if i < len(strategies) - 1:
            ax.plot([0.08, 0.92], [y - 0.062, y - 0.062], color=C["border"], lw=0.4,
                    alpha=0.5, transform=ax.transAxes)

    card.insight_box(ax, "核心口诀", "医药主线 · 老登副线 · 炸板刹车 · 收盘补证据", bottom=0.07, height=0.09, edge="gold")
    card.footer(ax, 7)
    save(fig, 7)


def main() -> None:
    for func in (page_1, page_2, page_3, page_4, page_5, page_6, page_7):
        func()


if __name__ == "__main__":
    main()