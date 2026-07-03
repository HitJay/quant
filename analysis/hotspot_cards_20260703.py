"""20260703 热点卡片 — 恒尚节能 4 连板 + 汽车零部涨停潮.

数据源: output/2026-07-03/today-hotspot/20260703/summary.json
产物: output/2026-07-03/today-hotspot/20260703/xhs_cards_v1/
"""

from __future__ import annotations
import json
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
DATE = "20260703"
DAY_HUM = "2026-07-03"
TOPIC = "hotspot_review"
VERSION = 1

DATA_DIR = ROOT / f"output/2026-07-03/today-hotspot/{DATE}"
SUMMARY = json.loads((DATA_DIR / "summary.json").read_text(encoding="utf-8"))
TOPICS = json.loads((DATA_DIR / "topics.json").read_text(encoding="utf-8"))

OUT = DATA_DIR / f"xhs_cards_v{VERSION}"
OUT.mkdir(parents=True, exist_ok=True)

C = {
    "bg": "#0d1117", "card": "#161b22", "card2": "#1c2129", "border": "#30363d",
    "text": "#c9d1d9", "muted": "#8b949e", "dim": "#6e7681",
    "blue": "#58a6ff", "green": "#3fb950", "red": "#f85149",
    "orange": "#d2991d", "purple": "#bc8cff", "gold": "#f0c040",
    "cyan": "#56d4dd", "rose": "#ff7b72",
}
CARD_W, CARD_H, DPI = 7.2, 9.6, 200

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "Droid Sans Fallback", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def new_card():
    fig, ax = plt.subplots(figsize=(CARD_W, CARD_H), facecolor=C["bg"])
    ax.set_facecolor(C["bg"])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)
    return fig, ax


def add_footer(ax, page, total=4):
    ax.text(0.5, 0.025, "* 数据: 东方财富 · 收盘复盘 · 不构成投资建议",
            ha="center", va="center", fontsize=7, color=C["muted"], transform=ax.transAxes)
    ax.text(0.95, 0.025, f"{page}/{total}", ha="right", va="center",
            fontsize=8, color=C["muted"], transform=ax.transAxes)
    ax.text(0.05, 0.025, "复旦杰伦", ha="left", va="center",
            fontsize=8, color=C["dim"], transform=ax.transAxes)


def pill(ax, x, y, txt, fc, fs=10):
    ax.text(x, y, txt, ha="center", va="center", fontsize=fs, fontweight="bold",
            color=C["bg"], bbox=dict(boxstyle="round,pad=0.4", fc=fc, ec="none"),
            transform=ax.transAxes)


def card_bg(ax, x, y, w, h, fc=None, ec=None):
    fc = fc or C["card"]; ec = ec or C["border"]
    ax.add_patch(FancyBboxPatch((x - w/2, y - h/2), w, h,
                                boxstyle="round,pad=0.005,rounding_size=0.02",
                                fc=fc, ec=ec, lw=0.8, transform=ax.transAxes))


def save(fig, page):
    p = OUT / f"page_{page:02d}.png"
    fig.savefig(p, dpi=DPI, bbox_inches="tight",
                facecolor=C["bg"], edgecolor="none", pad_inches=0.15)
    plt.close(fig)
    print(f"  ✓ saved {p}")


def pct_str(v):
    return f"{float(v):+.2f}%"


