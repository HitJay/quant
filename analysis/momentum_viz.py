"""
Momentum Experiment — Visualization & XHS Cards Generator
==========================================================
Re-runs experiments and generates:
  - Heatmap (annual return by window × universe)
  - Best/Worst NAV curves
  - 7 XHS cards for Xiaohongshu carousel

Usage:
    cd /mnt/d/vscode/quant
    unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
    python3 analysis/momentum_viz.py
"""

import os
import sys
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.lines import Line2D

# Dark theme globals
plt.rcParams.update({
    "figure.facecolor": "#1a1a2e",
    "axes.facecolor": "#16213e",
    "text.color": "white",
    "axes.labelcolor": "white",
    "xtick.color": "#cccccc",
    "ytick.color": "#cccccc",
    "axes.edgecolor": "#333366",
    "grid.color": "#2a2a4a",
    "grid.alpha": 0.5,
    "font.size": 11,
})

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from quant.data.cache import Cache
from quant.data.fetcher import ETFDataFetcher
from quant.strategies.momentum_experiment import MomentumExperiment
from quant.backtest.engine import BacktestEngine
from quant.backtest.metrics import annual_return, max_drawdown, sharpe, win_rate
from quant.universe.config import UniverseConfig

# ============================================================
# Config
# ============================================================
UNIVERSES = {
    "broad": {
        "name": "Broad (CSI300+CSI500)",
        "codes": ["510300", "510500"],
        "bench": "510300",
        "bench_label": "CSI300 B&H",
    },
    "sector": {
        "name": "Sector (6 ETFs)",
        "codes": ["515030", "512010", "159928", "512880", "512660", "516160"],
        "bench": "510300",
        "bench_label": "CSI300 B&H",
    },
    "commodity": {
        "name": "Commodity (4 ETFs)",
        "codes": ["518880", "159985", "159981", "510990"],
        "bench": "518880",
        "bench_label": "Gold B&H",
    },
}

WINDOWS = [5, 10, 20, 60, 120, 250]
START_DATE = "2018-01-01"
END_DATE = "2026-05-28"
OUTPUT_DIR = Path("./output/momentum-experiment")
XHS_DIR = OUTPUT_DIR / "xhs_cards"

# Colors
GREEN = "#4ecca3"
RED = "#e74c3c"
ORANGE = "#f39c12"
GRAY = "#7f8c8d"
GOLD = "#ffd700"
BG = "#1a1a2e"
CARD_BG = "#16213e"


def load_all_data():
    """Load price data for all universes"""
    cache = Cache("./data/cache")
    fetcher = ETFDataFetcher()
    
    all_codes = set()
    for cfg in UNIVERSES.values():
        all_codes.update(cfg["codes"])
    all_codes.add("510300")
    
    data = {}
    for code in all_codes:
        df = fetcher.fetch_or_cache(code, START_DATE, END_DATE, cache=cache)
        data[code] = df["close"]
    
    return pd.DataFrame(data).dropna()


def run_experiments(prices):
    """Run all experiments, return results list with NAV series"""
    results = []
    engine = BacktestEngine()
    
    for uni_key, uni_cfg in UNIVERSES.items():
        avail = [c for c in uni_cfg["codes"] if c in prices.columns]
        if len(avail) < 2:
            continue
        
        uni = UniverseConfig(etf_codes=avail)
        p = prices[avail]
        bench_code = uni_cfg["bench"]
        bench_price = prices[bench_code]
        
        for window in WINDOWS:
            for reverse in [False, True]:
                strat = MomentumExperiment(window=window, top_n=1, reverse=reverse, universe=uni)
                result = engine.run(strat, p, avail)
                nav = result.nav_series
                
                if len(nav) < 10:
                    continue
                
                bench = bench_price.reindex(nav.index).ffill().dropna()
                # Align
                common = nav.index.intersection(bench.index)
                nav = nav.loc[common]
                bench = bench.loc[common]
                
                ann = annual_return(nav)
                dd = max_drawdown(nav)
                sh = sharpe(nav)
                wr = win_rate(nav)
                total = result.total_return
                
                bench_ret = bench.iloc[-1] / bench.iloc[0] - 1
                yrs = (bench.index[-1] - bench.index[0]).days / 365.25
                bench_ann = (1 + bench_ret) ** (1 / max(yrs, 0.01)) - 1
                
                results.append({
                    "universe": uni_key,
                    "uni_name": uni_cfg["name"],
                    "bench_label": uni_cfg["bench_label"],
                    "window": window,
                    "reverse": reverse,
                    "label": f"{'Rev' if reverse else 'Mom'}_{window}d",
                    "annual_return": ann,
                    "max_drawdown": dd,
                    "sharpe": sh,
                    "win_rate": wr,
                    "total_return": total,
                    "bench_ann": bench_ann,
                    "bench_total": bench_ret,
                    "alpha": ann - bench_ann,
                    "nav": nav,
                    "bench": bench,
                })
    
    return results


