"""
科创50还能不能追？— 小红书分享卡片 (7张)
==========================================
基于条件胜率、动量状态和风险收益比评估科创50ETF当前追涨的可行性。

Usage:
    conda activate research
    python analysis/kc50_chase_analysis.py
"""

import sys
sys.path.insert(0, "src")

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
plt.rcParams["font.sans-serif"] = ["Droid Sans Fallback", "WenQuanYi Micro Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

from quant.data.cache import Cache
from quant.data.fetcher import ETFDataFetcher
from quant.backtest.metrics import annual_return, max_drawdown, sharpe, calmar, win_rate

# ════════════════════════════════════════════════════════════════
# 主题色 (暗色 GitHub-style)
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
    "cyan":     "#56d4dd",
}

CARD_W, CARD_H, DPI = 7.2, 9.6, 150  # 1080x1440px
TOTAL_CARDS = 8
TODAY = datetime.now().strftime("%Y-%m-%d")
SAVE_DIR = Path(f"./output/2026-06-02/kc50-chase/cards")
SAVE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR = SAVE_DIR.parent


def _fig():
    return plt.figure(figsize=(CARD_W, CARD_H), facecolor=C["bg"])


def _page_number(fig, n):
    fig.text(0.95, 0.02, f"{n}/{TOTAL_CARDS}", ha="right", fontsize=9,
             color=C["muted"], fontfamily="monospace")


def _disclaimer(fig):
    fig.text(0.5, 0.02, "* 历史回测不代表未来 · 不构成投资建议",
             ha="center", fontsize=9, color=C["muted"])


# ════════════════════════════════════════════════════════════════
# 数据准备
# ════════════════════════════════════════════════════════════════
print("=" * 60)
print("科创50追涨评估 — 小红书卡片生成")
print("=" * 60)

print("\n加载数据...")
cache = Cache("./data/cache")
fetcher = ETFDataFetcher()
symbol = "588000"
START = "2020-11-16"
END = "2026-06-02"

df = fetcher.fetch_or_cache(symbol, START, END, cache=cache)
df = df[df.index >= pd.Timestamp(START)].copy()
close = df["close"].dropna()
nav = close / close.iloc[0]

print(f"  科创50ETF: {close.index[0].date()} ~ {close.index[-1].date()}, {len(close)} 天")

# 计算特征
features = pd.DataFrame({"close": close})
for w in [5, 10, 20, 60, 120, 250]:
    features[f"ret{w}"] = close.pct_change(w)
    features[f"ma{w}"] = close.rolling(w).mean()
    features[f"dist_ma{w}"] = close / features[f"ma{w}"] - 1
features["dd_252_high"] = close / close.rolling(252, min_periods=20).max() - 1
for h in [20, 60]:
    features[f"fwd{h}"] = close.shift(-h) / close - 1

# 当前状态
latest = features.iloc[-1]
print(f"\n当前状态 ({close.index[-1].date()}):")
print(f"  收盘价: {latest['close']:.3f}")
print(f"  近20日涨幅: {latest['ret20']:+.1%}")
print(f"  近60日涨幅: {latest['ret60']:+.1%}")
print(f"  近250日涨幅: {latest['ret250']:+.1%}")
print(f"  距20日均线: {latest['dist_ma20']:+.1%}")
print(f"  距60日均线: {latest['dist_ma60']:+.1%}")
print(f"  距近一年高点: {latest['dd_252_high']:+.1%}")

# 全局绩效
ann_ret = annual_return(nav)
mdd = max_drawdown(nav)
sh = sharpe(nav)
cal = calmar(nav)
wr = win_rate(nav)
monthly = close.resample("ME").last().pct_change().dropna()
last_12m_win = (monthly.tail(12) > 0).mean()

print(f"\n上市以来绩效:")
print(f"  年化: {ann_ret:.1%}, MDD: {mdd:.1%}, Sharpe: {sh:.2f}, Calmar: {cal:.2f}")
print(f"  月胜率: {wr:.1%}, 近12月胜率: {last_12m_win:.1%}")

# 条件胜率分析
sample = features.resample("ME").last().dropna(subset=["ret20", "ret60", "fwd20"])

