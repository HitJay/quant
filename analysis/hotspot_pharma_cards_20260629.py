"""2026-06-29 医药热点 + 老登股副线 7 页小红书卡片."""

from __future__ import annotations

import json
from pathlib import Path
import textwrap

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATE = "20260629"
DAY_HUMAN = "2026-06-29"
SUMMARY_PATH = ROOT / f"output/hotspot/{DATE}/summary.json"
ZT_PATH = ROOT / f"output/hotspot/{DATE}/raw/zt_pool.parquet"
OUTPUT_DIR = ROOT / "output/2026-06-29/today-hotspots/cards"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SUMMARY = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
ZT_POOL = pd.read_parquet(ZT_PATH)

COLORS = {
    "bg": "#101418",
    "panel": "#171f24",
    "panel2": "#202a30",
    "line": "#35424a",
    "text": "#ecf2ee",
    "muted": "#9aa7a0",
    "dim": "#68766f",
    "pharma": "#49d17d",
    "old": "#f4c95d",
    "risk": "#ff6b5f",
    "blue": "#66b8ff",
    "cyan": "#5dd9c1",
    "ink": "#0b0f12",
}

CARD_WIDTH, CARD_HEIGHT, DPI = 7.2, 9.6, 200
TOTAL_PAGES = 7

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "Droid Sans Fallback", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.weight"] = "regular"


def wrap_cn(text: str, width: int) -> str:
    return "\n".join(textwrap.wrap(text, width=width, break_long_words=True, replace_whitespace=False))


def new_card() -> tuple[plt.Figure, plt.Axes]:
    figure, axis = plt.subplots(figsize=(CARD_WIDTH, CARD_HEIGHT), facecolor=COLORS["bg"])
    axis.set_facecolor(COLORS["bg"])
    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)
    axis.set_xticks([])
    axis.set_yticks([])
    for spine in axis.spines.values():
        spine.set_visible(False)
    return figure, axis


def add_footer(axis: plt.Axes, page_number: int) -> None:
    axis.text(
        0.05,
        0.035,
        "懂哥说",
        ha="left",
        va="center",
        fontsize=8,
        fontweight="bold",
        color=COLORS["ink"],
        bbox=dict(boxstyle="round,pad=0.26", fc=COLORS["cyan"], ec="none"),
        transform=axis.transAxes,
    )
    axis.text(
        0.5,
        0.035,
        "数据: 东方财富/雪球  不构成投资建议",
        ha="center",
        va="center",
        fontsize=8,
        color=COLORS["dim"],
        transform=axis.transAxes,
    )
    axis.text(
        0.95,
        0.035,
        f"{page_number}/{TOTAL_PAGES}",
        ha="right",
        va="center",
        fontsize=9,
        color=COLORS["muted"],
        transform=axis.transAxes,
    )


def pill(axis: plt.Axes, center_x: float, center_y: float, text: str, color: str, font_size: int = 11) -> None:
    axis.text(
        center_x,
        center_y,
        text,
        ha="center",
        va="center",
        fontsize=font_size,
        fontweight="bold",
        color=COLORS["ink"],
        bbox=dict(boxstyle="round,pad=0.42", fc=color, ec="none"),
        transform=axis.transAxes,
    )


def rounded_panel(
    axis: plt.Axes,
    left: float,
    bottom: float,
    width: float,
    height: float,
    face_color: str = "panel",
    edge_color: str = "line",
    alpha: float = 1.0,
    linewidth: float = 1.0,
) -> None:
    axis.add_patch(
        FancyBboxPatch(
            (left, bottom),
            width,
            height,
            boxstyle="round,pad=0.018,rounding_size=0.025",
            facecolor=COLORS[face_color],
            edgecolor=COLORS[edge_color],
            linewidth=linewidth,
            alpha=alpha,
            transform=axis.transAxes,
        )
    )


def draw_title(axis: plt.Axes, kicker: str, title: str, subtitle: str, accent: str) -> None:
    pill(axis, 0.5, 0.94, f"  {kicker}  ", COLORS[accent], font_size=10)
    axis.text(
        0.5,
        0.875,
        title,
        ha="center",
        va="center",
        fontsize=27,
        fontweight="bold",
        color=COLORS["text"],
        transform=axis.transAxes,
    )
    axis.text(
        0.5,
        0.825,
        subtitle,
        ha="center",
        va="center",
        fontsize=12,
        color=COLORS["muted"],
        transform=axis.transAxes,
    )


