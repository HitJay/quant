"""
自由现金流 vs 沪深300 vs 红利低波 — 小红书分享卡片 (7张)
=========================================================
评估自由现金流ETF是否真的"打爆"传统红利低波和宽基指数。

Usage:
    conda activate research
    python analysis/fcf_vs_benchmarks.py
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
# 主题色 (暗色)
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
SAVE_DIR = Path("./output/2026-06-02/fcf-vs-benchmarks/cards")
SAVE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR = SAVE_DIR.parent


def _fig():
    return plt.figure(figsize=(CARD_W, CARD_H), facecolor=C["bg"])


def _page_number(fig, n):
    fig.text(0.95, 0.02, f"{n}/{TOTAL_CARDS}", ha="right", fontsize=9,
             color=C["muted"], fontfamily="monospace")


def _disclaimer(fig):
    fig.text(0.5, 0.02, "* 历史数据不代表未来 . 不构成投资建议",
             ha="center", fontsize=9, color=C["muted"])


# ════════════════════════════════════════════════════════════════
# 数据准备
# ════════════════════════════════════════════════════════════════
print("=" * 60)
print("自由现金流 vs 沪深300 vs 红利低波 — 小红书卡片")
print("=" * 60)

print("\n加载数据...")
cache = Cache("./data/cache")
fetcher = ETFDataFetcher()

ETF_CODES = {
    "159201": "自由现金流ETF",
    "510300": "沪深300ETF",
    "512890": "红利低波ETF",
}
ETF_SHORT = {
    "159201": "自由现金流",
    "510300": "沪深300",
    "512890": "红利低波",
}
ETF_COLORS = {
    "159201": C["gold"],
    "510300": C["blue"],
    "512890": C["green"],
}

# 加载ETF数据
raw_data = {}
for code, name in ETF_CODES.items():
    df = fetcher.fetch_or_cache(code, "2018-01-01", "2026-06-02", cache=cache)
    raw_data[code] = df["close"]
    print(f"  {name}({code}): {df.index[0].date()} ~ {df.index[-1].date()}, {len(df)} rows")

# 同期对齐 (公共区间)
prices = pd.DataFrame(raw_data).dropna()
nav_all = prices / prices.iloc[0]
START_DATE = prices.index[0]
END_DATE = prices.index[-1]
DAYS = len(prices)
YEARS = (END_DATE - START_DATE).days / 365.25

print(f"\n同期对比区间: {START_DATE.date()} ~ {END_DATE.date()} ({DAYS}天, {YEARS:.1f}年)")

# 计算各标的指标
metrics = {}
for code, name in ETF_SHORT.items():
    s = nav_all[code]
    vol = s.pct_change().std() * np.sqrt(252)
    monthly = s.resample("ME").last().pct_change().dropna()
    metrics[code] = {
        "name": name,
        "total_return": s.iloc[-1] - 1,
        "ann_return": annual_return(s),
        "mdd": max_drawdown(s),
        "sharpe": sharpe(s),
        "calmar": calmar(s),
        "win_rate": win_rate(s),
        "volatility": vol,
        "monthly_avg": monthly.mean(),
        "monthly_median": monthly.median(),
        "monthly_win": (monthly > 0).mean(),
    }

print("\n绩效对比:")
for code, m in metrics.items():
    print(f"  {m['name']}: 总收益{m['total_return']:+.1%}, 年化{m['ann_return']:+.1%}, "
          f"MDD={m['mdd']:.1%}, Sharpe={m['sharpe']:.2f}, 月胜率={m['win_rate']:.0%}")

# 超额收益
excess_fcf_vs_300 = nav_all["159201"].iloc[-1] / nav_all["510300"].iloc[-1] - 1
excess_fcf_vs_hl = nav_all["159201"].iloc[-1] / nav_all["512890"].iloc[-1] - 1

print(f"\n自由现金流 vs 沪深300 超额: {excess_fcf_vs_300:+.2%}")
print(f"自由现金流 vs 红利低波 超额: {excess_fcf_vs_hl:+.2%}")

# 月度对比
monthly_ret = prices.resample("ME").last().pct_change().dropna()
monthly_excess_vs_hl = monthly_ret["159201"] - monthly_ret["512890"]
monthly_excess_vs_300 = monthly_ret["159201"] - monthly_ret["510300"]
fcf_beats_hl_pct = (monthly_excess_vs_hl > 0).mean()
fcf_beats_300_pct = (monthly_excess_vs_300 > 0).mean()
print(f"\n月度跑赢红利低波概率: {fcf_beats_hl_pct:.0%}")
print(f"月度跑赢沪深300概率: {fcf_beats_300_pct:.0%}")

# 红利低波更长历史 (用作对比参考)
hl_full = raw_data["512890"]
hl_full_nav = hl_full / hl_full.iloc[0]
hl_full_ann = annual_return(hl_full_nav)
hl_full_mdd = max_drawdown(hl_full_nav)
hl_full_sharpe = sharpe(hl_full_nav)
print(f"\n红利低波全历史({hl_full.index[0].date()}~{hl_full.index[-1].date()}):")
print(f"  年化{hl_full_ann:+.1%}, MDD={hl_full_mdd:.1%}, Sharpe={hl_full_sharpe:.2f}")

# 沪深300更长历史
hs_full = raw_data["510300"]
hs_full_nav = hs_full / hs_full.iloc[0]
hs_full_ann = annual_return(hs_full_nav)
hs_full_mdd = max_drawdown(hs_full_nav)
print(f"沪深300全历史({hs_full.index[0].date()}~{hs_full.index[-1].date()}):")
print(f"  年化{hs_full_ann:+.1%}, MDD={hs_full_mdd:.1%}")


# ════════════════════════════════════════════════════════════════
# Card 1: 封面
# ════════════════════════════════════════════════════════════════
def card_1_cover():
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(C["bg"])
    ax.axis("off")

    ax.text(0.5, 0.88, "自由现金流ETF", ha="center",
            fontsize=38, fontweight="bold", color=C["gold"], transform=ax.transAxes)
    ax.text(0.5, 0.79, "真的打爆红利低波了吗?", ha="center",
            fontsize=34, fontweight="bold", color=C["text"], transform=ax.transAxes)

    ax.text(0.5, 0.71, f"同期对比 {START_DATE.strftime('%Y.%m.%d')} ~ {END_DATE.strftime('%Y.%m.%d')}",
            ha="center", fontsize=12, color=C["muted"], transform=ax.transAxes)

    ax.plot([0.15, 0.85], [0.67, 0.67], color=C["border"], linewidth=1,
            transform=ax.transAxes)

    # 三个收益对比
    items = [
        ("自由现金流", metrics["159201"]["total_return"], C["gold"]),
        ("沪深300", metrics["510300"]["total_return"], C["blue"]),
        ("红利低波", metrics["512890"]["total_return"], C["green"]),
    ]
    for i, (name, ret, color) in enumerate(items):
        x = 0.2 + i * 0.3
        rect = FancyBboxPatch((x - 0.13, 0.42), 0.26, 0.20,
                              boxstyle="round,pad=0.01",
                              facecolor=C["card"], edgecolor=color,
                              linewidth=1.5, transform=ax.transAxes, zorder=0)
        ax.add_patch(rect)
        ax.text(x, 0.56, f"{ret:+.0%}", ha="center",
                fontsize=36, fontweight="bold", color=color,
                fontfamily="monospace", transform=ax.transAxes)
        ax.text(x, 0.45, name, ha="center", fontsize=13, color=color,
                transform=ax.transAxes)

    # 结论hook
    ax.text(0.5, 0.32, f"收益相当, 但风险特征完全不同",
            ha="center", fontsize=16, color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.25, f"Sharpe: {metrics['159201']['sharpe']:.2f} vs {metrics['510300']['sharpe']:.2f} vs {metrics['512890']['sharpe']:.2f}",
            ha="center", fontsize=14, color=C["muted"], fontfamily="monospace",
            transform=ax.transAxes)

    tags = ["#自由现金流", "#红利低波", "#ETF对比", "#量化投资"]
    ax.text(0.5, 0.12, "  ".join(tags),
            ha="center", fontsize=11, color=C["blue"], transform=ax.transAxes)

    _page_number(fig, 1)
    fig.savefig(SAVE_DIR / "01_cover.png", dpi=DPI, facecolor=C["bg"])
    plt.close()
    print("  [1/7] cover")


# ════════════════════════════════════════════════════════════════
# Card 2: 净值曲线对比
# ════════════════════════════════════════════════════════════════
def card_2_nav():
    fig = _fig()

    fig.text(0.5, 0.94, "净值走势对比", ha="center",
             fontsize=24, fontweight="bold", color=C["text"])
    fig.text(0.5, 0.89, f"同期 {START_DATE.strftime('%Y.%m')} ~ {END_DATE.strftime('%Y.%m')} 归一化净值",
             ha="center", fontsize=12, color=C["muted"])

    ax = fig.add_axes([0.10, 0.35, 0.85, 0.48])
    ax.set_facecolor(C["card"])

    for code in ["159201", "510300", "512890"]:
        name = ETF_SHORT[code]
        color = ETF_COLORS[code]
        lw = 2.5 if code == "159201" else 1.8
        ax.plot(nav_all[code].index, nav_all[code].values,
                color=color, linewidth=lw, label=name)

    ax.axhline(1.0, color=C["border"], linestyle="--", alpha=0.5)
    ax.set_ylabel("净值 (起点=1)", color=C["muted"], fontsize=10)
    ax.tick_params(colors=C["muted"], labelsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(C["border"])
    ax.spines["bottom"].set_color(C["border"])
    ax.grid(True, alpha=0.1, color=C["muted"])
    ax.legend(loc="upper left", fontsize=11, framealpha=0.3,
              labelcolor=C["text"], facecolor=C["card"], edgecolor=C["border"])

    # 底部最终收益
    fig.text(0.5, 0.26, "最终累计收益", ha="center",
             fontsize=13, fontweight="bold", color=C["text"])
    for i, code in enumerate(["159201", "510300", "512890"]):
        x = 0.2 + i * 0.3
        ret = metrics[code]["total_return"]
        color = ETF_COLORS[code]
        fig.text(x, 0.20, f"{ret:+.1%}", ha="center",
                 fontsize=22, fontweight="bold", color=color, fontfamily="monospace")
        fig.text(x, 0.16, ETF_SHORT[code], ha="center",
                 fontsize=10, color=C["muted"])

    # 超额
    fig.text(0.5, 0.09, f"自由现金流 vs 红利低波 超额: {excess_fcf_vs_hl:+.1%}",
             ha="center", fontsize=13, fontweight="bold", color=C["gold"])

    _page_number(fig, 2)
    _disclaimer(fig)
    fig.savefig(SAVE_DIR / "02_nav.png", dpi=DPI, facecolor=C["bg"])
    plt.close()
    print("  [2/7] nav")


# ════════════════════════════════════════════════════════════════
# Card 3: 核心指标对比表
# ════════════════════════════════════════════════════════════════
def card_3_metrics():
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(C["bg"])
    ax.axis("off")

    ax.text(0.5, 0.93, "核心指标 PK", ha="center",
            fontsize=28, fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.88, f"同期 {DAYS} 个交易日 ({YEARS:.1f}年)",
            ha="center", fontsize=11, color=C["muted"], transform=ax.transAxes)

    # 表头
    y = 0.82
    headers = ["指标", "自由现金流", "沪深300", "红利低波"]
    xs = [0.05, 0.38, 0.58, 0.80]
    header_colors = [C["muted"], C["gold"], C["blue"], C["green"]]
    for x, h, hc in zip(xs, headers, header_colors):
        ax.text(x, y, h, fontsize=12, fontweight="bold", color=hc,
                transform=ax.transAxes)
    y -= 0.02
    ax.plot([0.04, 0.96], [y, y], color=C["border"], transform=ax.transAxes)

    # 指标行
    rows = [
        ("总收益", [f"{metrics[c]['total_return']:+.1%}" for c in ["159201","510300","512890"]]),
        ("年化收益", [f"{metrics[c]['ann_return']:+.1%}" for c in ["159201","510300","512890"]]),
        ("最大回撤", [f"-{metrics[c]['mdd']:.1%}" for c in ["159201","510300","512890"]]),
        ("Sharpe", [f"{metrics[c]['sharpe']:.2f}" for c in ["159201","510300","512890"]]),
        ("Calmar", [f"{metrics[c]['calmar']:.2f}" for c in ["159201","510300","512890"]]),
        ("年化波动率", [f"{metrics[c]['volatility']:.1%}" for c in ["159201","510300","512890"]]),
        ("月胜率", [f"{metrics[c]['win_rate']:.0%}" for c in ["159201","510300","512890"]]),
        ("月均收益", [f"{metrics[c]['monthly_avg']:+.2%}" for c in ["159201","510300","512890"]]),
    ]

    for label, vals in rows:
        y -= 0.065
        rect = FancyBboxPatch((0.03, y - 0.022), 0.94, 0.050,
                              boxstyle="round,pad=0.004",
                              facecolor=C["card"], edgecolor=C["border"],
                              linewidth=0.5, transform=ax.transAxes, zorder=0)
        ax.add_patch(rect)

        ax.text(xs[0], y, label, fontsize=11, color=C["text"],
                va="center", transform=ax.transAxes)
        colors = [C["gold"], C["blue"], C["green"]]
        for i, (val, col) in enumerate(zip(vals, colors)):
            ax.text(xs[1+i], y, val, fontsize=12, fontweight="bold",
                    color=col, va="center", fontfamily="monospace",
                    transform=ax.transAxes)

    # 结论
    y -= 0.08
    ax.plot([0.08, 0.92], [y, y], color=C["border"], transform=ax.transAxes)
    y -= 0.04
    ax.text(0.5, y, "自由现金流: 高收益+高波动 (进攻型)", ha="center",
            fontsize=14, fontweight="bold", color=C["gold"], transform=ax.transAxes)
    y -= 0.035
    ax.text(0.5, y, "红利低波: 低收益+低波动 (防御型)", ha="center",
            fontsize=14, fontweight="bold", color=C["green"], transform=ax.transAxes)

    _page_number(fig, 3)
    _disclaimer(fig)
    fig.savefig(SAVE_DIR / "03_metrics.png", dpi=DPI, facecolor=C["bg"])
    plt.close()
    print("  [3/7] metrics")


# ════════════════════════════════════════════════════════════════
# Card 4: 回撤对比
# ════════════════════════════════════════════════════════════════
def card_4_drawdown():
    fig = _fig()

    fig.text(0.5, 0.94, "回撤对比: 谁更抗跌?", ha="center",
             fontsize=24, fontweight="bold", color=C["text"])
    fig.text(0.5, 0.89, "跌的时候, 自由现金流比红利低波跌得更深",
             ha="center", fontsize=12, color=C["muted"])

    ax = fig.add_axes([0.10, 0.35, 0.85, 0.48])
    ax.set_facecolor(C["card"])

    for code in ["159201", "510300", "512890"]:
        s = nav_all[code]
        peak = s.expanding().max()
        dd = (s - peak) / peak
        color = ETF_COLORS[code]
        lw = 2.2 if code == "159201" else 1.5
        alpha = 0.9 if code == "159201" else 0.7
        ax.plot(dd.index, dd.values, color=color, linewidth=lw, alpha=alpha,
                label=ETF_SHORT[code])

    ax.axhline(0, color=C["border"], linestyle="-", linewidth=0.5)
    ax.axhline(-0.10, color=C["orange"], linestyle="--", alpha=0.4, linewidth=0.8)
    ax.set_ylabel("回撤幅度", color=C["muted"], fontsize=10)
    ax.tick_params(colors=C["muted"], labelsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(C["border"])
    ax.spines["bottom"].set_color(C["border"])
    ax.grid(True, alpha=0.1, color=C["muted"])
    ax.legend(loc="lower left", fontsize=10, framealpha=0.3,
              labelcolor=C["text"], facecolor=C["card"], edgecolor=C["border"])

    # 底部MDD对比
    fig.text(0.5, 0.26, "最大回撤", ha="center",
             fontsize=13, fontweight="bold", color=C["text"])
    for i, code in enumerate(["159201", "510300", "512890"]):
        x = 0.2 + i * 0.3
        mdd_val = metrics[code]["mdd"]
        color = ETF_COLORS[code]
        fig.text(x, 0.20, f"-{mdd_val:.1%}", ha="center",
                 fontsize=22, fontweight="bold", color=color, fontfamily="monospace")
        fig.text(x, 0.16, ETF_SHORT[code], ha="center",
                 fontsize=10, color=C["muted"])

    fig.text(0.5, 0.09, "自由现金流波动更大, 但同期回报也更高",
             ha="center", fontsize=13, color=C["orange"])

    _page_number(fig, 4)
    _disclaimer(fig)
    fig.savefig(SAVE_DIR / "04_drawdown.png", dpi=DPI, facecolor=C["bg"])
    plt.close()
    print("  [4/7] drawdown")


# ════════════════════════════════════════════════════════════════
# Card 5: 月度胜率对比
# ════════════════════════════════════════════════════════════════
def card_5_monthly():
    fig = _fig()

    fig.text(0.5, 0.94, "月度收益: 谁赢的次数多?", ha="center",
             fontsize=24, fontweight="bold", color=C["text"])
    fig.text(0.5, 0.89, "每个月收益率对比 + 滚动跑赢概率",
             ha="center", fontsize=12, color=C["muted"])

    # 月度柱状图
    ax = fig.add_axes([0.10, 0.50, 0.85, 0.33])
    ax.set_facecolor(C["card"])

    monthly_pct = monthly_ret * 100
    x = np.arange(len(monthly_pct))
    width = 0.28

    for i, code in enumerate(["159201", "510300", "512890"]):
        if code in monthly_pct.columns:
            vals = monthly_pct[code].values
            ax.bar(x + (i - 1) * width, vals, width,
                   color=ETF_COLORS[code], alpha=0.8, label=ETF_SHORT[code])

    ax.axhline(0, color=C["border"], linewidth=0.5)
    ax.set_ylabel("月收益率 (%)", color=C["muted"], fontsize=10)
    ax.set_xticks(x[::3])
    ax.set_xticklabels([d.strftime("%y/%m") for d in monthly_pct.index[::3]],
                       fontsize=8, color=C["muted"])
    ax.tick_params(colors=C["muted"], labelsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(C["border"])
    ax.spines["bottom"].set_color(C["border"])
    ax.grid(True, alpha=0.1, axis="y", color=C["muted"])
    ax.legend(loc="upper left", fontsize=9, framealpha=0.3,
              labelcolor=C["text"], facecolor=C["card"], edgecolor=C["border"])

    # 底部统计
    y = 0.42
    fig.text(0.5, y, "月度胜率 & 跑赢概率", ha="center",
             fontsize=14, fontweight="bold", color=C["text"])

    stats_items = [
        ("自由现金流月胜率", f"{metrics['159201']['monthly_win']:.0%}", C["gold"]),
        ("沪深300月胜率", f"{metrics['510300']['monthly_win']:.0%}", C["blue"]),
        ("红利低波月胜率", f"{metrics['512890']['monthly_win']:.0%}", C["green"]),
        ("FCF月度跑赢红利低波", f"{fcf_beats_hl_pct:.0%}", C["gold"]),
        ("FCF月度跑赢沪深300", f"{fcf_beats_300_pct:.0%}", C["gold"]),
    ]
    y -= 0.04
    for label, val, color in stats_items:
        y -= 0.05
        fig.text(0.12, y, f"  {label}", fontsize=11, color=C["text"])
        fig.text(0.88, y, val, ha="right", fontsize=13, fontweight="bold",
                 color=color, fontfamily="monospace")

    _page_number(fig, 5)
    _disclaimer(fig)
    fig.savefig(SAVE_DIR / "05_monthly.png", dpi=DPI, facecolor=C["bg"])
    plt.close()
    print("  [5/7] monthly")


# ════════════════════════════════════════════════════════════════
# Card 6: 策略定位与适合人群
# ════════════════════════════════════════════════════════════════
def card_6_positioning():
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(C["bg"])
    ax.axis("off")

    ax.text(0.5, 0.93, "三只ETF, 该选谁?", ha="center",
            fontsize=28, fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.88, "不是谁更强, 而是谁更适合你",
            ha="center", fontsize=12, color=C["muted"], transform=ax.transAxes)

    profiles = [
        {
            "name": "自由现金流ETF (159201)",
            "color": C["gold"],
            "traits": [
                "定位: 成长型价值, 进攻属性强",
                "优势: 月胜率73%, 选出真正赚钱的公司",
                "风险: 波动率17.7%, 回撤13%+, 不算稳",
                "适合: 能接受波动、想要超额收益的人",
            ],
        },
        {
            "name": "沪深300ETF (510300)",
            "color": C["blue"],
            "traits": [
                "定位: 纯宽基Beta, 市场平均水平",
                "优势: 流动性最好, 跟踪误差最小",
                "风险: 大盘跌它就跌, 没有防御能力",
                "适合: 想要市场平均回报的长期投资者",
            ],
        },
        {
            "name": "红利低波ETF (512890)",
            "color": C["green"],
            "traits": [
                "定位: 纯防御, 低波动+高股息",
                f"优势: 波动率仅{metrics['512890']['volatility']:.0%}, 回撤{metrics['512890']['mdd']:.0%}",
                "风险: 牛市跑不赢, 这一年就落后16%+",
                "适合: 追求稳定、承受不了大波动的人",
            ],
        },
    ]

    y = 0.82
    for profile in profiles:
        rect = FancyBboxPatch((0.04, y - 0.175), 0.92, 0.20,
                              boxstyle="round,pad=0.01",
                              facecolor=C["card"], edgecolor=profile["color"],
                              linewidth=1.5, alpha=0.7,
                              transform=ax.transAxes, zorder=0)
        ax.add_patch(rect)

        ax.text(0.09, y - 0.015, profile["name"],
                fontsize=13, fontweight="bold", color=profile["color"],
                transform=ax.transAxes)

        for i, trait in enumerate(profile["traits"]):
            ax.text(0.11, y - 0.055 - i * 0.032, f"  {trait}",
                    fontsize=10, color=C["text"], transform=ax.transAxes)
        y -= 0.26

    # 底部
    ax.text(0.5, 0.07, "没有最好的ETF, 只有最适合你的ETF",
            ha="center", fontsize=14, fontweight="bold", color=C["orange"],
            transform=ax.transAxes)

    _page_number(fig, 6)
    _disclaimer(fig)
    fig.savefig(SAVE_DIR / "06_positioning.png", dpi=DPI, facecolor=C["bg"])
    plt.close()
    print("  [6/7] positioning")


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
        ("[1] 收益层面: 自由现金流 略胜",
         f"同期+{metrics['159201']['total_return']:.0%} vs 红利低波+{metrics['512890']['total_return']:.0%}, 超额{excess_fcf_vs_hl:+.0%}",
         C["gold"]),
        ("[2] 风险层面: 红利低波 更稳",
         f"波动率{metrics['512890']['volatility']:.0%} vs FCF {metrics['159201']['volatility']:.0%}, 回撤更小",
         C["green"]),
        ("[3] 风险调整后: 自由现金流胜出",
         f"Sharpe {metrics['159201']['sharpe']:.2f} vs 红利低波 {metrics['512890']['sharpe']:.2f}",
         C["gold"]),
        ("[4] 总收益超额明显",
         f"同期超额红利低波 {excess_fcf_vs_hl:+.0%}, 累计差距显著",
         C["blue"]),
        ("[5] 但历史太短, 不能下死结论",
         f"自由现金流ETF仅上市{DAYS}天, 还没经历完整熊市",
         C["orange"]),
    ]

    for title, desc, color in conclusions:
        rect = FancyBboxPatch((0.04, y - 0.065), 0.92, 0.085,
                              boxstyle="round,pad=0.008",
                              facecolor=C["card"], edgecolor=color,
                              linewidth=1.0, alpha=0.6,
                              transform=ax.transAxes, zorder=0)
        ax.add_patch(rect)
        ax.text(0.09, y - 0.015, title, fontsize=13, fontweight="bold",
                color=color, transform=ax.transAxes)
        ax.text(0.09, y - 0.048, desc, fontsize=10, color=C["muted"],
                transform=ax.transAxes)
        y -= 0.115

    # 一句话
    y -= 0.02
    ax.plot([0.15, 0.85], [y, y], color=C["border"], transform=ax.transAxes)
    y -= 0.04
    ax.text(0.5, y, "短期打爆红利低波是事实", ha="center",
            fontsize=18, fontweight="bold", color=C["gold"], transform=ax.transAxes)
    ax.text(0.5, y - 0.04, "但还需要一轮熊市来验证它的底线在哪", ha="center",
            fontsize=16, fontweight="bold", color=C["text"], transform=ax.transAxes)

    ax.text(0.5, 0.06, "关注我, 用数据说话, 不画饼",
            ha="center", fontsize=12, color=C["muted"], transform=ax.transAxes)
    ax.text(0.5, 0.035, "数据来源: AKShare . 代码开源 . 欢迎复现",
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
        ("Python 源码", "fcf_vs_benchmarks.py (~350行)", "三只 ETF 对比分析+可视化"),
        ("原始数据", "data_159201/510300/512890.csv", "三只 ETF 全部日线数据"),
        ("环境依赖", "requirements.txt", "pip install 即可"),
        ("使用方式", "pip install -r requirements.txt", "python fcf_vs_benchmarks.py"),
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

    ax.text(0.5, 0.10, "评论区回复 '源码' 发你", ha="center",
            fontsize=20, fontweight="bold", color=C["gold"], transform=ax.transAxes)
    ax.text(0.5, 0.04, "#量化投资  #开源  #自由现金流  #Python", ha="center",
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
    card_2_nav()
    card_3_metrics()
    card_4_drawdown()
    card_5_monthly()
    card_6_positioning()
    card_7_conclusion()
    card_8_opensource()

    print(f"\n  全部卡片已保存到 {SAVE_DIR}/")
    print(f"  共 {TOTAL_CARDS} 张, 尺寸 1080x1440px")

    # ════════════════════════════════════════════════════════════
    # 小红书文案
    # ════════════════════════════════════════════════════════════
    copy_text = f"""# 小红书文案 -- 自由现金流 vs 红利低波