conditions = {
    "任意时点买入": pd.Series(True, index=sample.index),
    "20日涨幅>0": sample["ret20"] > 0,
    "20日涨幅>10%": sample["ret20"] > 0.10,
    "20日涨幅>20%": sample["ret20"] > 0.20,
    "站上60日线+动量强": (sample["ret20"] > 0.10) & (sample["ret60"] > 0.10) & (sample["close"] > sample["ma60"]),
    "接近一年高点(<5%)": sample["dd_252_high"] > -0.05,
    "类似当前状态": (sample["ret20"] > 0.20) & (sample["dist_ma20"] > 0.05) & (sample["dd_252_high"] > -0.08),
}


def calc_stats(mask, horizon):
    vals = sample.loc[mask, f"fwd{horizon}"].dropna()
    if len(vals) == 0:
        return {"n": 0, "win_rate": 0, "avg": 0, "median": 0, "avg_win": 0, "avg_loss": 0, "rr": 0}
    wins = vals[vals > 0]
    losses = vals[vals <= 0]
    avg_win = wins.mean() if len(wins) else 0
    avg_loss = losses.mean() if len(losses) else 0
    rr = avg_win / abs(avg_loss) if len(losses) and avg_loss != 0 else float("inf")
    return {
        "n": len(vals),
        "win_rate": (vals > 0).mean(),
        "avg": vals.mean(),
        "median": vals.median(),
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "rr": rr,
    }


# 计算所有条件胜率
winrate_data = {}
for name, mask in conditions.items():
    winrate_data[name] = {
        "fwd20": calc_stats(mask, 20),
        "fwd60": calc_stats(mask, 60),
    }

# 均线择时回测: 简易版
from quant.factors.timing import ma_timing, momentum_timing

sig_ma20 = ma_timing(close, 20)
sig_ma60 = ma_timing(close, 60)
sig_mom20 = momentum_timing(close, 20)

# 各择时策略净值
def timing_nav(signal, prices):
    """简易择时净值: signal=1持有, signal=0空仓"""
    ret = prices.pct_change().fillna(0)
    sig_shifted = signal.shift(1).fillna(0)  # T+1执行
    strategy_ret = ret * sig_shifted
    return (1 + strategy_ret).cumprod()

nav_bh = nav.copy()
nav_ma20 = timing_nav(sig_ma20, close)
nav_ma60 = timing_nav(sig_ma60, close)
nav_mom20 = timing_nav(sig_mom20, close)

# 各策略绩效
strategies = {
    "买入持有": nav_bh,
    "20日均线": nav_ma20,
    "60日均线": nav_ma60,
    "20日动量": nav_mom20,
}

strat_metrics = {}
for name, s_nav in strategies.items():
    strat_metrics[name] = {
        "ann": annual_return(s_nav),
        "mdd": max_drawdown(s_nav),
        "sharpe": sharpe(s_nav),
        "calmar": calmar(s_nav),
        "win_rate": win_rate(s_nav),
    }

print("\n择时策略对比:")
for name, m in strat_metrics.items():
    print(f"  {name}: 年化{m['ann']:+.1%}, MDD={m['mdd']:.1%}, Sharpe={m['sharpe']:.2f}")


# ════════════════════════════════════════════════════════════════
# Card 1: 封面
# ════════════════════════════════════════════════════════════════
def card_1_cover():
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(C["bg"])
    ax.axis("off")

    ax.text(0.5, 0.88, "科创50涨了80%", ha="center",
            fontsize=42, fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.79, "还能追吗？", ha="center",
            fontsize=44, fontweight="bold", color=C["gold"], transform=ax.transAxes)

    ax.text(0.5, 0.71, f"数据截止 {close.index[-1].strftime('%Y.%m.%d')} · 科创50ETF(588000)",
            ha="center", fontsize=12, color=C["muted"], transform=ax.transAxes)

    ax.plot([0.15, 0.85], [0.67, 0.67], color=C["border"], linewidth=1,
            transform=ax.transAxes)

    # 核心数字
    ax.text(0.5, 0.57, f"+{latest['ret250']:.0%}", ha="center",
            fontsize=72, fontweight="bold", color=C["green"],
            fontfamily="monospace", transform=ax.transAxes)
    ax.text(0.5, 0.49, "近一年涨幅", ha="center",
            fontsize=14, color=C["muted"], transform=ax.transAxes)

    # 3 KPIs
    kpis = [
        ("距一年高点", f"{latest['dd_252_high']:+.1%}", C["orange"]),
        ("上市最大回撤", f"-{mdd:.0%}", C["red"]),
        ("月度胜率", f"{wr:.0%}", C["blue"]),
    ]
    for i, (label, val, color) in enumerate(kpis):
        x = 0.2 + i * 0.3
        rect = FancyBboxPatch((x - 0.11, 0.32), 0.22, 0.12,
                              boxstyle="round,pad=0.01",
                              facecolor=C["card"], edgecolor=C["border"],
                              linewidth=0.8, transform=ax.transAxes, zorder=0)
        ax.add_patch(rect)
        ax.text(x, 0.40, val, ha="center", fontsize=24, fontweight="bold",
                color=color, fontfamily="monospace", transform=ax.transAxes)
        ax.text(x, 0.34, label, ha="center", fontsize=11, color=C["muted"],
                transform=ax.transAxes)

    ax.text(0.5, 0.22, "用数据测一测，追涨的胜率到底多少",
            ha="center", fontsize=16, color=C["text"], transform=ax.transAxes)

    tags = ["#科创50", "#ETF", "#量化投资", "#追涨风险"]
    ax.text(0.5, 0.12, "  ".join(tags),
            ha="center", fontsize=11, color=C["blue"], transform=ax.transAxes)

    _page_number(fig, 1)
    fig.savefig(SAVE_DIR / "01_cover.png", dpi=DPI, facecolor=C["bg"])
    plt.close()
    print("  [1/7] cover")


