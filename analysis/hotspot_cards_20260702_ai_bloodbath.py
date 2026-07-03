"""20260702 AI/TMT 血洗日 · 7 页深度卡片

主线: 电子 -4.47% + 主力净出 831 亿, 高位大跌能抄吗?
    电子 3 年分位 99.9%, 半导体 99.9%, 通信 98.8% — 超高位
    对照有色 +0.42% + 主力净入 39.34亿, 3年分位 85.5%

数据源:
  - output/hotspot/20260702/summary.json (收盘)
  - output/hotspot/20260702/industry_board_fallback.json (push2 直连行业+概念板块)
  - output/hotspot/20260702/xueqiu_ai_stocks.json (雪球 6 只 AI 票当日行情)
  - output/hotspot/20260702/backtest_ai_bloodbath.json (申万电子/半导体/通信/有色/贵金属 6402 天回测)

胜率量化 (SW 电子, n=87):
  - 无条件 单日≥-4% 后 20d 胜率 57.5% (n=200, 均 +1.69%) — 一般大跌可以博反弹
  - 高位(分位>80%) + ≥-3% 后 20d 胜率 51.2% (n=123)
  - **超高位(分位>90%) + ≥-3% 后 20d 胜率 42.5% (n=87, 均 -0.51%, 中 -1.90%) — 追跌陷阱**
  - 差距: 57.5% vs 42.5% = 15pp 减档

反公式 (方向翻转版): "位置越高, 大跌越是陷阱"

产物: output/hotspot/20260702/xhs_ai_bloodbath_v1/
"""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

# ─── 路径 ──────────────────────────
ROOT = Path("/das/user/QYJI/quant")
DATE = "20260702"
DAY_HUM = "2026-07-02"
TOPIC = "ai_bloodbath"
VERSION = 2

SUMMARY = json.loads((ROOT / f"output/hotspot/{DATE}/summary.json").read_text())
BOARDS  = json.loads((ROOT / f"output/hotspot/{DATE}/industry_board_fallback.json").read_text())
XQ_AI   = json.loads((ROOT / f"output/hotspot/{DATE}/xueqiu_ai_stocks.json").read_text())
BT      = json.loads((ROOT / f"output/hotspot/{DATE}/backtest_ai_bloodbath.json").read_text())

OUT = ROOT / f"output/hotspot/{DATE}/xhs_{TOPIC}_v{VERSION}"
OUT.mkdir(parents=True, exist_ok=True)

# ─── 调色板 (A股红涨绿跌) ─────────
C = {
    "bg": "#0d1117", "card": "#161b22", "card2": "#1c2129", "border": "#30363d",
    "text": "#c9d1d9", "muted": "#8b949e", "dim": "#6e7681",
    "blue": "#58a6ff", "green": "#3fb950", "red": "#f85149",
    "orange": "#d2991d", "purple": "#bc8cff", "gold": "#f0c040",
    "cyan": "#56d4dd", "rose": "#ff7b72",
    "warn": "#ff9500",  # 警告色 (陷阱/避雷), 跟 green(跌) 区分
}
CARD_W, CARD_H, DPI = 7.2, 9.6, 200

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "Droid Sans Fallback", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.weight"] = "regular"

# ─── 工具 ─────────────────────────
def new_card():
    fig, ax = plt.subplots(figsize=(CARD_W, CARD_H), facecolor=C["bg"])
    ax.set_facecolor(C["bg"])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)
    return fig, ax