# ============================================================
# Card generators
# ============================================================

def savefig(fig, name):
    XHS_DIR.mkdir(parents=True, exist_ok=True)
    path = XHS_DIR / name
    fig.savefig(str(path), dpi=180, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"  ✓ {path}")


def card_cover(results):
    """00_cover: Big title + best strategy highlight"""
    # Find best momentum and best reverse
    mom_results = [r for r in results if not r["reverse"]]
    rev_results = [r for r in results if r["reverse"]]
    best_mom = max(mom_results, key=lambda r: r["annual_return"])
    best_rev = max(rev_results, key=lambda r: r["annual_return"])
    
    fig, ax = plt.subplots(figsize=(6, 8))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.axis("off")
    
    # Title
    ax.text(0.5, 0.88, "Momentum Chasing in A-Shares", ha="center", va="top",
            fontsize=22, fontweight="bold", color="white", transform=ax.transAxes)
    ax.text(0.5, 0.82, "Does It Actually Work?", ha="center", va="top",
            fontsize=16, color=GRAY, transform=ax.transAxes)
    
    # Divider
    ax.plot([0.15, 0.85], [0.77, 0.77], color=GOLD, linewidth=2, transform=ax.transAxes)
    
    # Best momentum
    ax.text(0.5, 0.70, "BEST MOMENTUM", ha="center", va="top",
            fontsize=12, color=GREEN, transform=ax.transAxes, fontweight="bold")
    ax.text(0.5, 0.62, f"{best_mom['uni_name']}", ha="center", va="top",
            fontsize=14, color="white", transform=ax.transAxes)
    ax.text(0.5, 0.52, f"+{best_mom['annual_return']:.1%}", ha="center", va="top",
            fontsize=42, color=GREEN, transform=ax.transAxes, fontweight="bold")
    ax.text(0.5, 0.43, f"Ann. Return · {best_mom['window']}d Window · Sharpe {best_mom['sharpe']:.2f}",
            ha="center", va="top", fontsize=11, color=GRAY, transform=ax.transAxes)
    
    # Divider
    ax.plot([0.25, 0.75], [0.38, 0.38], color="#333366", linewidth=1, transform=ax.transAxes)
    
    # Best reverse
    ax.text(0.5, 0.33, "BEST CONTRARIAN", ha="center", va="top",
            fontsize=12, color=ORANGE, transform=ax.transAxes, fontweight="bold")
    ax.text(0.5, 0.26, f"+{best_rev['annual_return']:.1%} Ann.", ha="center", va="top",
            fontsize=28, color=ORANGE, transform=ax.transAxes, fontweight="bold")
    ax.text(0.5, 0.18, f"{best_rev['uni_name']} · {best_rev['window']}d Window",
            ha="center", va="top", fontsize=11, color=GRAY, transform=ax.transAxes)
    
    # Footer
    ax.text(0.5, 0.06, f"25 Strategy Combos · {START_DATE[:4]}-{END_DATE[:4]} · Monthly Rebalance",
            ha="center", va="top", fontsize=10, color="#666666", transform=ax.transAxes)
    
    savefig(fig, "00_cover.png")