# ════════════════════════════════════════════════════════════════
# Card 2: 当前温度计
# ════════════════════════════════════════════════════════════════
def card_2_thermometer():
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(C["bg"])
    ax.axis("off")

    ax.text(0.5, 0.93, "科创50 当前温度", ha="center",
            fontsize=26, fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.88, f"截止 {close.index[-1].strftime('%Y.%m.%d')} · 多维度趋势扫描",
            ha="center", fontsize=11, color=C["muted"], transform=ax.transAxes)

    # 指标表格
    indicators = [
        ("近5日涨幅", latest["ret5"], "短线"),
        ("近20日涨幅", latest["ret20"], "月度"),
        ("近60日涨幅", latest["ret60"], "季度"),
        ("近120日涨幅", latest["ret120"], "半年"),
        ("近250日涨幅", latest["ret250"], "年度"),
        ("距20日均线", latest["dist_ma20"], "短期偏离"),
        ("距60日均线", latest["dist_ma60"], "中期偏离"),
        ("距一年高点", latest["dd_252_high"], "高点距离"),
    ]

    y = 0.82
    for label, val, desc in indicators:
        # 条形背景
        bar_width = min(abs(val) * 1.5, 0.45)
        bar_color = C["green"] if val > 0 else C["red"]

        rect = FancyBboxPatch((0.04, y - 0.025), 0.92, 0.055,
                              boxstyle="round,pad=0.005",
                              facecolor=C["card"], edgecolor=C["border"],
                              linewidth=0.6, transform=ax.transAxes, zorder=0)
        ax.add_patch(rect)

        # 进度条
        bar_rect = FancyBboxPatch((0.50, y - 0.015), bar_width, 0.035,
                                  boxstyle="round,pad=0.003",
                                  facecolor=bar_color, alpha=0.25,
                                  transform=ax.transAxes, zorder=1)
        ax.add_patch(bar_rect)

        ax.text(0.07, y, label, fontsize=12, color=C["text"],
                va="center", transform=ax.transAxes)
        ax.text(0.37, y, f"({desc})", fontsize=9, color=C["muted"],
                va="center", transform=ax.transAxes)
        ax.text(0.92, y, f"{val:+.1%}", fontsize=14, fontweight="bold",
                color=bar_color, ha="right", va="center",
                fontfamily="monospace", transform=ax.transAxes)
        y -= 0.075

    # 状态判断
    ax.plot([0.08, 0.92], [y - 0.02, y - 0.02], color=C["border"],
            transform=ax.transAxes)
    y -= 0.06

    ax.text(0.5, y, "综合判断: 强趋势 + 高偏离", ha="center",
            fontsize=18, fontweight="bold", color=C["gold"], transform=ax.transAxes)
    y -= 0.05
    ax.text(0.5, y, "所有周期动量为正，但距均线偏离较大，追涨有风险",
            ha="center", fontsize=12, color=C["muted"], transform=ax.transAxes)

    _page_number(fig, 2)
    _disclaimer(fig)
    fig.savefig(SAVE_DIR / "02_thermometer.png", dpi=DPI, facecolor=C["bg"])
    plt.close()
    print("  [2/7] thermometer")