def add_footer(ax, page, total=7):
    ax.text(0.5, 0.025, "* 数据: 东方财富/雪球/申万 · 回测基于 SW 电子/半导体/通信 6402 天日线 · 不构成投资建议",
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
    ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h,
                                boxstyle="round,pad=0.005,rounding_size=0.02",
                                fc=fc, ec=ec, lw=0.8, transform=ax.transAxes))

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
    pill(ax, 0.5, 0.955, f"  {DAY_HUM} · 量化复盘  ", C["gold"], fs=10)

    # 主标 — "AI 崩了 · 抄底 or 陷阱"
    ax.text(0.5, 0.885, "AI 血洗日", ha="center", fontsize=32, fontweight="bold",
            color=C["green"], transform=ax.transAxes)
    ax.text(0.5, 0.825, "电子 -4.47%  抄底 or 陷阱？", ha="center", fontsize=18,
            fontweight="bold", color=C["text"], transform=ax.transAxes)

    # 副标预告钩子
    pill(ax, 0.5, 0.762, "  历史高位大跌 · 20 日胜率仅 42.5%  ", C["warn"], fs=11)

    # 三大数字块 (卡)
    y_bar = 0.62
    for i, (val, sub, col) in enumerate([
        ("-831亿", "电子主力净出", C["green"]),
        ("99.9%", "近 3 年位置分位", C["warn"]),
        ("-11.56%", "新易盛领跌", C["green"]),
    ]):
        x = 0.185 + i*0.315
        card_bg(ax, x, y_bar, 0.27, 0.16)
        ax.text(x, y_bar+0.03, val, ha="center", fontsize=26, fontweight="bold",
                color=col, transform=ax.transAxes)
        ax.text(x, y_bar-0.048, sub, ha="center", fontsize=11, color=C["muted"],
                transform=ax.transAxes)

    # 反共识核心金句 (大卡)
    ax.text(0.5, 0.47, "反共识：", ha="center", fontsize=13, color=C["muted"],
            transform=ax.transAxes)
    ax.text(0.5, 0.415, "位置越高，越不是抄底", ha="center", fontsize=24,
            fontweight="bold", color=C["warn"], transform=ax.transAxes)
    ax.text(0.5, 0.362, "而是接盘", ha="center", fontsize=24, fontweight="bold",
            color=C["warn"], transform=ax.transAxes)

    # 底部对照数据 - 关键对比
    y_cmp = 0.24
    card_bg(ax, 0.5, y_cmp, 0.86, 0.13, fc=C["card2"])
    ax.text(0.5, y_cmp+0.038, "同样跌 4%，位置不同结果差 15pp", ha="center",
            fontsize=13, fontweight="bold", color=C["text"], transform=ax.transAxes)
    # 左右对比
    ax.text(0.30, y_cmp-0.008, "任意时段", ha="center", fontsize=10, color=C["muted"],
            transform=ax.transAxes)
    ax.text(0.30, y_cmp-0.046, "57.5%", ha="center", fontsize=20, fontweight="bold",
            color=C["red"], transform=ax.transAxes)
    ax.text(0.50, y_cmp-0.028, "→", ha="center", fontsize=22, color=C["dim"],
            transform=ax.transAxes)
    ax.text(0.70, y_cmp-0.008, "近 3 年高位", ha="center", fontsize=10, color=C["muted"],
            transform=ax.transAxes)
    ax.text(0.70, y_cmp-0.046, "42.5%", ha="center", fontsize=20, fontweight="bold",
            color=C["warn"], transform=ax.transAxes)

    ax.text(0.5, 0.155, "20 日反弹胜率 · 电子板块 6402 天回测", ha="center",
            fontsize=9, color=C["dim"], transform=ax.transAxes)

    ax.text(0.5, 0.105, "翻到下一页 →", ha="center", fontsize=11, color=C["cyan"],
            fontstyle="italic", transform=ax.transAxes)

    add_footer(ax, 1)
    save(fig, 1)