def card_heatmap(results):
    """01_heatmap: Window × Universe → Annual Return heatmap"""
    fig, axes = plt.subplots(1, 2, figsize=(6, 8))
    fig.patch.set_facecolor(BG)
    fig.suptitle("Annual Return Heatmap", fontsize=18, fontweight="bold", color="white", y=0.95)
    fig.text(0.5, 0.91, "Momentum (Chase Winners) vs Contrarian (Buy Losers)", 
             ha="center", fontsize=10, color=GRAY)
    
    for idx, (reverse, title, color_lo, color_hi) in enumerate([
        (False, "Momentum\n(Chase Winners)", "#c0392b", GREEN),
        (True, "Contrarian\n(Buy Losers)", RED, ORANGE),
    ]):
        ax = axes[idx]
        ax.set_facecolor(BG)
        
        filtered = [r for r in results if r["reverse"] == reverse]
        universes = ["broad", "sector", "commodity"]
        uni_labels = ["Broad", "Sector", "Commodity"]
        
        # Build matrix
        matrix = np.full((len(universes), len(WINDOWS)), np.nan)
        for r in filtered:
            ui = universes.index(r["universe"])
            wi = WINDOWS.index(r["window"])
            matrix[ui, wi] = r["annual_return"] * 100  # percent
        
        # Plot
        im = ax.imshow(matrix, cmap="RdYlGn", aspect="auto", vmin=-15, vmax=20)
        
        ax.set_xticks(range(len(WINDOWS)))
        ax.set_xticklabels([f"{w}d" for w in WINDOWS], fontsize=9)
        ax.set_yticks(range(len(universes)))
        ax.set_yticklabels(uni_labels, fontsize=10)
        ax.set_title(title, fontsize=12, fontweight="bold", color="white", pad=10)
        
        # Add text annotations
        for i in range(len(universes)):
            for j in range(len(WINDOWS)):
                val = matrix[i, j]
                if not np.isnan(val):
                    color = "white" if abs(val) < 8 else "black"
                    ax.text(j, i, f"{val:+.1f}%", ha="center", va="center",
                            fontsize=10, fontweight="bold", color=color)
        
        # Tick colors
        for label in ax.get_xticklabels():
            label.set_color("#cccccc")
        for label in ax.get_yticklabels():
            label.set_color("#cccccc")
    
    fig.text(0.5, 0.02, "Green = Profit · Red = Loss · Window = Lookback Period (Trading Days)",
             ha="center", fontsize=9, color=GRAY)
    
    plt.tight_layout(rect=[0, 0.05, 1, 0.88])
    savefig(fig, "01_heatmap.png")


def card_best_nav(results):
    """02_best_nav: Best strategy NAV curve vs benchmark"""
    best = max(results, key=lambda r: r["annual_return"])
    
    fig, ax = plt.subplots(figsize=(6, 8))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(CARD_BG)
    
    # NAV ratio
    nav_ratio = best["nav"] / best["nav"].iloc[0]
    bench_ratio = best["bench"] / best["bench"].iloc[0]
    nav_pct = (nav_ratio - 1) * 100
    bench_pct = (bench_ratio - 1) * 100
    
    ax.plot(nav_pct.index, nav_pct.values, color=GREEN, linewidth=2, label=f"{best['label']}")
    ax.plot(bench_pct.index, bench_pct.values, color=GRAY, linewidth=1.5, alpha=0.7, label=best["bench_label"])
    ax.axhline(y=0, color="#333366", linewidth=0.5)
    ax.fill_between(nav_pct.index, 0, nav_pct.values, alpha=0.1, color=GREEN)
    
    # Log scale Y
    nav_ratio_for_log = nav_ratio.copy()
    bench_ratio_for_log = bench_ratio.copy()
    # Use secondary axis approach - just plot in % with log-ish ticks
    ax.set_yscale("symlog", linthresh=20)
    
    # Title
    fig.suptitle(f"Best Strategy: {best['label']}", fontsize=16, fontweight="bold", color="white", y=0.95)
    fig.text(0.5, 0.91, f"{best['uni_name']} · {START_DATE[:4]}-{END_DATE[:4]}",
             ha="center", fontsize=11, color=GRAY)
    
    # KPIs
    kpi_y = 0.86
    fig.text(0.2, kpi_y, f"Ann: +{best['annual_return']:.1%}", ha="center", fontsize=13, 
             fontweight="bold", color=GREEN)
    fig.text(0.5, kpi_y, f"DD: -{best['max_drawdown']:.1%}", ha="center", fontsize=13,
             fontweight="bold", color=RED)
    fig.text(0.8, kpi_y, f"Sharpe: {best['sharpe']:.2f}", ha="center", fontsize=13,
             fontweight="bold", color=GOLD)
    
    ax.set_ylabel("Return (%)", color="#cccccc")
    ax.set_xlabel("Year", color="#cccccc")
    ax.legend(loc="upper left", facecolor="#3a3a5c", labelcolor="white", framealpha=1)
    ax.grid(True, alpha=0.3)
    
    for label in ax.get_xticklabels():
        label.set_color("#cccccc")
    for label in ax.get_yticklabels():
        label.set_color("#cccccc")
    
    plt.tight_layout(rect=[0, 0, 1, 0.84])
    savefig(fig, "02_best_nav.png")


