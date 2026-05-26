"""可视化模块 — 回测结果图表 (English labels for maximum compatibility)"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import numpy as np
from pathlib import Path


def plot_nav(
    nav: pd.Series,
    benchmark: pd.Series | None = None,
    title: str = "Strategy NAV",
    save_path: str | None = None,
):
    """绘制净值曲线 + 可选基准对比"""
    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(nav.index, nav.values / nav.values[0], label="Strategy", linewidth=1.5, color="#1f77b4")

    if benchmark is not None:
        bench_norm = benchmark / benchmark.iloc[0]
        ax.plot(
            bench_norm.index, bench_norm.values, label="Benchmark", linewidth=1, color="gray", alpha=0.7
        )

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_ylabel("NAV")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)

    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
    
    if benchmark is not None:
        bench_norm = benchmark.reindex(nav.index).ffill()
        bench_norm = bench_norm / bench_norm.iloc[0]
        strategy_norm = nav.values / nav.values[0]
        ax.fill_between(
            nav.index,
            strategy_norm,
            bench_norm.values if hasattr(bench_norm, 'values') else bench_norm,
            where=strategy_norm >= bench_norm,
            color="green",
            alpha=0.1,
            label="Alpha",
        )
        ax.fill_between(
            nav.index,
            strategy_norm,
            bench_norm.values if hasattr(bench_norm, 'values') else bench_norm,
            where=strategy_norm < bench_norm,
            color="red",
            alpha=0.1,
            label="Underperform",
        )

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close()
    return fig


def plot_drawdown(nav: pd.Series, title: str = "Drawdown", save_path: str | None = None):
    """绘制回撤曲线"""
    fig, ax = plt.subplots(figsize=(12, 3))

    peak = nav.expanding().max()
    drawdown = (nav - peak) / peak * 100

    ax.fill_between(drawdown.index, 0, drawdown.values, color="red", alpha=0.3)
    ax.plot(drawdown.index, drawdown.values, color="darkred", linewidth=0.8)
    ax.set_title(title, fontsize=12)
    ax.set_ylabel("Drawdown %")
    ax.grid(True, alpha=0.3)

    max_dd = drawdown.min()
    ax.axhline(y=max_dd, color="red", linestyle="--", linewidth=0.8, label=f"Max DD: {max_dd:.1f}%")
    ax.legend(loc="lower left")

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close()
    return fig


def plot_report(
    nav: pd.Series,
    metrics: dict,
    benchmark: pd.Series | None = None,
    title: str = "Backtest Report",
    save_path: str | None = None,
):
    """生成完整回测报告图（净值+回撤+指标）"""
    fig = plt.figure(figsize=(14, 8))
    gs = fig.add_gridspec(2, 2, height_ratios=[3, 1], hspace=0.3, wspace=0.3)

    # 左上：净值曲线
    ax1 = fig.add_subplot(gs[0, :])
    nav_norm = nav.values / nav.values[0]
    ax1.plot(nav.index, nav_norm, label="Strategy", linewidth=1.5, color="#1f77b4")
    if benchmark is not None:
        bench_norm = benchmark.reindex(nav.index).ffill()
        bench_norm = bench_norm / bench_norm.iloc[0]
        ax1.plot(bench_norm.index, bench_norm.values, label="Benchmark", linewidth=1, color="gray", alpha=0.7)
    ax1.set_title(title, fontsize=14, fontweight="bold")
    ax1.legend(loc="upper left")
    ax1.grid(True, alpha=0.3)
    ax1.set_ylabel("NAV")

    # 左下：回撤
    ax2 = fig.add_subplot(gs[1, 0])
    peak = nav.expanding().max()
    dd = (nav - peak) / peak * 100
    ax2.fill_between(dd.index, 0, dd.values, color="red", alpha=0.3)
    ax2.plot(dd.index, dd.values, color="darkred", linewidth=0.8)
    ax2.set_title("Drawdown", fontsize=11)
    ax2.set_ylabel("%")
    ax2.grid(True, alpha=0.3)

    # 右下：指标表
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.axis("off")
    metric_lines = [
        f"Ann.Ret: {metrics.get('annual_return', 0)*100:+.1f}%",
        f"Max DD:  {metrics.get('max_drawdown', 0)*100:.1f}%",
        f"Sharpe:  {metrics.get('sharpe', 0):.2f}",
        f"Calmar:  {metrics.get('calmar', 0):.2f}",
        f"Win Rate:{metrics.get('win_rate', 0)*100:.1f}%",
        f"Tot.Ret: {metrics.get('total_return', 0)*100:+.1f}%",
        f"Days:    {metrics.get('n_days', 0)}",
    ]
    y_pos = np.arange(len(metric_lines))[::-1] * 0.13
    ax3.set_ylim(-0.1, 1.0)
    ax3.set_xlim(0, 1)
    for y, line in zip(y_pos, metric_lines):
        ax3.text(0.05, y, line, fontsize=10, family="monospace")
    ax3.set_title("Performance", fontsize=11)

    plt.tight_layout()
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close()
    return fig