def draw_metric(axis: plt.Axes, center_x: float, center_y: float, value: str, label: str, color: str) -> None:
    axis.text(
        center_x,
        center_y,
        value,
        ha="center",
        va="center",
        fontsize=33,
        fontweight="bold",
        color=COLORS[color],
        transform=axis.transAxes,
    )
    axis.text(
        center_x,
        center_y - 0.055,
        label,
        ha="center",
        va="center",
        fontsize=10,
        color=COLORS["muted"],
        transform=axis.transAxes,
    )


def draw_bullet(axis: plt.Axes, top: float, text: str, color: str = "pharma", font_size: int = 12) -> float:
    axis.text(0.09, top, "-", ha="left", va="top", fontsize=font_size + 2, color=COLORS[color], transform=axis.transAxes)
    axis.text(
        0.13,
        top,
        wrap_cn(text, 26),
        ha="left",
        va="top",
        fontsize=font_size,
        color=COLORS["text"],
        linespacing=1.35,
        transform=axis.transAxes,
    )
    return top - 0.086


def industry_limit_up_names(industry: str, count: int = 8) -> list[str]:
    if "所属行业" not in ZT_POOL.columns or "名称" not in ZT_POOL.columns:
        return []
    stocks = ZT_POOL.loc[ZT_POOL["所属行业"].eq(industry), "名称"].head(count)
    return [str(stock_name) for stock_name in stocks]


def fmt_money(value: object) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if abs(number) >= 1e8:
        return f"{number / 1e8:.1f}亿"
    if abs(number) >= 1e4:
        return f"{number / 1e4:.0f}万"
    return f"{number:.0f}"


def save_card(figure: plt.Figure, page_number: int) -> None:
    output_path = OUTPUT_DIR / f"page_{page_number:02d}.png"
    figure.savefig(output_path, dpi=DPI, facecolor=COLORS["bg"], edgecolor="none")
    plt.close(figure)
    print(output_path)


def page_1() -> None:
    figure, axis = new_card()
    pill(axis, 0.5, 0.94, f"  {DAY_HUMAN} 盘中热点  ", COLORS["old"], font_size=11)
    axis.text(0.5, 0.84, "医药突然开大", ha="center", fontsize=38, fontweight="bold", color=COLORS["text"], transform=axis.transAxes)
    axis.text(0.5, 0.765, "老登股也没缺席", ha="center", fontsize=29, fontweight="bold", color=COLORS["old"], transform=axis.transAxes)
    axis.text(0.5, 0.705, "今天不是单一题材日, 是资金在重新找确定性", ha="center", fontsize=12, color=COLORS["muted"], transform=axis.transAxes)

    rounded_panel(axis, 0.07, 0.46, 0.86, 0.17, face_color="panel2", edge_color="pharma", linewidth=1.5)
    draw_metric(axis, 0.22, 0.565, "+4.63%", "医药生物", "pharma")
    draw_metric(axis, 0.50, 0.565, "13只", "化学制药涨停", "pharma")
    draw_metric(axis, 0.78, 0.565, "43只", "炸板", "risk")

    axis.text(0.5, 0.38, "一个有意思的反差", ha="center", fontsize=15, fontweight="bold", color=COLORS["cyan"], transform=axis.transAxes)
    axis.text(0.5, 0.315, wrap_cn("创新药、中药、医疗服务一起冲; 但茅台、格力、招商这些老牌关注股, 也还在散户讨论榜里。", 25), ha="center", va="center", fontsize=14, linespacing=1.45, color=COLORS["text"], transform=axis.transAxes)
    axis.text(0.5, 0.185, "所以今天的题, 不只是“医药涨了”", ha="center", fontsize=15, fontweight="bold", color=COLORS["old"], transform=axis.transAxes)
    axis.text(0.5, 0.135, "而是: 市场又开始偏爱能讲清楚现金流和确定性的东西", ha="center", fontsize=11, color=COLORS["muted"], transform=axis.transAxes)
    add_footer(axis, 1)
    save_card(figure, 1)