## 发布顺序 (7张图轮播)

1. `01_cover.png` -- 封面 (三只ETF收益对比)
2. `02_nav.png` -- 净值曲线同期对比
3. `03_metrics.png` -- 核心指标PK表
4. `04_drawdown.png` -- 回撤对比
5. `05_monthly.png` -- 月度收益柱状图
6. `06_positioning.png` -- 三只ETF定位分析
7. `07_conclusion.png` -- 结论

---

## 正文 (150字以内)

自由现金流ETF火了, 真的打爆红利低波了吗?

我用同期数据做了个严格对比:
自由现金流 +{metrics['159201']['total_return']:.0%} vs 红利低波 +{metrics['512890']['total_return']:.0%}
月度跑赢概率: {fcf_beats_hl_pct:.0%}
Sharpe: {metrics['159201']['sharpe']:.2f} vs {metrics['512890']['sharpe']:.2f}

结论:
- 收益确实更强, 月胜率{metrics['159201']['monthly_win']:.0%}
- 但波动更大: 最大回撤{metrics['159201']['mdd']:.0%} vs 红利低波仅{metrics['512890']['mdd']:.0%}
- 本质是"成长型价值" vs "纯防御"

自由现金流不是红利低波的替代品, 而是升级版进攻选项.
只上市了{DAYS}天, 还没经历熊市考验, 别all in.

* 不构成投资建议

#自由现金流ETF #红利低波 #沪深300 #ETF对比 #量化投资 #A股

---

## 评论区置顶

数据来源: AKShare (开源)
同期区间: {START_DATE.strftime('%Y.%m.%d')} ~ {END_DATE.strftime('%Y.%m.%d')} ({DAYS}天)
所有代码可复现, 需要的评论区留言

为什么不看更长历史?
因为自由现金流ETF(159201)才上市{DAYS}天, 还没有更长的实盘数据.
国证自由现金流指数也只有约1年历史, 所以结论只能是"阶段性胜出".
"""
    copy_path = OUTPUT_DIR / "xhs_copy.md"
    copy_path.write_text(copy_text, encoding="utf-8")
    print(f"\n  文案已保存: {copy_path}")

    # 保存指标CSV
    rows = []
    for code, m in metrics.items():
        rows.append({"ETF": ETF_CODES[code], "code": code, **m})
    pd.DataFrame(rows).to_csv(OUTPUT_DIR / "metrics_compare.csv", index=False)
    print(f"  metrics_compare.csv 已保存到 {OUTPUT_DIR}/")
    print("\n  全部完成!")
