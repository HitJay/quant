"""20260703 黄金 7 页深度卡片 — 贵金属 +5.43% 胜率回测 (盘中版).

数据源:
  - output/hotspot/20260703/summary.json (盘中 12:19)
  - SW 贵金属二级 801053 (akshare 2989 天日线, 2014-02-21 ~ 2026-07-02)
  - output/hotspot/20260703/gold_backtest.json (三层回测)

主线:
  - 7/2 SW 贵金属 +5.43% (落 [5%,7%) 档)
  - 7/3 盘中黄金概念 +2.51%, 主力净入 51.8 亿 (全概念 TOP1)
  - 5 只贵金属涨停 (招金/赤峰 2连板 + 山金/四川/西部首板)
  - 近 3 年分位 74.3% (中高位, 不是低位反弹)

胜率量化 (SW 贵金属 801053, 2989 天):
  - 单日 [3%,4%) 后 20d 胜率 45.9% (n=98)
  - 单日 [4%,5%) 后 20d 胜率 38.6% (n=58)
  - 单日 [5%,7%) 后 20d 胜率 38.2% (n=57, 均 -3.44%) ← 7/2 +5.43% 落此档
  - 单日 [7%+)   后 20d 胜率 50.0% (n=26, 但 60d 仅 24%)
  - 5 日内两次 >=3% 后 20d 胜率 34.2% (n=74, 均 -2.93%) ← 追高陷阱

产物: output/hotspot/20260703/xhs_gold_rally_v1/
"""

from __future__ import annotations
import json
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

# ─── 路径 ──────────────────────────
ROOT = Path("/das/user/QYJI/quant")
DATE = "20260703"
DAY_HUM = "2026-07-03"
TOPIC = "gold_rally"
VERSION = 1

SUMMARY = json.loads((ROOT / f"output/hotspot/{DATE}/summary.json").read_text())
BACKTEST = json.loads((ROOT / f"output/hotspot/{DATE}/gold_backtest.json").read_text())
OUT = ROOT / f"output/hotspot/{DATE}/xhs_{TOPIC}_v{VERSION}"
OUT.mkdir(parents=True, exist_ok=True)

# ─── 调色板 (A股红涨绿跌) ─────────
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
plt.rcParams["font.weight"] = "regular"


# ─── 工具函数 ────────────────────
def new_card():
    fig, ax = plt.subplots(figsize=(CARD_W, CARD_H), facecolor=C["bg"])
    ax.set_facecolor(C["bg"])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    return fig, ax


def add_footer(ax, page, total=7):
    ax.text(0.5, 0.025, "* 数据: 东方财富/雪球/申万 · 回测基于 SW 贵金属二级 2989 天日线 · 不构成投资建议",
            ha="center", va="center", fontsize=10, color=C["muted"], transform=ax.transAxes)
    ax.text(0.95, 0.025, f"{page}/{total}", ha="right", va="center",
            fontsize=10.5, color=C["muted"], transform=ax.transAxes)
    ax.text(0.05, 0.025, "复旦杰伦", ha="left", va="center",
            fontsize=10.5, color=C["dim"], transform=ax.transAxes)


def pill(ax, x, y, txt, fc, fs=11):
    ax.text(x, y, txt, ha="center", va="center", fontsize=fs, fontweight="bold",
            color=C["bg"],
            bbox=dict(boxstyle="round,pad=0.4", fc=fc, ec="none"),
            transform=ax.transAxes)


def save(fig, page):
    p = OUT / f"page_{page}.png"
    fig.savefig(p, dpi=DPI, bbox_inches=None, pad_inches=0,
                facecolor=C["bg"], edgecolor="none")
    plt.close(fig)
    print(f"  saved {p}")