def page_2() -> None:
    figure, axis = new_card()
    draw_title(axis, "钱去哪了", "医药包了涨幅榜", "行业涨幅前五几乎全是药味", "pharma")
    top_industries = SUMMARY["industry_top5"]
    max_gain = max(industry["pct_chg"] for industry in top_industries)
    row_tops = [0.72, 0.64, 0.56, 0.48, 0.40]
    for row_top, industry in zip(row_tops, top_industries):
        bar_width = 0.42 * industry["pct_chg"] / max_gain
        rounded_panel(axis, 0.08, row_top - 0.035, 0.84, 0.052, face_color="panel", edge_color="line", alpha=0.85)
        axis.add_patch(Rectangle((0.34, row_top - 0.018), bar_width, 0.026, color=COLORS["pharma"], alpha=0.88, transform=axis.transAxes))
        axis.text(0.12, row_top + 0.006, industry["name"], ha="left", va="center", fontsize=12, color=COLORS["text"], transform=axis.transAxes)
        axis.text(0.88, row_top + 0.006, f"+{industry['pct_chg']:.2f}%", ha="right", va="center", fontsize=13, fontweight="bold", color=COLORS["pharma"], transform=axis.transAxes)
        axis.text(0.12, row_top - 0.022, f"领涨 {industry.get('leader_name', '')}  主力 {fmt_money(industry.get('main_net_in', 0))}", ha="left", va="center", fontsize=8.5, color=COLORS["muted"], transform=axis.transAxes)

    rounded_panel(axis, 0.08, 0.185, 0.84, 0.12, face_color="panel2", edge_color="cyan")
    axis.text(0.13, 0.265, "读法", ha="left", va="center", fontsize=13, fontweight="bold", color=COLORS["cyan"], transform=axis.transAxes)
    axis.text(0.13, 0.225, wrap_cn("今天不是一只药明康德带节奏, 而是生物制品、化学制药、医疗服务、中药一起抬头。", 27), ha="left", va="top", fontsize=11.5, linespacing=1.35, color=COLORS["text"], transform=axis.transAxes)
    add_footer(axis, 2)
    save_card(figure, 2)


def page_3() -> None:
    figure, axis = new_card()
    draw_title(axis, "涨停池", "药味从哪里来", "化学制药是今天最集中的涨停行业", "pharma")
    groups = [
        ("化学制药", "13只涨停", industry_limit_up_names("化学制药"), "pharma"),
        ("中药II", "5只涨停", industry_limit_up_names("中药Ⅱ"), "old"),
        ("医疗服务", "3只涨停", industry_limit_up_names("医疗服务"), "cyan"),
    ]
    panel_tops = [0.70, 0.49, 0.29]
    for panel_top, (industry, label, stocks, color_key) in zip(panel_tops, groups):
        rounded_panel(axis, 0.07, panel_top - 0.13, 0.86, 0.14, face_color="panel2", edge_color=color_key, linewidth=1.35)
        axis.text(0.12, panel_top - 0.025, industry, ha="left", va="center", fontsize=18, fontweight="bold", color=COLORS[color_key], transform=axis.transAxes)
        axis.text(0.88, panel_top - 0.025, label, ha="right", va="center", fontsize=14, fontweight="bold", color=COLORS["text"], transform=axis.transAxes)
        axis.text(0.12, panel_top - 0.085, wrap_cn(" / ".join(stocks), 24), ha="left", va="center", fontsize=11.5, linespacing=1.28, color=COLORS["muted"], transform=axis.transAxes)

    axis.text(0.5, 0.145, "这类行情最怕只看一个龙头", ha="center", fontsize=16, fontweight="bold", color=COLORS["old"], transform=axis.transAxes)
    axis.text(0.5, 0.095, "真正有用的是看扩散: 创新药、中药、CXO/医疗服务是否同时被资金承认", ha="center", fontsize=10.5, color=COLORS["muted"], transform=axis.transAxes)
    add_footer(axis, 3)
    save_card(figure, 3)


