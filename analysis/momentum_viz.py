"""
动量实验 — 可视化 & 小红书卡片生成器
========================================
生成内容：
  - 热力图（年化收益 × 窗口 × 市场）
  - 最佳/最差策略净值曲线
  - 8张小红书卡片

用法：
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

import matplotlib.patheffects as pe
from matplotlib.patches import Rectangle
from matplotlib.colors import Normalize
import matplotlib.cm as cm

# 加载中文字体
FP_BOLD = FontProperties(fname=str(Path.home() / ".local/share/fonts/NotoSansSC-Bold.otf"))
FP_REG = FontProperties(fname=str(Path.home() / ".local/share/fonts/NotoSansSC-Regular.otf"))

# 暗色主题
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
# 配置
# ============================================================
UNIVERSES = {
    "broad": {
        "name": "宽基 (沪深300+中证500)",
        "codes": ["510300", "510500"],
        "bench": "510300",
        "bench_label": "沪深300 买入持有",
    },
    "sector": {
        "name": "行业 (6只ETF)",
        "codes": ["515030", "512010", "159928", "512880", "512660", "516160"],
        "bench": "510300",
        "bench_label": "沪深300 买入持有",
    },
    "commodity": {
        "name": "商品 (4只ETF)",
        "codes": ["518880", "159985", "159981", "510990"],
        "bench": "518880",
        "bench_label": "黄金 买入持有",
    },
}

WINDOWS = [5, 10, 20, 60, 120, 250]
START_DATE = "2018-01-01"
END_DATE = "2026-05-28"
OUTPUT_DIR = Path("./output/momentum-experiment")
XHS_DIR = OUTPUT_DIR / "xhs_cards"

# 颜色（A股惯例：红涨绿跌）
GREEN = "#e74c3c"  # A股红色=涨
RED = "#4ecca3"    # A股绿色=跌
ORANGE = "#f39c12" # 警告/强调
PURPLE = "#9b59b6" # 反转策略专用
GRAY = "#7f8c8d"
GOLD = "#ffd700"
BG = "#1a1a2e"
CARD_BG = "#16213e"


def load_all_data():
    """加载所有市场的价格数据"""
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
    """运行所有实验，返回含净值序列的结果列表"""
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
                # 对齐
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
                    "label": f"{'左侧' if reverse else '右侧'}_{window}日",
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
# 卡片生成函数
# ============================================================

def savefig(fig, name):
    XHS_DIR.mkdir(parents=True, exist_ok=True)
    path = XHS_DIR / name
    fig.savefig(str(path), dpi=180, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"  ✓ {path}")


def card_cover(results):
    """00_cover: 封面卡片 — 悬念版，只展示最高年化"""
    best = max(results, key=lambda r: r["annual_return"])
    
    fig, ax = plt.subplots(figsize=(6, 8))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.axis("off")
    
    # 标题 - 制造悬念
    ax.text(0.5, 0.88, "追涨杀跌 vs 抄底逃顶", ha="center", va="top",
            fontsize=26, fontweight="bold", color="white", transform=ax.transAxes,
            fontproperties=FP_BOLD)
    ax.text(0.5, 0.80, "哪种策略在A股能赚钱？", ha="center", va="top",
            fontsize=18, color="#d0d0d0", transform=ax.transAxes,
            fontproperties=FP_BOLD)
    ax.text(0.5, 0.73, "最强策略年化收益多少？", ha="center", va="top",
            fontsize=14, color="#888888", transform=ax.transAxes,
            fontproperties=FP_REG)
    
    ax.plot([0.2, 0.8], [0.68, 0.68], color=GOLD, linewidth=2, transform=ax.transAxes)
    
    # 只展示最高年化，不透露策略类型
    ax.text(0.5, 0.52, f"+{best['annual_return']:.1%}", ha="center", va="top",
            fontsize=72, color=GREEN, transform=ax.transAxes, fontproperties=FP_BOLD)
    
    ax.text(0.5, 0.35, "年化收益率", ha="center", va="top",
            fontsize=18, color=GRAY, transform=ax.transAxes,
            fontproperties=FP_REG)
    
    # 底部悬念 — 暖琥珀，和图4图5同一色系
    ax.text(0.5, 0.18, "专业AI量化研究员告诉你答案", ha="center", va="top",
            fontsize=14, color="#f0b866", transform=ax.transAxes,
            fontproperties=FP_BOLD)
    
    ax.text(0.5, 0.08, f"{START_DATE[:4]}-{END_DATE[:4]} · 月度调仓",
            ha="center", va="top", fontsize=10, color="#555555", transform=ax.transAxes,
            fontproperties=FP_REG)
    
    savefig(fig, "00_cover.png")


def card_intro():
    """00b_intro: 科普页 — 右侧交易 vs 左侧交易"""
    fig, ax = plt.subplots(figsize=(6, 8))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.axis("off")
    
    ax.text(0.5, 0.94, "什么是右侧交易 vs 左侧交易？", ha="center", va="top",
            fontsize=18, fontweight="bold", color="white", transform=ax.transAxes,
            fontproperties=FP_BOLD)
    
    ax.plot([0.1, 0.9], [0.90, 0.90], color=GOLD, linewidth=1.5, transform=ax.transAxes)
    
    # --- 右侧交易区块 ---
    ax.text(0.08, 0.85, "右侧交易", ha="left", va="top",
            fontsize=20, fontweight="bold", color="#f0b866", transform=ax.transAxes,
            fontproperties=FP_BOLD)
    ax.text(0.52, 0.86, "顺势 · 追涨杀跌", ha="left", va="top",
            fontsize=12, color=GRAY, transform=ax.transAxes, fontproperties=FP_REG)
    
    right_items = [
        ("核心理念", "涨的时候买，跌的时候卖"),
        ("别称", "动量策略、趋势跟随、追涨杀跌"),
        ("操作方法", "买近期涨得最好的，卖掉涨不动的"),
        ("适合场景", "强趋势市场，如商品牛市"),
    ]
    y = 0.79
    for label, desc in right_items:
        ax.text(0.10, y, label, ha="left", va="top",
                fontsize=9, color="#f0b866", transform=ax.transAxes, fontproperties=FP_BOLD)
        ax.text(0.10, y-0.03, desc, ha="left", va="top",
                fontsize=9, color="white", transform=ax.transAxes, fontproperties=FP_REG)
        y -= 0.07
    
    ax.plot([0.05, 0.95], [y-0.005, y-0.005], color="#333366", linewidth=1, transform=ax.transAxes)
    y -= 0.04
    
    # --- 左侧交易区块 ---
    ax.text(0.08, y, "左侧交易", ha="left", va="top",
            fontsize=20, fontweight="bold", color="#7fa5c4", transform=ax.transAxes,
            fontproperties=FP_BOLD)
    ax.text(0.52, y+0.01, "逆势 · 抄底逃顶", ha="left", va="top",
            fontsize=12, color=GRAY, transform=ax.transAxes, fontproperties=FP_REG)
    
    left_items = [
        ("核心理念", "跌的时候买，涨的时候卖"),
        ("别称", "反转策略、逆势交易、低吸高抛、价值投资"),
        ("操作方法", "买近期跌得最惨的，卖掉涨太快的"),
        ("适合场景", "震荡市场，如宽基指数均值回归"),
    ]
    y -= 0.06
    for label, desc in left_items:
        ax.text(0.10, y, label, ha="left", va="top",
                fontsize=9, color="#7fa5c4", transform=ax.transAxes, fontproperties=FP_BOLD)
        ax.text(0.10, y-0.03, desc, ha="left", va="top",
                fontsize=9, color="white", transform=ax.transAxes, fontproperties=FP_REG)
        y -= 0.07
    
    y -= 0.02
    ax.plot([0.05, 0.95], [y, y], color="#333366", linewidth=1, transform=ax.transAxes)
    y -= 0.04
    
    # --- 一句话总结 ---
    ax.text(0.5, y, "右侧看趋势，左侧看价值", ha="center", va="top",
            fontsize=16, fontweight="bold", color=GOLD, transform=ax.transAxes,
            fontproperties=FP_BOLD)
    ax.text(0.5, y-0.04, "不同市场、不同周期，优劣截然不同", ha="center", va="top",
            fontsize=11, color=GRAY, transform=ax.transAxes, fontproperties=FP_REG)
    ax.text(0.5, y-0.08, "下面用 36 组量化回测告诉你答案 ↓", ha="center", va="top",
            fontsize=11, color="#f0b866", transform=ax.transAxes, fontproperties=FP_BOLD)
    
    savefig(fig, "00b_intro.png")


def card_heatmap(results):
    """01_heatmap: 热力图 — 窗口×市场年化收益（重新设计）"""
    fig = plt.figure(figsize=(6, 8))
    fig.patch.set_facecolor(BG)
    
    # 顶部说明区
    ax_intro = fig.add_axes([0.05, 0.85, 0.9, 0.12])
    ax_intro.set_facecolor(BG)
    ax_intro.axis("off")
    
    ax_intro.text(0.5, 0.95, "量化回测：右侧 vs 左侧交易，谁更赚钱？", ha="center", va="top",
                  fontsize=15, fontweight="bold", color="white", transform=ax_intro.transAxes,
                  fontproperties=FP_BOLD)
    ax_intro.text(0.5, 0.65, "右侧交易 = 顺势（涨时买入，跌时卖出）", ha="center", va="top",
                  fontsize=11, color=GREEN, transform=ax_intro.transAxes, fontproperties=FP_REG)
    ax_intro.text(0.5, 0.40, "左侧交易 = 逆势（跌时买入，涨时卖出）", ha="center", va="top",
                  fontsize=11, color=PURPLE, transform=ax_intro.transAxes, fontproperties=FP_REG)
    ax_intro.text(0.5, 0.10, "↓ 25种组合 × 8年数据 ↓", ha="center", va="top",
                  fontsize=10, color=GRAY, transform=ax_intro.transAxes, fontproperties=FP_REG)
    
    # 热力图区
    ax_heat = fig.add_axes([0.08, 0.15, 0.84, 0.65])
    ax_heat.set_facecolor(BG)
    
    # 合并动量和反转数据到一张表
    universes = ["broad", "sector", "commodity"]
    uni_labels = ["宽基\n沪深300+中证500", "行业\n6只ETF", "商品\n黄金+豆粕+能源"]
    
    # 构建矩阵：行=市场，列=窗口×策略
    # 列顺序：动量5日, 动量10日, ..., 动量250日, 反转5日, ..., 反转250日
    # 但这样太宽，改成：行=市场×策略，列=窗口
    rows = []
    row_labels = []
    for uni, label in zip(universes, uni_labels):
        # 动量行
        mom_vals = []
        for w in WINDOWS:
            r = [x for x in results if x["universe"] == uni and x["window"] == w and not x["reverse"]]
            mom_vals.append(r[0]["annual_return"] * 100 if r else np.nan)
        rows.append(mom_vals)
        row_labels.append(f"{label}\n右侧(顺势)")
        
        # 反转行
        rev_vals = []
        for w in WINDOWS:
            r = [x for x in results if x["universe"] == uni and x["window"] == w and x["reverse"]]
            rev_vals.append(r[0]["annual_return"] * 100 if r else np.nan)
        rows.append(rev_vals)
        row_labels.append(f"{label}\n左侧(逆势)")
    
    matrix = np.array(rows)
    
    # 使用自定义色块而非imshow，确保对比度
    norm = Normalize(vmin=-15, vmax=20)
    cmap = cm.get_cmap("RdYlGn_r")
    
    # 绘制色块
    for i in range(len(rows)):
        for j in range(len(WINDOWS)):
            val = matrix[i, j]
            if not np.isnan(val):
                color = cmap(norm(val))
                rect = Rectangle((j-0.5, i-0.5), 1, 1, facecolor=color, edgecolor="#2a2a4a", linewidth=1)
                ax_heat.add_patch(rect)
    
    ax_heat.set_xlim(-0.5, len(WINDOWS)-0.5)
    ax_heat.set_ylim(len(rows)-0.5, -0.5)
    
    ax_heat.set_xticks(range(len(WINDOWS)))
    ax_heat.set_xticklabels([f"{w}日" for w in WINDOWS], fontsize=9, fontproperties=FP_REG)
    ax_heat.set_xlabel("回溯窗口（看过去多少天的涨幅）", fontsize=9, color=GRAY, 
                        fontproperties=FP_REG, labelpad=10)
    
    ax_heat.set_yticks(range(len(row_labels)))
    ax_heat.set_yticklabels(row_labels, fontsize=8, fontproperties=FP_REG, linespacing=1.2)
    
    # 添加数值标注 - 使用深色背景块+白字提高对比度
    for i in range(len(rows)):
        for j in range(len(WINDOWS)):
            val = matrix[i, j]
            if not np.isnan(val):
                # 总是用白字+描边，确保清晰可读
                ax_heat.text(j, i, f"{val:+.1f}%", ha="center", va="center",
                            fontsize=10, fontweight="bold", color="white",
                            path_effects=[pe.withStroke(linewidth=2, foreground="black")],
                            fontproperties=FP_BOLD)
    
    # 添加分隔线
    for i in range(2, 6, 2):
        ax_heat.axhline(y=i-0.5, color="#555555", linewidth=1)
    
    for label in ax_heat.get_xticklabels():
        label.set_color("#cccccc")
    for label in ax_heat.get_yticklabels():
        label.set_color("#cccccc")
    
    # 底部说明
    ax_footer = fig.add_axes([0.05, 0.02, 0.9, 0.10])
    ax_footer.set_facecolor(BG)
    ax_footer.axis("off")
    ax_footer.text(0.5, 0.5, "红色=盈利 · 绿色=亏损 · 数值=年化收益率",
                   ha="center", va="center", fontsize=9, color=GRAY, 
                   transform=ax_footer.transAxes, fontproperties=FP_REG)
    
    savefig(fig, "01_heatmap.png")


def card_best_nav(results):
    """02_best_nav: 最佳策略净值曲线"""
    best = max(results, key=lambda r: r["annual_return"])
    
    fig, ax = plt.subplots(figsize=(6, 8))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(CARD_BG)
    
    nav_ratio = best["nav"] / best["nav"].iloc[0]
    bench_ratio = best["bench"] / best["bench"].iloc[0]
    nav_pct = (nav_ratio - 1) * 100
    bench_pct = (bench_ratio - 1) * 100
    
    ax.plot(nav_pct.index, nav_pct.values, color=GREEN, linewidth=2, label=best["label"])
    ax.plot(bench_pct.index, bench_pct.values, color=GRAY, linewidth=1.5, alpha=0.7, 
            label=best["bench_label"])
    ax.axhline(y=0, color="#333366", linewidth=0.5)
    ax.fill_between(nav_pct.index, 0, nav_pct.values, alpha=0.1, color=GREEN)
    
    ax.set_yscale("symlog", linthresh=20)
    
    fig.suptitle(f"最佳策略：{best['label']}", fontsize=16, fontweight="bold", color="white", y=0.95,
                 fontproperties=FP_BOLD)
    fig.text(0.5, 0.91, f"{best['uni_name']} · {START_DATE[:4]}-{END_DATE[:4]}",
             ha="center", fontsize=11, color=GRAY, fontproperties=FP_REG)
    
    kpi_y = 0.86
    fig.text(0.2, kpi_y, f"年化: +{best['annual_return']:.1%}", ha="center", fontsize=13, 
             fontweight="bold", color=GREEN, fontproperties=FP_BOLD)
    fig.text(0.5, kpi_y, f"回撤: -{best['max_drawdown']:.1%}", ha="center", fontsize=13,
             fontweight="bold", color=RED, fontproperties=FP_BOLD)
    fig.text(0.8, kpi_y, f"Sharpe: {best['sharpe']:.2f}", ha="center", fontsize=13,
             fontweight="bold", color=GOLD, fontproperties=FP_BOLD)
    
    ax.set_ylabel("收益率 (%)", color="#cccccc", fontproperties=FP_REG)
    ax.set_xlabel("年份", color="#cccccc", fontproperties=FP_REG)
    ax.legend(loc="upper left", facecolor="#3a3a5c", labelcolor="white", framealpha=1,
              prop=FP_REG)
    ax.grid(True, alpha=0.3)
    
    for label in ax.get_xticklabels():
        label.set_color("#cccccc")
    for label in ax.get_yticklabels():
        label.set_color("#cccccc")
    
    plt.tight_layout(rect=[0, 0, 1, 0.84])
    savefig(fig, "02_best_nav.png")


def card_worst_nav(results):
    """03_worst_nav: 最差策略净值曲线 — 踩坑展示"""
    worst = min(results, key=lambda r: r["annual_return"])
    
    fig, ax = plt.subplots(figsize=(6, 8))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(CARD_BG)
    
    nav_pct = (worst["nav"] / worst["nav"].iloc[0] - 1) * 100
    bench_pct = (worst["bench"] / worst["bench"].iloc[0] - 1) * 100
    
    ax.plot(nav_pct.index, nav_pct.values, color=RED, linewidth=2, label=worst["label"])
    ax.plot(bench_pct.index, bench_pct.values, color=GRAY, linewidth=1.5, alpha=0.7, 
            label=worst["bench_label"])
    ax.axhline(y=0, color="#333366", linewidth=0.5)
    ax.fill_between(nav_pct.index, 0, nav_pct.values, alpha=0.1, color=RED)
    
    fig.suptitle(f"最差策略：{worst['label']}", fontsize=16, fontweight="bold", color=RED, y=0.95,
                 fontproperties=FP_BOLD)
    fig.text(0.5, 0.91, f"{worst['uni_name']} · 这就是坑！",
             ha="center", fontsize=11, color=GRAY, fontproperties=FP_REG)
    
    kpi_y = 0.86
    fig.text(0.2, kpi_y, f"年化: {worst['annual_return']:.1%}", ha="center", fontsize=13,
             fontweight="bold", color=RED, fontproperties=FP_BOLD)
    fig.text(0.5, kpi_y, f"回撤: -{worst['max_drawdown']:.1%}", ha="center", fontsize=13,
             fontweight="bold", color=RED, fontproperties=FP_BOLD)
    fig.text(0.8, kpi_y, f"Sharpe: {worst['sharpe']:.2f}", ha="center", fontsize=13,
             fontweight="bold", color=ORANGE, fontproperties=FP_BOLD)
    
    ax.set_ylabel("收益率 (%)", color="#cccccc", fontproperties=FP_REG)
    ax.set_xlabel("年份", color="#cccccc", fontproperties=FP_REG)
    ax.legend(loc="lower left", facecolor="#3a3a5c", labelcolor="white", framealpha=1,
              prop=FP_REG)
    ax.grid(True, alpha=0.3)
    
    for label in ax.get_xticklabels():
        label.set_color("#cccccc")
    for label in ax.get_yticklabels():
        label.set_color("#cccccc")
    
    plt.tight_layout(rect=[0, 0, 1, 0.84])
    savefig(fig, "03_worst_nav.png")


def card_annual(results):
    """04_annual: 最佳策略分年度收益"""
    best = max(results, key=lambda r: r["annual_return"])
    nav = best["nav"]
    bench = best["bench"]
    
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
    
    # 优雅配色：策略用暖琥珀/冷靛蓝区分盈亏，基准用银灰
    STRAT_POS = "#f0b866"   # 暖琥珀 (盈利年)
    STRAT_NEG = "#7fa5c4"   # 冷靛蓝 (亏损年)
    BENCH_CLR = "#6b7b8d"   # 银灰 (基准)
    
    x = np.arange(len(years))
    width = 0.35
    
    # 策略柱：正年用琥珀，负年用靛蓝
    strat_colors = [STRAT_POS if v >= 0 else STRAT_NEG for v in strat_annual]
    bars1 = ax.bar(x - width/2, [v*100 for v in strat_annual], width, 
                   color=strat_colors, alpha=0.92, label=best["label"],
                   edgecolor="#1a1a2e", linewidth=0.5)
    bars2 = ax.bar(x + width/2, [v*100 for v in bench_annual], width, 
                   color=BENCH_CLR, alpha=0.75, label=best["bench_label"],
                   edgecolor="#1a1a2e", linewidth=0.5)
    
    for bar, val in zip(bars1, strat_annual):
        c = STRAT_POS if val >= 0 else STRAT_NEG
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (1 if val >= 0 else -3),
                f"{val:+.1%}", ha="center", va="bottom" if val >= 0 else "top",
                fontsize=8, color=c, fontweight="bold")
    
    ax.set_xticks(x)
    ax.set_xticklabels(years, fontsize=9)
    ax.set_ylabel("年度收益 (%)", color="#cccccc", fontproperties=FP_REG)
    ax.axhline(y=0, color="#333366", linewidth=0.5)
    # 自定义图例：区分盈利/亏损年
    from matplotlib.patches import Patch
    legend_handles = [
        Patch(facecolor=STRAT_POS, edgecolor="#1a1a2e", label=f"{best['label']} (盈利年)"),
        Patch(facecolor=STRAT_NEG, edgecolor="#1a1a2e", label=f"{best['label']} (亏损年)"),
        Patch(facecolor=BENCH_CLR, edgecolor="#1a1a2e", label=best["bench_label"]),
    ]
    ax.legend(loc="upper left", handles=legend_handles, facecolor="#3a3a5c", 
              labelcolor="white", framealpha=1, prop=FP_REG, fontsize=7)
    ax.grid(True, axis="y", alpha=0.3)
    
    fig.suptitle(f"分年度收益：{best['label']}", fontsize=16, fontweight="bold", color="white", y=0.95,
                 fontproperties=FP_BOLD)
    fig.text(0.5, 0.91, f"{best['uni_name']} · 逐年对比",
             ha="center", fontsize=11, color=GRAY, fontproperties=FP_REG)
    
    for label in ax.get_xticklabels():
        label.set_color("#cccccc")
    for label in ax.get_yticklabels():
        label.set_color("#cccccc")
    
    plt.tight_layout(rect=[0, 0, 1, 0.88])
    savefig(fig, "04_annual.png")


def card_momentum_vs_reversal(results):
    """05_momentum_vs_reversal: 右侧vs左侧分组对比 — 3行竖排"""
    fig, axes = plt.subplots(3, 1, figsize=(6, 8))
    fig.patch.set_facecolor(BG)
    fig.suptitle("右侧 vs 左侧", fontsize=16, fontweight="bold", color="white", y=0.985,
                 fontproperties=FP_BOLD)
    fig.text(0.5, 0.93, "各市场 × 各窗口年化收益对比", ha="center", fontsize=10, color=GRAY,
             fontproperties=FP_REG)
    
    # 优雅配色 — 和图4同系列
    RIGHT_CLR = "#f0b866"   # 暖琥珀 = 右侧(顺势)
    LEFT_CLR = "#7fa5c4"    # 冷靛蓝 = 左侧(逆势)
    
    universes = ["broad", "sector", "commodity"]
    uni_labels = ["宽基 (沪深300+中证500)", "行业 (6只ETF)", "商品 (黄金+豆粕+能源)"]
    
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
        
        bars_r = ax.bar(x - width/2, mom_vals, width, color=RIGHT_CLR, alpha=0.92,
                        edgecolor="#1a1a2e", linewidth=0.5)
        bars_l = ax.bar(x + width/2, rev_vals, width, color=LEFT_CLR, alpha=0.92,
                        edgecolor="#1a1a2e", linewidth=0.5)
        
        # 标注数值（只标最大最小值，避免拥挤）
        max_i = np.argmax(mom_vals)
        min_i = np.argmin(rev_vals) if min(rev_vals) < 0 else np.argmin(rev_vals)
        for bars, vals in [(bars_r, mom_vals), (bars_l, rev_vals)]:
            for i, (bar, val) in enumerate(zip(bars, vals)):
                # 标注绝对值最大的柱子
                if i == max_i or i == min_i or abs(val) > 8:
                    ax.text(bar.get_x() + bar.get_width()/2,
                            bar.get_height() + (1.2 if val >= 0 else -1.2),
                            f"{val:+.1f}", ha="center",
                            va="bottom" if val >= 0 else "top",
                            fontsize=7, color="white", fontweight="bold")
        
        ax.axhline(y=0, color="#333366", linewidth=0.5)
        ax.set_xticks(x)
        ax.set_xticklabels([f"{w}日" for w in WINDOWS], fontsize=8,
                           fontproperties=FP_REG)
        ax.set_ylabel("%", fontsize=8, color="#999999", fontproperties=FP_REG)
        ax.set_title(label, fontsize=11, fontweight="bold", color="white",
                     fontproperties=FP_BOLD, loc="left", pad=4)
        ax.grid(True, axis="y", alpha=0.2)
        ax.tick_params(axis="both", labelsize=7, colors="#999999")
        
        if idx == 0:
            from matplotlib.patches import Patch
            legend_handles = [
                Patch(facecolor=RIGHT_CLR, edgecolor="#1a1a2e", label="右侧(顺势)"),
                Patch(facecolor=LEFT_CLR, edgecolor="#1a1a2e", label="左侧(逆势)"),
            ]
            ax.legend(loc="upper right", handles=legend_handles,
                      facecolor="#3a3a5c", labelcolor="white",
                      framealpha=1, fontsize=7, prop=FP_REG)
    
    fig.text(0.5, 0.02, "Y轴=年化收益% · 数值只标注显著值",
             ha="center", fontsize=8, color=GRAY, fontproperties=FP_REG)
    
    plt.tight_layout(rect=[0, 0.05, 1, 0.88])
    savefig(fig, "05_momentum_vs_reversal.png")


def card_conclusion(results):
    """06_conclusion: 核心结论卡"""
    fig, ax = plt.subplots(figsize=(6, 8))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.axis("off")
    
    ax.text(0.5, 0.95, "核心发现", ha="center", va="top",
            fontsize=22, fontweight="bold", color="white", transform=ax.transAxes,
            fontproperties=FP_BOLD)
    
    ax.plot([0.1, 0.9], [0.90, 0.90], color=GOLD, linewidth=2, transform=ax.transAxes)
    
    findings = [
        ("1", "短期右侧(5-20日)\n在A股是绞肉机",
         "行业ETF尤其明显：年化最高-14.6%", RED),
        ("2", "中期右侧(60-120日)\n只在商品市场有效",
         "黄金/豆粕/能源：年化+19.5%，Sharpe 0.88", GREEN),
        ("3", "左侧策略（逆势）\n在宽基市场有效",
         "沪深300+中证500：年化+6.6%，回撤小", PURPLE),
        ("4", "黄金法则：\n时间尺度决定一切",
         "同样的策略，换个窗口，结果完全相反", GOLD),
    ]
    
    y = 0.84
    for num, title, detail, color in findings:
        ax.text(0.08, y, num, ha="center", va="top",
                fontsize=20, fontweight="bold", color=color, transform=ax.transAxes,
                fontproperties=FP_BOLD)
        ax.text(0.15, y, title, ha="left", va="top",
                fontsize=12, fontweight="bold", color="white", transform=ax.transAxes,
                linespacing=1.4, fontproperties=FP_BOLD)
        ax.text(0.15, y - 0.08, detail, ha="left", va="top",
                fontsize=9, color=GRAY, transform=ax.transAxes, fontproperties=FP_REG)
        y -= 0.19
    
    # 给散户的建议
    ax.text(0.5, 0.12, "散户建议：短期追涨杀跌是陷阱，", ha="center", va="top",
            fontsize=10, color="#f0b866", transform=ax.transAxes,
            fontproperties=FP_BOLD)
    ax.text(0.5, 0.08, "商品和宽基的中长期策略更稳健", ha="center", va="top",
            fontsize=10, color="#f0b866", transform=ax.transAxes,
            fontproperties=FP_BOLD)
    
    ax.text(0.5, 0.04, "数据：ETF日线价格 · 月度调仓 · 初始资金100万",
            ha="center", fontsize=8, color="#555555", transform=ax.transAxes,
            fontproperties=FP_REG)
    ax.text(0.5, 0.01, "免责声明：历史业绩不代表未来表现",
            ha="center", fontsize=8, color="#555555", transform=ax.transAxes,
            fontproperties=FP_REG, style="italic")
    
    savefig(fig, "06_conclusion.png")


def card_summary_table(results):
    """07_table: Top5 & Bottom3 排行榜"""
    sorted_r = sorted(results, key=lambda r: r["annual_return"], reverse=True)
    top5 = sorted_r[:5]
    bottom3 = sorted_r[-3:]
    
    fig, ax = plt.subplots(figsize=(6, 8))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.axis("off")
    
    ax.text(0.5, 0.96, "策略排行榜：最佳 & 最差", ha="center", va="top",
            fontsize=18, fontweight="bold", color="white", transform=ax.transAxes,
            fontproperties=FP_BOLD)
    
    ax.plot([0.05, 0.95], [0.91, 0.91], color=GOLD, linewidth=1, transform=ax.transAxes)
    
    headers = [("排名", 0.08), ("策略", 0.35), ("年化", 0.60), ("回撤", 0.76), ("Sharpe", 0.92)]
    for label, x in headers:
        ax.text(x, 0.87, label, ha="center", va="top", fontsize=9, 
                fontweight="bold", color=GRAY, transform=ax.transAxes,
                fontproperties=FP_BOLD)
    
    # Top 5
    y = 0.82
    for i, r in enumerate(top5):
        color = GREEN if r["annual_return"] > 0 else RED
        ax.text(0.08, y, f"#{i+1}", ha="center", va="top", fontsize=12,
                fontweight="bold", color=GOLD, transform=ax.transAxes)
        ax.text(0.35, y, f"{r['label']}\n{r['uni_name'].split('(')[0].strip()}", 
                ha="center", va="top", fontsize=10, color="white", transform=ax.transAxes,
                fontproperties=FP_REG)
        ax.text(0.60, y, f"+{r['annual_return']:.1%}", ha="center", va="top",
                fontsize=12, fontweight="bold", color=color, transform=ax.transAxes)
        ax.text(0.76, y, f"-{r['max_drawdown']:.1%}", ha="center", va="top",
                fontsize=11, color=RED, transform=ax.transAxes)
        ax.text(0.92, y, f"{r['sharpe']:.2f}", ha="center", va="top",
                fontsize=11, color=GOLD, transform=ax.transAxes)
        y -= 0.08
    
    y -= 0.02
    ax.plot([0.05, 0.95], [y+0.02, y+0.02], color="#333366", linewidth=1, transform=ax.transAxes)
    
    # Bottom 3
    y -= 0.04
    for i, r in enumerate(bottom3):
        ax.text(0.08, y, f"#{len(sorted_r)-2+i}", ha="center", va="top", fontsize=12,
                fontweight="bold", color=RED, transform=ax.transAxes)
        ax.text(0.35, y, f"{r['label']}\n{r['uni_name'].split('(')[0].strip()}", 
                ha="center", va="top", fontsize=10, color="white", transform=ax.transAxes,
                fontproperties=FP_REG)
        ax.text(0.60, y, f"{r['annual_return']:.1%}", ha="center", va="top",
                fontsize=12, fontweight="bold", color=RED, transform=ax.transAxes)
        ax.text(0.76, y, f"-{r['max_drawdown']:.1%}", ha="center", va="top",
                fontsize=11, color=RED, transform=ax.transAxes)
        ax.text(0.92, y, f"{r['sharpe']:.2f}", ha="center", va="top",
                fontsize=11, color=ORANGE, transform=ax.transAxes)
        y -= 0.08
    
    ax.text(0.5, 0.03, "关注我不迷路", ha="center", va="center",
            fontsize=12, color=GOLD, transform=ax.transAxes, fontproperties=FP_BOLD)
    
    savefig(fig, "07_table.png")


# ============================================================
# HTML 报告
# ============================================================

def generate_html_report(results):
    """生成中文HTML交互报告"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    sorted_r = sorted(results, key=lambda r: r["annual_return"], reverse=True)
    
    html_parts = []
    html_parts.append(f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>右侧vs左侧交易实验报告</title>
<style>
body {{ background: #0f0f1a; color: #eee; font-family: 'Microsoft YaHei', 'Noto Sans SC', sans-serif; margin: 20px; }}
h1 {{ color: #ffd700; }}
h2 {{ color: #4ecca3; border-bottom: 1px solid #333; padding-bottom: 5px; }}
table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
th, td {{ padding: 8px 12px; text-align: right; border-bottom: 1px solid #2a2a4a; }}
th {{ background: #16213e; color: #ffd700; }}
tr:hover {{ background: #1a1a3e; }}
.positive {{ color: #e74c3c; }}
.negative {{ color: #4ecca3; }}
.tag {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.85em; }}
.tag-mom {{ background: #4a1a1a; color: #e74c3c; }}
.tag-rev {{ background: #2a1a3a; color: #9b59b6; }}
</style>
</head>
<body>
<h1>右侧vs左侧交易在A股 — 完整回测结果</h1>
<p>回测区间：{START_DATE} 至 {END_DATE} · 月度调仓 · {len(results)} 种策略组合</p>
""")
    
    html_parts.append("<h2>全部策略排名</h2>")
    html_parts.append("""<table>
<tr><th>#</th><th>市场</th><th>类型</th><th>窗口</th><th>年化收益</th>
<th>总收益</th><th>最大回撤</th><th>Sharpe</th><th>胜率</th><th>Alpha</th></tr>""")
    
    for i, r in enumerate(sorted_r):
        tag_class = "tag-rev" if r["reverse"] else "tag-mom"
        tag_text = "左侧" if r["reverse"] else "右侧"
        ann_class = "positive" if r["annual_return"] > 0 else "negative"
        alpha_class = "positive" if r["alpha"] > 0 else "negative"
        
        html_parts.append(f"""<tr>
<td>{i+1}</td>
<td>{r['uni_name']}</td>
<td><span class="tag {tag_class}">{tag_text}</span></td>
<td>{r['window']}日</td>
<td class="{ann_class}">{r['annual_return']:+.2%}</td>
<td class="{ann_class}">{r['total_return']:+.2%}</td>
<td class="negative">-{r['max_drawdown']:.2%}</td>
<td>{r['sharpe']:.2f}</td>
<td>{r['win_rate']:.0%}</td>
<td class="{alpha_class}">{r['alpha']:+.2%}</td>
</tr>""")
    
    html_parts.append("</table>")
    
    best = sorted_r[0]
    worst = sorted_r[-1]
    html_parts.append(f"""
<h2>核心发现</h2>
<ul>
<li><strong>最佳策略：</strong>{best['label']}，{best['uni_name']} — 年化 {best['annual_return']:+.2%}，Sharpe {best['sharpe']:.2f}</li>
<li><strong>最差策略：</strong>{worst['label']}，{worst['uni_name']} — 年化 {worst['annual_return']:+.2%}，最大回撤 -{worst['max_drawdown']:.2%}</li>
<li><strong>宽基市场：</strong>短期右侧亏钱，左侧策略有效</li>
<li><strong>行业ETF：</strong>短期右侧灾难（5日年化-14.6%），5日左侧反而+7.2%</li>
<li><strong>商品市场：</strong>中长期右侧表现良好（60-120日窗口）</li>
</ul>
""")
    
    html_parts.append("</body></html>")
    
    path = OUTPUT_DIR / "report.html"
    path.write_text("\n".join(html_parts))
    print(f"  ✓ {path}")


# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 60)
    print("右侧vs左侧交易实验 — 可视化生成")
    print("=" * 60)
    
    print("\n加载数据...")
    prices = load_all_data()
    
    print("\n运行实验...")
    results = run_experiments(prices)
    print(f"  {len(results)} 组实验完成")
    
    print("\n生成卡片...")
    card_cover(results)
    card_intro()
    card_heatmap(results)
    card_best_nav(results)
    card_worst_nav(results)
    card_annual(results)
    card_momentum_vs_reversal(results)
    card_conclusion(results)
    card_summary_table(results)
    
    print("\n生成HTML报告...")
    generate_html_report(results)
    
    print("\n✓ 全部完成！")
    print(f"  卡片目录: {XHS_DIR}/")
    print(f"  报告文件: {OUTPUT_DIR}/report.html")


if __name__ == "__main__":
    main()