# ═══════════════════════════════════════════
# Page 1 — 封面: 黄金 +5.43% 别急着追
# ═══════════════════════════════════════════
def page1():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, f"  {DAY_HUM} · 量化复盘  ", C["gold"], fs=11)

    # 主标题
    ax.text(0.5, 0.865, "贵金属  +5.43%", ha="center", fontsize=30, fontweight="bold",
            color=C["gold"], transform=ax.transAxes)
    ax.text(0.5, 0.77, "别急着追", ha="center", fontsize=42, fontweight="bold",
            color=C["gold"], transform=ax.transAxes)
    ax.text(0.5, 0.695, "先看这张胜率表", ha="center", fontsize=19, fontweight="bold",
            color=C["text"], transform=ax.transAxes)

    # 三大数字
    nums = [
        ("+5.43%", "7/2 贵金属", C["gold"], 32),
        ("5 只", "贵金属涨停", C["red"], 32),
        ("+51.8亿", "主力净入", C["red"], 32),
    ]
    for i, (n, lbl, col, fs) in enumerate(nums):
        x = [0.18, 0.50, 0.82][i]
        ax.text(x, 0.545, n, ha="center", fontsize=fs, fontweight="bold",
                color=col, transform=ax.transAxes)
        ax.text(x, 0.475, lbl, ha="center", fontsize=12.5,
                color=C["muted"], transform=ax.transAxes)

    # 反共识钩子 — 大卡
    rect = FancyBboxPatch((0.08, 0.245), 0.84, 0.13,
                          boxstyle="round,pad=0.015", fc=C["card2"], ec=C["gold"], lw=1.5,
                          transform=ax.transAxes)
    ax.add_patch(rect)
    ax.text(0.5, 0.335, "历史 74 次同类形态", ha="center", fontsize=13,
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.5, 0.285, "\"5 日内两次 +3%\" 20 日胜率仅 34%",
            ha="center", fontsize=15, fontweight="bold", color=C["gold"],
            transform=ax.transAxes)

    ax.text(0.5, 0.185, "7/2 贵金属 +5.43% 已是第二次大涨",
            ha="center", fontsize=13, color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.14, "翻到下一页 → 看完整胜率分档",
            ha="center", fontsize=11, color=C["cyan"], style="italic",
            transform=ax.transAxes)

    add_footer(ax, 1)
    save(fig, 1)