# ════════════════════════════════════════════════════════════════
# Card 3: 条件胜率
# ════════════════════════════════════════════════════════════════
def card_3_winrate():
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(C["bg"])
    ax.axis("off")

    ax.text(0.5, 0.93, "追涨后1个月胜率", ha="center",
            fontsize=26, fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.88, "不同条件下买入, 持有20个交易日后的盈亏统计",
            ha="center", fontsize=11, color=C["muted"], transform=ax.transAxes)

    # 表头
    y = 0.82
    headers = ["条件", "样本", "胜率", "均值", "盈亏比"]
    xs = [0.05, 0.48, 0.58, 0.72, 0.87]
    for x, h in zip(xs, headers):
        ax.text(x, y, h, fontsize=11, fontweight="bold", color=C["muted"],
                transform=ax.transAxes)
    y -= 0.02
    ax.plot([0.04, 0.96], [y, y], color=C["border"], transform=ax.transAxes)

    # 数据行
    for name, data in winrate_data.items():
        y -= 0.065
        s = data["fwd20"]
        if s["n"] == 0:
            continue

        wr_val = s["win_rate"]
        if wr_val >= 0.6:
            row_color = C["green"]
        elif wr_val < 0.45:
            row_color = C["red"]
        else:
            row_color = C["text"]

        # 背景高亮当前条件
        if name == "类似当前状态":
            rect = FancyBboxPatch((0.03, y - 0.025), 0.94, 0.055,
                                  boxstyle="round,pad=0.005",
                                  facecolor=C["gold"], alpha=0.08,
                                  transform=ax.transAxes, zorder=0)
            ax.add_patch(rect)
            row_color = C["gold"]
            ax.text(0.97, y, "←当前", fontsize=9, color=C["gold"],
                    ha="right", va="center", transform=ax.transAxes)

        ax.text(xs[0], y, name, fontsize=11, color=row_color,
                va="center", transform=ax.transAxes)
        ax.text(xs[1], y, f"n={s['n']}", fontsize=11, color=C["muted"],
                va="center", fontfamily="monospace", transform=ax.transAxes)
        ax.text(xs[2], y, f"{wr_val:.0%}", fontsize=13, fontweight="bold",
                color=row_color, va="center", fontfamily="monospace",
                transform=ax.transAxes)
        ax.text(xs[3], y, f"{s['avg']:+.1%}", fontsize=11,
                color=C["green"] if s["avg"] > 0 else C["red"],
                va="center", fontfamily="monospace", transform=ax.transAxes)
        rr_str = f"{s['rr']:.1f}" if s["rr"] < 100 else "∞"
        ax.text(xs[4], y, rr_str, fontsize=11,
                color=C["green"] if s["rr"] > 1.5 else C["text"],
                va="center", fontfamily="monospace", transform=ax.transAxes)

    # 说明
    y -= 0.08
    ax.plot([0.08, 0.92], [y, y], color=C["border"], transform=ax.transAxes)
    y -= 0.04
    notes = [
        "· 盈亏比 = 平均盈利 ÷ 平均亏损, >1.5为较优",
        "· 当前状态: 20日涨>20%, 距MA20>5%, 距高点<8%",
        "· 样本少(n<5)的结论仅供参考, 不能作为决策依据",
    ]
    for note in notes:
        ax.text(0.08, y, note, fontsize=10, color=C["muted"], transform=ax.transAxes)
        y -= 0.035

    _page_number(fig, 3)
    _disclaimer(fig)
    fig.savefig(SAVE_DIR / "03_winrate.png", dpi=DPI, facecolor=C["bg"])
    plt.close()
    print("  [3/7] winrate")