# ═══════════════════════════════════════════
# Page 1 — 封面: 恒尚节能 4 连板 + 汽车零部涨停潮
# ═══════════════════════════════════════════
def page1():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, f"  {DAY_HUM} · 收盘复盘  ", C["gold"], fs=10)

    ax.text(0.5, 0.88, "恒尚节能 4 连板", ha="center", fontsize=32, fontweight="bold",
            color=C["red"], transform=ax.transAxes)
    ax.text(0.5, 0.81, "汽车零部涨停潮", ha="center", fontsize=24,
            fontweight="bold", color=C["text"], transform=ax.transAxes)

    # 三大数字
    nums = [
        ("60", "涨停", C["red"]),
        ("4 板", "最高连板", C["gold"]),
        ("15", "炸板", C["green"]),
    ]
    for i, (n, lbl, col) in enumerate(nums):
        x = 0.185 + i * 0.315
        card_bg(ax, x, 0.62, 0.27, 0.16)
        ax.text(x, 0.648, n, ha="center", fontsize=28, fontweight="bold",
                color=col, transform=ax.transAxes)
        ax.text(x, 0.572, lbl, ha="center", fontsize=11, color=C["muted"],
                transform=ax.transAxes)

    # 主线标签
    pill(ax, 0.3, 0.45, "  汽车零部 10 只涨停  ", C["orange"], fs=11)
    pill(ax, 0.7, 0.45, "  贵金属 +7.42%  ", C["red"], fs=11)

    # 一句话
    ax.text(0.5, 0.32, "宽度够了，高度还没打开", ha="center", fontsize=16,
            fontweight="bold", color=C["cyan"], transform=ax.transAxes)
    ax.text(0.5, 0.25, "明天看承接", ha="center", fontsize=14, color=C["muted"],
            transform=ax.transAxes)

    ax.text(0.5, 0.12, "→ 翻页看涨停天梯 & 行业拆解", ha="center", fontsize=11,
            color=C["cyan"], fontstyle="italic", transform=ax.transAxes)

    add_footer(ax, 1)
    save(fig, 1)


# ═══════════════════════════════════════════
# Page 2 — 涨停天梯 TOP10
# ═══════════════════════════════════════════
def page2():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  P2 · 涨停天梯  ", C["cyan"], fs=10)

    ax.text(0.5, 0.885, "今日涨停天梯 TOP10", ha="center", fontsize=22,
            fontweight="bold", color=C["text"], transform=ax.transAxes)

    zt_top = SUMMARY.get("zt_top10", [])
    # 表头
    headers = ["代码", "名称", "连板", "行业", "涨幅"]
    col_x = [0.08, 0.28, 0.52, 0.66, 0.88]
    for j, (hdr, cx) in enumerate(zip(headers, col_x)):
        ax.text(cx, 0.81, hdr, ha="left" if j < 2 else "center", fontsize=9,
                color=C["muted"], fontweight="bold", transform=ax.transAxes)

    # 分隔线
    ax.axhline(y=0.795, xmin=0.04, xmax=0.96, color=C["border"], lw=0.5)

    for i, item in enumerate(zt_top):
        y = 0.76 - i * 0.065
        boards = item.get("连板数", 0)
        bcolor = C["gold"] if boards >= 4 else (C["red"] if boards >= 3 else C["text"])
        row = [
            item.get("代码", ""),
            item.get("名称", ""),
            str(boards),
            item.get("所属行业", ""),
            pct_str(item.get("涨跌幅", 0)),
        ]
        aligns = ["left", "left", "center", "center", "center"]
        for j, (val, cx) in enumerate(zip(row, col_x)):
            c = bcolor if j == 2 else (C["text"] if j == 1 else C["muted"])
            fs = 11 if j == 1 else 10
            ax.text(cx, y, val, ha=aligns[j], fontsize=fs, color=c,
                    fontweight="bold" if j in (1, 2) else "normal",
                    transform=ax.transAxes)

    # 底部信息
    card_bg(ax, 0.5, 0.09, 0.88, 0.1, fc=C["card2"])
    ax.text(0.5, 0.11, "恒尚节能 4 连板领跑 · 宜宾纸业 3 连板跟随 · 8 只 2 连板",
            ha="center", fontsize=10, color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.07, "涨停宽度好但高度仅 4 板，说明投机情绪还没过热",
            ha="center", fontsize=9, color=C["dim"], transform=ax.transAxes)

    add_footer(ax, 2)
    save(fig, 2)


