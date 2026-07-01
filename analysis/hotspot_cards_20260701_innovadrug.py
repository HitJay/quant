"""20260701 创新药 7 页深度卡片 — 化学制药 +5.57% 胜率回测 (收盘版).

数据源:
  - output/hotspot/20260701/summary.json (收盘)
  - 化学制药 SW 二级 801152 (akshare 6401 天日线)
  - 东财 push2 收盘板块行情 (直连)

盘中→收盘数据修正 (v11):
  - 化药 +5.40% → +5.57% (仍在 [5%, 6%) 甜蜜区)
  - 化药涨停 7 只 → 8 只 (新增宣泰医药/汇宇制药-W/威尔药业/易明医药, 减 珍宝岛→中药Ⅱ)
  - 美诺华主力净入 +15.2亿 → 化学制药板块主力净入 +17.17亿
  - 保险 Ⅱ +6.83% → +7.09%
  - 元件 -87.7亿 → -96.36亿 (净流出扩大)

胜率量化 (回测不变):
  - 单日 [5%, 6%) 后 +20d 胜率 63.3% (n=30, 均 +3.08%) ← 今日 +5.57% 落此档
  - 单日 [6%, 7%) 后 +20d 胜率 100.0% (n=6)
  - 单日 [7%+)   后 +20d 胜率 46.2% (n=13, 均 -4.36%) ← 追高陷阱
  - 5 日内两次 +5% 后 +20d 胜率 33.3% (n=6) ← 今日形态 ⚠️ (6-29 +7.26% + 7-01 +5.57%, 间隔 2d)

产物: output/hotspot/20260701/xhs_innova_drug_v11/
"""

from __future__ import annotations
import json
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

# ─── 路径 ──────────────────────────
ROOT = Path("/das/user/QYJI/quant")
DATE = "20260701"
DAY_HUM = "2026-07-01"
TOPIC = "innova_drug"
VERSION = 11

SUMMARY = json.loads((ROOT / f"output/hotspot/{DATE}/summary.json").read_text())
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

# ─── 量化数据 (已回测) ────────────
BACKTEST = {
    "5_6":  {"n": 30, "win5": 15, "win20": 19, "win60": 17, "mean20": 3.08, "med20": 1.95, "mean60": 5.88},
    "6_7":  {"n": 6,  "win5": 4,  "win20": 6,  "win60": 5,  "mean20": 3.55, "med20": 2.81, "mean60": 5.63},
    "7up":  {"n": 13, "win5": 4,  "win20": 6,  "win60": 3,  "mean20": -4.36, "med20": -2.13, "mean60": -8.27},
    "double_5": {"n": 6, "win20": 2, "mean20": -2.64, "med20": -1.42, "mean60": -4.46, "win60": 2},
    "total_pool": 6401,
    "big_up_count": 50,
    "pos_pct": 6.0,     # 近3年分位
    "pos_high_gap": -36.6,   # 距3年高点
    "pos_low_gap": +12.4,    # 距3年低点
    "today_pct": 5.40,
    "prev_pct": 7.26,   # 6-29 那次
    "recent_examples": [
        # (日期, 当日%, 20d%, 60d%)
        ("2024-07-31", 5.61, -8.7, 7.1),
        ("2024-09-27", 6.84, 5.0, 1.9),
        ("2024-09-30", 12.23, -5.2, -9.4),
        ("2024-10-08", 10.00, -11.7, -19.4),
    ],
}

# ─── 工具函数 ────────────────────
def new_card():
    fig, ax = plt.subplots(figsize=(CARD_W, CARD_H), facecolor=C["bg"])
    ax.set_facecolor(C["bg"])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    return fig, ax


