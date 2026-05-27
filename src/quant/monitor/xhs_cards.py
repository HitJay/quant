"""小红书卡片生成器 — matplotlib版，拆分报告为多张3:4竖屏PNG"""

import pandas as pd
import numpy as np
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.patches import FancyBboxPatch


# 主题色
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
}

# 小红书 3:4 竖屏 (inch at 150dpi → 1080x1440)
CARD_W = 7.2
CARD_H = 9.6
DPI = 150


def generate_xhs_cards(
    nav: pd.Series,
    metrics: dict,
    benchmark: pd.Series | None = None,
    benchmark_label: str = "Benchmark",
    title: str = "Strategy",
    save_dir: str = "./output/xhs_cards",
    subtitle: str = "",
) -> list[str]:
    """生成多张小红书卡片，返回文件路径列表"""
    
    nav_ratio = nav / nav.iloc[0]
    nav_pct = (nav_ratio - 1) * 100
    peak = nav.expanding().max()
    dd = (nav - peak) / peak * 100
    monthly_ret = nav.resample("ME").last().pct_change().dropna()
    monthly_matrix = _monthly_heatmap_data(monthly_ret)
    annual_ret = nav.resample("YE").last().pct_change().dropna()
    rolling_1y = nav.pct_change(252).dropna() * 100
    
    bench_nav = bench_ratio = None
    if benchmark is not None:
        bench_nav = benchmark.reindex(nav.index).ffill().dropna()
        bench_ratio = bench_nav / bench_nav.iloc[0]
    
    save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)
    
    cards = []
    cards.append(_card_cover(title, subtitle, metrics, nav_ratio, save_path))
    cards.append(_card_kpi_nav(nav_ratio, nav_pct, metrics, bench_ratio,
                                benchmark_label, title, save_path))
    cards.append(_card_drawdown(dd, metrics, title, save_path))
    cards.append(_card_annual(annual_ret, bench_nav, benchmark_label, title, save_path))
    if monthly_matrix is not None:
        cards.append(_card_heatmap(monthly_matrix, title, save_path))
    cards.append(_card_rolling(rolling_1y, title, save_path))
    cards.append(_card_table(metrics, bench_nav, benchmark_label, title, save_path))
    
    return cards


def _setup_fig():
    fig, ax = plt.subplots(figsize=(CARD_W, CARD_H), facecolor=C["bg"])
    ax.set_facecolor(C["bg"])
    return fig, ax


def _style_ax(ax):
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]:
        ax.spines[s].set_color(C["border"])
        ax.spines[s].set_linewidth(0.8)
    ax.tick_params(colors=C["muted"], labelsize=9)
    ax.grid(True, color=C["border"], linewidth=0.3, alpha=0.5)