# ═══════════════════════════════════════════
# Page 2 — 资金搬家 (主力净出 vs 净入)
# ═══════════════════════════════════════════
def page2():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  P2 · 资金搬家日  ", C["cyan"], fs=10)

    # 主标 (v2: 顶部下移, 避开 pill)
    ax.text(0.5, 0.885, "机构今天砸盘了 831 亿", ha="center", fontsize=22,
            fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.837, "全流向老经济 + 有色", ha="center", fontsize=14, color=C["muted"],
            transform=ax.transAxes)

    # 净出 TOP5 (跌方, 绿) & 净入 TOP5 (涨方, 红)
    industries = sorted(BOARDS["industries"], key=lambda x: x["main_net_in"])
    out_top = industries[:5]
    in_top = sorted(BOARDS["industries"], key=lambda x: -x["main_net_in"])[:5]

    # 左右列标题
    ax.text(0.25, 0.775, "主力净流出 TOP5", ha="center", fontsize=12,
            fontweight="bold", color=C["green"], transform=ax.transAxes)
    ax.text(0.25, 0.747, "(AI/TMT 全军覆没)", ha="center", fontsize=9,
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.75, 0.775, "主力净流入 TOP5", ha="center", fontsize=12,
            fontweight="bold", color=C["red"], transform=ax.transAxes)
    ax.text(0.75, 0.747, "(老经济 + 有色接力)", ha="center", fontsize=9,
            color=C["muted"], transform=ax.transAxes)

    # v2: 5 行数据行距压缩到 0.05 (原 0.075), 5 行占 y=[0.48, 0.70]
    for i, x in enumerate(out_top):
        y = 0.69 - i*0.048
        amount = x["main_net_in"] / 1e8
        pct = x["pct_chg"]
        ax.text(0.06, y, x["name"], ha="left", fontsize=10.5, color=C["text"],
                fontweight="bold", transform=ax.transAxes)
        ax.text(0.42, y+0.008, f"{amount:+.0f}亿", ha="right", fontsize=12,
                color=C["green"], fontweight="bold", transform=ax.transAxes)
        ax.text(0.42, y-0.016, f"{pct:+.2f}%", ha="right", fontsize=8.5,
                color=C["green"], transform=ax.transAxes)

    for i, x in enumerate(in_top):
        y = 0.69 - i*0.048
        amount = x["main_net_in"] / 1e8
        pct = x["pct_chg"]
        col = C["red"] if pct >= 0 else C["green"]
        ax.text(0.56, y, x["name"], ha="left", fontsize=10.5, color=C["text"],
                fontweight="bold", transform=ax.transAxes)
        ax.text(0.94, y+0.008, f"+{amount:.0f}亿", ha="right", fontsize=12,
                color=C["red"], fontweight="bold", transform=ax.transAxes)
        ax.text(0.94, y-0.016, f"{pct:+.2f}%", ha="right", fontsize=8.5,
                color=col, transform=ax.transAxes)

    # v2: 21× 量级差 移到两列下方独立带, 视觉重锤 (不被夹在两列之间)
    y_mag = 0.415
    card_bg(ax, 0.5, y_mag, 0.86, 0.10, fc=C["card2"], ec=C["warn"])
    ax.text(0.5, y_mag+0.028, "净出/净入 量级差", ha="center", fontsize=11,
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.32, y_mag-0.015, "-831亿", ha="center", fontsize=20, fontweight="bold",
            color=C["green"], transform=ax.transAxes)
    ax.text(0.5, y_mag-0.010, "vs", ha="center", fontsize=13, color=C["muted"],
            transform=ax.transAxes)
    ax.text(0.68, y_mag-0.015, "+39亿", ha="center", fontsize=20, fontweight="bold",
            color=C["red"], transform=ax.transAxes)
    ax.text(0.87, y_mag-0.010, "~ 21×", ha="center", fontsize=15, fontweight="bold",
            color=C["warn"], transform=ax.transAxes)

    # 核心解读卡 (v2: 保留原样, 是全页锚点)
    card_bg(ax, 0.5, 0.23, 0.86, 0.14, fc=C["card2"])
    ax.text(0.5, 0.28, "机构在做什么？", ha="center", fontsize=12,
            fontweight="bold", color=C["cyan"], transform=ax.transAxes)
    ax.text(0.5, 0.238, "从 AI/半导体撤 831 亿，只往老经济回补 39 亿", ha="center",
            fontsize=11, color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.198, "剩下的 792 亿净卖出 · 无人接盘", ha="center", fontsize=11,
            fontweight="bold", color=C["warn"], transform=ax.transAxes)
    ax.text(0.5, 0.161, "= 大盘失血", ha="center", fontsize=10, color=C["muted"],
            fontstyle="italic", transform=ax.transAxes)

    ax.text(0.5, 0.09, "→ 下一页看板块涨跌全光谱",
            ha="center", fontsize=10, color=C["dim"], fontstyle="italic",
            transform=ax.transAxes)

    add_footer(ax, 2)
    save(fig, 2)


