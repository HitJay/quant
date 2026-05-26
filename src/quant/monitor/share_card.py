"""小红书风格分享卡片 — 专业炫酷版"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path


def share_card(
    nav,
    metrics: dict,
    benchmark_label: str = "",
    strategy_name: str = "",
    period: str = "",
    save_path: str = "./output/share_card.png",
    dpi: int = 200,
):
    BG = "#fafbfc"
    ACCENT = "#2563eb"
    GREEN = "#059669"
    RED = "#dc2626"
    DARK = "#111827"
    MUTED = "#6b7280"
    CARD_BG = "#ffffff"
    CARD_SHADOW = "#e5e7eb"

    fig = plt.figure(figsize=(6, 8), facecolor=BG)

    ann_ret = metrics.get("annual_return", 0)
    mdd_val = metrics.get("max_drawdown", 0)
    shp_val = metrics.get("sharpe", 0)
    tot_ret = metrics.get("total_return", 0)
    bench_ann = metrics.get("bench_annual")
    bench_tot = metrics.get("bench_total", 0)
    n_days = metrics.get("n_days", 0)
    yrs = n_days / 252

    # ====== 顶部：标题 + Hero ======
    fig.text(0.5, 0.97, strategy_name, fontsize=24, fontweight="bold", color=DARK, ha="center", va="top")
    fig.text(0.5, 0.93, period, fontsize=11, color=MUTED, ha="center", va="top")

    hero_color = GREEN if tot_ret > 0 else RED
    fig.text(0.5, 0.86, f"{tot_ret*100:+.1f}%", fontsize=54, fontweight="bold",
             color=hero_color, ha="center", va="center")
    fig.text(0.5, 0.81, "Total Return", fontsize=12, color=MUTED, ha="center", va="center")
    if bench_ann is not None:
        delta = ann_ret - bench_ann
        sign = "+" if delta >= 0 else ""
        fig.text(0.5, 0.78, f"Ann. {ann_ret*100:+.1f}%  vs  {benchmark_label} {bench_ann*100:+.1f}%",
                 fontsize=10, color=MUTED, ha="center", va="center")

    # ====== 三列 KPI ======
    card_y = 0.65
    card_h = 0.08
    card_w = 0.28
    xs = [0.06, 0.38, 0.70]

    kpis = [
        ("Sharpe", f"{shp_val:.2f}", ACCENT),
        ("Max DD", f"{mdd_val*100:.1f}%", RED),
        ("Win Rate", f"{metrics.get('win_rate',0)*100:.0f}%", ACCENT),
    ]
    for (label, value, color), x in zip(kpis, xs):
        rect = mpatches.FancyBboxPatch(
            (x, card_y), card_w, card_h,
            boxstyle="round,pad=0.02", facecolor=CARD_BG,
            edgecolor=CARD_SHADOW, linewidth=1.2,
            transform=fig.transFigure, zorder=0,
        )
        fig.patches.append(rect)
        fig.text(x + card_w/2, card_y + card_h - 0.012, label,
                 fontsize=8, color=MUTED, ha="center", va="top")
        fig.text(x + card_w/2, card_y + card_h/2 - 0.008, value,
                 fontsize=18, fontweight="bold", color=color, ha="center", va="center")

    # ====== NAV 大图 ======
    nav_ratio = nav / nav.iloc[0]
    ax_chart = fig.add_axes([0.08, 0.22, 0.84, 0.37])
    ax_chart.fill_between(nav.index, nav_ratio, 1, where=nav_ratio >= 1,
                          alpha=0.12, color=GREEN)
    ax_chart.fill_between(nav.index, nav_ratio, 1, where=nav_ratio < 1,
                          alpha=0.06, color=RED)
    ax_chart.plot(nav.index, nav_ratio, color=ACCENT, linewidth=2.2)
    ax_chart.axhline(y=1, color=MUTED, linewidth=0.6, linestyle="--", alpha=0.4)
    ax_chart.set_facecolor(BG)
    for s in ["top", "right"]: ax_chart.spines[s].set_visible(False)
    ax_chart.spines["left"].set_color(MUTED); ax_chart.spines["left"].set_alpha(0.3)
    ax_chart.spines["bottom"].set_color(MUTED); ax_chart.spines["bottom"].set_alpha(0.3)
    ax_chart.tick_params(colors=MUTED, labelsize=7)
    ax_chart.set_ylabel("NAV", color=MUTED, fontsize=8)
    ax_chart.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.1f}x"))
    # 标注起始和结束
    ax_chart.annotate(f"×{nav_ratio.iloc[-1]:.1f}", xy=(nav.index[-1], nav_ratio.iloc[-1]),
                      xytext=(6, 6), textcoords="offset points", fontsize=9,
                      color=hero_color, ha="left", fontweight="bold")

    # ====== 底部横条：策略 vs 基准对比 ======
    bar_y = 0.04
    rect = mpatches.FancyBboxPatch(
        (0.06, bar_y), 0.88, 0.12,
        boxstyle="round,pad=0.02", facecolor=DARK, edgecolor="none",
        transform=fig.transFigure, zorder=0,
    )
    fig.patches.append(rect)

    # 对比条：策略 vs 基准
    label_x = 0.12
    bar_x0 = 0.22
    bar_total_w = 0.45
    bar_h = 0.016
    gap = 0.025
    top_y = bar_y + 0.082
    bot_y = top_y - gap

    # 标签（居中对齐+加粗，与条中心对齐）
    fig.text(label_x, top_y, f"{benchmark_label}", fontsize=9,
             color="#9ca3af", ha="left", va="center", fontweight="bold")
    fig.text(label_x, bot_y, "Strategy", fontsize=9,
             color=GREEN, ha="left", va="center", fontweight="bold")

    # 基准条
    bench_ratio = min(1.0, abs((1+bench_tot)/(1+tot_ret))) if tot_ret != 0 else 1.0
    bench_width = bar_total_w * bench_ratio
    ax_bb = fig.add_axes([bar_x0, top_y - bar_h/2, bar_total_w, bar_h])
    ax_bb.barh(0, bench_width, color="#4b5563", height=0.8)
    ax_bb.set_xlim(0, 1); ax_bb.axis("off")
    pct_x = bar_x0 + bar_total_w + 0.03
    fig.text(pct_x, top_y, f"{bench_tot*100:+.1f}%",
             fontsize=10, color="#9ca3af", va="center", ha="left", fontweight="bold")

    # 策略条（绿色满格）
    ax_sb = fig.add_axes([bar_x0, bot_y - bar_h/2, bar_total_w, bar_h])
    ax_sb.barh(0, 1.0, color=GREEN, height=0.8)
    ax_sb.set_xlim(0, 1); ax_sb.axis("off")
    fig.text(pct_x, bot_y, f"{tot_ret*100:+.1f}%",
             fontsize=11, color=GREEN, va="center", ha="left", fontweight="bold")

    # 底部说明
    fig.text(0.5, bar_y + 0.015, f"{n_days} trading days · ~{yrs:.1f} years · for reference only",
             fontsize=7, color="#9ca3af", ha="center", va="center")

    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, dpi=dpi, facecolor=BG, edgecolor="none", pad_inches=0.3)
    plt.close(fig)
    return save_path


def share_card_dark(
    nav,
    metrics: dict,
    benchmark_label: str = "",
    strategy_name: str = "",
    period: str = "",
    save_path: str = "./output/share_card_dark.png",
    dpi: int = 200,
):
    """深色主题版分享卡片"""
    BG = "#0d1117"
    ACCENT = "#58a6ff"
    GREEN = "#3fb950"
    RED = "#f85149"
    DARK_BAR = "#161b22"
    CARD_BG = "#21262d"
    CARD_BORDER = "#30363d"
    TEXT = "#c9d1d9"
    MUTED = "#8b949e"

    fig = plt.figure(figsize=(6, 8), facecolor=BG)

    ann_ret = metrics.get("annual_return", 0)
    mdd_val = metrics.get("max_drawdown", 0)
    shp_val = metrics.get("sharpe", 0)
    tot_ret = metrics.get("total_return", 0)
    bench_ann = metrics.get("bench_annual")
    bench_tot = metrics.get("bench_total", 0)
    n_days = metrics.get("n_days", 0)
    yrs = n_days / 252

    # 标题
    fig.text(0.5, 0.97, strategy_name, fontsize=24, fontweight="bold", color=TEXT, ha="center", va="top")
    fig.text(0.5, 0.93, period, fontsize=11, color=MUTED, ha="center", va="top")

    # Hero
    hero_color = GREEN if tot_ret > 0 else RED
    fig.text(0.5, 0.86, f"{tot_ret*100:+.1f}%", fontsize=54, fontweight="bold",
             color=hero_color, ha="center", va="center")
    fig.text(0.5, 0.81, "Total Return", fontsize=12, color=MUTED, ha="center", va="center")
    if bench_ann is not None:
        fig.text(0.5, 0.78, f"Ann. {ann_ret*100:+.1f}%  vs  {benchmark_label} {bench_ann*100:+.1f}%",
                 fontsize=10, color=MUTED, ha="center", va="center")

    # 三列 KPI
    card_y, card_h, card_w = 0.65, 0.08, 0.28
    xs = [0.06, 0.38, 0.70]
    kpis = [
        ("Sharpe", f"{shp_val:.2f}", ACCENT),
        ("Max DD", f"{mdd_val*100:.1f}%", RED),
        ("Win Rate", f"{metrics.get('win_rate',0)*100:.0f}%", ACCENT),
    ]
    for (label, value, color), x in zip(kpis, xs):
        rect = mpatches.FancyBboxPatch(
            (x, card_y), card_w, card_h, boxstyle="round,pad=0.02",
            facecolor=CARD_BG, edgecolor=CARD_BORDER, linewidth=1.2,
            transform=fig.transFigure, zorder=0,
        )
        fig.patches.append(rect)
        fig.text(x + card_w/2, card_y + card_h - 0.012, label,
                 fontsize=8, color=MUTED, ha="center", va="top")
        fig.text(x + card_w/2, card_y + card_h/2 - 0.008, value,
                 fontsize=18, fontweight="bold", color=color, ha="center", va="center")

    # NAV 图
    nav_ratio = nav / nav.iloc[0]
    ax_chart = fig.add_axes([0.08, 0.22, 0.84, 0.37])
    ax_chart.fill_between(nav.index, nav_ratio, 1, where=nav_ratio >= 1,
                          alpha=0.15, color=GREEN)
    ax_chart.fill_between(nav.index, nav_ratio, 1, where=nav_ratio < 1,
                          alpha=0.08, color=RED)
    ax_chart.plot(nav.index, nav_ratio, color=ACCENT, linewidth=2.2)
    ax_chart.axhline(y=1, color=MUTED, linewidth=0.6, linestyle="--", alpha=0.3)
    ax_chart.set_facecolor(BG)
    for s in ["top", "right"]: ax_chart.spines[s].set_visible(False)
    ax_chart.spines["left"].set_color(MUTED); ax_chart.spines["left"].set_alpha(0.3)
    ax_chart.spines["bottom"].set_color(MUTED); ax_chart.spines["bottom"].set_alpha(0.3)
    ax_chart.tick_params(colors=MUTED, labelsize=7)
    ax_chart.set_ylabel("NAV", color=MUTED, fontsize=8)
    ax_chart.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.1f}x"))
    ax_chart.annotate(f"×{nav_ratio.iloc[-1]:.1f}", xy=(nav.index[-1], nav_ratio.iloc[-1]),
                      xytext=(6, 6), textcoords="offset points", fontsize=9,
                      color=hero_color, ha="left", fontweight="bold")

    # 底部对比条
    bar_y = 0.04
    rect = mpatches.FancyBboxPatch(
        (0.06, bar_y), 0.88, 0.12, boxstyle="round,pad=0.02",
        facecolor=DARK_BAR, edgecolor=CARD_BORDER, linewidth=1,
        transform=fig.transFigure, zorder=0,
    )
    fig.patches.append(rect)

    label_x, bar_x0, bar_total_w, bar_h = 0.12, 0.22, 0.45, 0.016
    gap = 0.025
    top_y = bar_y + 0.082
    bot_y = top_y - gap

    fig.text(label_x, top_y, f"{benchmark_label}", fontsize=9,
             color=MUTED, ha="left", va="center", fontweight="bold")
    fig.text(label_x, bot_y, "Strategy", fontsize=9,
             color=GREEN, ha="left", va="center", fontweight="bold")

    bench_ratio = min(1.0, abs((1+bench_tot)/(1+tot_ret))) if tot_ret != 0 else 1.0
    bench_width = bar_total_w * bench_ratio
    ax_bb = fig.add_axes([bar_x0, top_y - bar_h/2, bar_total_w, bar_h])
    ax_bb.barh(0, bench_width, color="#484f58", height=0.8)
    ax_bb.set_xlim(0, 1); ax_bb.axis("off")
    pct_x = bar_x0 + bar_total_w + 0.03
    fig.text(pct_x, top_y, f"{bench_tot*100:+.1f}%",
             fontsize=10, color=MUTED, va="center", ha="left", fontweight="bold")

    ax_sb = fig.add_axes([bar_x0, bot_y - bar_h/2, bar_total_w, bar_h])
    ax_sb.barh(0, 1.0, color=GREEN, height=0.8)
    ax_sb.set_xlim(0, 1); ax_sb.axis("off")
    fig.text(pct_x, bot_y, f"{tot_ret*100:+.1f}%",
             fontsize=11, color=GREEN, va="center", ha="left", fontweight="bold")

    fig.text(0.5, bar_y + 0.015, f"{n_days} trading days · ~{yrs:.1f} years · for reference only",
             fontsize=7, color=MUTED, ha="center", va="center")

    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, dpi=dpi, facecolor=BG, edgecolor="none", pad_inches=0.3)
    plt.close(fig)
    return save_path