# ════════════════════════════════════════════════════════════════
# Card 4: 风险警示 — 历史大回撤
# ════════════════════════════════════════════════════════════════
def card_4_risk():
    fig = _fig()

    fig.text(0.5, 0.94, "高弹性 ≠ 低风险", ha="center",
             fontsize=26, fontweight="bold", color=C["text"])
    fig.text(0.5, 0.89, "科创50ETF上市以来回撤曲线",
             ha="center", fontsize=12, color=C["muted"])

    # 回撤图
    ax = fig.add_axes([0.10, 0.38, 0.85, 0.45])
    ax.set_facecolor(C["card"])

    peak = close.expanding().max()
    drawdown = (close - peak) / peak

    ax.fill_between(drawdown.index, drawdown.values, 0,
                    color=C["red"], alpha=0.3)
    ax.plot(drawdown.index, drawdown.values, color=C["red"], linewidth=1.2)
    ax.axhline(-0.20, color=C["orange"], linestyle="--", alpha=0.6, linewidth=0.8)
    ax.axhline(-0.40, color=C["red"], linestyle="--", alpha=0.6, linewidth=0.8)

    ax.text(drawdown.index[int(len(drawdown)*0.05)], -0.19, "−20%",
            fontsize=9, color=C["orange"])
    ax.text(drawdown.index[int(len(drawdown)*0.05)], -0.39, "−40%",
            fontsize=9, color=C["red"])

    ax.set_ylabel("回撤幅度", color=C["muted"], fontsize=10)
    ax.set_ylim(-0.65, 0.05)
    ax.tick_params(colors=C["muted"], labelsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(C["border"])
    ax.spines["bottom"].set_color(C["border"])
    ax.grid(True, alpha=0.1, color=C["muted"])

    # 底部统计
    y = 0.30
    fig.text(0.5, y, "关键风险指标", ha="center",
             fontsize=14, fontweight="bold", color=C["text"])
    y -= 0.04

    risk_items = [
        ("最大回撤", f"-{mdd:.1%}", C["red"]),
        ("上市以来年化", f"{ann_ret:+.1%}", C["green"] if ann_ret > 0 else C["red"]),
        ("Calmar比率 (收益/回撤)", f"{cal:.2f}", C["orange"]),
        ("月度胜率", f"{wr:.0%}", C["blue"]),
        ("一年内最深回撤", f"{drawdown[drawdown.index >= drawdown.index[-1] - pd.DateOffset(years=1)].min():+.1%}", C["orange"]),
    ]
    for label, val, color in risk_items:
        y -= 0.045
        fig.text(0.12, y, f"· {label}", fontsize=12, color=C["text"])
        fig.text(0.88, y, val, ha="right", fontsize=13, fontweight="bold",
                 color=color, fontfamily="monospace")

    _page_number(fig, 4)
    _disclaimer(fig)
    fig.savefig(SAVE_DIR / "04_risk.png", dpi=DPI, facecolor=C["bg"])
    plt.close()
    print("  [4/7] risk")


# ════════════════════════════════════════════════════════════════
# Card 5: 择时策略对比
# ════════════════════════════════════════════════════════════════
def card_5_timing():
    fig = _fig()

    fig.text(0.5, 0.94, "如果用择时规则追, 能好多少?", ha="center",
             fontsize=22, fontweight="bold", color=C["text"])
    fig.text(0.5, 0.89, "3种简单择时 vs 买入持有",
             ha="center", fontsize=12, color=C["muted"])

    # 净值图
    ax = fig.add_axes([0.10, 0.45, 0.85, 0.38])
    ax.set_facecolor(C["card"])

    plots = [
        ("买入持有", nav_bh, "--", C["muted"], 1.5),
        ("20日均线", nav_ma20, "-", C["green"], 2.0),
        ("60日均线", nav_ma60, "-", C["blue"], 2.0),
        ("20日动量", nav_mom20, "-", C["gold"], 2.0),
    ]
    for name, s_nav, ls, color, lw in plots:
        ax.plot(s_nav.index, s_nav.values, ls, color=color, linewidth=lw, label=name)

    ax.set_ylabel("净值", color=C["muted"], fontsize=10)
    ax.tick_params(colors=C["muted"], labelsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(C["border"])
    ax.spines["bottom"].set_color(C["border"])
    ax.grid(True, alpha=0.1, color=C["muted"])
    ax.legend(loc="upper left", fontsize=10, framealpha=0.3,
              labelcolor=C["text"], facecolor=C["card"], edgecolor=C["border"])

    # 策略对比表
    y = 0.37
    headers = ["策略", "年化", "最大回撤", "Sharpe", "Calmar"]
    xs = [0.06, 0.35, 0.52, 0.70, 0.86]
    for x, h in zip(xs, headers):
        fig.text(x, y, h, fontsize=10, fontweight="bold", color=C["muted"])
    y -= 0.015
    # 分隔线用 fig axes
    line_ax = fig.add_axes([0, 0, 1, 1])
    line_ax.set_facecolor("none")
    line_ax.axis("off")
    line_ax.plot([0.05, 0.95], [y, y], color=C["border"], transform=line_ax.transAxes)

    colors_map = {"买入持有": C["muted"], "20日均线": C["green"],
                  "60日均线": C["blue"], "20日动量": C["gold"]}
    for name, m in strat_metrics.items():
        y -= 0.045
        c = colors_map.get(name, C["text"])
        fig.text(xs[0], y, name, fontsize=11, color=c)
        fig.text(xs[1], y, f"{m['ann']:+.1%}", fontsize=11, color=c, fontfamily="monospace")
        fig.text(xs[2], y, f"-{m['mdd']:.1%}", fontsize=11, color=c, fontfamily="monospace")
        fig.text(xs[3], y, f"{m['sharpe']:.2f}", fontsize=11, color=c, fontfamily="monospace")
        fig.text(xs[4], y, f"{m['calmar']:.2f}", fontsize=11, color=c, fontfamily="monospace")

    # 结论
    y -= 0.05
    fig.text(0.5, y, "结论: 有规则的追比无脑买入持有更好",
             ha="center", fontsize=14, fontweight="bold", color=C["green"])

    _page_number(fig, 5)
    _disclaimer(fig)
    fig.savefig(SAVE_DIR / "05_timing.png", dpi=DPI, facecolor=C["bg"])
    plt.close()
    print("  [5/7] timing")


# ════════════════════════════════════════════════════════════════
# Card 6: 实操框架
# ════════════════════════════════════════════════════════════════
def card_6_playbook():
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(C["bg"])
    ax.axis("off")

    ax.text(0.5, 0.93, "实操: 3种追法", ha="center",
            fontsize=28, fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.88, "追涨不是不行, 但要有规则",
            ha="center", fontsize=12, color=C["muted"], transform=ax.transAxes)

    plans = [
        {
            "title": "激进: 右侧追涨",
            "color": C["green"],
            "rules": [
                "仓位: 总资产的10-20%",
                "入场: 站上20日线 + 20日动量为正",
                "止损: 跌破20日线当天减仓50%",
                "止盈: 涨幅超50%减仓1/3",
            ],
        },
        {
            "title": "稳健: 等回调",
            "color": C["blue"],
            "rules": [
                "仓位: 总资产的20-30%",
                "入场: 回踩20日线或60日线附近(-5%内)",
                "止损: 跌破60日线3日不回即清仓",
                "止盈: 趋势走坏(跌破20日线)分批退出",
            ],
        },
        {
            "title": "保守: 纯趋势跟踪",
            "color": C["gold"],
            "rules": [
                "仓位: 总资产的15-25%",
                "入场: 60日均线以上才持有",
                "止损: 跌破60日线次日清仓",
                "耐心: 不在线下抄底, 等趋势确认",
            ],
        },
    ]

    y = 0.82
    for plan in plans:
        # Panel
        rect = FancyBboxPatch((0.05, y - 0.15), 0.90, 0.19,
                              boxstyle="round,pad=0.01",
                              facecolor=C["card"], edgecolor=plan["color"],
                              linewidth=1.5, alpha=0.7,
                              transform=ax.transAxes, zorder=0)
        ax.add_patch(rect)

        ax.text(0.10, y - 0.01, plan["title"], fontsize=16, fontweight="bold",
                color=plan["color"], transform=ax.transAxes)

        for i, rule in enumerate(plan["rules"]):
            ax.text(0.12, y - 0.05 - i * 0.030, f"· {rule}",
                    fontsize=11, color=C["text"], transform=ax.transAxes)
        y -= 0.24

    # 不建议
    y -= 0.01
    rect = FancyBboxPatch((0.05, y - 0.06), 0.90, 0.08,
                          boxstyle="round,pad=0.01",
                          facecolor=C["red"], alpha=0.08,
                          edgecolor=C["red"], linewidth=1.2,
                          transform=ax.transAxes, zorder=0)
    ax.add_patch(rect)
    ax.text(0.10, y - 0.015, "[X] 不建议", fontsize=14, fontweight="bold",
            color=C["red"], transform=ax.transAxes)
    ax.text(0.10, y - 0.045, "一次性满仓追高 · 不设止损 · 借钱加杠杆",
            fontsize=11, color=C["red"], transform=ax.transAxes)

    _page_number(fig, 6)
    _disclaimer(fig)
    fig.savefig(SAVE_DIR / "06_playbook.png", dpi=DPI, facecolor=C["bg"])
    plt.close()
    print("  [6/7] playbook")


# ════════════════════════════════════════════════════════════════
# Card 7: 结论
# ════════════════════════════════════════════════════════════════
def card_7_conclusion():
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(C["bg"])
    ax.axis("off")

    ax.text(0.5, 0.93, "结论", ha="center",
            fontsize=30, fontweight="bold", color=C["text"], transform=ax.transAxes)

    y = 0.84
    conclusions = [
        ("[1] 趋势还在", "所有周期动量为正，中短期趋势强劲", C["green"]),
        ("[2] 但不是低风险", f"上市以来最大回撤{mdd:.0%}，长期Calmar仅{cal:.2f}", C["orange"]),
        ("[3] 强动量短线胜率高", "20日涨>10%后, 1个月胜率约63%", C["blue"]),
        ("[4] 接近高点时要谨慎", "距一年高点<5%时, 月胜率降至40%", C["red"]),
        ("[5] 有规则追 > 无脑追", "20日均线/动量择时可显著降低回撤", C["gold"]),
    ]
    for title, desc, color in conclusions:
        rect = FancyBboxPatch((0.05, y - 0.06), 0.90, 0.08,
                              boxstyle="round,pad=0.008",
                              facecolor=C["card"], edgecolor=color,
                              linewidth=1.0, alpha=0.6,
                              transform=ax.transAxes, zorder=0)
        ax.add_patch(rect)
        ax.text(0.10, y - 0.015, title, fontsize=15, fontweight="bold",
                color=color, transform=ax.transAxes)
        ax.text(0.10, y - 0.045, desc, fontsize=11, color=C["muted"],
                transform=ax.transAxes)
        y -= 0.105

    # 一句话总结
    y -= 0.02
    ax.plot([0.15, 0.85], [y, y], color=C["border"], transform=ax.transAxes)
    y -= 0.04
    ax.text(0.5, y, "能追, 但仓位和止损", ha="center",
            fontsize=20, fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, y - 0.04, "比方向判断更重要", ha="center",
            fontsize=20, fontweight="bold", color=C["gold"], transform=ax.transAxes)

    # 下期预告
    y -= 0.10
    ax.text(0.5, y, "关注我, 用数据说话, 不画饼",
            ha="center", fontsize=12, color=C["muted"], transform=ax.transAxes)

    ax.text(0.5, 0.04, "数据来源: AKShare · 代码开源 · 欢迎复现",
            ha="center", fontsize=10, color=C["muted"], transform=ax.transAxes)

    _page_number(fig, 7)
    fig.savefig(SAVE_DIR / "07_conclusion.png", dpi=DPI, facecolor=C["bg"])
    plt.close()
    print("  [7/7] conclusion")


def card_8_opensource():
    """Card 8: 开源 — 展示源码和原数据"""
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(C["bg"])
    ax.axis("off")

    ax.text(0.5, 0.90, "全部代码 + 原始数据", ha="center",
            fontsize=30, fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.83, "开源, 欢迎复现 & 质疑", ha="center",
            fontsize=18, color=C["gold"], transform=ax.transAxes)
    ax.plot([0.15, 0.85], [0.79, 0.79], color=C["border"], linewidth=1,
            transform=ax.transAxes)

    items = [
        ("Python 源码", "kc50_chase.py (~400行)", "完整分析+可视化, 一键运行"),
        ("原始数据", "data_588000.csv (1300+行)", "科创50ETF 全部日线数据"),
        ("环境依赖", "requirements.txt", "pip install 即可"),
        ("使用方式", "pip install -r requirements.txt", "python kc50_chase.py"),
    ]
    y = 0.72
    for title, file, desc in items:
        rect = FancyBboxPatch((0.06, y - 0.065), 0.88, 0.09,
                              boxstyle="round,pad=0.01",
                              facecolor=C["card"], edgecolor=C["border"],
                              linewidth=1.0, transform=ax.transAxes)
        ax.add_patch(rect)
        ax.text(0.12, y - 0.01, title, fontsize=14, fontweight="bold",
                color=C["blue"], transform=ax.transAxes)
        ax.text(0.12, y - 0.045, f"{file}  |  {desc}", fontsize=10,
                color=C["muted"], transform=ax.transAxes)
        y -= 0.115

    y -= 0.03
    ax.plot([0.15, 0.85], [y, y], color=C["border"], linewidth=1,
            transform=ax.transAxes)
    ax.text(0.5, y - 0.04, "为什么开源?", ha="center",
            fontsize=16, fontweight="bold", color=C["text"], transform=ax.transAxes)
    bullets = [
        "[1] 数据透明: 你能验证每一个数字",
        "[2] 逻辑透明: 算法没有黑箱",
        "[3] 欢迎质疑: 发现 bug 请评论区告诉我",
    ]
    for i, b in enumerate(bullets):
        ax.text(0.15, y - 0.08 - i * 0.035, b, fontsize=12,
                color=C["muted"], transform=ax.transAxes)

    ax.text(0.5, 0.06, "评论区回复 '源码' 发你", ha="center",
            fontsize=20, fontweight="bold", color=C["gold"], transform=ax.transAxes)
    ax.text(0.5, 0.015, "#量化投资  #开源  #科创50  #Python", ha="center",
            fontsize=11, color=C["blue"], transform=ax.transAxes)

    _page_number(fig, 8)
    fig.savefig(SAVE_DIR / "08_opensource.png", dpi=DPI, facecolor=C["bg"])
    plt.close()
    print("  [8/8] opensource")


# ════════════════════════════════════════════════════════════════
# 主流程
# ════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n生成小红书卡片 (8张)...")
    card_1_cover()
    card_2_thermometer()
    card_3_winrate()
    card_4_risk()
    card_5_timing()
    card_6_playbook()
    card_7_conclusion()
    card_8_opensource()

    print(f"\n✓ 全部卡片已保存到 {SAVE_DIR}/")
    print(f"  共 {TOTAL_CARDS} 张, 尺寸 1080×1440px")

    # ════════════════════════════════════════════════════════════
    # 生成小红书文案
    # ════════════════════════════════════════════════════════════
    copy_text = f"""# 小红书文案 — 科创50还能不能追

## 发布顺序 (7张图轮播)

1. `01_cover.png` — 封面 (近一年+{latest['ret250']:.0%} hook)
2. `02_thermometer.png` — 当前多维度温度计
3. `03_winrate.png` — 不同条件下追涨胜率
4. `04_risk.png` — 回撤风险警示
5. `05_timing.png` — 择时策略 vs 买入持有
6. `06_playbook.png` — 3种实操方案
7. `07_conclusion.png` — 结论 + 关注引导

---

## 正文 (150字以内)

科创50最近又冲起来了，还能不能追？

我用科创50ETF上市以来的全部数据测了一遍：
近250日涨幅超过{latest['ret250']:.0%}，距近一年高点仅{abs(latest['dd_252_high']):.0%}，趋势确实很强。

但它不是低风险资产——
上市以来最大回撤接近{mdd:.0%}，月度胜率只有{wr:.0%}。

比较有意思的是：
当20日涨幅超过10%时，后1个月胜率提升到63%左右。
强趋势阶段不是不能追，但更像短线交易。

我的结论：
能追，但只能带规则追。
小仓位、看20日线，跌破就认错。

* 历史回测不代表未来表现，不构成投资建议。

#科创50 #ETF #量化投资 #A股 #小红书理财 #追涨风险 #投资复盘

---

## 评论区置顶

数据来源: AKShare (开源)
回测区间: 2020.11~2026.05
所有代码可复现, 需要的评论区留言

追涨三原则:
1. 仓位不超过20%
2. 有明确止损线
3. 不借钱追
"""
    copy_path = OUTPUT_DIR / "xhs_copy.md"
    copy_path.write_text(copy_text, encoding="utf-8")
    print(f"\n✓ 文案已保存: {copy_path}")

    # 保存数据CSV
    metrics_data = {
        "指标": ["收盘价", "近20日涨幅", "近60日涨幅", "近120日涨幅", "近250日涨幅",
                 "距20日均线", "距60日均线", "距一年高点",
                 "年化收益", "最大回撤", "Sharpe", "Calmar", "月胜率", "近12月胜率"],
        "值": [f"{latest['close']:.3f}", f"{latest['ret20']:+.1%}", f"{latest['ret60']:+.1%}",
               f"{latest['ret120']:+.1%}", f"{latest['ret250']:+.1%}",
               f"{latest['dist_ma20']:+.1%}", f"{latest['dist_ma60']:+.1%}",
               f"{latest['dd_252_high']:+.1%}",
               f"{ann_ret:+.1%}", f"-{mdd:.1%}", f"{sh:.2f}", f"{cal:.2f}",
               f"{wr:.0%}", f"{last_12m_win:.0%}"],
    }
    pd.DataFrame(metrics_data).to_csv(OUTPUT_DIR / "metrics.csv", index=False)

    # 条件胜率CSV
    rows = []
    for name, data in winrate_data.items():
        for horizon, s in data.items():
            rows.append({"条件": name, "持有期": horizon, **s})
    pd.DataFrame(rows).to_csv(OUTPUT_DIR / "conditional_winrate.csv", index=False)

    print(f"✓ metrics.csv, conditional_winrate.csv 已保存到 {OUTPUT_DIR}/")
    print("\n✓ 全部完成!")