def page_4() -> None:
    figure, axis = new_card()
    draw_title(axis, "创新药", "今天的叙事钩子", "不是只有涨幅, 还有医保目录这个新闻锚", "blue")
    rounded_panel(axis, 0.07, 0.61, 0.86, 0.15, face_color="panel2", edge_color="blue")
    axis.text(0.12, 0.72, "新闻锚", ha="left", va="center", fontsize=13, fontweight="bold", color=COLORS["blue"], transform=axis.transAxes)
    axis.text(0.12, 0.675, wrap_cn("7款已在商保目录的创新药, 寻求进入新一轮基本医保目录。", 25), ha="left", va="center", fontsize=15, fontweight="bold", color=COLORS["text"], linespacing=1.35, transform=axis.transAxes)
    axis.text(0.12, 0.625, "这句话本身就够市场脑补: 放量、降价、商业化、政策窗口。", ha="left", va="center", fontsize=9.5, color=COLORS["muted"], transform=axis.transAxes)

    rounded_panel(axis, 0.07, 0.38, 0.41, 0.15, face_color="panel", edge_color="pharma")
    rounded_panel(axis, 0.52, 0.38, 0.41, 0.15, face_color="panel", edge_color="old")
    axis.text(0.275, 0.48, "药明康德", ha="center", fontsize=18, fontweight="bold", color=COLORS["pharma"], transform=axis.transAxes)
    axis.text(0.275, 0.43, "雪球讨论榜前十\n讨论量 30,788", ha="center", fontsize=11, color=COLORS["text"], linespacing=1.35, transform=axis.transAxes)
    axis.text(0.725, 0.48, "海思科/万邦", ha="center", fontsize=18, fontweight="bold", color=COLORS["old"], transform=axis.transAxes)
    axis.text(0.725, 0.43, "行业领涨代表\n药味从个股扩散", ha="center", fontsize=11, color=COLORS["text"], linespacing=1.35, transform=axis.transAxes)

    axis.text(0.5, 0.28, "但这里有个反常识", ha="center", fontsize=16, fontweight="bold", color=COLORS["risk"], transform=axis.transAxes)
    axis.text(0.5, 0.22, wrap_cn("医保目录不是单纯利好。它同时意味着进院放量和价格谈判, 所以更适合写“预期交易”, 不适合写“闭眼冲”。", 28), ha="center", va="center", fontsize=12, linespacing=1.4, color=COLORS["text"], transform=axis.transAxes)
    add_footer(axis, 4)
    save_card(figure, 4)


def page_5() -> None:
    figure, axis = new_card()
    draw_title(axis, "老登股", "它们其实也在场", "不冲涨停, 但一直是散户情绪锚", "old")
    old_discussions = [
        ("贵州茅台", "97,670", "长期关注第1"),
        ("格力电器", "40,368", "长期关注第4"),
        ("招商银行", "32,296", "长期关注第3"),
        ("恒瑞医药", "关注榜", "医药老牌核心"),
    ]
    positions = [(0.08, 0.58), (0.53, 0.58), (0.08, 0.37), (0.53, 0.37)]
    for (left, bottom), (name, value, note) in zip(positions, old_discussions):
        rounded_panel(axis, left, bottom, 0.39, 0.16, face_color="panel2", edge_color="old")
        axis.text(left + 0.195, bottom + 0.108, name, ha="center", va="center", fontsize=17, fontweight="bold", color=COLORS["old"], transform=axis.transAxes)
        axis.text(left + 0.195, bottom + 0.062, value, ha="center", va="center", fontsize=20, fontweight="bold", color=COLORS["text"], transform=axis.transAxes)
        axis.text(left + 0.195, bottom + 0.026, note, ha="center", va="center", fontsize=9, color=COLORS["muted"], transform=axis.transAxes)

    rounded_panel(axis, 0.08, 0.18, 0.84, 0.14, face_color="panel", edge_color="cyan")
    axis.text(0.13, 0.275, "内容切法", ha="left", fontsize=13, fontweight="bold", color=COLORS["cyan"], transform=axis.transAxes)
    axis.text(0.13, 0.232, wrap_cn("老登股不是今天最猛, 而是市场不想玩纯题材时, 它们会重新变成比较坐标。", 26), ha="left", va="top", fontsize=11, linespacing=1.32, color=COLORS["text"], transform=axis.transAxes)
    axis.text(0.5, 0.12, "这条副线, 能把医药内容写得更像人话", ha="center", fontsize=13.5, fontweight="bold", color=COLORS["old"], transform=axis.transAxes)
    add_footer(axis, 5)
    save_card(figure, 5)