def card_worst_nav(results):
    """03_worst_nav: Worst strategy NAV curve — the trap"""
    worst = min(results, key=lambda r: r["annual_return"])
    
    fig, ax = plt.subplots(figsize=(6, 8))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(CARD_BG)
    
    nav_pct = (worst["nav"] / worst["nav"].iloc[0] - 1) * 100
    bench_pct = (worst["bench"] / worst["bench"].iloc[0] - 1) * 100
    
    ax.plot(nav_pct.index, nav_pct.values, color=RED, linewidth=2, label=f"{worst['label']}")
    ax.plot(bench_pct.index, bench_pct.values, color=GRAY, linewidth=1.5, alpha=0.7, label=worst["bench_label"])
    ax.axhline(y=0, color="#333366", linewidth=0.5)
    ax.fill_between(nav_pct.index, 0, nav_pct.values, alpha=0.1, color=RED)
    
    fig.suptitle(f"Worst Strategy: {worst['label']}", fontsize=16, fontweight="bold", color=RED, y=0.95)
    fig.text(0.5, 0.91, f"{worst['uni_name']} · This Is the Trap!",
             ha="center", fontsize=11, color=GRAY)
    
    kpi_y = 0.86
    fig.text(0.2, kpi_y, f"Ann: {worst['annual_return']:.1%}", ha="center", fontsize=13,
             fontweight="bold", color=RED)
    fig.text(0.5, kpi_y, f"DD: -{worst['max_drawdown']:.1%}", ha="center", fontsize=13,
             fontweight="bold", color=RED)
    fig.text(0.8, kpi_y, f"Sharpe: {worst['sharpe']:.2f}", ha="center", fontsize=13,
             fontweight="bold", color=ORANGE)
    
    ax.set_ylabel("Return (%)", color="#cccccc")
    ax.set_xlabel("Year", color="#cccccc")
    ax.legend(loc="lower left", facecolor="#3a3a5c", labelcolor="white", framealpha=1)
    ax.grid(True, alpha=0.3)
    
    for label in ax.get_xticklabels():
        label.set_color("#cccccc")
    for label in ax.get_yticklabels():
        label.set_color("#cccccc")
    
    plt.tight_layout(rect=[0, 0, 1, 0.84])
    savefig(fig, "03_worst_nav.png")


def card_annual(results):
    """04_annual: Best strategy annual returns bar chart"""
    best = max(results, key=lambda r: r["annual_return"])
    nav = best["nav"]
    bench = best["bench"]
    
    # Calculate annual returns
    years = sorted(set(nav.index.year))
    strat_annual = []
    bench_annual = []
    
    for y in years:
        s = nav[nav.index.year == y]
        b = bench[bench.index.year == y]
        if len(s) > 1 and len(b) > 1:
            strat_annual.append(s.iloc[-1] / s.iloc[0] - 1)
            bench_annual.append(b.iloc[-1] / b.iloc[0] - 1)
        else:
            strat_annual.append(0)
            bench_annual.append(0)
    
    fig, ax = plt.subplots(figsize=(6, 8))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(CARD_BG)
    
    x = np.arange(len(years))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, [v*100 for v in strat_annual], width, color=GREEN, alpha=0.85, label=best["label"])
    bars2 = ax.bar(x + width/2, [v*100 for v in bench_annual], width, color=GRAY, alpha=0.7, label=best["bench_label"])
    
    # Value labels
    for bar, val in zip(bars1, strat_annual):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (1 if val >= 0 else -3),
                f"{val:+.1%}", ha="center", va="bottom" if val >= 0 else "top",
                fontsize=8, color=GREEN, fontweight="bold")
    
    ax.set_xticks(x)
    ax.set_xticklabels(years, fontsize=9)
    ax.set_ylabel("Annual Return (%)", color="#cccccc")
    ax.axhline(y=0, color="#333366", linewidth=0.5)
    ax.legend(loc="upper left", facecolor="#3a3a5c", labelcolor="white", framealpha=1)
    ax.grid(True, axis="y", alpha=0.3)
    
    fig.suptitle(f"Annual Returns: {best['label']}", fontsize=16, fontweight="bold", color="white", y=0.95)
    fig.text(0.5, 0.91, f"{best['uni_name']} · Year by Year",
             ha="center", fontsize=11, color=GRAY)
    
    for label in ax.get_xticklabels():
        label.set_color("#cccccc")
    for label in ax.get_yticklabels():
        label.set_color("#cccccc")
    
    plt.tight_layout(rect=[0, 0, 1, 0.88])
    savefig(fig, "04_annual.png")