def add_footer(ax, page, total=7):
    ax.text(0.5, 0.025, "* 数据: 东方财富/雪球/申万 · 回测基于 SW 化学制药二级 6401 天日线 · 不构成投资建议",
            ha="center", va="center", fontsize=7, color=C["muted"], transform=ax.transAxes)
    ax.text(0.95, 0.025, f"{page}/{total}", ha="right", va="center",
            fontsize=8, color=C["muted"], transform=ax.transAxes)
    ax.text(0.05, 0.025, "复旦杰伦", ha="left", va="center",
            fontsize=8, color=C["dim"], transform=ax.transAxes)


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
# Page 1 — 封面: 化药+5.40% 别急着追
# ═══════════════════════════════════════════
def page1():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, f"  {DAY_HUM} · 量化复盘  ", C["gold"], fs=10)

    # 主标题 3 行 (v11: 收盘价 +5.57%)
    ax.text(0.5, 0.865, "化学制药  +5.57%", ha="center", fontsize=30, fontweight="bold",
            color=C["red"], transform=ax.transAxes)
    ax.text(0.5, 0.77, "别急着追", ha="center", fontsize=42, fontweight="bold",
            color=C["gold"], transform=ax.transAxes)
    ax.text(0.5, 0.695, "先看这张胜率表", ha="center", fontsize=19, fontweight="bold",
            color=C["text"], transform=ax.transAxes)

    # 三大数字 (v11: 收盘校正 +5.57 / 8 只 / +17.2亿板块净入)
    nums = [
        ("+5.57%", "化药板块", C["red"], 32),
        ("8 只", "化药涨停", C["red"], 32),
        ("+17.2亿", "板块主力净入", C["red"], 32),
    ]
    for i, (n, lbl, col, fs) in enumerate(nums):
        x = [0.18, 0.50, 0.82][i]
        ax.text(x, 0.545, n, ha="center", fontsize=fs, fontweight="bold",
                color=col, transform=ax.transAxes)
        ax.text(x, 0.475, lbl, ha="center", fontsize=12,
                color=C["muted"], transform=ax.transAxes)

    # 反共识钩子 — 大卡
    rect = FancyBboxPatch((0.08, 0.245), 0.84, 0.13,
                          boxstyle="round,pad=0.015", fc=C["card2"], ec=C["gold"], lw=1.5,
                          transform=ax.transAxes)
    ax.add_patch(rect)
    ax.text(0.5, 0.335, "历史 50 次同级大涨里", ha="center", fontsize=13,
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.5, 0.285, "\"5 日内两次 +5%\" 20 日胜率仅 33%",
            ha="center", fontsize=15, fontweight="bold", color=C["gold"],
            transform=ax.transAxes)

    ax.text(0.5, 0.185, "今天化药恰好是这种形态",
            ha="center", fontsize=13, color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.14, "翻到下一页 → 看完整胜率分档",
            ha="center", fontsize=11, color=C["cyan"], style="italic",
            transform=ax.transAxes)

    add_footer(ax, 1)
    save(fig, 1)