# ═══════════════════════════════════════════
# Page 3 — 行业 & 概念拆解
# ═══════════════════════════════════════════
def page3():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  P3 · 行业 & 概念拆解  ", C["cyan"], fs=10)

    # 左半：行业涨幅 TOP5
    ax.text(0.15, 0.885, "行业涨幅 TOP5", ha="center", fontsize=14,
            fontweight="bold", color=C["red"], transform=ax.transAxes)
    ind_top = SUMMARY.get("industry_top5", [])
    for i, item in enumerate(ind_top):
        y = 0.82 - i * 0.095
        name = item.get("name", "")
        pct = item.get("pct_chg", 0)
        leader = item.get("leader_name", "")
        net_in = float(item.get("main_net_in", 0)) / 1e8
        # 名称 + 涨幅
        ax.text(0.06, y + 0.015, name, ha="left", fontsize=11, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        ax.text(0.06, y - 0.018, f"领涨: {leader}", ha="left", fontsize=8.5,
                color=C["muted"], transform=ax.transAxes)
        ax.text(0.34, y, f"{pct_str(pct)}", ha="right", fontsize=13,
                fontweight="bold", color=C["red"], transform=ax.transAxes)
        ax.text(0.34, y - 0.025, f"净入 {net_in:+.1f}亿", ha="right", fontsize=8,
                color=C["muted"], transform=ax.transAxes)

    # 右半：行业跌幅 TOP3
    ax.text(0.75, 0.885, "行业跌幅 TOP3", ha="center", fontsize=14,
            fontweight="bold", color=C["green"], transform=ax.transAxes)
    ind_bot = SUMMARY.get("industry_bottom5", [])[:3]
    for i, item in enumerate(ind_bot):
        y = 0.82 - i * 0.095
        name = item.get("name", "")
        pct = item.get("pct_chg", 0)
        net_in = float(item.get("main_net_in", 0)) / 1e8
        ax.text(0.48, y + 0.015, name, ha="left", fontsize=11, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        ax.text(0.48, y - 0.018, f"净出 {abs(net_in):.1f}亿", ha="left", fontsize=8.5,
                color=C["muted"], transform=ax.transAxes)
        ax.text(0.92, y, f"{pct_str(pct)}", ha="right", fontsize=13,
                fontweight="bold", color=C["green"], transform=ax.transAxes)

    # 下半：涨停行业分布 (条形图风格)
    ax.text(0.5, 0.43, "涨停行业分布", ha="center", fontsize=14,
            fontweight="bold", color=C["text"], transform=ax.transAxes)

    zt_ind = SUMMARY.get("zt_top_industries", [])
    max_zt = max(item.get("涨停数", 0) for item in zt_ind) if zt_ind else 1
    y_start = 0.36
    for i, item in enumerate(zt_ind[:7]):
        y = y_start - i * 0.045
        name = item.get("行业", "")
        count = item.get("涨停数", 0)
        bar_w = 0.6 * (count / max_zt)
        # 背景条
        ax.add_patch(FancyBboxPatch((0.13, y - 0.008), bar_w, 0.03,
                                    boxstyle="round,pad=0.002,rounding_size=0.01",
                                    fc=C["orange"] if count >= 5 else C["blue"],
                                    ec="none", alpha=0.7, transform=ax.transAxes))
        ax.text(0.1, y, f"{name}", ha="right", fontsize=10, color=C["text"],
                fontweight="bold", transform=ax.transAxes)
        ax.text(0.15 + bar_w + 0.02, y, f"{count} 只", ha="left", fontsize=10,
                color=C["muted"], transform=ax.transAxes)

    # 概念 TOP5
    ax.text(0.5, 0.08, "概念涨幅 TOP5", ha="center", fontsize=11,
            fontweight="bold", color=C["purple"], transform=ax.transAxes)
    con_top = SUMMARY.get("concept_top5", [])
    for i, item in enumerate(con_top):
        x = 0.1 + i * 0.2
        ax.text(x, 0.04, f"{item.get('name','')}", ha="center", fontsize=7.5,
                color=C["muted"], transform=ax.transAxes)
        ax.text(x, 0.018, pct_str(item.get('pct_chg', 0)), ha="center", fontsize=9,
                fontweight="bold", color=C["red"], transform=ax.transAxes)

    add_footer(ax, 3)
    save(fig, 3)


# ═══════════════════════════════════════════
# Page 4 — 明日跟踪框架 + 风险提示
# ═══════════════════════════════════════════
def page4():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  P4 · 明日跟踪 + 快讯  ", C["cyan"], fs=10)

    ax.text(0.5, 0.90, "明天看什么？", ha="center", fontsize=20,
            fontweight="bold", color=C["text"], transform=ax.transAxes)

    checks = [
        ("[主线]", "汽车零部 / 贵金属", "继续强 = 主线确认", "转弱 = 高潮日"),
        ("[高度]", "连板能否到 5 板", "打开空间", "宽度够高度弱"),
        ("[反抽]", "半导体 / 光学", "风格回摆", "主线吸金继续"),
        ("[人气]", "恒尚 / 招金黄金", "大众确认", "热度退潮"),
    ]

    for i, (icon, target, cont, weak) in enumerate(checks):
        y = 0.80 - i * 0.115
        card_bg(ax, 0.5, y, 0.88, 0.09, fc=C["card"])
        ax.text(0.08, y + 0.012, icon, ha="left", fontsize=12, fontweight="bold",
                color=C["gold"], transform=ax.transAxes)
        ax.text(0.22, y + 0.012, target, ha="left", fontsize=11, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        ax.text(0.22, y - 0.02, f"[+] {cont}", ha="left", fontsize=9,
                color=C["red"], transform=ax.transAxes)
        ax.text(0.62, y - 0.02, f"[-] {weak}", ha="left", fontsize=9,
                color=C["green"], transform=ax.transAxes)

    # 关键快讯
    ax.text(0.5, 0.37, "盘中快讯", ha="center", fontsize=13,
            fontweight="bold", color=C["orange"], transform=ax.transAxes)

    news = SUMMARY.get("news_recent30", [])
    # 取 4 条最有价值的
    key_news = []
    for n in news:
        title = n.get("title", "") or n.get("content", "") or ""
        if any(kw in title for kw in ["创新药", "通化金马", "电网", "华明装备", "华为", "铠侠", "人形机器人", "宇树"]):
            key_news.append(title[:60])
        if len(key_news) >= 4:
            break

    for i, n in enumerate(key_news[:4]):
        y = 0.31 - i * 0.055
        ax.text(0.08, y, f"> {n}", ha="left", fontsize=8.5, color=C["muted"],
                transform=ax.transAxes)

    # 金句
    card_bg(ax, 0.5, 0.12, 0.88, 0.08, fc=C["card2"])
    ax.text(0.5, 0.135, "不急着追高 — 60 只涨停但最高仅 4 板，等明天确认承接",
            ha="center", fontsize=10, fontweight="bold", color=C["gold"],
            transform=ax.transAxes)
    ax.text(0.5, 0.10, "汽车零部继续强 = 主线确认  |  汽车零部退潮 = 高潮日",
            ha="center", fontsize=9, color=C["muted"], transform=ax.transAxes)

    ax.text(0.5, 0.05, "[!] 本报告仅供个人复盘，不构成投资建议",
            ha="center", fontsize=7.5, color=C["dim"], transform=ax.transAxes)

    add_footer(ax, 4)
    save(fig, 4)


def main():
    print(f"生成 XHS 卡片到 {OUT}")
    page1()
    page2()
    page3()
    page4()
    print(f"完成！共 4 页 → {OUT}")


if __name__ == "__main__":
    main()