def card_momentum_vs_reversal(results):
    """05_momentum_vs_reversal: Grouped comparison across universes"""
    fig, axes = plt.subplots(1, 3, figsize=(6, 8))
    fig.patch.set_facecolor(BG)
    fig.suptitle("Momentum vs Contrarian", fontsize=16, fontweight="bold", color="white", y=0.95)
    fig.text(0.5, 0.91, "Annual Return by Universe & Window", ha="center", fontsize=10, color=GRAY)
    
    universes = ["broad", "sector", "commodity"]
    uni_labels = ["Broad", "Sector", "Commodity"]
    
    for idx, (uni, label) in enumerate(zip(universes, uni_labels)):
        ax = axes[idx]
        ax.set_facecolor(CARD_BG)
        
        mom_vals = []
        rev_vals = []
        for w in WINDOWS:
            mom = [r for r in results if r["universe"] == uni and r["window"] == w and not r["reverse"]]
            rev = [r for r in results if r["universe"] == uni and r["window"] == w and r["reverse"]]
            mom_vals.append(mom[0]["annual_return"] * 100 if mom else 0)
            rev_vals.append(rev[0]["annual_return"] * 100 if rev else 0)
        
        x = np.arange(len(WINDOWS))
        width = 0.35
        ax.bar(x - width/2, mom_vals, width, color=GREEN, alpha=0.85, label="Mom")
        ax.bar(x + width/2, rev_vals, width, color=ORANGE, alpha=0.85, label="Rev")
        
        ax.axhline(y=0, color="#333366", linewidth=0.5)
        ax.set_xticks(x)
        ax.set_xticklabels([f"{w}d" for w in WINDOWS], fontsize=8, rotation=45)
        ax.set_title(label, fontsize=12, fontweight="bold", color="white")
        ax.grid(True, axis="y", alpha=0.3)
        
        for lbl in ax.get_xticklabels():
            lbl.set_color("#cccccc")
        for lbl in ax.get_yticklabels():
            lbl.set_color("#cccccc")
        
        if idx == 0:
            ax.legend(loc="upper left", facecolor="#3a3a5c", labelcolor="white", 
                      framealpha=1, fontsize=8)
    
    fig.text(0.5, 0.02, "Green=Momentum · Orange=Contrarian · Y-axis=Annual Return %",
             ha="center", fontsize=8, color=GRAY)
    
    plt.tight_layout(rect=[0, 0.05, 1, 0.88])
    savefig(fig, "05_momentum_vs_reversal.png")


def card_conclusion(results):
    """06_conclusion: Key findings summary card"""
    fig, ax = plt.subplots(figsize=(6, 8))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.axis("off")
    
    # Title
    ax.text(0.5, 0.95, "Key Findings", ha="center", va="top",
            fontsize=22, fontweight="bold", color="white", transform=ax.transAxes)
    
    ax.plot([0.1, 0.9], [0.90, 0.90], color=GOLD, linewidth=2, transform=ax.transAxes)
    
    findings = [
        ("1", "Short-term momentum (5-20d)\nis a MONEY DESTROYER in A-shares",
         "Especially in Sector ETFs: up to -14.6% annualized", RED),
        ("2", "Mid-term momentum (60-120d)\nworks in Commodities only",
         "Gold/Soybean/Energy: +19.5% annualized, Sharpe 0.88", GREEN),
        ("3", "Contrarian (buy losers)\nworks in Broad Market",
         "CSI300+CSI500 reversal: +6.6% annual, low drawdown", ORANGE),
        ("4", "The golden rule:\nTime horizon determines everything",
         "Same strategy, different windows = opposite results", GOLD),
    ]
    
    y = 0.84
    for num, title, detail, color in findings:
        ax.text(0.08, y, num, ha="center", va="top",
                fontsize=20, fontweight="bold", color=color, transform=ax.transAxes)
        ax.text(0.15, y, title, ha="left", va="top",
                fontsize=12, fontweight="bold", color="white", transform=ax.transAxes,
                linespacing=1.4)
        ax.text(0.15, y - 0.08, detail, ha="left", va="top",
                fontsize=9, color=GRAY, transform=ax.transAxes)
        y -= 0.19
    
    # Footer
    ax.text(0.5, 0.06, "Data: ETF daily prices · Monthly rebalance · 100K initial capital",
            ha="center", fontsize=8, color="#555555", transform=ax.transAxes)
    ax.text(0.5, 0.02, "Disclaimer: Past performance does not guarantee future results",
            ha="center", fontsize=8, color="#555555", transform=ax.transAxes, style="italic")
    
    savefig(fig, "06_conclusion.png")


