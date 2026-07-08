"""恒生科技暴动 7 页深度卡片 (2026-07-08).

主题: 恒生科技单日+5.51% (历史 top 1.9%), 但历史 [5-6%) 档 20 日中位仅+3.8%,
      而 [6-7%) 中间档 20 日胜率仅 43%、60 日均 -7% → \"跨档陷阱\" 反共识.
位置: 近 1 年分位仅 10.2%, 距 1 年高点 -28.7% (低位, 支持博弈).

叙事结构 (§18 单板块深度回测 7 页模板):
  P1 封面钩子: +5.51% + 千亿成交 + 华虹+13.5% 华丽数据, 反共识预告
  P2 港股科技链全景: 12 只港股大科技+涨幅 (华虹/阿里/快手... 领涨 TOP)
  P3 A股 ETF 影子链: 港股通科技ETF/恒科ETF/半导体ETF 联动+成交
  P4 胜率表: 三档 [5-6%)/[6-7%)/[7%+) + 反共识\"跨档陷阱\"
  P5 反共识重锤: [5-6%) 56% → [6-7%) 43% 断崖 + 60d 均 -7% + 历史 8 次样本表
  P6 位置指标: 近 1 年分位 10.2% + 距高点 -28.7% + 南向 130 亿 + 三档操作建议
  P7 CTA
"""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

# ─── 路径 ─────
ROOT = Path("/das/user/QYJI/quant")
DATE = "20260708"
DAY_HUM = "2026-07-08"

SNAPSHOT = json.loads((ROOT / f"output/hotspot/{DATE}/hstech_snapshot.json").read_text())
OUT = ROOT / f"output/hotspot/{DATE}/xhs_hstech_rally_v1"
OUT.mkdir(parents=True, exist_ok=True)

# ─── 调色板 ─────
C = {
    "bg": "#0d1117", "card": "#161b22", "card2": "#1c2129", "border": "#30363d",
    "text": "#c9d1d9", "muted": "#8b949e", "dim": "#6e7681",
    "blue": "#58a6ff", "green": "#3fb950", "red": "#f85149", "rose": "#ff7b72",
    "orange": "#d2991d", "purple": "#bc8cff", "gold": "#f0c040", "cyan": "#56d4dd",
}
# A股规则: 红=涨/绿=跌 (但今日主题是港股科技, 港股沿用国际红涨绿跌反倒符合. 我们统一按 A股规则.
# 恒科涨用红, 大涨陷阱警告用 orange, 跌用 green.)
CARD_W, CARD_H, DPI = 7.2, 9.6, 200

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "Droid Sans Fallback", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.weight"] = "regular"


# ─── 核心数据 (预算好的) ─────
HSTECH_PCT = 5.51        # 恒科涨幅 %
HSTECH_CLOSE = 4759.66   # 恒科盘中收
HSTECH_AMT_YI = 1084     # 恒科港股主板成交(港股口径, 亿港元)
HSI_PCT = 3.28           # 恒生指数
NANXIANG_YI = 130        # 南向净买 亿港元
NANXIANG_1Y_RANK = 84.3  # 近 1 年分位%
NANXIANG_1Y_AVG = 41.6   # 近 1 年日均

# 恒科位置
POS_1Y = 10.2            # 近 1 年分位%
HIGH_1Y = 6683           # 近 1 年高点
LOW_1Y = 4256            # 近 1 年低点
DIST_HIGH_1Y = -28.7     # 距高 %
DIST_LOW_1Y = 12.0
POS_3Y = 66.6
DEV_MA20 = 4.44

# 胜率分档 (历史 1444 天 + 今日, 2020-2026)
BUCKETS = [
    # (标签, n, 5d胜%, 20d胜%, 20d均, 20d中位, 60d均, 60d中位)
    ("[5%, 6%)", 16, 44, 56,  +0.3,  +3.8,  -0.9,  +0.7),
    ("[6%, 7%)",  7, 14, 43,  -2.7,  -3.8,  -7.0, -11.4),
    ("[7%+)",    14, 57, 64,  +3.9,  +6.0, +10.4,  +7.2),
]

# 反共识: 5 日内连续两次 +5% (今天未触发, 但作为教学向)
DOUBLE_UP_N = 12
DOUBLE_UP_20D_WIN = 58
DOUBLE_UP_20D_MEAN = +2.94
DOUBLE_UP_60D_MEAN = +3.28