# ═══════════════════════════════════════════
# Page 3 — 板块光谱 (概念涨跌 TOP)
# ═══════════════════════════════════════════
def page3():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  P3 · 概念板块全光谱  ", C["cyan"], fs=10)

    ax.text(0.5, 0.905, "涨的都是避险 · 跌的全是抱团", ha="center", fontsize=18,
            fontweight="bold", color=C["text"], transform=ax.transAxes)

    concepts = BOARDS["concepts"]
    top = sorted(concepts, key=lambda x: -x["pct_chg"])[:5]
    bot = sorted(concepts, key=lambda x: x["pct_chg"])[:5]

    max_abs = max(top[0]["pct_chg"], abs(bot[0]["pct_chg"]))

    # 涨幅 TOP5 (红字, A股规范)
    ax.text(0.25, 0.83, "涨幅 TOP5", ha="center", fontsize=12,
            fontweight="bold", color=C["red"], transform=ax.transAxes)
    ax.text(0.25, 0.805, "避险/中药/黄金", ha="center", fontsize=9, color=C["muted"],
            transform=ax.transAxes)

    ax.text(0.75, 0.83, "跌幅 TOP5", ha="center", fontsize=12,
            fontweight="bold", color=C["green"], transform=ax.transAxes)
    ax.text(0.75, 0.805, "AI 硬件/苹果链/基金重仓", ha="center", fontsize=9,
            color=C["muted"], transform=ax.transAxes)

    # 柱图
    bar_max_w = 0.30
    for i, x in enumerate(top):
        y = 0.76 - i*0.06
        w = bar_max_w * (x["pct_chg"] / max_abs)
        ax.add_patch(Rectangle((0.15, y-0.021), w, 0.028, fc=C["red"], ec="none",
                              alpha=0.75, transform=ax.transAxes))
        ax.text(0.13, y-0.006, x["name"], ha="right", fontsize=10.5,
                color=C["text"], transform=ax.transAxes)
        ax.text(0.16+w, y-0.007, f"{x['pct_chg']:+.2f}%", ha="left", fontsize=10.5,
                color=C["red"], fontweight="bold", transform=ax.transAxes)

    for i, x in enumerate(bot):
        y = 0.76 - i*0.06
        w = bar_max_w * (abs(x["pct_chg"]) / max_abs)
        ax.add_patch(Rectangle((0.55, y-0.021), w, 0.028, fc=C["green"], ec="none",
                              alpha=0.75, transform=ax.transAxes))
        ax.text(0.53, y-0.006, x["name"], ha="right", fontsize=10.5,
                color=C["text"], transform=ax.transAxes)
        ax.text(0.56+w, y-0.007, f"{x['pct_chg']:+.2f}%", ha="left", fontsize=10.5,
                color=C["green"], fontweight="bold", transform=ax.transAxes)

    # 核心洞察卡
    y_ins = 0.34
    card_bg(ax, 0.5, y_ins, 0.86, 0.20, fc=C["card2"])
    ax.text(0.5, 0.415, "光谱两端在说什么？", ha="center", fontsize=13,
            fontweight="bold", color=C["cyan"], transform=ax.transAxes)

    # 双列: 涨方共同点 / 跌方共同点
    ax.text(0.25, 0.365, "涨方共同点", ha="center", fontsize=10.5,
            fontweight="bold", color=C["red"], transform=ax.transAxes)
    for i, t in enumerate(["低估值老经济", "避险 (黄金)", "抗周期 (中药)"]):
        ax.text(0.25, 0.325 - i*0.028, "· " + t, ha="center", fontsize=9.5,
                color=C["text"], transform=ax.transAxes)

    ax.text(0.75, 0.365, "跌方共同点", ha="center", fontsize=10.5,
            fontweight="bold", color=C["green"], transform=ax.transAxes)
    for i, t in enumerate(["AI 抱团票 (创业成份)", "TMT 硬件 (蓝宝石/苹果)", "基金重仓 (-3.15%)"]):
        ax.text(0.75, 0.325 - i*0.028, "· " + t, ha="center", fontsize=9.5,
                color=C["text"], transform=ax.transAxes)

    ax.text(0.5, 0.225, "→ 下一页看散户抱团的雪球 6 只 AI 今天全被埋",
            ha="center", fontsize=10, color=C["dim"], fontstyle="italic",
            transform=ax.transAxes)

    # 底部提示
    ax.text(0.5, 0.155, "基金重仓 -3.15%  ·  机构在真砸不是喊", ha="center",
            fontsize=11, fontweight="bold", color=C["warn"],
            transform=ax.transAxes)

    add_footer(ax, 3)
    save(fig, 3)