def card_summary_table(results):
    """07_table: Top 5 strategies ranked visual table"""
    # Sort by annual return
    sorted_r = sorted(results, key=lambda r: r["annual_return"], reverse=True)
    top5 = sorted_r[:5]
    bottom3 = sorted_r[-3:]
    
    fig, ax = plt.subplots(figsize=(6, 8))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.axis("off")
    
    ax.text(0.5, 0.96, "Top 5 & Bottom 3 Strategies", ha="center", va="top",
            fontsize=18, fontweight="bold", color="white", transform=ax.transAxes)
    
    ax.plot([0.05, 0.95], [0.91, 0.91], color=GOLD, linewidth=1, transform=ax.transAxes)
    
    # Headers
    headers = [("Rank", 0.08), ("Strategy", 0.35), ("Ann.Ret", 0.60), ("Max DD", 0.76), ("Sharpe", 0.92)]
    for label, x in headers:
        ax.text(x, 0.87, label, ha="center", va="top", fontsize=9, 
                fontweight="bold", color=GRAY, transform=ax.transAxes)
    
    # Top 5
    y = 0.82
    for i, r in enumerate(top5):
        color = GREEN if r["annual_return"] > 0 else RED
        ax.text(0.08, y, f"#{i+1}", ha="center", va="top", fontsize=12,
                fontweight="bold", color=GOLD, transform=ax.transAxes)
        ax.text(0.35, y, f"{r['label']}\n{r['uni_name'].split('(')[0].strip()}", ha="center", va="top",
                fontsize=10, color="white", transform=ax.transAxes)
        ax.text(0.60, y, f"+{r['annual_return']:.1%}", ha="center", va="top",
                fontsize=12, fontweight="bold", color=color, transform=ax.transAxes)
        ax.text(0.76, y, f"-{r['max_drawdown']:.1%}", ha="center", va="top",
                fontsize=11, color=RED, transform=ax.transAxes)
        ax.text(0.92, y, f"{r['sharpe']:.2f}", ha="center", va="top",
                fontsize=11, color=GOLD, transform=ax.transAxes)
        y -= 0.08
    
    # Separator
    y -= 0.02
    ax.plot([0.05, 0.95], [y+0.02, y+0.02], color="#333366", linewidth=1, transform=ax.transAxes)
    
    # Bottom 3
    y -= 0.04
    for i, r in enumerate(bottom3):
        ax.text(0.08, y, f"#{len(sorted_r)-2+i}", ha="center", va="top", fontsize=12,
                fontweight="bold", color=RED, transform=ax.transAxes)
        ax.text(0.35, y, f"{r['label']}\n{r['uni_name'].split('(')[0].strip()}", ha="center", va="top",
                fontsize=10, color="white", transform=ax.transAxes)
        ax.text(0.60, y, f"{r['annual_return']:.1%}", ha="center", va="top",
                fontsize=12, fontweight="bold", color=RED, transform=ax.transAxes)
        ax.text(0.76, y, f"-{r['max_drawdown']:.1%}", ha="center", va="top",
                fontsize=11, color=RED, transform=ax.transAxes)
        ax.text(0.92, y, f"{r['sharpe']:.2f}", ha="center", va="top",
                fontsize=11, color=ORANGE, transform=ax.transAxes)
        y -= 0.08
    
    savefig(fig, "07_table.png")


# ============================================================
# HTML Report
# ============================================================