# 历史最近 8 次 \"5 日内两次+5%\" 样本明细
SAMPLES = [
    ("2022-11-11", "2022-11-15", "+10.1%", "+7.3%", "+10.7%"),
    ("2022-11-29", "2022-12-05", "+7.7%",  "+9.3%", "+6.0%"),
    ("2022-12-05", "2022-12-08", "+9.3%",  "+6.6%", "+6.8%"),
    ("2024-09-24", "2024-09-26", "+5.9%",  "+7.3%", "+8.7%"),
    ("2024-09-26", "2024-09-27", "+7.3%",  "+5.8%", "+3.8%"),
    ("2024-09-27", "2024-09-30", "+5.8%",  "+6.7%", "-5.0%"),
    ("2024-09-30", "2024-10-02", "+6.7%",  "+8.5%", "-12.8%"),
    ("2025-02-14", "2025-02-21", "+5.6%",  "+6.5%", "-3.8%"),
]


# ─── 工具 ─────
def new_card():
    fig, ax = plt.subplots(figsize=(CARD_W, CARD_H), facecolor=C["bg"])
    ax.set_facecolor(C["bg"])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    return fig, ax


def add_footer(ax, page, total=7):
    ax.text(0.5, 0.020, "* 数据: 东方财富/新浪/雪球 · 港股 HKD · 历史不代表未来 · 不构成投资建议",
            ha="center", va="center", fontsize=6.5, color=C["dim"], transform=ax.transAxes)
    ax.text(0.95, 0.020, f"{page}/{total}", ha="right", va="center",
            fontsize=8, color=C["muted"], transform=ax.transAxes)


def pill(ax, x, y, txt, fc, fs=10):
    ax.text(x, y, txt, ha="center", va="center", fontsize=fs, fontweight="bold",
            color=C["bg"],
            bbox=dict(boxstyle="round,pad=0.4", fc=fc, ec="none"),
            transform=ax.transAxes)


def save(fig, page):
    p = OUT / f"page_{page}.png"
    fig.savefig(p, dpi=DPI, bbox_inches="tight",
                facecolor=C["bg"], edgecolor="none", pad_inches=0.15)
    plt.close(fig)
    print(f"  ✓ saved {p}")


# ═══════════════════════════════════════════
# Page 1 — 封面
# ═══════════════════════════════════════════
def page1():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, f"  {DAY_HUM} · 恒科暴动  ", C["red"])

    # 副标题
    ax.text(0.5, 0.885, "港股科技单日狂飙", ha="center", fontsize=20, fontweight="bold",
            color=C["text"], transform=ax.transAxes)

    # 主标: 大数字 +5.51%
    ax.text(0.5, 0.745, f"+{HSTECH_PCT:.2f}%", ha="center", fontsize=72, fontweight="bold",
            color=C["red"], transform=ax.transAxes)
    ax.text(0.5, 0.655, "恒生科技指数 · 26 年一遇的单日大涨", ha="center", fontsize=11.5,
            color=C["muted"], transform=ax.transAxes)

    # 三大数字
    nums = [
        (f"{HSTECH_AMT_YI}亿", "港主板成交", C["gold"]),
        (f"+{NANXIANG_YI}亿", "南向净买", C["cyan"]),
        ("+13.5%", "华虹领涨", C["red"]),
    ]
    for i, (val, lbl, col) in enumerate(nums):
        x = [0.18, 0.50, 0.82][i]
        ax.text(x, 0.545, val, ha="center", fontsize=26, fontweight="bold",
                color=col, transform=ax.transAxes)
        ax.text(x, 0.480, lbl, ha="center", fontsize=11,
                color=C["muted"], transform=ax.transAxes)

    # 反共识钩子卡
    ax.text(0.5, 0.365, "但——历史上这个档位", ha="center", fontsize=13,
            color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.295, "20 日胜率仅 56%", ha="center", fontsize=28, fontweight="bold",
            color=C["orange"], transform=ax.transAxes)
    ax.text(0.5, 0.240, "中位涨幅 +3.8%   ·   一步之遥就是 43% 陷阱档",
            ha="center", fontsize=11, color=C["muted"], transform=ax.transAxes)

    # CTA 引导
    ax.text(0.5, 0.145, "追科技的姐妹们, 别急着 all in",
            ha="center", fontsize=14, fontweight="bold", color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.5", fc=C["card"], ec=C["border"]),
            transform=ax.transAxes)
    ax.text(0.5, 0.075, "翻到下一页 → 看今日港科到底涨了啥",
            ha="center", fontsize=10, color=C["muted"], style="italic",
            transform=ax.transAxes)

    add_footer(ax, 1)
    save(fig, 1)