def page_6() -> None:
    figure, axis = new_card()
    draw_title(axis, "别上头", "热闹不等于好追", "今天的短线情绪其实很拧巴", "risk")
    rounded_panel(axis, 0.07, 0.56, 0.86, 0.18, face_color="panel2", edge_color="risk", linewidth=1.4)
    draw_metric(axis, 0.22, 0.665, str(SUMMARY["zt_count"]), "涨停", "pharma")
    draw_metric(axis, 0.50, 0.665, str(SUMMARY["zb_count"]), "炸板", "risk")
    draw_metric(axis, 0.78, 0.665, f"{SUMMARY['zt_max_board']}板", "最高高度", "old")

    current_top = 0.46
    current_top = draw_bullet(axis, current_top, "79只涨停说明场子热, 但43只炸板说明追高并不舒服。", "risk", 12)
    current_top = draw_bullet(axis, current_top, "最高只有3连板, 代表短线高度还没有真正打开。", "old", 12)
    draw_bullet(axis, current_top, "医药是今天的主线, 但主线和买点是两件事。", "pharma", 12)

    axis.text(0.5, 0.17, "一句话", ha="center", fontsize=13, color=COLORS["muted"], transform=axis.transAxes)
    axis.text(0.5, 0.125, "可以复盘, 不要把复盘写成劝人追板", ha="center", fontsize=16, fontweight="bold", color=COLORS["risk"], transform=axis.transAxes)
    add_footer(axis, 6)
    save_card(figure, 6)


def page_7() -> None:
    figure, axis = new_card()
    draw_title(axis, "发文选题", "今天最值得写这条", "医药主线 + 老登股副线 + 风险刹车", "cyan")
    topics = [
        ("主标题", "创新药又爆了: 今天医药为什么突然成主线?", "pharma"),
        ("副标题", "老登股没有消失, 它们只是换了一种方式回到讨论区", "old"),
        ("风险钩子", "79只涨停背后, 还有43只炸板", "risk"),
    ]
    panel_bottom = 0.63
    for label, title, color_key in topics:
        rounded_panel(axis, 0.07, panel_bottom, 0.86, 0.105, face_color="panel2", edge_color=color_key, linewidth=1.2)
        axis.text(0.12, panel_bottom + 0.073, label, ha="left", va="center", fontsize=9.5, fontweight="bold", color=COLORS[color_key], transform=axis.transAxes)
        axis.text(0.12, panel_bottom + 0.036, wrap_cn(title, 28), ha="left", va="center", fontsize=12.5, fontweight="bold", color=COLORS["text"], linespacing=1.22, transform=axis.transAxes)
        panel_bottom -= 0.145

    rounded_panel(axis, 0.07, 0.13, 0.86, 0.145, face_color="panel", edge_color="line")
    axis.text(0.12, 0.238, "正文第一句可以这样开", ha="left", fontsize=12, fontweight="bold", color=COLORS["cyan"], transform=axis.transAxes)
    axis.text(0.12, 0.202, wrap_cn("今天A股最有意思的不是医药涨了, 而是资金突然开始奖励那些能讲出业绩、政策和现金流逻辑的方向。", 30), ha="left", va="top", fontsize=11.2, linespacing=1.3, color=COLORS["text"], transform=axis.transAxes)
    axis.text(0.5, 0.092, "收藏这组, 收盘后可以再补龙虎榜", ha="center", fontsize=13.5, fontweight="bold", color=COLORS["old"], transform=axis.transAxes)
    add_footer(axis, 7)
    save_card(figure, 7)


def main() -> None:
    for page_func in (page_1, page_2, page_3, page_4, page_5, page_6, page_7):
        page_func()


if __name__ == "__main__":
    main()