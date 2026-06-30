"""2026-06-30 小红书 7 页卡片 - 苹果概念背后的 AI 硬件链.

故事线: 今日最强表面是苹果概念, 底层是光学光电子、通信设备、元件、
电子、半导体共同扩散的 AI 硬件链。重点讲板块宽度和资金路径, 避免写成
单票喊单。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from xhs_card_template import COLORS as C, XHSCard, money_text, wrap_text  # noqa: E402

DATE = "20260630"
DAY_HUMAN = "2026-06-30"
BASE = ROOT / "output/2026-06-30/today-hotspot"
OUT = BASE / "cards_ai_hardware"
SUMMARY = json.loads((BASE / "summary.json").read_text(encoding="utf-8"))
ZT_POOL = pd.read_parquet(BASE / "raw/zt_pool.parquet")
XQ_TWEET = pd.read_parquet(BASE / "raw/xueqiu_tweet.parquet")
CONCEPT = pd.read_parquet(BASE / "raw/concept_board.parquet")
INDUSTRY = pd.read_parquet(BASE / "raw/industry_board.parquet")

card = XHSCard(total_pages=7, brand="复旦杰伦")


def pct_text(value: float) -> str:
    return f"{value:+.2f}%"


def money_e(value: object) -> str:
    return money_text(value)


def find_row(rows: list[dict], name: str) -> dict:
    for row in rows:
        if row.get("name") == name:
            return row
    raise KeyError(name)


def industry_row(name: str) -> dict:
    row = INDUSTRY.loc[INDUSTRY["name"].eq(name)]
    if row.empty:
        raise KeyError(name)
    return row.iloc[0].to_dict()


def concept_row(name: str) -> dict:
    row = CONCEPT.loc[CONCEPT["name"].eq(name)]
    if row.empty:
        raise KeyError(name)
    return row.iloc[0].to_dict()


APPLE = concept_row("苹果概念")
WEARABLE = concept_row("智能穿戴")
IOT = concept_row("物联网")
CLOUD = concept_row("云计算")
OPTICAL = industry_row("光学光电子")
COMM = industry_row("通信设备")
SEMI = industry_row("半导体")
COMPONENT = industry_row("元件")
ELECTRONICS = industry_row("电子")
CONSUMER = industry_row("消费电子")
DEFENSE = industry_row("国防军工")


def save(fig, page: int) -> None:
    path = card.save(fig, OUT, page)
    print(path)


def add_side_label(ax, text: str, y: float, color: str = "gold") -> None:
    ax.text(
        0.06,
        y,
        text,
        fontsize=10.5,
        color=C["ink"],
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.30", fc=C[color], ec="none"),
        transform=ax.transAxes,
    )


def page_1() -> None:
    fig, ax = card.canvas()
    ax.text(0.06, 0.945, f"今日主线 · {DAY_HUMAN}", fontsize=14, color=C["gold"], transform=ax.transAxes, fontweight="bold")
    ax.text(0.5, 0.855, "苹果概念大涨", fontsize=34, color=C["text"], transform=ax.transAxes, ha="center", fontweight="bold")
    ax.text(0.5, 0.805, "先别急着喊苹果", fontsize=25, color=C["muted"], transform=ax.transAxes, ha="center", fontweight="bold")

    ax.text(0.5, 0.675, "+104亿", fontsize=80, color=C["red"], transform=ax.transAxes, ha="center", fontweight="bold")
    ax.text(0.5, 0.610, "苹果概念主力净流入", fontsize=15, color=C["muted"], transform=ax.transAxes, ha="center")
    ax.text(0.5, 0.565, f"涨幅 {pct_text(APPLE['pct_chg'])} · 上涨 {int(APPLE['up_count'])} / 下跌 {int(APPLE['down_count'])}", fontsize=14, color=C["gold"], transform=ax.transAxes, ha="center", fontweight="bold")

    hero_cards = [
        ("电子", f"{money_e(ELECTRONICS['main_net_in'])}", "主力净流入", "red"),
        ("光学光电子", pct_text(OPTICAL["pct_chg"]), "行业涨幅第 1", "cyan"),
    ]
    for x, (title, value, note, color) in zip([0.07, 0.52], hero_cards):
        card.panel(ax, x, 0.365, 0.41, 0.145, edge=color, face="panel2", lw=1.2)
        ax.text(x + 0.205, 0.472, title, fontsize=13, color=C["muted"], transform=ax.transAxes, ha="center")
        ax.text(x + 0.205, 0.420, value, fontsize=27, color=C[color], transform=ax.transAxes, ha="center", fontweight="bold")
        ax.text(x + 0.205, 0.382, note, fontsize=10.5, color=C["muted"], transform=ax.transAxes, ha="center")

    metrics = [
        (str(SUMMARY["zt_count"]), "只涨停", "gold", True),
        (f"{SUMMARY['zt_max_board']}板", "最高连板", "cyan", False),
        ("5条", "电子链同涨", "orange", False),
    ]
    for i, (value, note, color, mono) in enumerate(metrics):
        x = [0.20, 0.50, 0.80][i]
        ax.text(x, 0.285, value, fontsize=30, color=C[color], transform=ax.transAxes, ha="center", fontweight="bold", fontfamily="monospace" if mono else None)
        ax.text(x, 0.242, note, fontsize=11, color=C["muted"], transform=ax.transAxes, ha="center")

    card.cta(ax, "数字结论: 表面是苹果, 底层是 AI 硬件链", y=0.155, color="cyan", size=14.5)
    ax.text(0.5, 0.098, "翻下去: 用板块、资金、涨停宽度拆开看", fontsize=11.5, color=C["muted"], transform=ax.transAxes, ha="center")
    card.footer(ax, 1)
    save(fig, 1)


def page_2() -> None:
    fig, ax = card.canvas()
    card.header(ax, "PAGE 02 · 板块证据", "谁在一起涨", "如果只是苹果概念, 不会有这么宽的电子链扩散")
    rows = [OPTICAL, COMM, SEMI, COMPONENT, ELECTRONICS]
    max_pct = max(float(row["pct_chg"]) for row in rows)
    for i, row in enumerate(rows):
        y = 0.705 - i * 0.100
        card.panel(ax, 0.06, y - 0.038, 0.88, 0.078, face="panel2", edge="border", lw=0.6)
        ax.text(0.09, y + 0.014, row["name"], fontsize=15.2, color=C["text"], transform=ax.transAxes, fontweight="bold")
        ax.text(0.09, y - 0.018, f"上涨 {int(row['up_count'])} / 下跌 {int(row['down_count'])} · 领涨 {row['leader_name']}", fontsize=10.2, color=C["muted"], transform=ax.transAxes)
        width = 0.25 * float(row["pct_chg"]) / max_pct
        ax.add_patch(Rectangle((0.43, y - 0.014), width, 0.030, fc=C["red"], alpha=0.34, ec="none", transform=ax.transAxes))
        ax.text(0.755, y + 0.002, pct_text(row["pct_chg"]), fontsize=14, color=C["red"], transform=ax.transAxes, ha="right", fontweight="bold")
        ax.text(0.895, y + 0.002, money_e(row["main_net_in"]), fontsize=10.8, color=C["gold"], transform=ax.transAxes, ha="right")
    card.insight_box(ax, "这不是单点行情", "光学、通信、元件、电子、半导体同步进攻; 主线宽度比连板高度更重要", bottom=0.095, height=0.12, edge="gold")
    card.footer(ax, 2)
    save(fig, 2)


def page_3() -> None:
    fig, ax = card.canvas()
    card.header(ax, "PAGE 03 · 资金路径", "钱是怎么走的", "从消费电子标签, 扩散到 AI 硬件基础设施")
    nodes = [
        ("入口标签", "苹果概念", pct_text(APPLE["pct_chg"]), money_e(APPLE["main_net_in"]), "gold"),
        ("终端形态", "智能穿戴", pct_text(WEARABLE["pct_chg"]), money_e(WEARABLE["main_net_in"]), "cyan"),
        ("连接层", "通信设备", pct_text(COMM["pct_chg"]), money_e(COMM["main_net_in"]), "blue"),
        ("零部件", "元件", pct_text(COMPONENT["pct_chg"]), money_e(COMPONENT["main_net_in"]), "orange"),
        ("上游大脑", "半导体", pct_text(SEMI["pct_chg"]), money_e(SEMI["main_net_in"]), "purple"),
    ]
    for i, (tag, name, pct, net, color) in enumerate(nodes):
        y = 0.725 - i * 0.118
        card.panel(ax, 0.08, y - 0.038, 0.84, 0.084, edge=color, face="panel2", lw=1.0)
        ax.text(0.115, y + 0.008, tag, fontsize=8.8, color=C["ink"], fontweight="bold", bbox=dict(boxstyle="round,pad=0.25", fc=C[color], ec="none"), transform=ax.transAxes)
        ax.text(0.285, y + 0.006, name, fontsize=17, color=C["text"], fontweight="bold", transform=ax.transAxes)
        ax.text(0.635, y + 0.006, pct, fontsize=16, color=C["red"], fontweight="bold", transform=ax.transAxes, ha="right")
        ax.text(0.885, y + 0.006, net, fontsize=12.5, color=C["gold"], transform=ax.transAxes, ha="right")
    card.insight_box(ax, "一句话: 苹果只是入口", "真正被交易的是端侧 AI 硬件弹性, 要看概念能不能扩成产业链", bottom=0.080, height=0.115, edge="cyan")
    card.footer(ax, 3)
    save(fig, 3)


def page_4() -> None:
    fig, ax = card.canvas()
    card.header(ax, "PAGE 04 · 反共识", "半导体不是最干净", "涨幅很强, 但资金更集中在光学、通信、元件")
    compare = [
        ("通信设备", COMM, "blue"),
        ("光学光电子", OPTICAL, "cyan"),
        ("元件", COMPONENT, "orange"),
        ("半导体", SEMI, "purple"),
    ]
    max_net = max(abs(float(row["main_net_in"])) for _, row, _ in compare)
    for i, (name, row, color) in enumerate(compare):
        y = 0.690 - i * 0.135
        card.panel(ax, 0.07, y - 0.048, 0.86, 0.100, face="panel2", edge=color, lw=1.0)
        ax.text(0.11, y + 0.020, name, fontsize=16, color=C["text"], transform=ax.transAxes, fontweight="bold")
        ax.text(0.11, y - 0.020, f"涨幅 {pct_text(row['pct_chg'])} · 净流入占比 {float(row['main_net_in_pct']):.2f}%", fontsize=10.6, color=C["muted"], transform=ax.transAxes)
        width = 0.30 * abs(float(row["main_net_in"])) / max_net
        ax.add_patch(Rectangle((0.45, y - 0.015), width, 0.033, fc=C[color], alpha=0.34, ec="none", transform=ax.transAxes))
        ax.text(0.865, y + 0.002, money_e(row["main_net_in"]), fontsize=14.5, color=C[color], transform=ax.transAxes, ha="right", fontweight="bold")
    card.insight_box(ax, "数据里的反直觉", "半导体 +4.43%, 但净流入只有 4.3 亿; 通信设备是 100.5 亿", bottom=0.085, height=0.12, edge="gold")
    card.footer(ax, 4)
    save(fig, 4)


def page_5() -> None:
    fig, ax = card.canvas()
    card.header(ax, "PAGE 05 · 涨停验证", "强度来自宽度", "最高只有 3 板, 但电子链涨停分布很集中")
    industries = SUMMARY["zt_top_industries"][:5]
    max_count = max(item["涨停数"] for item in industries)
    for i, item in enumerate(industries):
        y = 0.715 - i * 0.085
        width = 0.42 * item["涨停数"] / max_count
        ax.text(0.08, y, item["行业"], fontsize=15, color=C["text"], transform=ax.transAxes, va="center", fontweight="bold")
        ax.add_patch(Rectangle((0.36, y - 0.018), width, 0.034, fc=C["red"], alpha=0.32, ec="none", transform=ax.transAxes))
        ax.text(0.84, y, f"{item['涨停数']} 只", fontsize=15, color=C["red"], transform=ax.transAxes, ha="right", va="center", fontweight="bold")

    samples = []
    for industry in ["光学光电", "半导体", "通信设备"]:
        names = ZT_POOL.loc[ZT_POOL["所属行业"].eq(industry), "名称"].head(4).astype(str).tolist()
        if names:
            samples.append((industry, " / ".join(names)))
    card.panel(ax, 0.06, 0.105, 0.88, 0.210, face="panel2", edge="cyan", lw=1.0)
    ax.text(0.10, 0.275, "涨停样本", fontsize=13.5, color=C["cyan"], transform=ax.transAxes, fontweight="bold")
    ax.text(0.73, 0.275, "不是妖股高度, 是板块宽度", fontsize=11.2, color=C["gold"], transform=ax.transAxes, ha="center", fontweight="bold")
    y = 0.225
    for industry, names in samples:
        ax.text(0.10, y, industry, fontsize=12.2, color=C["gold"], transform=ax.transAxes, fontweight="bold")
        ax.text(0.26, y, wrap_text(names, 35), fontsize=10.8, color=C["muted"], transform=ax.transAxes, va="center", linespacing=1.2)
        y -= 0.052
    card.footer(ax, 5)
    save(fig, 5)


def page_6() -> None:
    fig, ax = card.canvas()
    card.header(ax, "PAGE 06 · 散户雷达", "讨论也在往硬件挤", "白马还在榜首, 但科技链已经挤进核心讨论区")
    tech_names = {"胜宏科技", "寒武纪", "新易盛", "中际旭创", "药明康德"}
    rows = XQ_TWEET.head(9).to_dict("records")
    for i, row in enumerate(rows):
        y = 0.735 - i * 0.055
        name = row["股票简称"]
        is_tech = name in tech_names
        color = "cyan" if is_tech else "muted"
        if is_tech:
            ax.add_patch(Rectangle((0.055, y - 0.021), 0.89, 0.039, fc=C["cyan"], alpha=0.10, ec="none", transform=ax.transAxes))
        ax.text(0.08, y, f"{i + 1:02d}", fontsize=12.5, color=C[color], transform=ax.transAxes, va="center", fontweight="bold")
        ax.text(0.17, y, name, fontsize=14, color=C["text"], transform=ax.transAxes, va="center", fontweight="bold" if is_tech else "regular")
        ax.text(0.50, y, str(row["股票代码"]), fontsize=10.5, color=C["muted"], transform=ax.transAxes, va="center")
        ax.text(0.88, y, f"讨论 {float(row['关注']) / 10000:.1f}w", fontsize=11.5, color=C[color], transform=ax.transAxes, ha="right", va="center")
    card.insight_box(ax, "关注度结论", "胜宏科技、寒武纪、新易盛、中际旭创挤进前十, 算力硬件情绪还在", bottom=0.075, height=0.105, edge="cyan")
    card.footer(ax, 6)
    save(fig, 6)


def page_7() -> None:
    fig, ax = card.canvas()
    card.header(ax, "PAGE 07 · 明日观察", "别把复盘写成喊单", "明天只看 5 个信号, 不靠脑补")
    checks = [
        ("01", "苹果概念", "能否继续站在概念涨幅前列", "gold"),
        ("02", "光学 / 通信 / 元件", "是否继续有净流入, 不只是一日游", "cyan"),
        ("03", "半导体", "资金能否补上, 否则只是普涨标签", "purple"),
        ("04", "涨停高度", "最高 3 板能否抬到 4-5 板", "orange"),
        ("05", "弱势方向", "医药、银行、食品饮料是否继续失血", "blue"),
    ]
    for i, (num, title, body, color) in enumerate(checks):
        y = 0.715 - i * 0.115
        card.panel(ax, 0.07, y - 0.045, 0.86, 0.083, face="panel2", edge="border", lw=0.7)
        ax.text(0.10, y - 0.004, num, fontsize=22, color=C[color], transform=ax.transAxes, fontweight="bold", va="center")
        ax.text(0.205, y + 0.012, title, fontsize=15.5, color=C["text"], transform=ax.transAxes, fontweight="bold", va="center")
        ax.text(0.205, y - 0.023, body, fontsize=11.2, color=C["muted"], transform=ax.transAxes, va="center")
    card.insight_box(ax, "最终判断", "今天适合讲产业链扩散, 不适合追着单票讲故事", bottom=0.075, height=0.105, edge="gold")
    card.footer(ax, 7)
    save(fig, 7)


def main() -> None:
    for func in (page_1, page_2, page_3, page_4, page_5, page_6, page_7):
        func()


if __name__ == "__main__":
    main()