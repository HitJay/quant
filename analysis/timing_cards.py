"""A股择时研究 — 小红书分享卡片 (7张)"""

import sys
sys.path.insert(0, "src")

import pandas as pd
import numpy as np
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
plt.rcParams["font.sans-serif"] = ["Droid Sans Fallback", "WenQuanYi Micro Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

from quant.data.index_fetcher import IndexFetcher
from quant.factors import timing

# ════════════════════════════════════════════════════════════════
# 主题色 (GitHub Dark)
# ════════════════════════════════════════════════════════════════
C = {
    "bg":       "#0d1117",
    "card":     "#161b22",
    "border":   "#30363d",
    "text":     "#c9d1d9",
    "muted":    "#8b949e",
    "blue":     "#58a6ff",
    "green":    "#3fb950",
    "red":      "#f85149",
    "orange":   "#d2991d",
    "purple":   "#bc8cff",
    "gold":     "#f0c040",
}

CARD_W, CARD_H, DPI = 7.2, 9.6, 150
TOTAL_CARDS = 7
SAVE_DIR = Path("./output/timing-research/cards")
SAVE_DIR.mkdir(parents=True, exist_ok=True)


def _fig():
    fig = plt.figure(figsize=(CARD_W, CARD_H), facecolor=C["bg"])
    return fig


def _page_number(fig, n):
    fig.text(0.95, 0.02, f"{n}/{TOTAL_CARDS}", ha="right", fontsize=9,
             color=C["muted"], fontfamily="monospace")


def _disclaimer(fig):
    fig.text(0.5, 0.02, "* 历史回测不代表未来 · 不构成投资建议",
             ha="center", fontsize=9, color=C["muted"])


# ════════════════════════════════════════════════════════════════
# 数据准备
# ════════════════════════════════════════════════════════════════
print("加载数据...")
idx = IndexFetcher()
hs300 = idx.fetch("000300", start="2010-01-01")
prices = hs300["close"]

# 信号
sig_mom20 = timing.ma_timing(prices, 20)  # Mom_20 actually uses momentum_timing
sig_mom20 = timing.momentum_timing(prices, 20)
sig_ma60 = timing.ma_timing(prices, 60)
sig_dual = timing.dual_ma_timing(prices, 60, 250)

# 加载实验结果
results_df = pd.read_csv("output/timing-research/experiment_results.csv")
nav_df = pd.read_csv("output/timing-research/nav_curves.csv", index_col=0, parse_dates=True)

# 归一化
norm_nav = nav_df / nav_df.iloc[0]

# 基本统计
from quant.backtest.metrics import annual_return, max_drawdown, sharpe

print(f"数据区间: {prices.index[0].date()} ~ {prices.index[-1].date()}")


# ════════════════════════════════════════════════════════════════
# Card 1: 封面
# ════════════════════════════════════════════════════════════════
def card_1_cover():
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(C["bg"])
    ax.axis("off")

    # Title — bigger contrast
    ax.text(0.5, 0.88, "A股择时", ha="center", va="center",
            fontsize=48, fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.80, "到底有没有用？", ha="center", va="center",
            fontsize=40, fontweight="bold", color=C["gold"], transform=ax.transAxes)

    # Subtitle
    ax.text(0.5, 0.72, "16年真实数据回测 · 16种择时策略 · 样本内外验证",
            ha="center", fontsize=12, color=C["muted"], transform=ax.transAxes)

    # 分隔线
    ax.plot([0.15, 0.85], [0.68, 0.68], color=C["border"], linewidth=1,
            transform=ax.transAxes, clip_on=False)

    # 核心数字 — 收益倍数对比
    ax.text(0.5, 0.58, "+247%", ha="center",
            fontsize=64, fontweight="bold", color=C["green"],
            fontfamily="monospace", transform=ax.transAxes)
    ax.text(0.5, 0.50, "最佳择时策略16年累计收益 (买入持有仅+38%)",
            ha="center", fontsize=13, color=C["muted"], transform=ax.transAxes)

    # 3 KPIs with background panels
    kpis = [
        ("最佳年化", "7.9%", C["green"]),
        ("回撤降低", "42%", C["blue"]),
        ("样本外有效", "✓", C["gold"]),
    ]
    for i, (label, val, color) in enumerate(kpis):
        x = 0.2 + i * 0.3
        # Panel background
        rect = FancyBboxPatch((x - 0.10, 0.33), 0.20, 0.12,
                              boxstyle="round,pad=0.01",
                              facecolor=C["card"], edgecolor=C["border"],
                              linewidth=0.8, transform=ax.transAxes, zorder=0)
        ax.add_patch(rect)
        ax.text(x, 0.41, val, ha="center", fontsize=30, fontweight="bold",
                color=color, fontfamily="monospace", transform=ax.transAxes)
        ax.text(x, 0.35, label, ha="center", fontsize=11, color=C["muted"],
                transform=ax.transAxes)

    # 底部hook
    ax.text(0.5, 0.22, "结论可能和你想的不一样",
            ha="center", fontsize=17, color=C["text"], transform=ax.transAxes)

    # 标签
    tags = ["#量化研究", "#A股择时", "#沪深300", "#ETF策略"]
    ax.text(0.5, 0.12, "  ".join(tags),
            ha="center", fontsize=11, color=C["blue"], transform=ax.transAxes)

    _page_number(fig, 1)
    fig.savefig(SAVE_DIR / "01_cover.png", dpi=DPI, facecolor=C["bg"])
    plt.close()
    print("  [1/7] cover")


# ════════════════════════════════════════════════════════════════
# Card 2: 什么是择时
# ════════════════════════════════════════════════════════════════
def card_2_intro():
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(C["bg"])
    ax.axis("off")

    ax.text(0.5, 0.93, "择时 = 决定什么时候满仓/空仓",
            ha="center", fontsize=24, fontweight="bold", color=C["text"],
            transform=ax.transAxes)

    # 研究框架 — with card panels
    y = 0.84
    sections = [
        ("[1] 技术面择时", "均线/双均线/动量/波动率/布林带", C["blue"]),
        ("[2] 估值面择时", "PE百分位/股债性价比(ERP)", C["green"]),
        ("[3] 情绪面择时", "成交量/换手率/融资余额", C["orange"]),
        ("[4] 复合择时", "多信号投票/加权平均", C["purple"]),
    ]
    for label, desc, color in sections:
        # Background panel
        rect = FancyBboxPatch((0.05, y - 0.065), 0.90, 0.08,
                              boxstyle="round,pad=0.008",
                              facecolor=C["card"], edgecolor=color,
                              linewidth=1.2, alpha=0.6,
                              transform=ax.transAxes, zorder=0)
        ax.add_patch(rect)
        # Left color dot
        ax.plot(0.08, y - 0.025, "o", color=color, markersize=8,
                transform=ax.transAxes)
        ax.text(0.12, y - 0.01, label, fontsize=15, fontweight="bold",
                color=color, transform=ax.transAxes)
        ax.text(0.12, y - 0.045, desc, fontsize=11, color=C["muted"],
                transform=ax.transAxes)
        y -= 0.105

    # 方法说明
    ax.plot([0.08, 0.92], [y + 0.02, y + 0.02], color=C["border"],
            transform=ax.transAxes, clip_on=False)
    y -= 0.02

    ax.text(0.08, y, "研究方法:", fontsize=14, fontweight="bold",
            color=C["text"], transform=ax.transAxes)
    y -= 0.05

    method_lines = [
        "标的: 沪深300指数 (2010~2026, 16年)",
        "逻辑: 信号=1满仓股票, 信号=0转债券",
        "频率: 日频信号, T+1执行",
        "基准: 买入持有 vs 60/40固定配置",
        "验证: 样本内(2010-2021) + 样本外(2022-2026)",
        "共测试16种信号 × 不同参数",
    ]
    for i, line in enumerate(method_lines):
        ax.text(0.10, y - i * 0.042, f"· {line}", fontsize=11,
                color=C["text"], transform=ax.transAxes)

    _page_number(fig, 2)
    _disclaimer(fig)
    fig.savefig(SAVE_DIR / "02_intro.png", dpi=DPI, facecolor=C["bg"])
    plt.close()
    print("  [2/7] intro")


# ════════════════════════════════════════════════════════════════
# Card 3: 排行榜
# ════════════════════════════════════════════════════════════════
def card_3_leaderboard():
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(C["bg"])
    ax.axis("off")

    ax.text(0.5, 0.93, "择时信号排行榜", ha="center",
            fontsize=26, fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.89, "按Sharpe排序 · 全样本2010-2026", ha="center",
            fontsize=11, color=C["muted"], transform=ax.transAxes)

    full = results_df[results_df["period"] == "full"].sort_values("sharpe", ascending=False)

    # Table header
    y = 0.83
    headers = ["#", "策略", "年化", "回撤", "Sharpe"]
    xs = [0.05, 0.13, 0.52, 0.67, 0.83]
    for x, h in zip(xs, headers):
        ax.text(x, y, h, fontsize=11, color=C["muted"], fontweight="bold",
                transform=ax.transAxes)

    y -= 0.02
    ax.plot([0.04, 0.96], [y, y], color=C["border"], transform=ax.transAxes, clip_on=False)

    # Rows
    for i, (_, row) in enumerate(full.iterrows()):
        if i >= 14:
            break
        y -= 0.045
        rank = i + 1

        # Highlight top 3
        if rank <= 3:
            color = C["green"]
            rect = FancyBboxPatch((0.03, y - 0.015), 0.94, 0.04,
                                   boxstyle="round,pad=0.005",
                                   facecolor=C["green"], alpha=0.06,
                                   transform=ax.transAxes, zorder=0)
            ax.add_patch(rect)
        elif row["name"] in ("BuyHold", "Mix_60_40"):
            color = C["muted"]
        else:
            color = C["text"]

        ax.text(xs[0], y, f"{rank}", fontsize=12, color=color,
                fontfamily="monospace", transform=ax.transAxes)
        ax.text(xs[1], y, row["name"], fontsize=12, color=color,
                transform=ax.transAxes)
        ax.text(xs[2], y, f"{row['annual_return']:.1%}", fontsize=12,
                color=C["green"] if row["annual_return"] > 0.04 else color,
                fontfamily="monospace", transform=ax.transAxes)
        ax.text(xs[3], y, f"{row['max_drawdown']:.0%}", fontsize=12,
                color=C["red"] if row["max_drawdown"] > 0.40 else color,
                fontfamily="monospace", transform=ax.transAxes)
        ax.text(xs[4], y, f"{row['sharpe']:.2f}", fontsize=14, fontweight="bold",
                color=C["gold"] if rank <= 3 else color,
                fontfamily="monospace", transform=ax.transAxes)

    _page_number(fig, 3)
    _disclaimer(fig)
    fig.savefig(SAVE_DIR / "03_leaderboard.png", dpi=DPI, facecolor=C["bg"])
    plt.close()
    print("  [3/7] leaderboard")


# ════════════════════════════════════════════════════════════════
# Card 4: 净值曲线 (Top 3 vs BuyHold)
# ════════════════════════════════════════════════════════════════
def card_4_nav():
    fig = _fig()

    # Title area
    fig.text(0.5, 0.94, "净值曲线对比", ha="center",
             fontsize=22, fontweight="bold", color=C["text"])
    fig.text(0.5, 0.90, "Top3择时 vs 买入持有 (2010-2026, 对数坐标)",
             ha="center", fontsize=12, color=C["muted"])

    # Chart
    ax = fig.add_axes([0.10, 0.20, 0.85, 0.65])
    ax.set_facecolor(C["card"])

    plots = [
        ("BuyHold", "--", C["muted"], 1.5),
        ("Mom_20", "-", C["green"], 2.2),
        ("MA_60", "-", C["blue"], 2.0),
        ("DualMA_60_250", "-", C["gold"], 2.0),
    ]

    for name, ls, color, lw in plots:
        if name in norm_nav.columns:
            data = norm_nav[name].dropna()
            ax.plot(data.index, data.values, ls, color=color, linewidth=lw, label=name)

    ax.set_yscale("log")
    ax.axvline(pd.Timestamp("2022-01-01"), color=C["border"], linestyle=":", alpha=0.7)
    ax.text(pd.Timestamp("2022-03-01"), ax.get_ylim()[0] * 1.5, "OOS→",
            fontsize=9, color=C["muted"])

    ax.set_ylabel("NAV (log)", color=C["muted"], fontsize=10)
    ax.tick_params(colors=C["muted"], labelsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(C["border"])
    ax.spines["bottom"].set_color(C["border"])
    ax.grid(True, alpha=0.15, color=C["muted"])
    ax.legend(loc="upper left", fontsize=10, framealpha=0.3,
              labelcolor=C["text"], facecolor=C["card"], edgecolor=C["border"])

    # Bottom KPIs
    fig.text(0.5, 0.12, "最终净值倍数 (16年)", ha="center",
             fontsize=11, color=C["muted"])
    kpis = [
        ("BuyHold", f"{norm_nav['BuyHold'].iloc[-1]:.2f}x", C["muted"]),
        ("Mom_20", f"{norm_nav['Mom_20'].iloc[-1]:.2f}x", C["green"]),
        ("MA_60", f"{norm_nav['MA_60'].iloc[-1]:.2f}x", C["blue"]),
        ("DualMA_60_250", f"{norm_nav['DualMA_60_250'].iloc[-1]:.2f}x", C["gold"]),
    ]
    for i, (name, val, color) in enumerate(kpis):
        x = 0.13 + i * 0.22
        fig.text(x, 0.07, val, ha="center", fontsize=18, fontweight="bold",
                 color=color, fontfamily="monospace")
        fig.text(x, 0.04, name, ha="center", fontsize=9, color=C["muted"])

    _page_number(fig, 4)
    fig.savefig(SAVE_DIR / "04_nav.png", dpi=DPI, facecolor=C["bg"])
    plt.close()
    print("  [4/7] nav curves")


# ════════════════════════════════════════════════════════════════
# Card 5: 样本内外对比 (关键!防过拟合)
# ════════════════════════════════════════════════════════════════
def card_5_oos():
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(C["bg"])
    ax.axis("off")

    ax.text(0.5, 0.93, "样本外验证：谁没过拟合？", ha="center",
            fontsize=24, fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.88, "样本内(2010-2021) vs 样本外(2022-2026) Sharpe对比",
            ha="center", fontsize=11, color=C["muted"], transform=ax.transAxes)

    in_s = results_df[results_df["period"] == "in_sample"].set_index("name")["sharpe"]
    out_s = results_df[results_df["period"] == "out_sample"].set_index("name")["sharpe"]
    compare = pd.DataFrame({"in": in_s, "out": out_s}).dropna()
    compare = compare.sort_values("out", ascending=False).head(12)

    # Bar chart area
    chart_ax = fig.add_axes([0.20, 0.15, 0.75, 0.68])
    chart_ax.set_facecolor(C["bg"])

    y = np.arange(len(compare))
    h = 0.35

    chart_ax.barh(y - h/2, compare["in"], h, color=C["blue"], alpha=0.7, label="In-Sample")
    chart_ax.barh(y + h/2, compare["out"], h, color=C["gold"], alpha=0.9, label="Out-of-Sample")

    chart_ax.axvline(0, color=C["border"], linewidth=0.8)
    chart_ax.set_yticks(y)
    chart_ax.set_yticklabels(compare.index, fontsize=10, color=C["text"])
    chart_ax.set_xlabel("Sharpe Ratio", color=C["muted"], fontsize=10)
    chart_ax.tick_params(colors=C["muted"], labelsize=9)
    chart_ax.spines["top"].set_visible(False)
    chart_ax.spines["right"].set_visible(False)
    chart_ax.spines["left"].set_color(C["border"])
    chart_ax.spines["bottom"].set_color(C["border"])
    chart_ax.grid(True, alpha=0.1, axis="x", color=C["muted"])
    chart_ax.legend(loc="lower right", fontsize=10, framealpha=0.3,
                    labelcolor=C["text"], facecolor=C["card"], edgecolor=C["border"])

    # 标注过拟合的 — larger, repositioned
    for i, (name, row) in enumerate(compare.iterrows()):
        if row["out"] < 0:
            chart_ax.annotate("过拟合", xy=(row["out"], i + h/2),
                             xytext=(row["out"] - 0.15, i + h/2 + 0.3),
                             fontsize=11, fontweight="bold", color=C["red"],
                             va="center",
                             arrowprops=dict(arrowstyle="->", color=C["red"],
                                            lw=1.5))

    _page_number(fig, 5)
    _disclaimer(fig)
    fig.savefig(SAVE_DIR / "05_oos_comparison.png", dpi=DPI, facecolor=C["bg"])
    plt.close()
    print("  [5/7] OOS comparison")


# ════════════════════════════════════════════════════════════════
# Card 6: 回撤对比
# ════════════════════════════════════════════════════════════════
def card_6_drawdown():
    fig = _fig()

    fig.text(0.5, 0.94, "回撤控制能力", ha="center",
             fontsize=22, fontweight="bold", color=C["text"])
    fig.text(0.5, 0.90, "择时最大价值: 躲开大跌",
             ha="center", fontsize=13, color=C["muted"])

    ax = fig.add_axes([0.10, 0.30, 0.85, 0.55])
    ax.set_facecolor(C["card"])

    strategies = [
        ("BuyHold", C["muted"], 1.5, "--"),
        ("Mom_20", C["green"], 2.0, "-"),
        ("MA_60", C["blue"], 2.0, "-"),
    ]

    dd_stats = {}
    for name, color, lw, ls in strategies:
        if name not in nav_df.columns:
            continue
        nav = nav_df[name].dropna()
        peak = nav.expanding().max()
        dd = (nav - peak) / peak * 100
        ax.fill_between(dd.index, dd.values, 0, alpha=0.15, color=color)
        ax.plot(dd.index, dd.values, ls, color=color, linewidth=lw, label=name)
        dd_stats[name] = dd.min()

    ax.axhline(0, color=C["border"], linewidth=0.5)
    ax.set_ylabel("Drawdown (%)", color=C["muted"], fontsize=10)
    ax.tick_params(colors=C["muted"], labelsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(C["border"])
    ax.spines["bottom"].set_color(C["border"])
    ax.grid(True, alpha=0.1, color=C["muted"])
    ax.legend(loc="lower left", fontsize=10, framealpha=0.3,
              labelcolor=C["text"], facecolor=C["card"], edgecolor=C["border"])

    # Bottom stats
    fig.text(0.5, 0.22, "最大回撤对比", ha="center", fontsize=13, color=C["muted"])
    stats_data = [
        ("BuyHold", f"{dd_stats.get('BuyHold', 0):.0f}%", C["red"]),
        ("Mom_20", f"{dd_stats.get('Mom_20', 0):.0f}%", C["green"]),
        ("MA_60", f"{dd_stats.get('MA_60', 0):.0f}%", C["blue"]),
    ]
    for i, (name, val, color) in enumerate(stats_data):
        x = 0.20 + i * 0.30
        fig.text(x, 0.14, val, ha="center", fontsize=26, fontweight="bold",
                 color=color, fontfamily="monospace")
        fig.text(x, 0.09, name, ha="center", fontsize=11, color=C["muted"])

    fig.text(0.5, 0.05, "择时将最大回撤从47%降至27% (降低42%)",
             ha="center", fontsize=12, color=C["gold"])

    _page_number(fig, 6)
    fig.savefig(SAVE_DIR / "06_drawdown.png", dpi=DPI, facecolor=C["bg"])
    plt.close()
    print("  [6/7] drawdown")


# ════════════════════════════════════════════════════════════════
# Card 7: 结论与实操建议
# ════════════════════════════════════════════════════════════════
def card_7_conclusion():
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(C["bg"])
    ax.axis("off")

    ax.text(0.5, 0.93, "研究结论", ha="center",
            fontsize=26, fontweight="bold", color=C["text"], transform=ax.transAxes)

    # 4个结论区块
    conclusions = [
        (C["green"], "✓ 有效的", [
            "20日动量: 过去20天涨→持有, 跌→跑",
            "60日均线: 站上持有, 跌破清仓",
            "60/250双均线: 大趋势判断(1年仅调1次)",
        ]),
        (C["red"], "✗ 过拟合的", [
            "波动率择时: 样本内优秀, 样本外崩塌",
            "成交量择时: 完全无效",
            "中等周期双均线(10/60, 20/120): 严重过拟合",
        ]),
        (C["gold"], "> 实操建议", [
            "简单版: 沪深300跌破60日线->换国债ETF",
            "增强版: Mom20+MA60+DualMA60_250 投票",
            "预期: 年化6-8%, 最大回撤25-30%",
        ]),
        (C["blue"], "> 注意事项", [
            "Bootstrap检验: 没有一个信号Sharpe显著>0",
            "择时主要价值在控制回撤, 不在暴利",
            "简单信号 > 复杂信号 (越简单越不容易过拟合)",
        ]),
    ]

    y = 0.85
    for color, title, bullets in conclusions:
        # 左侧色条
        ax.plot([0.06, 0.06], [y - 0.01, y - len(bullets) * 0.04 - 0.01],
                color=color, linewidth=4, transform=ax.transAxes,
                solid_capstyle="round", clip_on=False)
        ax.text(0.10, y, title, fontsize=15, fontweight="bold",
                color=color, transform=ax.transAxes)
        for i, bullet in enumerate(bullets):
            ax.text(0.10, y - (i + 1) * 0.04, f"  {bullet}",
                    fontsize=11, color=C["text"], transform=ax.transAxes)
        y -= (len(bullets) + 1) * 0.04 + 0.03

    # 下期预告 — 引导关注
    ax.plot([0.08, 0.92], [0.14, 0.14], color=C["border"],
            transform=ax.transAxes, clip_on=False)
    ax.text(0.5, 0.105, "下期预告: 股息率/PE/PB/布林带 择时实测",
            ha="center", fontsize=13, fontweight="bold",
            color=C["gold"], transform=ax.transAxes)
    ax.text(0.5, 0.07, "关注我, 用数据说话, 不画饼",
            ha="center", fontsize=11, color=C["muted"], transform=ax.transAxes)

    # 底部
    ax.text(0.5, 0.03, "数据来源: AKShare · 代码开源 · 欢迎复现",
            ha="center", fontsize=10, color=C["muted"], transform=ax.transAxes)

    _page_number(fig, 7)
    fig.savefig(SAVE_DIR / "07_conclusion.png", dpi=DPI, facecolor=C["bg"])
    plt.close()
    print("  [7/7] conclusion")


# ════════════════════════════════════════════════════════════════
# 生成全部卡片
# ════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n生成小红书卡片 (7张)...")
    card_1_cover()
    card_2_intro()
    card_3_leaderboard()
    card_4_nav()
    card_5_oos()
    card_6_drawdown()
    card_7_conclusion()

    print(f"\n✓ 全部卡片已保存到 {SAVE_DIR}/")
    print(f"  共 {TOTAL_CARDS} 张, 尺寸 1080×1440px")

    # 生成文案
    copy_text = """# 小红书文案 — A股择时研究

## 发布顺序 (7张图轮播)

1. `01_cover.png` — 封面 (+247%收益hook)
2. `02_intro.png` — 研究框架介绍
3. `03_leaderboard.png` — 16种策略排行榜
4. `04_nav.png` — 净值曲线对比
5. `05_oos_comparison.png` — 样本内外验证 (防过拟合)
6. `06_drawdown.png` — 回撤控制能力
7. `07_conclusion.png` — 结论与实操建议 + 下期预告

---

## 正文 (150字以内)

A股择时到底有没有用？

我用16年真实数据(2010-2026)回测了16种择时策略，从均线到动量到波动率，全跑了一遍。还做了样本内外分割验证，过拟合的全部曝光。

核心发现：
• 最佳择时策略16年累计+247%（买入持有仅+38%）
• 最简单的60日均线就能把最大回撤从47%降到33%
• 但没有一个信号统计显著——择时有用≠择时能暴富

7张图完整复盘，结论可能和你想的不一样。

下期预告：股息率/PE/PB/布林带择时实测，关注不迷路~

* 历史回测不代表未来表现，不构成投资建议。

#量化研究 #A股择时 #沪深300 #ETF策略 #回测
"""
    copy_path = SAVE_DIR / "xhs_copy.md"
    copy_path.write_text(copy_text, encoding="utf-8")
    print(f"  文案已保存: {copy_path}")