def _card_cover(title, subtitle, metrics, nav_ratio, save_path):
    """Card 0: Cover / Hero card for Xiaohongshu feed"""
    fig, ax = _setup_fig()
    ax.set_position([0, 0, 1, 1])
    ax.axis("off")
    
    # 背景渐变效果（用多层矩形模拟）
    for i in range(20):
        alpha = 0.03 + i * 0.005
        y = 1 - i * 0.05
        ax.axhspan(y - 0.05, y, color=C["blue"], alpha=alpha, zorder=0)
    
    # 策略标题（大字）
    ax.text(0.5, 0.82, title,
            ha="center", va="center", fontsize=42, fontweight="bold",
            color=C["text"], transform=ax.transAxes, zorder=10)
    
    # 副标题（如果有）
    if subtitle:
        ax.text(0.5, 0.76, subtitle,
                ha="center", va="center", fontsize=16, color=C["muted"],
                transform=ax.transAxes, zorder=10)
    
    # 核心KPI：总收益（超大字）
    tot_ret = metrics.get("total_return", 0)
    ret_color = C["green"] if tot_ret > 0 else C["red"]
    ax.text(0.5, 0.60, f"{tot_ret*100:+.1f}%",
            ha="center", va="center", fontsize=72, fontweight="bold",
            color=ret_color, fontfamily="monospace", transform=ax.transAxes, zorder=10)
    
    ax.text(0.5, 0.52, "TOTAL RETURN",
            ha="center", va="center", fontsize=18, color=C["muted"],
            fontweight="bold", transform=ax.transAxes, zorder=10)
    
    # 次级KPI：年化 + 夏普
    ann_ret = metrics.get("annual_return", 0)
    shp_val = metrics.get("sharpe", 0)
    
    ax.text(0.30, 0.40, f"Ann. {ann_ret*100:+.1f}%",
            ha="center", va="center", fontsize=28, fontweight="bold",
            color=C["green"] if ann_ret > 0 else C["red"],
            fontfamily="monospace", transform=ax.transAxes, zorder=10)
    ax.text(0.30, 0.36, "ANNUAL RETURN",
            ha="center", va="center", fontsize=11, color=C["muted"],
            fontweight="bold", transform=ax.transAxes, zorder=10)
    
    ax.text(0.70, 0.40, f"{shp_val:.2f}",
            ha="center", va="center", fontsize=28, fontweight="bold",
            color=C["blue"], fontfamily="monospace", transform=ax.transAxes, zorder=10)
    ax.text(0.70, 0.36, "SHARPE RATIO",
            ha="center", va="center", fontsize=11, color=C["muted"],
            fontweight="bold", transform=ax.transAxes, zorder=10)
    
    # 底部NAV迷你曲线
    ax_nav = fig.add_axes([0.1, 0.05, 0.8, 0.22])
    ax_nav.set_facecolor(C["bg"])
    ax_nav.plot(nav_ratio.index, nav_ratio, color=C["blue"], linewidth=2.5, zorder=5)
    ax_nav.fill_between(nav_ratio.index, nav_ratio, nav_ratio.iloc[0],
                        where=nav_ratio >= nav_ratio.iloc[0], alpha=0.15, color=C["green"])
    ax_nav.fill_between(nav_ratio.index, nav_ratio, nav_ratio.iloc[0],
                        where=nav_ratio < nav_ratio.iloc[0], alpha=0.1, color=C["red"])
    
    # 清理坐标轴
    for s in ax_nav.spines.values():
        s.set_visible(False)
    ax_nav.set_xticks([])
    ax_nav.set_yticks([])
    
    out = save_path / "00_cover.png"
    fig.savefig(str(out), dpi=DPI, facecolor=C["bg"], bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    return str(out)


def _card_kpi_nav(nav_ratio, nav_pct, metrics, bench_ratio,
                   benchmark_label, title, save_path):
    """Card 1: KPI + NAV"""
    fig, ax = _setup_fig()
    
    # KPI区域 (顶部 15%)
    ann_ret = metrics.get("annual_return", 0)
    mdd_val = metrics.get("max_drawdown", 0)
    shp_val = metrics.get("sharpe", 0)
    tot_ret = metrics.get("total_return", 0)
    
    kpis = [
        ("ANN. RETURN", f"{ann_ret*100:+.1f}%", C["green"] if ann_ret > 0 else C["red"]),
        ("MAX DD", f"{mdd_val*100:.1f}%", C["red"]),
        ("SHARPE", f"{shp_val:.2f}", C["blue"]),
        ("TOTAL RETURN", f"{tot_ret*100:+.1f}%", C["green"] if tot_ret > 0 else C["red"]),
    ]
    
    for i, (label, value, color) in enumerate(kpis):
        x = 0.125 + i * 0.25
        fig.text(x, 0.94, label, ha="center", va="center",
                 fontsize=8, color=C["muted"], fontweight="bold")
        fig.text(x, 0.90, value, ha="center", va="center",
                 fontsize=22, color=color, fontweight="bold", fontfamily="monospace")
    
    # 标题
    fig.text(0.5, 0.98, title, ha="center", va="center",
             fontsize=20, color=C["text"], fontweight="bold")
    
    # 分隔线
    ax.axhline(y=nav_ratio.min(), color=C["border"], linewidth=0)  # dummy
    ax.set_position([0.12, 0.08, 0.82, 0.78])
    
    # NAV曲线
    ax.plot(nav_ratio.index, nav_ratio, color=C["blue"], linewidth=2.2, label="Strategy", zorder=5)
    ax.fill_between(nav_ratio.index, nav_ratio, 1,
                     where=nav_ratio >= 1, alpha=0.12, color=C["green"])
    ax.fill_between(nav_ratio.index, nav_ratio, 1,
                     where=nav_ratio < 1, alpha=0.08, color=C["red"])
    
    if bench_ratio is not None:
        ax.plot(bench_ratio.index, bench_ratio, color=C["muted"], linewidth=1.2,
                linestyle="--", alpha=0.7, label=benchmark_label)
    
    ax.axhline(y=1, color=C["border"], linewidth=0.8, linestyle="--", alpha=0.5)
    
    # 自适应Y轴
    y_lo, y_hi, y_ticks, y_labels = _adaptive_yticks(nav_ratio, bench_ratio)
    ax.set_yscale("log")
    ax.set_ylim(y_lo, y_hi)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels, fontsize=9, color=C["muted"])
    
    _style_ax(ax)
    leg = ax.legend(loc="upper left", fontsize=9, framealpha=0.7,
                    edgecolor=C["border"], facecolor=C["card"])
    for t in leg.get_texts():
        t.set_color(C["text"])
    
    out = save_path / "01_kpi_nav.png"
    fig.savefig(str(out), dpi=DPI, facecolor=C["bg"], bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    return str(out)


def _card_drawdown(dd, metrics, title, save_path):
    """Card 2: 回撤"""
    fig, ax = _setup_fig()
    ax.set_position([0.12, 0.08, 0.82, 0.78])
    
    fig.text(0.5, 0.97, title, ha="center", fontsize=20, color=C["text"], fontweight="bold")
    fig.text(0.5, 0.94, "Drawdown", ha="center", fontsize=14, color=C["muted"])
    
    ax.fill_between(dd.index, dd, 0, color=C["red"], alpha=0.2)
    ax.plot(dd.index, dd, color=C["red"], linewidth=1.5)
    ax.axhline(y=dd.min(), color=C["red"], linewidth=1, linestyle=":", alpha=0.6)
    
    # Max DD标注
    min_idx = dd.idxmin()
    ax.annotate(f"Max DD: {dd.min():.1f}%",
                xy=(min_idx, dd.min()), xytext=(0.05, 0.3),
                textcoords="axes fraction",
                fontsize=14, color=C["orange"], fontweight="bold", fontfamily="monospace",
                arrowprops=dict(arrowstyle="->", color=C["orange"], lw=1.5))
    
    ax.set_ylabel("Drawdown %", fontsize=11, color=C["muted"])
    _style_ax(ax)
    
    out = save_path / "02_drawdown.png"
    fig.savefig(str(out), dpi=DPI, facecolor=C["bg"], bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    return str(out)


def _card_annual(annual_ret, bench_nav, benchmark_label, title, save_path):
    """Card 3: 年度收益"""
    fig, ax = _setup_fig()
    ax.set_position([0.12, 0.08, 0.82, 0.78])
    
    fig.text(0.5, 0.97, title, ha="center", fontsize=20, color=C["text"], fontweight="bold")
    fig.text(0.5, 0.94, "Annual Returns", ha="center", fontsize=14, color=C["muted"])
    
    years = [str(d.year) for d in annual_ret.index]
    vals = annual_ret.values * 100
    colors = [C["green"] if v > 0 else C["red"] for v in vals]
    
    x = np.arange(len(years))
    width = 0.35 if bench_nav is not None else 0.6
    
    bars = ax.bar(x - width/2 if bench_nav is not None else x, vals, width,
                  color=colors, alpha=0.9, label="Strategy", zorder=5)
    
    # 数值标签
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (1 if v >= 0 else -3),
                f"{v:+.1f}%", ha="center", va="bottom" if v >= 0 else "top",
                fontsize=9, color=C["text"], fontweight="bold")
    
    # 基准
    if bench_nav is not None:
        bench_annual = bench_nav.resample("YE").last().pct_change().dropna()
        if len(bench_annual) > 0:
            bench_years = [str(d.year) for d in bench_annual.index]
            bench_vals = bench_annual.values * 100
            # 对齐年份
            common_idx = []
            bench_vals_aligned = []
            for i, y in enumerate(years):
                if y in bench_years:
                    bi = bench_years.index(y)
                    common_idx.append(i)
                    bench_vals_aligned.append(bench_vals[bi])
            if common_idx:
                bx = np.array([x[i] for i in common_idx]) + width/2
                ax.bar(bx, bench_vals_aligned, width, color=C["muted"],
                       alpha=0.5, label=benchmark_label, zorder=4)
    
    ax.axhline(y=0, color=C["border"], linewidth=1, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(years, fontsize=10, color=C["muted"])
    ax.set_ylabel("Return %", fontsize=11, color=C["muted"])
    _style_ax(ax)
    
    leg = ax.legend(loc="upper left", fontsize=10, framealpha=0.7,
                    edgecolor=C["border"], facecolor=C["card"])
    for t in leg.get_texts():
        t.set_color(C["text"])
    
    out = save_path / "03_annual.png"
    fig.savefig(str(out), dpi=DPI, facecolor=C["bg"], bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    return str(out)


def _card_heatmap(monthly_matrix, title, save_path):
    """Card 4: 月度热力图"""
    MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    fig, ax = _setup_fig()
    ax.set_position([0.10, 0.08, 0.85, 0.78])
    
    fig.text(0.5, 0.97, title, ha="center", fontsize=20, color=C["text"], fontweight="bold")
    fig.text(0.5, 0.94, "Monthly Returns", ha="center", fontsize=14, color=C["muted"])
    
    yrs = sorted(monthly_matrix.keys(), reverse=True)
    z = np.full((len(yrs), 12), np.nan)
    for i, y in enumerate(yrs):
        for m in range(12):
            v = monthly_matrix[y].get(m, None)
            if v is not None:
                z[i, m] = v * 100
    
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("rg", [C["red"], C["card"], C["green"]])
    
    im = ax.imshow(z, cmap=cmap, aspect="auto", vmin=-10, vmax=10)
    
    ax.set_xticks(range(12))
    ax.set_xticklabels(MONTHS, fontsize=8, color=C["muted"])
    ax.set_yticks(range(len(yrs)))
    ax.set_yticklabels([str(y) for y in yrs], fontsize=10, color=C["muted"])
    
    # 数值
    for i in range(len(yrs)):
        for j in range(12):
            v = z[i, j]
            if not np.isnan(v):
                color = "white" if abs(v) > 5 else C["text"]
                ax.text(j, i, f"{v:+.1f}", ha="center", va="center",
                        fontsize=8, color=color, fontweight="bold")
    
    out = save_path / "04_heatmap.png"
    fig.savefig(str(out), dpi=DPI, facecolor=C["bg"], bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    return str(out)


def _card_rolling(rolling_1y, title, save_path):
    """Card 5: 滚动1年收益"""
    fig, ax = _setup_fig()
    ax.set_position([0.12, 0.08, 0.82, 0.78])
    
    fig.text(0.5, 0.97, title, ha="center", fontsize=20, color=C["text"], fontweight="bold")
    fig.text(0.5, 0.94, "Rolling 1Y Return", ha="center", fontsize=14, color=C["muted"])
    
    roll_ratio = (rolling_1y / 100) + 1
    ax.plot(rolling_1y.index, roll_ratio, color=C["blue"], linewidth=1.5)
    ax.fill_between(rolling_1y.index, roll_ratio, 1,
                     where=roll_ratio >= 1, alpha=0.1, color=C["green"])
    ax.fill_between(rolling_1y.index, roll_ratio, 1,
                     where=roll_ratio < 1, alpha=0.08, color=C["red"])
    ax.axhline(y=1, color=C["border"], linewidth=1, linestyle="-")
    
    ax.set_yscale("log")
    y_lo, y_hi, y_ticks, y_labels = _adaptive_yticks(roll_ratio, None)
    ax.set_ylim(y_lo, y_hi)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels, fontsize=9, color=C["muted"])
    
    ax.set_ylabel("Return (log scale)", fontsize=11, color=C["muted"])
    _style_ax(ax)
    
    out = save_path / "05_rolling.png"
    fig.savefig(str(out), dpi=DPI, facecolor=C["bg"], bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    return str(out)


def _card_table(metrics, bench_nav, benchmark_label, title, save_path):
    """Card 6: Visual performance comparison with aligned bars"""
    fig, ax = _setup_fig()
    ax.set_position([0.05, 0.05, 0.9, 0.85])
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 14)
    
    # Title
    fig.text(0.5, 0.97, title, ha="center", fontsize=20, color=C["text"], fontweight="bold")
    fig.text(0.5, 0.94, "Performance Summary", ha="center", fontsize=14, color=C["muted"])
    
    # 计算基准数据
    bench = {}
    if bench_nav is not None:
        b_ann = _calc_annual_return(bench_nav)
        b_mdd = _calc_max_dd(bench_nav)
        b_shp = _calc_sharpe(bench_nav)
        b_tot = bench_nav.iloc[-1] / bench_nav.iloc[0] - 1
        b_wr = _calc_win_rate(bench_nav)
        b_cal = b_ann / b_mdd if b_mdd > 0 else 0
        bench = {"ann": b_ann, "mdd": b_mdd, "shp": b_shp, "tot": b_tot, "wr": b_wr, "cal": b_cal}
    
    # 策略数据
    s_ann = metrics.get("annual_return", 0)
    s_mdd = metrics.get("max_drawdown", 0)
    s_shp = metrics.get("sharpe", 0)
    s_cal = metrics.get("calmar", 0)
    s_wr = metrics.get("win_rate", 0)
    s_tot = metrics.get("total_return", 0)
    
    # 每行数据：(label, strategy_text, benchmark_text, color, strategy_value, benchmark_value)
    rows_data = [
        ("ANNUAL RETURN", f"{s_ann*100:+.1f}%",
         f"{bench.get('ann',0)*100:+.1f}%" if bench else None,
         C["green"] if s_ann > 0 else C["red"],
         s_ann*100, bench.get("ann",0)*100 if bench else None),
        ("MAX DRAWDOWN", f"{s_mdd*100:.1f}%",
         f"{bench.get('mdd',0)*100:.1f}%" if bench else None,
         C["red"],
         -s_mdd*100, -bench.get("mdd",0)*100 if bench else None),
        ("SHARPE RATIO", f"{s_shp:.2f}",
         f"{bench.get('shp',0):.2f}" if bench else None,
         C["blue"],
         s_shp, bench.get("shp",0) if bench else None),
        ("CALMAR RATIO", f"{s_cal:.2f}" if s_cal else "-",
         f"{bench.get('cal',0):.2f}" if bench else None, C["blue"],
         s_cal if s_cal else 0, bench.get("cal",0) if bench else None),
        ("MONTHLY WIN RATE", f"{s_wr*100:.0f}%",
         f"{bench.get('wr',0)*100:.0f}%" if bench else None,
         C["green"],
         s_wr*100, bench.get("wr",0)*100 if bench else None),
        ("TOTAL RETURN", f"{s_tot*100:+.1f}%",
         f"{bench.get('tot',0)*100:+.1f}%" if bench else None,
         C["green"] if s_tot > 0 else C["red"],
         s_tot*100, bench.get("tot",0)*100 if bench else None),
    ]
    
    y_start = 12.5
    row_h = 1.8
    
    for i, (label, s_text, b_text, color, s_val, b_val) in enumerate(rows_data):
        y = y_start - i * row_h
        
        # 标签（固定x=0.3，上方）
        ax.text(0.3, y + 0.5, label, fontsize=9, color=C["muted"],
                fontweight="bold", fontfamily="monospace", va="center", ha="left")
        
        # 策略数值（固定x=0.3，下方，大字体）
        ax.text(0.3, y, s_text, fontsize=24, color=color,
                fontweight="bold", fontfamily="monospace", va="center", ha="left")
        
        # 对比条（垂直居中于y，从x=4.5开始）
        if b_text is not None and b_val is not None:
            bar_left = 4.5
            bar_width = 4.8
            bar_h = 0.3
            max_abs = max(abs(s_val), abs(b_val), 1)
            
            # 策略条（y + 0.2，上方）
            s_w = abs(s_val) / max_abs * bar_width
            ax.barh(y + 0.2, s_w, height=bar_h, left=bar_left,
                    color=color, alpha=0.85, zorder=5)
            ax.text(bar_left + s_w + 0.15, y + 0.2, "STRAT", fontsize=7,
                    color=color, fontweight="bold", va="center", ha="left")
            
            # 基准条（y - 0.2，下方）
            b_w = abs(b_val) / max_abs * bar_width
            ax.barh(y - 0.2, b_w, height=bar_h, left=bar_left,
                    color=C["muted"], alpha=0.45, zorder=5)
            ax.text(bar_left + b_w + 0.15, y - 0.2, benchmark_label[:10], fontsize=7,
                    color=C["muted"], va="center", ha="left")
    
    # Trading days
    n_days = metrics.get("n_days", 0)
    yrs = n_days / 252
    ax.text(5, 0.3, f"{n_days} trading days · ~{yrs:.1f} years",
            ha="center", fontsize=9, color=C["muted"], va="center")
    ax.text(5, -0.1, "for reference only · past performance ≠ future results",
            ha="center", fontsize=7, color=C["muted"], va="center", style="italic")
    
    out = save_path / "06_table.png"
    fig.savefig(str(out), dpi=DPI, facecolor=C["bg"], bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    return str(out)


# ---- 工具函数 ----

def _adaptive_yticks(nav_ratio, bench_ratio):
    """自适应log Y轴ticks"""
    all_vals = [nav_ratio.min(), nav_ratio.max()]
    if bench_ratio is not None:
        all_vals.extend([bench_ratio.min(), bench_ratio.max()])
    data_min = min(v for v in all_vals if v > 0)
    data_max = max(all_vals)
    
    candidates = [
        0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,
        1, 1.1, 1.2, 1.3, 1.5, 1.7, 2, 2.5, 3, 4, 5, 6, 7, 8, 10,
        12, 15, 20, 25, 30, 40, 50, 60, 70, 80, 100,
    ]
    
    pad_lo = data_min * 0.85
    pad_hi = data_max * 1.15 if data_max > 1 else max(data_max * 1.15, 1.1)
    pad_lo = max(0.05, pad_lo)
    pad_hi = min(200, pad_hi)
    
    in_range = [c for c in candidates if pad_lo <= c <= pad_hi]
    if 1.0 not in in_range and pad_lo <= 1.0 <= pad_hi:
        in_range.append(1.0)
        in_range.sort()
    if len(in_range) > 7:
        priority = [0.1, 0.2, 0.3, 0.5, 0.7, 1, 1.5, 2, 2.5, 3, 5, 7, 10, 15, 20, 30, 50, 70, 100]
        in_range = [c for c in in_range if c in priority][:7]
    if len(in_range) < 3:
        nice = sorted(candidates)
        lo = max([c for c in nice if c <= pad_lo] or [nice[0]])
        hi = min([c for c in nice if c >= pad_hi] or [nice[-1]])
        mid_candidates = [c for c in nice if lo < c < hi]
        mid = mid_candidates[len(mid_candidates)//2] if mid_candidates else (1.0 if lo < 1.0 < hi else (lo+hi)/2)
        in_range = sorted(set([lo, mid, hi]))
    
    y_lo = min(in_range) * 0.9
    y_hi = max(in_range) * 1.1
    
    labels = []
    for v in in_range:
        pct = (v - 1) * 100
        if abs(pct) < 0.5:
            labels.append("0%")
        else:
            labels.append(f"{pct:+.0f}%")
    
    return y_lo, y_hi, in_range, labels


def _monthly_heatmap_data(monthly_ret):
    if len(monthly_ret) == 0:
        return None
    data = {}
    for dt, ret in monthly_ret.items():
        y = dt.year
        m = dt.month - 1
        if y not in data:
            data[y] = {}
        data[y][m] = float(ret)
    return data


def _calc_annual_return(nav):
    years = (nav.index[-1] - nav.index[0]).days / 365.25
    total = nav.iloc[-1] / nav.iloc[0] - 1
    return float((1 + total) ** (1 / years) - 1) if years > 0.01 else 0.0


def _calc_max_dd(nav):
    return float(abs(((nav - nav.expanding().max()) / nav.expanding().max()).min()))


def _calc_sharpe(nav, risk_free=0.02):
    daily = nav.pct_change().dropna()
    if len(daily) < 2 or daily.std() == 0:
        return 0.0
    return float((daily.mean()*252 - risk_free) / (daily.std()*np.sqrt(252)))


def _calc_win_rate(nav):
    monthly = nav.resample("ME").last().pct_change().dropna()
    return float((monthly > 0).sum() / len(monthly)) if len(monthly) > 0 else 0.0