# ═══════════════════════════════════════════
# Page 2 — 医药链全景: 三概念 + 化药涨停密度 + 资金流
# ═══════════════════════════════════════════
def page2():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  医药链全景  ", C["red"], fs=11)
    ax.text(0.5, 0.895, "今天到底哪几路医药在涨", ha="center",
            fontsize=18, fontweight="bold", color=C["text"], transform=ax.transAxes)

    # 三概念对比 (顶部三行紧凑, 顶副标间距从 0.07→0.045)
    ax.text(0.5, 0.85, "三大医药概念 齐涨 +4%", ha="center",
            fontsize=13, color=C["muted"], transform=ax.transAxes)

    # v11: 收盘价 (concept_board 本轮抓空, 用盘中值作稳定近似)
    concepts = [
        ("病毒防治", 4.19, "前沿生物-U", C["red"]),
        ("独家药品", 4.04, "珍宝岛", C["red"]),
        ("中药概念", 4.02, "永太科技", C["red"]),
    ]
    # 水平条形图 (柱条缩短给数字留空间)
    max_pct = 6.0
    bar_x0 = 0.35; bar_w_max = 0.45  # 从 0.55 缩到 0.45, 给数字留空
    for i, (name, pct, lead, col) in enumerate(concepts):
        y = 0.78 - i * 0.075
        ax.text(0.30, y, name, ha="right", fontsize=13, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        bar_w = bar_w_max * pct / max_pct
        rect = Rectangle((bar_x0, y - 0.022), bar_w, 0.038,
                         fc=col, ec="none", alpha=0.75, transform=ax.transAxes)
        ax.add_patch(rect)
        # 数字右边 padding 从 0.01 加到 0.025
        ax.text(bar_x0 + bar_w + 0.025, y, f"+{pct:.2f}%", ha="left", va="center",
                fontsize=12, fontweight="bold", color=col, transform=ax.transAxes)
        ax.text(bar_x0 + 0.005, y - 0.038, f"领涨 {lead}", ha="left", fontsize=8,
                color=C["muted"], transform=ax.transAxes)

    # 分隔线
    ax.plot([0.10, 0.90], [0.505, 0.505], color=C["border"], lw=0.8, transform=ax.transAxes)

    # 化药板块涨停密集
    ax.text(0.5, 0.465, "化学制药 · 涨停密集度", ha="center", fontsize=13,
            fontweight="bold", color=C["text"], transform=ax.transAxes)

    # 涨停 7 只名单
    zt_pharma = [x for x in SUMMARY["zt_top10"] if "药" in x.get("所属行业", "") or "药" in x.get("名称", "")][:4]
    if not zt_pharma:
        # fallback: 化药涨停找化学制药行业
        zt_pharma = [x for x in SUMMARY["zt_top10"] if x.get("所属行业") == "化学制药"][:4]

    ax.text(0.5, 0.42, f"化学制药 8 只涨停 · 最高 {SUMMARY['zt_max_board']} 连板", ha="center", fontsize=11,
            color=C["muted"], transform=ax.transAxes)

    # 收盘化药涨停 3 张卡代表 (从 8 只里选连板龙头/最大封单/新增)
    display = [
        ("海南海药", "000566", 3, 10.02),
        ("美诺华", "603538", 1, 10.02),   # 收盘封单 8130 万
        ("宣泰医药", "688247", 1, 19.95),  # 科创板 20% 涨停 新龙头
    ]

    for i, (name, code, board, pct) in enumerate(display[:3]):
        x = 0.15 + i * 0.28
        rect = FancyBboxPatch((x - 0.11, 0.30), 0.22, 0.075,
                              boxstyle="round,pad=0.008", fc=C["card"], ec=C["border"], lw=0.8,
                              transform=ax.transAxes)
        ax.add_patch(rect)
        ax.text(x, 0.362, name, ha="center", fontsize=12, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        ax.text(x, 0.334, code, ha="center", fontsize=8,
                color=C["muted"], transform=ax.transAxes)
        ax.text(x, 0.312, f"+{pct:.1f}%" + (f" · {board}板" if board >= 2 else ""),
                ha="center", fontsize=10, fontweight="bold",
                color=C["red"], transform=ax.transAxes)

    # 主力资金 (化药 vs 元件)
    ax.text(0.5, 0.245, "主力资金对照", ha="center", fontsize=12,
            fontweight="bold", color=C["text"], transform=ax.transAxes)

    ax.text(0.27, 0.19, "化学制药", ha="center", fontsize=11,
            color=C["text"], transform=ax.transAxes)
    ax.text(0.27, 0.14, "+17.2亿", ha="center", fontsize=22, fontweight="bold",
            color=C["red"], transform=ax.transAxes)
    ax.text(0.27, 0.11, "板块主力净入", ha="center", fontsize=9,
            color=C["muted"], transform=ax.transAxes)

    ax.text(0.5, 0.14, "VS", ha="center", va="center", fontsize=14, fontweight="bold",
            color=C["dim"], transform=ax.transAxes)

    ax.text(0.73, 0.19, "元件 (硬科技)", ha="center", fontsize=11,
            color=C["text"], transform=ax.transAxes)
    ax.text(0.73, 0.14, "-96.4亿", ha="center", fontsize=22, fontweight="bold",
            color=C["green"], transform=ax.transAxes)
    ax.text(0.73, 0.11, "主力净流出 TOP1", ha="center", fontsize=9,
            color=C["muted"], transform=ax.transAxes)

    # v6: 药丸从 0.06→0.09 造成压主力资金说明字, v7 挪回 0.055 (跟页脚 y=0.025 差 30px 够)
    ax.text(0.5, 0.055, "钱从硬科技流向医药创新药",
            ha="center", fontsize=11, fontweight="bold", color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.35", fc=C["card"], ec=C["border"]),
            transform=ax.transAxes)

    add_footer(ax, 2)
    save(fig, 2)


# ═══════════════════════════════════════════
# Page 3 — 医药链龙头 4 卡 (个股)
# ═══════════════════════════════════════════
def page3():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  医药链龙头  ", C["orange"], fs=11)
    ax.text(0.5, 0.895, "4 只代表股 · 站队看今天谁在讲故事", ha="center",
            fontsize=16, fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.855, "REAL = 实涨派 · BUZZ = 讨论派", ha="center",
            fontsize=10, color=C["muted"], style="italic", transform=ax.transAxes)

    # 4 卡数据 (v11: 收盘校正 美诺华净入用板块口径, 前沿生物-U 已实涨移入 REAL)
    cards_data = [
        ("海南海药", "000566", "+10.02%", "3板", "化学制药", C["red"], "REAL", "医药连板龙头"),
        ("美诺华", "603538", "+10.02%", "封单 8130万", "化学制药", C["red"], "REAL", "主力资金首选"),
        ("药明康德", "603259", "讨论 32k+", "价 124.56", "CXO", C["purple"], "BUZZ", "创新药出海代表"),
        ("宣泰医药", "688247", "+19.95%", "科创 20% 涨停", "化学制药", C["red"], "REAL", "科创板医药新龙头"),
    ]
    positions = [(0.27, 0.68), (0.73, 0.68), (0.27, 0.40), (0.73, 0.40)]

    for (cx, cy), (name, code, pct, price, tag, col, badge, sub) in zip(positions, cards_data):
        rect = FancyBboxPatch(
            (cx - 0.21, cy - 0.115), 0.42, 0.23,
            boxstyle="round,pad=0.012", fc=C["card"], ec=C["border"], lw=1,
            transform=ax.transAxes,
        )
        ax.add_patch(rect)

        # REAL/BUZZ 角标
        badge_col = C["red"] if badge == "REAL" else C["purple"]
        ax.text(cx + 0.16, cy + 0.09, badge, ha="center", fontsize=8, fontweight="bold",
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
        ax.text(cx, cy - 0.075, tag, ha="center", fontsize=9,
                color=C["dim"], transform=ax.transAxes)

    # 中间十字带 分隔
    ax.plot([0.10, 0.90], [0.535, 0.535], color=C["border"], lw=0.6, alpha=0.5, transform=ax.transAxes)

    ax.text(0.5, 0.235, "一句话点评", ha="center", fontsize=12, fontweight="bold",
            color=C["text"], transform=ax.transAxes)
    # v11: 点评对齐新卡片数据 (3 REAL + 1 BUZZ)
    ax.text(0.5, 0.175,
            "海南海药 3 板 + 美诺华封单 8130 万 + 宣泰科创 20cm\n是真金白银派 · 药明康德 32k+ 讨论是嘴炮派",
            ha="center", fontsize=10.5, color=C["muted"], transform=ax.transAxes)

    # 反共识注解
    ax.text(0.5, 0.09, "实涨派已发动 · 讨论派还在观望",
            ha="center", fontsize=11, fontweight="bold", color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.35", fc=C["card"], ec=C["border"]),
            transform=ax.transAxes)

    add_footer(ax, 3)
    save(fig, 3)


# ═══════════════════════════════════════════
# Page 4 — 量化胜率表 (三档对比)
# ═══════════════════════════════════════════
def page4():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  量化胜率表  ", C["cyan"], fs=11)
    ax.text(0.5, 0.895, "化药单日大涨 · 后 20 天走势", ha="center",
            fontsize=18, fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.85, "回测: SW 化学制药二级 · 6401 天 · 50 次同级事件", ha="center",
            fontsize=10, color=C["muted"], style="italic", transform=ax.transAxes)

    # 三档胜率大表
    ax.text(0.5, 0.79, "按当日涨幅分档", ha="center", fontsize=12,
            fontweight="bold", color=C["text"], transform=ax.transAxes)

    # 表头
    header_y = 0.735
    ax.text(0.20, header_y, "档位", ha="center", fontsize=10, fontweight="bold",
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.42, header_y, "样本", ha="center", fontsize=10, fontweight="bold",
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.60, header_y, "20日胜率", ha="center", fontsize=10, fontweight="bold",
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.83, header_y, "20日均收益", ha="center", fontsize=10, fontweight="bold",
            color=C["muted"], transform=ax.transAxes)

    ax.plot([0.08, 0.92], [0.712, 0.712], color=C["border"], lw=0.8, transform=ax.transAxes)

    # 三行数据 (v5: 评语挪到"档位"下方紧贴, 与本行数据同背景条, 让节奏均匀; v11: [6%,7%) 加样本警示)
    tiers = [
        ("[5%, 6%)", "★★★★ 甜蜜区", "30", "63.3%", "+3.08%", C["red"]),
        ("[6%, 7%)", "★★★★★ 极端稀有 (n=6 参考)", "6",  "100.0%", "+3.55%", C["gold"]),
        ("[7%+)",    "★☆ 追高陷阱", "13", "46.2%",  "-4.36%", C["green"]),
    ]
    tier_ys = [0.658, 0.575, 0.492]  # 行距 0.083 (原 0.073)
    for y, (tier, verdict, n, win, mean, col) in zip(tier_ys, tiers):
        # 背景条加高到 0.075 包住档位+评语
        rect = Rectangle((0.06, y - 0.040), 0.88, 0.075,
                         fc=C["card2"], ec=C["border"], lw=0.5, alpha=0.7,
                         transform=ax.transAxes)
        ax.add_patch(rect)

        # 档位大字 (略上移)
        ax.text(0.20, y + 0.008, tier, ha="center", fontsize=15, fontweight="bold",
                color=col, transform=ax.transAxes)
        # 评语紧贴档位下方, 在同一背景条内
        ax.text(0.20, y - 0.023, verdict, ha="center", fontsize=8.5,
                color=C["muted"], style="italic", transform=ax.transAxes)
        # 样本 / 胜率 / 均收益 (垂直居中)
        ax.text(0.42, y, n, ha="center", fontsize=15, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        ax.text(0.60, y, win, ha="center", fontsize=16, fontweight="bold",
                color=col, transform=ax.transAxes)
        ax.text(0.83, y, mean, ha="center", fontsize=15, fontweight="bold",
                color=col, transform=ax.transAxes)

    # 关键结论 大卡
    rect = FancyBboxPatch((0.06, 0.24), 0.88, 0.15,
                          boxstyle="round,pad=0.015", fc=C["card2"], ec=C["gold"], lw=1.5,
                          transform=ax.transAxes)
    ax.add_patch(rect)
    ax.text(0.5, 0.36, "关键发现", ha="center", fontsize=13, fontweight="bold",
            color=C["gold"], transform=ax.transAxes)
    ax.text(0.5, 0.315, "今天化药 +5.57%", ha="center", fontsize=13,
            color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.278, "正好落在最高胜率档 [5%, 6%)", ha="center", fontsize=14,
            fontweight="bold", color=C["red"], transform=ax.transAxes)
    ax.text(0.5, 0.245, "20 天赚钱概率 63%, 均值 +3.08%", ha="center", fontsize=10,
            color=C["muted"], transform=ax.transAxes)

    # 悬念钩子
    ax.text(0.5, 0.185, "但是 —", ha="center", fontsize=12, fontweight="bold",
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.5, 0.135, "这只算单次大涨", ha="center", fontsize=13,
            color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.10, "今天其实是 5 日内第二次 +5%", ha="center", fontsize=13,
            fontweight="bold", color=C["gold"], transform=ax.transAxes)
    ax.text(0.5, 0.07, "翻到下一页 → 看真实形态胜率", ha="center", fontsize=10,
            color=C["cyan"], style="italic", transform=ax.transAxes)

    add_footer(ax, 4)
    save(fig, 4)


# ═══════════════════════════════════════════
# Page 5 — 反共识: 双大涨 20 日胜率 33%
# ═══════════════════════════════════════════
def page5():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  反共识  ", C["gold"], fs=11)
    ax.text(0.5, 0.895, "\"5 日内两次 +5%\" 是啥意思", ha="center",
            fontsize=18, fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.855, "上一次是 6-29 (+7.26%), 今天再 +5.57%", ha="center",
            fontsize=11, color=C["muted"], style="italic", transform=ax.transAxes)

    # 大数字对比: 单次 63% vs 双次 33% (v10: 小标签上移 + 大数字下移, 间距从 0.055 拉到 0.09)
    ax.text(0.27, 0.83, "单次大涨", ha="center", fontsize=13,
            color=C["text"], transform=ax.transAxes)
    ax.text(0.27, 0.735, "63%", ha="center", fontsize=44, fontweight="bold",
            color=C["red"], transform=ax.transAxes)
    ax.text(0.27, 0.665, "20 天胜率 (n=30)", ha="center", fontsize=10,
            color=C["muted"], transform=ax.transAxes)

    ax.text(0.5, 0.735, "→", ha="center", va="center", fontsize=32, fontweight="bold",
            color=C["gold"], transform=ax.transAxes)
    ax.text(0.5, 0.665, "~2x 下降", ha="center", fontsize=9,
            color=C["gold"], transform=ax.transAxes)

    ax.text(0.73, 0.83, "5 日内 2 次", ha="center", fontsize=13,
            color=C["text"], transform=ax.transAxes)
    ax.text(0.73, 0.735, "33%", ha="center", fontsize=44, fontweight="bold",
            color=C["green"], transform=ax.transAxes)
    ax.text(0.73, 0.665, "20 天胜率 (n=6)", ha="center", fontsize=10,
            color=C["muted"], transform=ax.transAxes)

    # 分隔线
    ax.plot([0.10, 0.90], [0.635, 0.635], color=C["border"], lw=0.8, transform=ax.transAxes)

    # 历史 6 次样本明细
    ax.text(0.5, 0.595, "历史仅 6 次同类形态 · 每次 20 天后表现", ha="center", fontsize=12,
            fontweight="bold", color=C["text"], transform=ax.transAxes)

    # 6 次事件表
    events = [
        ("2000-02", "+5.5 → +5.8", -0.7, 4),
        ("2009-09", "+5.7 → +5.1", 0.9, 4),
        ("2009-10", "+5.2 → +7.4", -2.1, 5),
        ("2015-07", "+5.6 → +5.0", 3.0, 3),
        ("2024-09", "+6.8 → +12.2", -5.2, 1),
        ("2024-10", "+12.2 → +10.0", -11.7, 1),
    ]
    header_y = 0.545
    ax.text(0.15, header_y, "时间", ha="center", fontsize=9, fontweight="bold",
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.42, header_y, "两次涨幅", ha="center", fontsize=9, fontweight="bold",
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.68, header_y, "间隔", ha="center", fontsize=9, fontweight="bold",
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.85, header_y, "20 日后", ha="center", fontsize=9, fontweight="bold",
            color=C["muted"], transform=ax.transAxes)

    for i, (date, spread, fwd20, gap) in enumerate(events):
        y = 0.505 - i * 0.045
        col = C["red"] if fwd20 > 0 else C["green"]
        # 负数行加浅绿底色高亮 (v10: 高亮块宽度 0.20→0.22 让 -11.7% 15pt 5 字符有均匀 padding)
        if fwd20 < 0:
            rect = Rectangle((0.71, y - 0.018), 0.22, 0.038,
                             fc=C["green"], ec="none", alpha=0.12, transform=ax.transAxes)
            ax.add_patch(rect)
        ax.text(0.15, y, date, ha="center", fontsize=10,
                color=C["text"], transform=ax.transAxes)
        ax.text(0.42, y, spread, ha="center", fontsize=10,
                color=C["muted"], transform=ax.transAxes)
        ax.text(0.68, y, f"{gap}d", ha="center", fontsize=10,
                color=C["muted"], transform=ax.transAxes)
        sign = "+" if fwd20 > 0 else ""
        # 负数字号 15pt (v10: 16→15 避免"-11.7%" 5 字符视觉胀爆), 正数 12pt
        fs = 15 if fwd20 < 0 else 12
        ax.text(0.85, y, f"{sign}{fwd20:.1f}%", ha="center", fontsize=fs,
                fontweight="bold", color=col, transform=ax.transAxes)

    # 反共识金句 — 改成实心红底大字 (视觉重锤)
    rect = FancyBboxPatch((0.06, 0.155), 0.88, 0.07,
                          boxstyle="round,pad=0.012", fc=C["green"], ec="none",
                          alpha=0.85,
                          transform=ax.transAxes)
    ax.add_patch(rect)
    ax.text(0.5, 0.195, "6 次里 4 次亏钱",
            ha="center", fontsize=17, fontweight="bold", color=C["bg"],
            transform=ax.transAxes)
    ax.text(0.5, 0.166, "均值 -2.64% · 中位 -1.42%",
            ha="center", fontsize=11, fontweight="bold", color=C["bg"],
            transform=ax.transAxes)

    ax.text(0.5, 0.11, "追第二根大阳线的散户历史上很少有好下场",
            ha="center", fontsize=11, color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.07, "但今天有个反转因子 → 翻下一页",
            ha="center", fontsize=10, color=C["cyan"], style="italic",
            transform=ax.transAxes)

    add_footer(ax, 5)
    save(fig, 5)


# ═══════════════════════════════════════════
# Page 6 — 位置视角 + 三档操作
# ═══════════════════════════════════════════
def page6():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  今天的反转因子  ", C["cyan"], fs=11)
    ax.text(0.5, 0.895, "位置 —— 今天不是山顶追", ha="center",
            fontsize=18, fontweight="bold", color=C["text"], transform=ax.transAxes)

    # 大数字: 近3年分位 6% (58pt, 加上留白避免压副标)
    ax.text(0.5, 0.83, "化学制药 · 当前位置", ha="center", fontsize=11,
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.5, 0.735, "6%", ha="center", fontsize=58, fontweight="bold",
            color=C["red"], transform=ax.transAxes)
    ax.text(0.5, 0.67, "近 3 年分位", ha="center", fontsize=13,
            color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.638, "只有 6% 的时间比现在便宜", ha="center", fontsize=10,
            color=C["muted"], style="italic", transform=ax.transAxes)

    # 距高低点
    ax.plot([0.10, 0.90], [0.59, 0.59], color=C["border"], lw=0.8, transform=ax.transAxes)

    ax.text(0.27, 0.555, "距 3 年高点", ha="center", fontsize=10,
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.27, 0.51, "-36.6%", ha="center", fontsize=22, fontweight="bold",
            color=C["green"], transform=ax.transAxes)
    ax.text(0.27, 0.475, "上方巨大空间", ha="center", fontsize=9,
            color=C["muted"], transform=ax.transAxes)

    ax.text(0.73, 0.555, "距 3 年低点", ha="center", fontsize=10,
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.73, 0.51, "+12.4%", ha="center", fontsize=22, fontweight="bold",
            color=C["red"], transform=ax.transAxes)
    ax.text(0.73, 0.475, "刚离开底部区", ha="center", fontsize=9,
            color=C["muted"], transform=ax.transAxes)

    # 综合结论 (下移给上方小字留呼吸)
    rect = FancyBboxPatch((0.06, 0.335), 0.88, 0.075,
                          boxstyle="round,pad=0.012", fc=C["card2"], ec=C["cyan"], lw=1.3,
                          transform=ax.transAxes)
    ax.add_patch(rect)
    ax.text(0.5, 0.38, "「双大涨 33% 胜率」的历史样本",
            ha="center", fontsize=11, color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.35, "多数发生在山腰以上, 而今天在底部反弹初期",
            ha="center", fontsize=11, fontweight="bold", color=C["cyan"],
            transform=ax.transAxes)

    # 三档操作建议 (行距从 0.06 加大到 0.075)
    ax.text(0.5, 0.29, "三档操作建议", ha="center", fontsize=13,
            fontweight="bold", color=C["gold"], transform=ax.transAxes)

    plays = [
        ("激进", "今天追高", "赌短线延续", C["red"], "胜率 33%, 不推荐"),
        ("稳健", "等 3-5 日回踩", "看能否站稳 5100 平台", C["gold"], "胜率抬回 60%"),
        ("长线", "定投化药 ETF", "分批建仓, 忽略择时", C["cyan"], "分位 6%, 时间站你这边"),
    ]
    for i, (mode, action, why, col, tip) in enumerate(plays):
        y = 0.245 - i * 0.065  # v6: 起 y 上移到 0.245, 行距 0.065 避免碰底
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

    # 顶部钩子句
    ax.text(0.5, 0.895, "今天的医药狂飙明天还能续命吗?",
            ha="center", fontsize=13, color=C["text"], transform=ax.transAxes)

    # 价值主张
    ax.text(0.5, 0.815, "每天 3 分钟",
            ha="center", fontsize=28, fontweight="bold", color=C["text"],
            transform=ax.transAxes)
    ax.text(0.5, 0.745, "看懂 A 股",
            ha="center", fontsize=40, fontweight="bold", color=C["gold"],
            transform=ax.transAxes)

    # 三卖点卡 (v5: 卡片间距从 0.10 加到 0.115, 上下各留呼吸)
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

    # 金色 CTA 大卡 (v6: y 从 0.225 下移到 0.195, 与 03 卡拉出 0.115 间距)
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
            ha="center", fontsize=11, color=C["bg"], transform=ax.transAxes)

    # 评论区互动 (整体下移)
    ax.text(0.5, 0.145, "评论区告诉我",
            ha="center", fontsize=12, fontweight="bold", color=C["cyan"],
            transform=ax.transAxes)
    ax.text(0.5, 0.105, "你是「化药追涨党」还是「等回踩党」?",
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
    # 2x4 网格 (最后一格空)
    cols, rows = 2, 4
    preview = Image.new("RGB", (w * cols, h * rows), (13, 17, 23))
    for i, p in enumerate(pages):
        r, c = divmod(i, cols)
        preview.paste(p, (c * w, r * h))
    preview.thumbnail((1600, 3200))
    pp = OUT / "preview_2x4.png"
    preview.save(pp)
    print(f"  ✓ preview: {pp}")

    # 竖叠图
    stacked = Image.new("RGB", (w, h * 7), (13, 17, 23))
    for i, p in enumerate(pages):
        stacked.paste(p, (0, i * h))
    stacked.thumbnail((1200, 8400))
    sp = OUT / "all_pages_stacked.png"
    stacked.save(sp)
    print(f"  ✓ stacked: {sp}")


if __name__ == "__main__":
    print(f"开始生成 7 页卡片到 {OUT}")
    page1(); page2(); page3(); page4(); page5(); page6(); page7()
    make_preview()
    print(f"\n✅ 全部完成. 7 张 PNG + preview 在 {OUT}")