# ═══════════════════════════════════════════
# Page 4 — 讨论抱团反面教材 (雪球 6 只 AI)
# ═══════════════════════════════════════════
def page4():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  P4 · 讨论抱团反面教材  ", C["cyan"], fs=10)

    ax.text(0.5, 0.905, "雪球讨论 TOP10 里 6 只 AI", ha="center", fontsize=18,
            fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.858, "今天全被埋", ha="center", fontsize=22, fontweight="bold",
            color=C["green"], transform=ax.transAxes)

    # 6 只票网格 (2x3)
    stocks = sorted(XQ_AI, key=lambda x: x["pct"])  # 按跌幅从大到小
    positions = [(0.25, 0.68), (0.5, 0.68), (0.75, 0.68),
                 (0.25, 0.48), (0.5, 0.48), (0.75, 0.48)]

    for stk, (cx, cy) in zip(stocks, positions):
        card_bg(ax, cx, cy, 0.28, 0.16)
        # 股票名
        ax.text(cx, cy+0.05, stk["name"], ha="center", fontsize=13, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        # 大跌幅
        pct = stk["pct"]
        ax.text(cx, cy+0.005, f"{pct:+.2f}%", ha="center", fontsize=22,
                fontweight="bold", color=C["green"], transform=ax.transAxes)
        # 讨论量
        tw = next((t for t in SUMMARY["xueqiu_tweet_top10"] if t["股票代码"].endswith(stk["code"])), None)
        if tw:
            ax.text(cx, cy-0.045, f"讨论量 {tw['关注']/1e3:.1f}k", ha="center", fontsize=9,
                    color=C["purple"], transform=ax.transAxes)

    # 核心反差金句
    ax.text(0.5, 0.335, "越聊越跌 · 讨论量登顶=情绪透支", ha="center", fontsize=14,
            fontweight="bold", color=C["warn"], transform=ax.transAxes)

    # 统计
    avg_pct = sum(s["pct"] for s in stocks) / len(stocks)
    n_over_6 = sum(1 for s in stocks if s["pct"] < -6)
    card_bg(ax, 0.5, 0.235, 0.86, 0.14, fc=C["card2"])
    ax.text(0.5, 0.284, "6 只票平均跌幅", ha="center", fontsize=10.5,
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.5, 0.235, f"{avg_pct:+.2f}%", ha="center", fontsize=32,
            fontweight="bold", color=C["green"], transform=ax.transAxes)
    ax.text(0.5, 0.185, f"{n_over_6} 只跌超 6%  ·  同日沪指仅跌 1% 左右",
            ha="center", fontsize=10, color=C["muted"], transform=ax.transAxes)

    ax.text(0.5, 0.11, "→ 下一页看历史数据 · 高位大跌能不能抄底",
            ha="center", fontsize=10, color=C["cyan"], fontstyle="italic",
            transform=ax.transAxes)

    add_footer(ax, 4)
    save(fig, 4)


# ═══════════════════════════════════════════
# Page 5 — 胜率表 (三档条件对比)
# ═══════════════════════════════════════════
def page5():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  P5 · 大跌能抄底吗 · 电子回测  ", C["gold"], fs=10)

    ax.text(0.5, 0.9, "6402 天历史 · 三档胜率", ha="center", fontsize=18,
            fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.858, "位置越高，抄底越危险", ha="center", fontsize=13,
            color=C["muted"], transform=ax.transAxes)

    # 三行卡片
    e = BT["SW电子"]["results"]
    rows = [
        ("无条件 单日≥-4%", e["无条件 单日≥-4%"], C["red"], "任意时段的大跌都可以博反弹"),
        ("高位 (分位>80%) + ≥-3%", e["高位(>80%)+≥-3%"], C["orange"], "位置偏高，胜率明显下降"),
        ("超高位 (分位>90%) + ≥-3%", e["超高位(>90%)+≥-3%"], C["warn"], "追跌陷阱 · n=87 样本充足"),
    ]

    # 表头
    y_head = 0.79
    ax.text(0.05, y_head, "档位", ha="left", fontsize=10, color=C["muted"],
            fontweight="bold", transform=ax.transAxes)
    ax.text(0.55, y_head, "样本 n", ha="center", fontsize=10, color=C["muted"],
            fontweight="bold", transform=ax.transAxes)
    ax.text(0.72, y_head, "20 日胜率", ha="center", fontsize=10, color=C["muted"],
            fontweight="bold", transform=ax.transAxes)
    ax.text(0.9, y_head, "均值", ha="center", fontsize=10, color=C["muted"],
            fontweight="bold", transform=ax.transAxes)

    # 分隔线
    ax.plot([0.05, 0.95], [0.775, 0.775], color=C["border"], lw=0.6,
            transform=ax.transAxes)

    for i, (name, data, col, note) in enumerate(rows):
        y = 0.72 - i*0.13
        # 卡片底 (超高位一档用底色高亮)
        if i == 2:
            ax.add_patch(Rectangle((0.03, y-0.045), 0.94, 0.10, fc=col, ec="none",
                                  alpha=0.13, transform=ax.transAxes))
        # 档名
        ax.text(0.05, y+0.023, name, ha="left", fontsize=11.5, fontweight="bold",
                color=col, transform=ax.transAxes)
        ax.text(0.05, y-0.015, note, ha="left", fontsize=9, color=C["muted"],
                transform=ax.transAxes)
        # 数字
        ax.text(0.55, y+0.005, f"{data['n']}", ha="center", fontsize=15,
                color=C["text"], transform=ax.transAxes)
        # 胜率大字
        win_col = C["red"] if data["win20"] > 50 else col
        ax.text(0.72, y+0.005, f"{data['win20']:.1f}%", ha="center", fontsize=20,
                fontweight="bold", color=win_col, transform=ax.transAxes)
        # 均值 (符号敏感 A股红涨绿跌)
        mean_col = C["red"] if data["mean20"] > 0 else C["green"]
        ax.text(0.9, y+0.005, f"{data['mean20']:+.2f}%", ha="center", fontsize=14,
                fontweight="bold", color=mean_col, transform=ax.transAxes)

    # 关键差距金句 (底部大结论)
    card_bg(ax, 0.5, 0.22, 0.86, 0.14, fc=C["warn"], ec=C["warn"])
    ax.text(0.5, 0.278, "同样跌 4%，位置一变胜率减档", ha="center", fontsize=13,
            fontweight="bold", color=C["bg"], transform=ax.transAxes)
    ax.text(0.5, 0.222, "57.5%  →  42.5%", ha="center", fontsize=28,
            fontweight="bold", color=C["bg"], transform=ax.transAxes)
    ax.text(0.5, 0.168, "减档 15 pp · 均值从 +1.69% 掉到 -0.51%",
            ha="center", fontsize=10, color=C["bg"], transform=ax.transAxes)

    ax.text(0.5, 0.09, "→ 下一页看长期视角 (60 日) + 三档操作策略",
            ha="center", fontsize=10, color=C["cyan"], fontstyle="italic",
            transform=ax.transAxes)

    add_footer(ax, 5)
    save(fig, 5)


# ═══════════════════════════════════════════
# Page 6 — 反共识 + 操作策略
# ═══════════════════════════════════════════
def page6():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  P6 · 长期视角 · 操作策略  ", C["gold"], fs=10)

    ax.text(0.5, 0.9, "60 日视角更狠", ha="center", fontsize=22,
            fontweight="bold", color=C["text"], transform=ax.transAxes)

    # 通信板块 60 日胜率极值展示 (核心反公式重锤)
    tx = BT["SW通信"]["results"]["高位(>80%)+≥-4%"]
    card_bg(ax, 0.5, 0.795, 0.86, 0.10, fc=C["card2"])
    ax.text(0.5, 0.832, "SW 通信 · 高位 + 单日≥-4%", ha="center", fontsize=11,
            fontweight="bold", color=C["warn"], transform=ax.transAxes)
    ax.text(0.5, 0.783, f"60 日均值 {tx['mean60']:+.2f}%  ·  胜率 {tx['win60']:.1f}%",
            ha="center", fontsize=14, fontweight="bold", color=C["green"],
            transform=ax.transAxes)
    ax.text(0.5, 0.755, f"n={tx['n']} · 高位大跌不但短期不反弹，60 日仍在跌",
            ha="center", fontsize=9, color=C["muted"], transform=ax.transAxes)

    # 三档操作
    ax.text(0.5, 0.685, "三档操作建议", ha="center", fontsize=15,
            fontweight="bold", color=C["cyan"], transform=ax.transAxes)

    strategies = [
        ("激进抄底党", C["red"],
         "只做 5 日博反弹，止损 -3%，不隔夜留仓",
         "样本 5 日胜率 49.4% · 均 -0.94% · 期望负"),
        ("稳健派", C["orange"],
         "等分位跌到 60% 以下 (~3 年中位)再入",
         "回测 20 日胜率能回到 50%+ · 至少不接刀"),
        ("长线定投", C["green"],
         "AI 是长期方向，但今天不是好入场点",
         "指数级投资等分位<40%再启动 DCA"),
    ]

    for i, (title, col, act, evd) in enumerate(strategies):
        y = 0.58 - i*0.115
        card_bg(ax, 0.5, y, 0.88, 0.10)
        # 左侧 pill 标题
        ax.text(0.09, y+0.028, title, ha="left", fontsize=12,
                fontweight="bold", color=col, transform=ax.transAxes)
        # 操作
        ax.text(0.09, y-0.008, act, ha="left", fontsize=10, color=C["text"],
                transform=ax.transAxes)
        # 数据佐证
        ax.text(0.09, y-0.037, "· " + evd, ha="left", fontsize=9,
                color=C["muted"], fontstyle="italic", transform=ax.transAxes)

    # 底部反共识金句
    card_bg(ax, 0.5, 0.19, 0.88, 0.11, fc=C["card2"])
    ax.text(0.5, 0.226, "记住这句话", ha="center", fontsize=10, color=C["muted"],
            transform=ax.transAxes)
    ax.text(0.5, 0.178, "位置比跌幅重要", ha="center", fontsize=20,
            fontweight="bold", color=C["gold"], transform=ax.transAxes)
    ax.text(0.5, 0.14, "跌 4% 不等于便宜 · 得先看你在什么位置", ha="center",
            fontsize=9.5, color=C["muted"], fontstyle="italic",
            transform=ax.transAxes)

    ax.text(0.5, 0.09, "下一页：为什么我敢每天发反共识？→", ha="center", fontsize=10,
            color=C["cyan"], fontstyle="italic", transform=ax.transAxes)

    add_footer(ax, 6)
    save(fig, 6)


# ═══════════════════════════════════════════
# Page 7 — CTA
# ═══════════════════════════════════════════
def page7():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  最后一页 · 关于账号  ", C["purple"], fs=10)

    # 大标题
    ax.text(0.5, 0.855, "复旦杰伦", ha="center", fontsize=42, fontweight="bold",
            color=C["gold"], transform=ax.transAxes)
    ax.text(0.5, 0.795, "拒绝小作文  ·  拒绝喊单", ha="center", fontsize=16,
            color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.755, "只讲数据 · 只讲胜率 · 只讲位置", ha="center", fontsize=12,
            color=C["muted"], transform=ax.transAxes)

    # 三档卡片 · 内容线
    y_cards = 0.62
    for i, (icon, title, desc) in enumerate([
        ("01", "每日热点", "散户在聊啥 · 涨停/炸板/龙虎榜"),
        ("02", "深度回测", "6400+ 天数据 · 胜率/均值/中位数"),
        ("03", "反共识", "帮你避坑 · 不做接盘侠"),
    ]):
        y = y_cards - i*0.10
        card_bg(ax, 0.5, y, 0.86, 0.08)
        ax.text(0.09, y, icon, ha="left", fontsize=24, fontweight="bold",
                color=C["gold"], transform=ax.transAxes)
        ax.text(0.20, y+0.015, title, ha="left", fontsize=13, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        ax.text(0.20, y-0.015, desc, ha="left", fontsize=10, color=C["muted"],
                transform=ax.transAxes)

    # CTA 大卡
    card_bg(ax, 0.5, 0.24, 0.88, 0.12, fc=C["card2"], ec=C["cyan"])
    ax.text(0.5, 0.288, "今天你是哪一派？", ha="center", fontsize=13,
            fontweight="bold", color=C["cyan"], transform=ax.transAxes)
    ax.text(0.5, 0.238, "抄底党 · 观望党 · 早跑党", ha="center", fontsize=16,
            fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.198, "评论区聊聊 · 明天出打脸/兑现追更",
            ha="center", fontsize=10, color=C["muted"],
            fontstyle="italic", transform=ax.transAxes)

    ax.text(0.5, 0.11, "关注 · 点赞 · 收藏  ·  下期见", ha="center", fontsize=11,
            fontweight="bold", color=C["gold"], transform=ax.transAxes)

    add_footer(ax, 7)
    save(fig, 7)


# ═══════════════════════════════════════════
# Preview & Stack
# ═══════════════════════════════════════════
def compose():
    from PIL import Image
    pngs = [OUT / f"page_{i}.png" for i in range(1, 8)]
    imgs = [Image.open(p) for p in pngs]
    w, h = imgs[0].size
    # 2x4
    W, H = w*4, h*2
    canvas = Image.new("RGB", (W, H), (13, 17, 23))
    for i, im in enumerate(imgs):
        canvas.paste(im, ((i%4)*w, (i//4)*h))
    canvas.thumbnail((2000, 2000))
    canvas.save(OUT / "preview_2x4.png")
    print(f"  ✓ preview_2x4.png")
    # 竖叠
    S = Image.new("RGB", (w, h*7), (13, 17, 23))
    for i, im in enumerate(imgs):
        S.paste(im, (0, i*h))
    S.thumbnail((1200, 8500))
    S.save(OUT / "all_pages_stacked.png")
    print(f"  ✓ all_pages_stacked.png")


if __name__ == "__main__":
    print(f"渲染 → {OUT}")
    page1(); page2(); page3(); page4(); page5(); page6(); page7()
    compose()
    print("done")