# ═══════════════════════════════════════════
# Page 2 — 黄金链全景: 概念 + 涨停密度 + 资金流
# ═══════════════════════════════════════════
def page2():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  黄金链全景  ", C["gold"], fs=11)
    ax.text(0.5, 0.895, "今天到底哪几路黄金在涨", ha="center",
            fontsize=18, fontweight="bold", color=C["text"], transform=ax.transAxes)

    # 三概念对比
    ax.text(0.5, 0.85, "三大避险概念 今日涨幅", ha="center",
            fontsize=13, color=C["muted"], transform=ax.transAxes)

    concepts = [
        ("黄金概念", 2.51, "招金黄金", C["gold"]),
        ("航天航空", 2.81, "航发科技", C["red"]),
        ("军工", 2.13, "铖昌科技", C["red"]),
    ]
    max_pct = 3.5
    bar_x0 = 0.35; bar_w_max = 0.40
    for i, (name, pct, lead, col) in enumerate(concepts):
        y = 0.78 - i * 0.075
        ax.text(0.30, y, name, ha="right", fontsize=13.5, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        bar_w = bar_w_max * pct / max_pct
        rect = Rectangle((bar_x0, y - 0.022), bar_w, 0.038,
                         fc=col, ec="none", alpha=0.75, transform=ax.transAxes)
        ax.add_patch(rect)
        ax.text(bar_x0 + bar_w + 0.025, y, f"+{pct:.2f}%", ha="left", va="center",
                fontsize=12.5, fontweight="bold", color=col, transform=ax.transAxes)
        ax.text(bar_x0 + 0.005, y - 0.038, f"领涨 {lead}", ha="left", fontsize=9,
                color=C["muted"], transform=ax.transAxes)

    # 分隔线
    ax.plot([0.10, 0.90], [0.505, 0.505], color=C["border"], lw=0.8, transform=ax.transAxes)

    # 贵金属涨停密集
    ax.text(0.5, 0.465, "贵金属 · 涨停密集度", ha="center", fontsize=13,
            fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.42, "贵金属 5 只涨停 · 2 只 2 连板", ha="center", fontsize=11,
            color=C["muted"], transform=ax.transAxes)

    # 3 张代表卡
    display = [
        ("招金黄金", "000506", 2, 9.99),
        ("赤峰黄金", "600988", 2, 10.00),
        ("山金国际", "000975", 1, 9.98),
    ]
    for i, (name, code, board, pct) in enumerate(display[:3]):
        x = 0.15 + i * 0.28
        rect = FancyBboxPatch((x - 0.11, 0.30), 0.22, 0.075,
                              boxstyle="round,pad=0.008", fc=C["card"], ec=C["border"], lw=0.8,
                              transform=ax.transAxes)
        ax.add_patch(rect)
        ax.text(x, 0.362, name, ha="center", fontsize=12.5, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        ax.text(x, 0.334, code, ha="center", fontsize=9,
                color=C["muted"], transform=ax.transAxes)
        ax.text(x, 0.312, f"+{pct:.1f}%" + (f" · {board}板" if board >= 2 else ""),
                ha="center", fontsize=10.5, fontweight="bold",
                color=C["red"], transform=ax.transAxes)

    # 主力资金 (黄金 vs 化工)
    ax.text(0.5, 0.245, "主力资金对照", ha="center", fontsize=12,
            fontweight="bold", color=C["text"], transform=ax.transAxes)

    ax.text(0.27, 0.19, "黄金概念", ha="center", fontsize=11,
            color=C["text"], transform=ax.transAxes)
    ax.text(0.27, 0.14, "+51.8亿", ha="center", fontsize=22, fontweight="bold",
            color=C["red"], transform=ax.transAxes)
    ax.text(0.27, 0.11, "全概念净入 TOP1", ha="center", fontsize=9,
            color=C["muted"], transform=ax.transAxes)

    ax.text(0.5, 0.14, "VS", ha="center", va="center", fontsize=14, fontweight="bold",
            color=C["dim"], transform=ax.transAxes)

    ax.text(0.73, 0.19, "化工原料", ha="center", fontsize=11,
            color=C["text"], transform=ax.transAxes)
    ax.text(0.73, 0.14, "-27.4亿", ha="center", fontsize=22, fontweight="bold",
            color=C["green"], transform=ax.transAxes)
    ax.text(0.73, 0.11, "主力净流出 TOP1", ha="center", fontsize=9,
            color=C["muted"], transform=ax.transAxes)

    ax.text(0.5, 0.055, "避险主线回归 · 资金从化工搬进黄金",
            ha="center", fontsize=11, fontweight="bold", color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.35", fc=C["card"], ec=C["border"]),
            transform=ax.transAxes)

    add_footer(ax, 2)
    save(fig, 2)


# ═══════════════════════════════════════════
# Page 3 — 黄金龙头 4 卡 (个股)
# ═══════════════════════════════════════════
def page3():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  黄金龙头  ", C["orange"], fs=11)
    ax.text(0.5, 0.895, "5 只贵金属涨停 · 谁在讲故事", ha="center",
            fontsize=16, fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.855, "2 板派 = 连板龙头 · 1 板派 = 新进资金", ha="center",
            fontsize=10, color=C["muted"], style="italic", transform=ax.transAxes)

    # 4 卡数据
    cards_data = [
        ("招金黄金", "000506", "+9.99%", "2 板", "贵金属", C["gold"], "2板", "连板龙头"),
        ("赤峰黄金", "600988", "+10.00%", "2 板", "贵金属", C["gold"], "2板", "封板资金 10.7 亿"),
        ("山金国际", "000975", "+9.98%", "1 板", "贵金属", C["red"], "1板", "成交 12.4 亿"),
        ("四川黄金", "001337", "+10.01%", "1 板", "贵金属", C["red"], "1板", "次新股首板"),
    ]
    positions = [(0.27, 0.68), (0.73, 0.68), (0.27, 0.40), (0.73, 0.40)]

    for (cx, cy), (name, code, pct, price, tag, col, badge, sub) in zip(positions, cards_data):
        rect = FancyBboxPatch(
            (cx - 0.21, cy - 0.115), 0.42, 0.23,
            boxstyle="round,pad=0.012", fc=C["card"], ec=C["border"], lw=1,
            transform=ax.transAxes,
        )
        ax.add_patch(rect)

        # 2板/1板 角标
        badge_col = C["gold"] if "2板" in badge else C["red"]
        ax.text(cx + 0.16, cy + 0.09, badge, ha="center", fontsize=9, fontweight="bold",
                color=C["bg"],
                bbox=dict(boxstyle="round,pad=0.25", fc=badge_col, ec="none"),
                transform=ax.transAxes)

        ax.text(cx - 0.185, cy + 0.09, name, ha="left", fontsize=14, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        ax.text(cx - 0.185, cy + 0.055, code, ha="left", fontsize=9,
                color=C["muted"], transform=ax.transAxes)

        ax.text(cx, cy + 0.005, pct, ha="center", fontsize=17, fontweight="bold",
                color=col, transform=ax.transAxes)
        ax.text(cx, cy - 0.04, price, ha="center", fontsize=10,
                color=C["text"], transform=ax.transAxes)
        ax.text(cx, cy - 0.075, sub, ha="center", fontsize=9,
                color=C["dim"], transform=ax.transAxes)

    # 中间十字带
    ax.plot([0.10, 0.90], [0.535, 0.535], color=C["border"], lw=0.6, alpha=0.5, transform=ax.transAxes)

    ax.text(0.5, 0.235, "一句话点评", ha="center", fontsize=12, fontweight="bold",
            color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.175,
            "招金 + 赤峰双 2 连板是真金白银\n山金 + 四川 + 西部 3 只首板是新进资金追入",
            ha="center", fontsize=10.5, color=C["muted"], transform=ax.transAxes)

    ax.text(0.5, 0.09, "5 只齐封 · 板块级共识已形成",
            ha="center", fontsize=11, fontweight="bold", color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.35", fc=C["card"], ec=C["border"]),
            transform=ax.transAxes)

    add_footer(ax, 3)
    save(fig, 3)


# ═══════════════════════════════════════════
# Page 4 — 量化胜率表 (四档对比)
# ═══════════════════════════════════════════
def page4():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  量化胜率表  ", C["cyan"], fs=11)
    ax.text(0.5, 0.895, "贵金属单日大涨 · 后 20 天走势", ha="center",
            fontsize=18, fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.85, "回测: SW 贵金属二级 · 2989 天 · 239 次同级事件", ha="center",
            fontsize=10, color=C["muted"], style="italic", transform=ax.transAxes)

    ax.text(0.5, 0.79, "按当日涨幅分档", ha="center", fontsize=12,
            fontweight="bold", color=C["text"], transform=ax.transAxes)

    # 表头
    header_y = 0.735
    ax.text(0.20, header_y, "档位", ha="center", fontsize=10.5, fontweight="bold",
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.42, header_y, "样本", ha="center", fontsize=10.5, fontweight="bold",
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.60, header_y, "20日胜率", ha="center", fontsize=10.5, fontweight="bold",
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.83, header_y, "20日均收益", ha="center", fontsize=10.5, fontweight="bold",
            color=C["muted"], transform=ax.transAxes)

    ax.plot([0.08, 0.92], [0.712, 0.712], color=C["border"], lw=0.8, transform=ax.transAxes)

    # 四行数据
    tiers = [
        ("[3%, 4%)", "★★★ 温和反弹", "98", "45.9%", "+0.69%", C["red"]),
        ("[4%, 5%)", "★★ 中等拉升", "58", "38.6%", "-0.60%", C["green"]),
        ("[5%, 7%)", "★ 追高陷阱", "57", "38.2%", "-3.44%", C["green"]),
        ("[7%+)",    "★ 极端拉升", "26", "50.0%", "-2.43%", C["green"]),
    ]
    tier_ys = [0.658, 0.575, 0.492, 0.409]
    for y, (tier, verdict, n, win, mean, col) in zip(tier_ys, tiers):
        rect = Rectangle((0.06, y - 0.040), 0.88, 0.075,
                         fc=C["card2"], ec=C["border"], lw=0.5, alpha=0.7,
                         transform=ax.transAxes)
        ax.add_patch(rect)

        ax.text(0.20, y + 0.008, tier, ha="center", fontsize=14.5, fontweight="bold",
                color=col, transform=ax.transAxes)
        ax.text(0.20, y - 0.023, verdict, ha="center", fontsize=8.5,
                color=C["muted"], style="italic", transform=ax.transAxes)
        ax.text(0.42, y, n, ha="center", fontsize=15, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        ax.text(0.60, y, win, ha="center", fontsize=16, fontweight="bold",
                color=col, transform=ax.transAxes)
        ax.text(0.83, y, mean, ha="center", fontsize=15, fontweight="bold",
                color=col, transform=ax.transAxes)

    # 关键结论
    rect = FancyBboxPatch((0.06, 0.20), 0.88, 0.15,
                          boxstyle="round,pad=0.015", fc=C["card2"], ec=C["gold"], lw=1.5,
                          transform=ax.transAxes)
    ax.add_patch(rect)
    ax.text(0.5, 0.32, "关键发现", ha="center", fontsize=13, fontweight="bold",
            color=C["gold"], transform=ax.transAxes)
    ax.text(0.5, 0.285, "7/2 贵金属 +5.43%", ha="center", fontsize=13,
            color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.248, "落在追高陷阱档 [5%, 7%)", ha="center", fontsize=14,
            fontweight="bold", color=C["green"], transform=ax.transAxes)
    ax.text(0.5, 0.215, "20 天赚钱概率仅 38%, 均值 -3.44%", ha="center", fontsize=10,
            color=C["muted"], transform=ax.transAxes)

    # 悬念钩子
    ax.text(0.5, 0.155, "但是 —", ha="center", fontsize=12, fontweight="bold",
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.5, 0.115, "单次大涨只是表象", ha="center", fontsize=13,
            color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.08, "5 日内两次 +3% 胜率更低 → 翻下一页",
            ha="center", fontsize=10, color=C["cyan"], style="italic",
            transform=ax.transAxes)

    add_footer(ax, 4)
    save(fig, 4)


# ═══════════════════════════════════════════
# Page 5 — 反共识: 双大涨 20 日胜率 34%
# ═══════════════════════════════════════════
def page5():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  反共识  ", C["gold"], fs=11)
    ax.text(0.5, 0.895, "\"5 日内两次 +3%\" 是啥意思", ha="center",
            fontsize=18, fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.855, "6/15 +5.39% → 7/2 +5.43%, 间隔 17 天内多次", ha="center",
            fontsize=11, color=C["muted"], style="italic", transform=ax.transAxes)

    # 大数字对比: 单次 45.9% vs 双次 34.2%
    ax.text(0.27, 0.83, "单次大涨", ha="center", fontsize=13,
            color=C["text"], transform=ax.transAxes)
    ax.text(0.27, 0.735, "46%", ha="center", fontsize=44, fontweight="bold",
            color=C["red"], transform=ax.transAxes)
    ax.text(0.27, 0.665, "20 天胜率 (n=98)", ha="center", fontsize=10,
            color=C["muted"], transform=ax.transAxes)

    ax.text(0.5, 0.735, "→", ha="center", va="center", fontsize=32, fontweight="bold",
            color=C["gold"], transform=ax.transAxes)
    ax.text(0.5, 0.665, "~1.3x 下降", ha="center", fontsize=9,
            color=C["gold"], transform=ax.transAxes)

    ax.text(0.73, 0.83, "5 日内 2 次", ha="center", fontsize=13,
            color=C["text"], transform=ax.transAxes)
    ax.text(0.73, 0.735, "34%", ha="center", fontsize=44, fontweight="bold",
            color=C["green"], transform=ax.transAxes)
    ax.text(0.73, 0.665, "20 天胜率 (n=74)", ha="center", fontsize=10,
            color=C["muted"], transform=ax.transAxes)

    # 分隔线
    ax.plot([0.10, 0.90], [0.635, 0.635], color=C["border"], lw=0.8, transform=ax.transAxes)

    # 历史 6 次样本明细
    ax.text(0.5, 0.595, "最近 6 次同类形态 · 每次 20 天后表现", ha="center", fontsize=12,
            fontweight="bold", color=C["text"], transform=ax.transAxes)

    events = [
        ("2026-01-28", "+10.1 → +5.7", 1, -20.2),
        ("2026-02-24", "+5.6 → +3.0", 3, -15.5),
        ("2026-02-27", "+3.0 → +10.2", 3, -19.5),
        ("2026-03-25", "+3.5 → +3.3", 2, -2.0),
        ("2026-03-27", "+3.3 → +5.0", 3, -9.3),
        ("2026-06-12", "+4.6 → +5.4", 3, None),
    ]
    header_y = 0.545
    ax.text(0.15, header_y, "时间", ha="center", fontsize=9.5, fontweight="bold",
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.42, header_y, "两次涨幅", ha="center", fontsize=9.5, fontweight="bold",
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.68, header_y, "间隔", ha="center", fontsize=9.5, fontweight="bold",
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.85, header_y, "20 日后", ha="center", fontsize=9.5, fontweight="bold",
            color=C["muted"], transform=ax.transAxes)

    for i, (date, spread, gap, fwd20) in enumerate(events):
        y = 0.505 - i * 0.045
        if fwd20 is not None:
            col = C["red"] if fwd20 > 0 else C["green"]
            if fwd20 < 0:
                rect = Rectangle((0.71, y - 0.018), 0.22, 0.038,
                                 fc=C["green"], ec="none", alpha=0.12, transform=ax.transAxes)
                ax.add_patch(rect)
        else:
            col = C["muted"]
        ax.text(0.15, y, date, ha="center", fontsize=10,
                color=C["text"], transform=ax.transAxes)
        ax.text(0.42, y, spread, ha="center", fontsize=10,
                color=C["muted"], transform=ax.transAxes)
        ax.text(0.68, y, f"{gap}d", ha="center", fontsize=10,
                color=C["muted"], transform=ax.transAxes)
        if fwd20 is not None:
            sign = "+" if fwd20 > 0 else ""
            fs = 15 if fwd20 < 0 else 12
            ax.text(0.85, y, f"{sign}{fwd20:.1f}%", ha="center", fontsize=fs,
                    fontweight="bold", color=col, transform=ax.transAxes)
        else:
            ax.text(0.85, y, "待验证", ha="center", fontsize=9,
                    color=C["muted"], style="italic", transform=ax.transAxes)

    # 反共识金句 — 实心绿底大字
    rect = FancyBboxPatch((0.06, 0.155), 0.88, 0.07,
                          boxstyle="round,pad=0.012", fc=C["green"], ec="none",
                          alpha=0.85,
                          transform=ax.transAxes)
    ax.add_patch(rect)
    ax.text(0.5, 0.195, "74 次里 48 次亏钱",
            ha="center", fontsize=17, fontweight="bold", color=C["bg"],
            transform=ax.transAxes)
    ax.text(0.5, 0.166, "均值 -2.93% · 中位 -3.53%",
            ha="center", fontsize=11, fontweight="bold", color=C["bg"],
            transform=ax.transAxes)

    ax.text(0.5, 0.11, "追第二根大阳线的散户历史上很少有好下场",
            ha="center", fontsize=11, color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.07, "但位置视角有反转因子 → 翻下一页",
            ha="center", fontsize=10, color=C["cyan"], style="italic",
            transform=ax.transAxes)

    add_footer(ax, 5)
    save(fig, 5)


# ═══════════════════════════════════════════
# Page 6 — 位置视角 + 三档操作
# ═══════════════════════════════════════════
def page6():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  位置视角  ", C["cyan"], fs=11)
    ax.text(0.5, 0.895, "位置 —— 中高位不是低位反弹", ha="center",
            fontsize=18, fontweight="bold", color=C["text"], transform=ax.transAxes)

    # 大数字: 近3年分位 74.3%
    ax.text(0.5, 0.83, "贵金属 · 当前位置", ha="center", fontsize=11,
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.5, 0.735, "74%", ha="center", fontsize=58, fontweight="bold",
            color=C["gold"], transform=ax.transAxes)
    ax.text(0.5, 0.67, "近 3 年分位", ha="center", fontsize=13,
            color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.638, "74% 的时间比现在便宜", ha="center", fontsize=10,
            color=C["muted"], style="italic", transform=ax.transAxes)

    # 距高低点
    ax.plot([0.10, 0.90], [0.59, 0.59], color=C["border"], lw=0.8, transform=ax.transAxes)

    ax.text(0.27, 0.555, "距 3 年高点", ha="center", fontsize=10,
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.27, 0.51, "-51.1%", ha="center", fontsize=22, fontweight="bold",
            color=C["green"], transform=ax.transAxes)
    ax.text(0.27, 0.475, "3 年高点 42197", ha="center", fontsize=9,
            color=C["muted"], transform=ax.transAxes)

    ax.text(0.73, 0.555, "距 3 年低点", ha="center", fontsize=10,
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.73, 0.51, "+91.7%", ha="center", fontsize=22, fontweight="bold",
            color=C["red"], transform=ax.transAxes)
    ax.text(0.73, 0.475, "已翻倍 · 不是底部", ha="center", fontsize=9,
            color=C["muted"], transform=ax.transAxes)

    # 综合结论
    rect = FancyBboxPatch((0.06, 0.335), 0.88, 0.075,
                          boxstyle="round,pad=0.012", fc=C["card2"], ec=C["orange"], lw=1.3,
                          transform=ax.transAxes)
    ax.add_patch(rect)
    ax.text(0.5, 0.38, "「双大涨 34% 胜率」的历史样本",
            ha="center", fontsize=11, color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.35, "多数发生在中高位, 今天 74% 分位正属此列",
            ha="center", fontsize=11, fontweight="bold", color=C["orange"],
            transform=ax.transAxes)

    # 三档操作建议
    ax.text(0.5, 0.29, "三档操作建议", ha="center", fontsize=13,
            fontweight="bold", color=C["gold"], transform=ax.transAxes)

    plays = [
        ("激进", "今天追高", "赌短线延续", C["red"], "胜率 34%, 不推荐"),
        ("稳健", "等 3-5 日回踩", "看 20000 平台能否站稳", C["gold"], "胜率抬回 46%"),
        ("长线", "定投黄金 ETF", "518880 分批建仓", C["cyan"], "避险属性长期有效"),
    ]
    for i, (mode, action, why, col, tip) in enumerate(plays):
        y = 0.245 - i * 0.065
        ax.text(0.13, y, mode, ha="center", fontsize=11, fontweight="bold",
                color=col, transform=ax.transAxes)
        ax.text(0.26, y, action, ha="left", fontsize=11, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        ax.text(0.26, y - 0.024, why + " · " + tip, ha="left", fontsize=9,
                color=C["muted"], transform=ax.transAxes)

    ax.text(0.5, 0.06, "翻到下一页 → 明天继续给你递数据",
            ha="center", fontsize=10, color=C["cyan"], style="italic",
            transform=ax.transAxes)

    add_footer(ax, 6)
    save(fig, 6)


# ═══════════════════════════════════════════
# Page 7 — CTA 求关注
# ═══════════════════════════════════════════
def page7():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  关注我  ", C["rose"], fs=11)

    ax.text(0.5, 0.895, "今天的黄金狂飙明天还能续命吗?",
            ha="center", fontsize=13, color=C["text"], transform=ax.transAxes)

    ax.text(0.5, 0.815, "每天 3 分钟",
            ha="center", fontsize=28, fontweight="bold", color=C["text"],
            transform=ax.transAxes)
    ax.text(0.5, 0.745, "看懂 A 股",
            ha="center", fontsize=40, fontweight="bold", color=C["gold"],
            transform=ax.transAxes)

    sellings = [
        ("01", "涨停/资金 每日复盘", "行业冠亚军 · 主力搬家 · 龙头速览", C["red"]),
        ("02", "散户情绪雷达", "雪球新热点 · 讨论派 vs 实涨派", C["purple"]),
        ("03", "量化胜率不喊单", "回测数据说话 · 拒绝小作文", C["cyan"]),
    ]
    for i, (num, title, sub, col) in enumerate(sellings):
        y = 0.62 - i * 0.115
        rect = FancyBboxPatch(
            (0.06, y - 0.038), 0.88, 0.07,
            boxstyle="round,pad=0.01", fc=C["card"], ec=col, lw=1.3,
            transform=ax.transAxes,
        )
        ax.add_patch(rect)
        ax.text(0.13, y, num, ha="center", fontsize=22, fontweight="bold",
                color=col, transform=ax.transAxes)
        ax.text(0.24, y + 0.012, title, ha="left", fontsize=13, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        ax.text(0.24, y - 0.018, sub, ha="left", fontsize=10,
                color=C["muted"], transform=ax.transAxes)

    # 金色 CTA 大卡
    rect = FancyBboxPatch(
        (0.06, 0.195), 0.88, 0.10,
        boxstyle="round,pad=0.012", fc=C["gold"], ec="none",
        transform=ax.transAxes,
    )
    ax.add_patch(rect)
    ax.text(0.5, 0.265, "点关注 + 收藏 不迷路",
            ha="center", fontsize=17, fontweight="bold", color=C["bg"],
            transform=ax.transAxes)
    ax.text(0.5, 0.223, "明早 9:15 给你递盘前情报",
            ha="center", fontsize=11, color=C["bg"],
            transform=ax.transAxes)

    # 评论区互动
    ax.text(0.5, 0.145, "评论区告诉我",
            ha="center", fontsize=12, fontweight="bold", color=C["cyan"],
            transform=ax.transAxes)
    ax.text(0.5, 0.105, "你是「黄金追涨党」还是「等回踩党」?",
            ha="center", fontsize=12, color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.065, "明天想看哪只票的盘后追踪? 评论区点名 →",
            ha="center", fontsize=10, color=C["muted"], transform=ax.transAxes)

    add_footer(ax, 7)
    save(fig, 7)


# ═══════════════════════════════════════════
# 拼图预览
# ═══════════════════════════════════════════
def make_preview():
    from PIL import Image
    pages = [Image.open(OUT / f"page_{i}.png") for i in range(1, 8)]
    w, h = pages[0].size
    cols, rows = 2, 4
    preview = Image.new("RGB", (w * cols, h * rows), (13, 17, 23))
    for i, p in enumerate(pages):
        r, c = divmod(i, cols)
        preview.paste(p, (c * w, r * h))
    preview.thumbnail((1600, 3200))
    pp = OUT / "preview_2x4.png"
    preview.save(pp)
    print(f"  preview: {pp}")

    stacked = Image.new("RGB", (w, h * 7), (13, 17, 23))
    for i, p in enumerate(pages):
        stacked.paste(p, (0, i * h))
    stacked.thumbnail((1200, 8400))
    sp = OUT / "all_pages_stacked.png"
    stacked.save(sp)
    print(f"  stacked: {sp}")


if __name__ == "__main__":
    print(f"开始生成 7 页卡片到 {OUT}")
    page1(); page2(); page3(); page4(); page5(); page6(); page7()
    make_preview()
    print(f"\n全部完成. 7 张 PNG + preview 在 {OUT}")