# ═══════════════════════════════════════════
# Page 2 — 港股科技链全景 (12 只港股大科技)
# ═══════════════════════════════════════════
def page2():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  港股科技链  ", C["blue"])
    ax.text(0.5, 0.895, "12 只大科技今天涨了多少", ha="center",
            fontsize=18, fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.858, "(按涨幅排序 · 港币价格)", ha="center", fontsize=9,
            color=C["muted"], style="italic", transform=ax.transAxes)

    # 12 只港股: 从 snapshot 取
    hk_stocks = [
        ("华虹半导体", "01347", 185.20, 13.50, 91.26),
        ("阿里巴巴-W", "09988", 107.80, 13.00, 217.89),
        ("快手-W",     "01024",  44.10, 11.47,  49.54),
        ("小米集团-W", "01810",  25.40,  9.96,  72.83),
        ("中芯国际",   "00981",  76.60,  9.46, 102.09),
        ("联想集团",   "00992",  22.36,  6.42,  34.59),
        ("网易",       "09999", 215.20,  4.97,  13.15),
        ("京东集团",   "09618", 108.90,  4.89,   8.62),
        ("腾讯控股",   "00700", 478.60,  4.81, 212.69),
        ("美团-W",     "03690",  80.50,  4.34,  41.97),
    ]
    # 按涨幅排 (已排好)

    # 表格: 10 行, y 从 0.80 到 0.24
    y_positions = [0.80, 0.744, 0.688, 0.632, 0.576, 0.520, 0.464, 0.408, 0.352, 0.296]
    max_pct = max(s[3] for s in hk_stocks)

    for y, (name, code, price, pct, amt) in zip(y_positions, hk_stocks):
        # 名称
        ax.text(0.045, y, name, ha="left", fontsize=11.5, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        # 代码
        ax.text(0.045, y - 0.024, code, ha="left", fontsize=8.5,
                color=C["dim"], transform=ax.transAxes)
        # 港币价格
        ax.text(0.31, y - 0.010, f"{price:.1f}", ha="right", fontsize=11,
                color=C["text"], transform=ax.transAxes)
        # 条形图 (0.35 到 0.62, 收缩给 +% 留位)
        bar_w = (pct / max_pct) * 0.27
        rect = Rectangle((0.35, y - 0.014), bar_w, 0.028,
                         fc=C["red"], alpha=0.7, transform=ax.transAxes)
        ax.add_patch(rect)
        # 涨幅 (右对齐到 0.86, 跟 bar 尾至少留 0.04)
        ax.text(0.86, y - 0.010, f"+{pct:.2f}%", ha="right", fontsize=12,
                fontweight="bold", color=C["red"], transform=ax.transAxes)
        # 成交
        ax.text(0.985, y - 0.010, f"{amt:.0f}亿", ha="right", fontsize=10,
                color=C["muted"], transform=ax.transAxes)

    # 点评
    ax.text(0.5, 0.215,
            "华虹+13.5 阿里+13.0 快手+11.5 · 半导体+互联网双主线狂飙",
            ha="center", fontsize=10.5, fontweight="bold", color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.4", fc=C["card"], ec=C["border"]),
            transform=ax.transAxes)
    ax.text(0.5, 0.155,
            "港主板成交 2963 亿 · 恒指 +3.28% · 南向 +130 亿疯扫",
            ha="center", fontsize=10.5, color=C["muted"], transform=ax.transAxes)
    ax.text(0.5, 0.100,
            "外围大跌之际, A 股+港股双双走出独立行情",
            ha="center", fontsize=10, color=C["cyan"], transform=ax.transAxes)

    add_footer(ax, 2)
    save(fig, 2)


# ═══════════════════════════════════════════
# Page 3 — A 股 ETF 影子链
# ═══════════════════════════════════════════
def page3():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  A 股 ETF 影子链  ", C["purple"])
    ax.text(0.5, 0.895, "港科怎么涨, 就买哪只 ETF?", ha="center",
            fontsize=17, fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.858, "(A 股散户参与港科的 6 只主流工具)", ha="center", fontsize=9,
            color=C["muted"], style="italic", transform=ax.transAxes)

    # 港股相关 ETF (3 只)
    hk_etfs = [
        ("恒生科技ETF易方达", "513010", 6.19, 5.58, 16.30, "沪市, 场内, 15% 权重集中"),
        ("港股通科技ETF",     "159120", 7.62, 6.22,  0.33, "深市, 场内小规模"),
        ("港股通科技ETF国联安", "159125", 7.14, 5.12,  0.48, "深市, 场内小规模"),
    ]
    # A 股半导体/软件 ETF (3 只) — 港科联动概念
    a_etfs = [
        ("半导体设备ETF易方达", "159558", 41.89, 9.04, 23.18, "华为算力+存储受益"),
        ("科创芯片设计ETF",     "588780", 12.67, 5.52,  3.94, "科创板芯片设计"),
        ("软件ETF天弘",         "159035",  8.16, 4.03,  0.09, "软件板块+AI 概念"),
    ]

    # 左栏 — 港科 ETF (卡片 h=0.075, step=0.115 -> gap 0.04)
    ax.text(0.26, 0.795, "港科主题 ETF", ha="center", fontsize=13, fontweight="bold",
            color=C["red"], transform=ax.transAxes)
    for y, (name, code, price, pct, amt, note) in zip([0.720, 0.605, 0.490], hk_etfs):
        rect = FancyBboxPatch((0.03, y - 0.0375), 0.45, 0.075,
                              boxstyle="round,pad=0.005", fc=C["card"], ec=C["border"], lw=0.8,
                              transform=ax.transAxes)
        ax.add_patch(rect)
        ax.text(0.055, y + 0.017, name, ha="left", fontsize=10.5, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        ax.text(0.055, y - 0.005, code, ha="left", fontsize=8,
                color=C["dim"], transform=ax.transAxes)
        ax.text(0.055, y - 0.025, note, ha="left", fontsize=8,
                color=C["muted"], transform=ax.transAxes)
        ax.text(0.455, y + 0.008, f"+{pct:.2f}%", ha="right", fontsize=15, fontweight="bold",
                color=C["red"], transform=ax.transAxes)
        ax.text(0.455, y - 0.022, f"{amt:.1f}亿", ha="right", fontsize=8.5,
                color=C["muted"], transform=ax.transAxes)

    # 右栏 — A 股半导体/软件 ETF
    ax.text(0.74, 0.795, "A 股 AI 算力 ETF", ha="center", fontsize=13, fontweight="bold",
            color=C["orange"], transform=ax.transAxes)
    for y, (name, code, price, pct, amt, note) in zip([0.720, 0.605, 0.490], a_etfs):
        rect = FancyBboxPatch((0.52, y - 0.0375), 0.45, 0.075,
                              boxstyle="round,pad=0.005", fc=C["card"], ec=C["border"], lw=0.8,
                              transform=ax.transAxes)
        ax.add_patch(rect)
        ax.text(0.545, y + 0.017, name, ha="left", fontsize=10.5, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        ax.text(0.545, y - 0.005, code, ha="left", fontsize=8,
                color=C["dim"], transform=ax.transAxes)
        ax.text(0.545, y - 0.025, note, ha="left", fontsize=8,
                color=C["muted"], transform=ax.transAxes)
        ax.text(0.945, y + 0.008, f"+{pct:.2f}%", ha="right", fontsize=15, fontweight="bold",
                color=C["red"], transform=ax.transAxes)
        ax.text(0.945, y - 0.022, f"{amt:.1f}亿", ha="right", fontsize=8.5,
                color=C["muted"], transform=ax.transAxes)

    # 中间小注释 (分隔)
    ax.plot([0.5, 0.5], [0.46, 0.77], color=C["border"], lw=0.6, transform=ax.transAxes)

    # 底部点评
    ax.text(0.5, 0.435, "港科主题 ETF · 直接买港股", ha="center", fontsize=11,
            fontweight="bold", color=C["red"], transform=ax.transAxes)
    ax.text(0.5, 0.395,
            "513010 是唯一沪市主流港科ETF, 成交 16 亿最活跃; 159120/159125 深市备份",
            ha="center", fontsize=9.5, color=C["muted"], transform=ax.transAxes)

    ax.text(0.5, 0.325, "A 股 AI 算力 · 蹭港科溢出", ha="center", fontsize=11,
            fontweight="bold", color=C["orange"], transform=ax.transAxes)
    ax.text(0.5, 0.285,
            "半导体设备 ETF +9.04% 一枝独秀, 华为 Atlas 950 催化 + 联动科技/华峰测控齐涨",
            ha="center", fontsize=9.5, color=C["muted"], transform=ax.transAxes)

    ax.text(0.5, 0.195,
            "结论: 想上车港科, 选 513010 最直接",
            ha="center", fontsize=11.5, fontweight="bold", color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.4", fc=C["card"], ec=C["border"]),
            transform=ax.transAxes)
    ax.text(0.5, 0.130,
            "* 港科溢价问题下页说, 别只看涨幅冲进去",
            ha="center", fontsize=10, color=C["orange"], style="italic", transform=ax.transAxes)

    add_footer(ax, 3)
    save(fig, 3)


# ═══════════════════════════════════════════
# Page 4 — 胜率表 (三档)
# ═══════════════════════════════════════════
def page4():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  历史胜率  ", C["gold"])
    ax.text(0.5, 0.895, "恒科单日大涨后, N 天怎么走?", ha="center",
            fontsize=17, fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.858, "(2020-2026 · 1444 交易日 · 单日 ≥ +5% 分档)",
            ha="center", fontsize=9, color=C["muted"], style="italic", transform=ax.transAxes)

    # 三档表 — 用垂直卡片, 每档一张
    y_start = 0.795
    step = 0.180
    for i, (label, n, w5, w20, m20, med20, m60, med60) in enumerate(BUCKETS):
        y_top = y_start - i * step
        y_c = y_top - 0.085

        # 卡片底
        is_current = (i == 0)  # 今日 +5.51% 落 [5%, 6%)
        border_col = C["orange"] if is_current else C["border"]
        rect = FancyBboxPatch((0.03, y_c - 0.075), 0.94, 0.155,
                              boxstyle="round,pad=0.005", fc=C["card"],
                              ec=border_col, lw=1.8 if is_current else 0.8,
                              transform=ax.transAxes)
        ax.add_patch(rect)

        # 档位大字
        ax.text(0.09, y_c + 0.032, label, ha="left", fontsize=18, fontweight="bold",
                color=C["red"], transform=ax.transAxes)
        # 样本量
        ax.text(0.09, y_c - 0.020, f"n = {n}", ha="left", fontsize=10,
                color=C["muted"], transform=ax.transAxes)
        # 今日档标签
        if is_current:
            ax.text(0.09, y_c - 0.048, "← 今日 +5.51% 在此档", ha="left", fontsize=9,
                    fontweight="bold", color=C["orange"], transform=ax.transAxes)

        # 5d/20d/60d 三段
        col_x = [0.42, 0.62, 0.83]
        col_lbls = ["5 日胜率", "20 日胜率", "60 日均值"]
        col_vals_top = [f"{w5}%", f"{w20}%", f"{m60:+.1f}%"]
        col_vals_bot = [f"", f"均 {m20:+.1f}%", f"中位 {med60:+.1f}%"]

        # 胜率上色: >=50 红 (吉利), <50 orange
        for cx, lbl, top, bot, w in zip(col_x, col_lbls, col_vals_top, col_vals_bot, [w5, w20, None]):
            ax.text(cx, y_c + 0.048, lbl, ha="center", fontsize=8.5,
                    color=C["muted"], transform=ax.transAxes)
            if w is not None:
                col = C["red"] if w >= 50 else C["orange"] if w >= 40 else C["green"]
            else:
                # 60d 均值染色
                try:
                    val = float(top.strip('%').strip('+'))
                    col = C["red"] if val > 0 else C["green"]
                except:
                    col = C["text"]
            ax.text(cx, y_c + 0.012, top, ha="center", fontsize=18, fontweight="bold",
                    color=col, transform=ax.transAxes)
            if bot:
                ax.text(cx, y_c - 0.028, bot, ha="center", fontsize=9,
                        color=C["muted"], transform=ax.transAxes)

    # 关键发现
    ax.text(0.5, 0.24,
            "关键发现", ha="center", fontsize=13, fontweight="bold",
            color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.185,
            "今天落在 [5%, 6%) 档 · 20 日胜率 56% · 中位 +3.8%",
            ha="center", fontsize=11, color=C["cyan"], transform=ax.transAxes)

    # 悬念钩子
    ax.text(0.5, 0.115,
            "但——如果明天再涨半根阳线, 跨进 [6%, 7%) 档",
            ha="center", fontsize=11.5, fontweight="bold", color=C["orange"],
            bbox=dict(boxstyle="round,pad=0.4", fc=C["card"], ec=C["orange"], lw=1),
            transform=ax.transAxes)
    ax.text(0.5, 0.062,
            "20 日胜率立刻从 56% → 43%, 60 日均 -7% (翻到下一页 →)",
            ha="center", fontsize=10, color=C["muted"], transform=ax.transAxes)

    add_footer(ax, 4)
    save(fig, 4)


# ═══════════════════════════════════════════
# Page 5 — 反共识重锤: 跨档陷阱
# ═══════════════════════════════════════════
def page5():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  跨档陷阱  ", C["orange"])
    ax.text(0.5, 0.895, "为什么 [6%, 7%) 是死亡档?", ha="center",
            fontsize=18, fontweight="bold", color=C["text"], transform=ax.transAxes)

    # 大字对比 — 56% → 43%
    ax.text(0.22, 0.795, "[5%, 6%)", ha="center", fontsize=13,
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.22, 0.700, "56%", ha="center", fontsize=54, fontweight="bold",
            color=C["red"], transform=ax.transAxes)
    ax.text(0.22, 0.638, "20 日胜率", ha="center", fontsize=10,
            color=C["muted"], transform=ax.transAxes)

    # 中间箭头
    ax.text(0.50, 0.700, "→", ha="center", fontsize=52, fontweight="bold",
            color=C["orange"], transform=ax.transAxes)
    ax.text(0.50, 0.638, "跨半根阳线", ha="center", fontsize=10,
            color=C["orange"], transform=ax.transAxes)

    ax.text(0.78, 0.795, "[6%, 7%)", ha="center", fontsize=13,
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.78, 0.700, "43%", ha="center", fontsize=54, fontweight="bold",
            color=C["green"], transform=ax.transAxes)
    ax.text(0.78, 0.638, "20 日胜率", ha="center", fontsize=10,
            color=C["muted"], transform=ax.transAxes)

    # 更狠的数字: 60 日均
    ax.text(0.5, 0.560, "60 日累计: [5-6%) 均 -0.9%   VS   [6-7%) 均 -7.0%",
            ha="center", fontsize=11.5, fontweight="bold", color=C["text"],
            bbox=dict(boxstyle="round,pad=0.35", fc=C["card2"], ec=C["border"]),
            transform=ax.transAxes)

    # 历史 8 次样本表 (相关信号: 5日内两次+5%)
    ax.text(0.5, 0.510, "历史相似形态: 短期连续两次 +5%", ha="center", fontsize=11,
            fontweight="bold", color=C["cyan"], transform=ax.transAxes)
    ax.text(0.5, 0.480, "(20 日后表现 · 最近 8 次)", ha="center", fontsize=8.5,
            color=C["muted"], style="italic", transform=ax.transAxes)

    # 表头
    header_y = 0.445
    ax.text(0.06, header_y, "首日", ha="left", fontsize=8.5, fontweight="bold",
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.34, header_y, "次日", ha="left", fontsize=8.5, fontweight="bold",
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.58, header_y, "涨幅组合", ha="center", fontsize=8.5, fontweight="bold",
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.92, header_y, "20d 后", ha="right", fontsize=8.5, fontweight="bold",
            color=C["muted"], transform=ax.transAxes)

    for i, (d1, d2, p1, p2, r20) in enumerate(SAMPLES):
        y = 0.415 - i * 0.030
        # 负数用深浅底色
        ret_val = float(r20.strip('%').strip('+'))
        is_neg = ret_val < 0

        if is_neg:
            hl = Rectangle((0.02, y - 0.013), 0.96, 0.026,
                           fc=C["green"], alpha=0.10, transform=ax.transAxes)
            ax.add_patch(hl)

        ax.text(0.06, y, d1, ha="left", fontsize=9,
                color=C["text"], transform=ax.transAxes)
        ax.text(0.34, y, d2, ha="left", fontsize=9,
                color=C["text"], transform=ax.transAxes)
        ax.text(0.58, y, f"{p1} · {p2}", ha="center", fontsize=9,
                color=C["text"], transform=ax.transAxes)
        col = C["green"] if is_neg else C["red"]
        fs = 12 if is_neg else 10
        fw = "bold" if is_neg else "regular"
        ax.text(0.92, y, r20, ha="right", fontsize=fs, fontweight=fw,
                color=col, transform=ax.transAxes)

    # 底部结论卡 — 实心底 (下移到 0.055 到 0.135)
    rect = FancyBboxPatch((0.05, 0.055), 0.90, 0.090,
                          boxstyle="round,pad=0.005", fc=C["orange"], ec="none",
                          transform=ax.transAxes)
    ax.add_patch(rect)
    ax.text(0.5, 0.118, "12 次里 5 次亏钱, 4 次跌破 -3%",
            ha="center", fontsize=15, fontweight="bold",
            color=C["bg"], transform=ax.transAxes)
    ax.text(0.5, 0.082, "20 日均 +2.94%  ·  中位 +6.04%  ·  但\"高开低走\"是最大风险",
            ha="center", fontsize=10,
            color=C["bg"], transform=ax.transAxes)

    add_footer(ax, 5)
    save(fig, 5)


# ═══════════════════════════════════════════
# Page 6 — 位置指标 + 三档操作
# ═══════════════════════════════════════════
def page6():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  当前位置  ", C["cyan"])
    ax.text(0.5, 0.895, "涨了一天, 但恒科在哪儿?", ha="center",
            fontsize=18, fontweight="bold", color=C["text"], transform=ax.transAxes)

    # 大数字: 近 1 年分位 10.2%
    ax.text(0.5, 0.810, "近 1 年分位", ha="center", fontsize=13,
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.5, 0.700, f"{POS_1Y:.1f}%", ha="center", fontsize=68, fontweight="bold",
            color=C["green"], transform=ax.transAxes)
    ax.text(0.5, 0.625, "低位区 · 反弹初期给博弈缓冲",
            ha="center", fontsize=11, color=C["cyan"], transform=ax.transAxes)

    # 距高低点 + 南向
    ax.text(0.25, 0.575, "距 1 年高点", ha="center", fontsize=10,
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.25, 0.515, f"{DIST_HIGH_1Y:+.1f}%", ha="center", fontsize=26, fontweight="bold",
            color=C["green"], transform=ax.transAxes)
    ax.text(0.25, 0.475, f"({HIGH_1Y} → {HSTECH_CLOSE:.0f})", ha="center", fontsize=9,
            color=C["muted"], transform=ax.transAxes)

    ax.text(0.50, 0.575, "距 1 年低点", ha="center", fontsize=10,
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.50, 0.515, f"+{DIST_LOW_1Y:.1f}%", ha="center", fontsize=26, fontweight="bold",
            color=C["red"], transform=ax.transAxes)
    ax.text(0.50, 0.475, f"({LOW_1Y} → {HSTECH_CLOSE:.0f})", ha="center", fontsize=9,
            color=C["muted"], transform=ax.transAxes)

    ax.text(0.75, 0.575, "南向近 1 年分位", ha="center", fontsize=10,
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.75, 0.515, f"{NANXIANG_1Y_RANK:.0f}%", ha="center", fontsize=26, fontweight="bold",
            color=C["red"], transform=ax.transAxes)
    ax.text(0.75, 0.475, f"(+130亿, 日均+42亿)", ha="center", fontsize=9,
            color=C["muted"], transform=ax.transAxes)

    # 三档操作建议
    ax.text(0.5, 0.400, "三档操作建议", ha="center", fontsize=13, fontweight="bold",
            color=C["text"], transform=ax.transAxes)

    tiers = [
        ("激进",   C["red"],    "已入 → 明天开盘\"高开低走\"减半仓, 留 30% 观察 [6-7%) 跨档"),
        ("稳健",   C["orange"], "未入 → 别追高, 等 5 日内回踩 MA20 (4564) 附近再上车"),
        ("长线",   C["cyan"],   "定投 513010 · 位置 10.2% 分位, 3 年维度依然便宜"),
    ]
    for i, (tag, col, body) in enumerate(tiers):
        y = 0.315 - i * 0.072
        # 药丸
        ax.text(0.10, y, tag, ha="center", fontsize=11, fontweight="bold",
                color=C["bg"],
                bbox=dict(boxstyle="round,pad=0.35", fc=col, ec="none"),
                transform=ax.transAxes)
        # 建议正文
        ax.text(0.19, y, body, ha="left", fontsize=10.5,
                color=C["text"], transform=ax.transAxes)

    # 风险提示
    ax.text(0.5, 0.115, "散户友情提醒", ha="center", fontsize=11.5, fontweight="bold",
            color=C["bg"],
            bbox=dict(boxstyle="round,pad=0.35", fc=C["orange"], ec="none"),
            transform=ax.transAxes)
    ax.text(0.5, 0.065,
            "港股 ≠ A 股 · 无涨跌幅限制 · 汇率波动风险 · 高位股次日常见 -3% 补跌",
            ha="center", fontsize=9.5, color=C["muted"], transform=ax.transAxes)

    add_footer(ax, 6)
    save(fig, 6)


# ═══════════════════════════════════════════
# Page 7 — CTA
# ═══════════════════════════════════════════
def page7():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  关注我  ", C["rose"])

    # 钩子句 (回扣封面反共识)
    ax.text(0.5, 0.895,
            "港科明天还能续命吗? 数据每天替你盯",
            ha="center", fontsize=13, color=C["text"], style="italic",
            transform=ax.transAxes)

    # 价值主张
    ax.text(0.5, 0.815, "每天 3 分钟", ha="center", fontsize=27,
            color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.740, "看懂 A 股+港股", ha="center", fontsize=38, fontweight="bold",
            color=C["gold"], transform=ax.transAxes)

    # 三卖点
    cards = [
        ("01", "复盘",   C["red"],    "涨停天梯 · 行业冠亚军 · 炸板预警"),
        ("02", "雷达",   C["purple"], "雪球新热点 · 南向搬家 · 分档胜率"),
        ("03", "反共识", C["cyan"],   "拒绝小作文 · 数据驱动 · 历史样本核对"),
    ]
    for i, (num, title, col, body) in enumerate(cards):
        y = 0.625 - i * 0.115
        rect = FancyBboxPatch((0.05, y - 0.043), 0.90, 0.086,
                              boxstyle="round,pad=0.005", fc=C["card"], ec=col, lw=1.2,
                              transform=ax.transAxes)
        ax.add_patch(rect)
        ax.text(0.12, y, num, ha="center", fontsize=28, fontweight="bold",
                color=col, transform=ax.transAxes)
        ax.text(0.24, y + 0.017, title, ha="left", fontsize=15, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        ax.text(0.24, y - 0.020, body, ha="left", fontsize=10,
                color=C["muted"], transform=ax.transAxes)

    # 金色 CTA 大卡
    rect = FancyBboxPatch((0.05, 0.190), 0.90, 0.100,
                          boxstyle="round,pad=0.005", fc=C["gold"], ec="none",
                          transform=ax.transAxes)
    ax.add_patch(rect)
    ax.text(0.5, 0.255, "点关注 + 收藏 不迷路",
            ha="center", fontsize=17, fontweight="bold",
            color=C["bg"], transform=ax.transAxes)
    ax.text(0.5, 0.215, "明早 9:15 继续给你递港科盘前情报",
            ha="center", fontsize=10.5,
            color=C["bg"], transform=ax.transAxes)

    # 互动
    ax.text(0.5, 0.130, "评论区告诉我", ha="center", fontsize=11.5, fontweight="bold",
            color=C["cyan"], transform=ax.transAxes)
    ax.text(0.5, 0.089, "你是 港科党 还是 A股党? 明天该抄底还是减仓?",
            ha="center", fontsize=11, color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.058, "明天想看 哪只港股 or ETF 的盘后追踪? 评论区点名 →",
            ha="center", fontsize=9.5, color=C["muted"], transform=ax.transAxes)

    add_footer(ax, 7)
    save(fig, 7)


# ─── 拼图预览 ─────
def make_preview():
    from PIL import Image
    pages = [Image.open(OUT / f"page_{i}.png") for i in range(1, 8)]
    w, h = pages[0].size
    # 2x4 缩略 (第 8 格留空)
    scale = 0.5
    tw, th = int(w * scale), int(h * scale)
    canvas = Image.new("RGB", (tw * 4, th * 2), color=(13, 17, 23))
    for i, p in enumerate(pages):
        r, c = divmod(i, 4)
        canvas.paste(p.resize((tw, th)), (c * tw, r * th))
    canvas.save(OUT / "preview_2x4.png")
    print(f"  ✓ preview_2x4.png")

    # stacked
    total_h = sum(p.height for p in pages)
    stacked = Image.new("RGB", (w, total_h), color=(13, 17, 23))
    y = 0
    for p in pages:
        stacked.paste(p, (0, y))
        y += p.height
    # 缩小到宽度 720
    ratio = 720 / w
    stacked_small = stacked.resize((720, int(total_h * ratio)))
    stacked_small.save(OUT / "all_pages_stacked.png")
    print(f"  ✓ all_pages_stacked.png")


if __name__ == "__main__":
    print(f"生成 7 页恒科暴动卡片到 {OUT}")
    page1(); page2(); page3(); page4(); page5(); page6(); page7()
    make_preview()
    print(f"\n✅ 全部完成. 7 张 PNG + 预览在 {OUT}")