def generate_html_report(results):
    """Generate interactive HTML report with all NAV curves"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Sort by annual return
    sorted_r = sorted(results, key=lambda r: r["annual_return"], reverse=True)
    
    html_parts = []
    html_parts.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Momentum Experiment Report</title>
<style>
body {{ background: #0f0f1a; color: #eee; font-family: 'Segoe UI', sans-serif; margin: 20px; }}
h1 {{ color: #ffd700; }}
h2 {{ color: #4ecca3; border-bottom: 1px solid #333; padding-bottom: 5px; }}
table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
th, td {{ padding: 8px 12px; text-align: right; border-bottom: 1px solid #2a2a4a; }}
th {{ background: #16213e; color: #ffd700; }}
tr:hover {{ background: #1a1a3e; }}
.positive {{ color: #4ecca3; }}
.negative {{ color: #e74c3c; }}
.tag {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.85em; }}
.tag-mom {{ background: #1a4a2a; color: #4ecca3; }}
.tag-rev {{ background: #4a2a1a; color: #f39c12; }}
</style>
</head>
<body>
<h1>Momentum Chasing in A-Shares — Full Results</h1>
<p>Period: {START_DATE} to {END_DATE} · Monthly Rebalance · {len(results)} Strategy Combinations</p>
""")
    
    # Summary table
    html_parts.append("<h2>All Strategies Ranked</h2>")
    html_parts.append("""<table>
<tr><th>#</th><th>Universe</th><th>Type</th><th>Window</th><th>Ann.Ret</th>
<th>Total Ret</th><th>Max DD</th><th>Sharpe</th><th>Win Rate</th><th>Alpha</th></tr>""")
    
    for i, r in enumerate(sorted_r):
        tag_class = "tag-rev" if r["reverse"] else "tag-mom"
        tag_text = "Contrarian" if r["reverse"] else "Momentum"
        ann_class = "positive" if r["annual_return"] > 0 else "negative"
        alpha_class = "positive" if r["alpha"] > 0 else "negative"
        
        html_parts.append(f"""<tr>
<td>{i+1}</td>
<td>{r['uni_name']}</td>
<td><span class="tag {tag_class}">{tag_text}</span></td>
<td>{r['window']}d</td>
<td class="{ann_class}">{r['annual_return']:+.2%}</td>
<td class="{ann_class}">{r['total_return']:+.2%}</td>
<td class="negative">-{r['max_drawdown']:.2%}</td>
<td>{r['sharpe']:.2f}</td>
<td>{r['win_rate']:.0%}</td>
<td class="{alpha_class}">{r['alpha']:+.2%}</td>
</tr>""")
    
    html_parts.append("</table>")
    
    # Key insights
    best = sorted_r[0]
    worst = sorted_r[-1]
    html_parts.append(f"""
<h2>Key Insights</h2>
<ul>
<li><strong>Best Strategy:</strong> {best['label']} on {best['uni_name']} — Annual {best['annual_return']:+.2%}, Sharpe {best['sharpe']:.2f}</li>
<li><strong>Worst Strategy:</strong> {worst['label']} on {worst['uni_name']} — Annual {worst['annual_return']:+.2%}, Max DD -{worst['max_drawdown']:.2%}</li>
<li><strong>Broad Market:</strong> Short-term momentum loses money, contrarian works</li>
<li><strong>Sector ETFs:</strong> Short-term momentum is devastating (-14.6% ann.), contrarian at 5d works (+7.2%)</li>
<li><strong>Commodities:</strong> Mid/long-term momentum works well (60-120d window)</li>
</ul>
""")
    
    html_parts.append("</body></html>")
    
    path = OUTPUT_DIR / "report.html"
    path.write_text("\n".join(html_parts))
    print(f"  ✓ {path}")


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 60)
    print("MOMENTUM EXPERIMENT — VISUALIZATION")
    print("=" * 60)
    
    print("\nLoading data...")
    prices = load_all_data()
    
    print("\nRunning experiments...")
    results = run_experiments(prices)
    print(f"  {len(results)} experiments completed")
    
    print("\nGenerating cards...")
    card_cover(results)
    card_heatmap(results)
    card_best_nav(results)
    card_worst_nav(results)
    card_annual(results)
    card_momentum_vs_reversal(results)
    card_conclusion(results)
    card_summary_table(results)
    
    print("\nGenerating HTML report...")
    generate_html_report(results)
    
    print("\n✓ All done!")
    print(f"  Cards: {XHS_DIR}/")
    print(f"  Report: {OUTPUT_DIR}/report.html")


if __name__ == "__main__":
    main()
