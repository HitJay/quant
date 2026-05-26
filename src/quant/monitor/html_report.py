"""可视化模块 — 精美交互式 HTML 报告 (Plotly dark theme)"""

import pandas as pd
import numpy as np
from pathlib import Path


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
    "purple":   "#bc8cff",
}


def report_html(
    nav: pd.Series,
    metrics: dict,
    benchmark: pd.Series | None = None,
    benchmark_label: str = "Benchmark",
    title: str = "Backtest Report",
    save_path: str = "./output/report.html",
) -> str:
    """生成精美交互式 HTML 回测报告（暗色主题 + KPI + 多图）"""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    # ---- 数据准备 ----
    nav_ratio = nav / nav.iloc[0]
    nav_pct = (nav_ratio - 1) * 100
    peak = nav.expanding().max()
    dd = (nav - peak) / peak * 100
    daily_ret = nav.pct_change().dropna()
    monthly_ret = nav.resample("ME").last().pct_change().dropna()
    monthly_matrix = _monthly_heatmap_data(monthly_ret)
    annual_ret = nav.resample("YE").last().pct_change().dropna()
    rolling_1y = nav.pct_change(252).dropna() * 100
    MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    # 基准
    bench_ratio = bench_pct = bench_annual_ret = bench_nav = None
    if benchmark is not None:
        bench_nav = benchmark.reindex(nav.index).ffill().dropna()
        bench_ratio = bench_nav / bench_nav.iloc[0]
        bench_pct = (bench_ratio - 1) * 100
        bench_annual_ret = bench_nav.resample("YE").last().pct_change().dropna()

    # ---- KPI 数据 ----
    ann_ret = metrics.get("annual_return", 0)
    mdd_val = metrics.get("max_drawdown", 0)
    shp_val = metrics.get("sharpe", 0)
    tot_ret = metrics.get("total_return", 0)

    # ---- 构建图表 ----
    fig = make_subplots(
        rows=5, cols=4,
        row_heights=[0.10, 0.28, 0.22, 0.22, 0.18],
        column_widths=[0.25, 0.25, 0.25, 0.25],
        vertical_spacing=0.06,
        horizontal_spacing=0.04,
        specs=[
            [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
            [{"type": "xy", "colspan": 4}, None, None, None],
            [{"type": "xy", "colspan": 2}, None, {"type": "xy", "colspan": 2}, None],
            [{"type": "heatmap", "colspan": 2}, None, {"type": "table", "colspan": 2}, None],
            [{"type": "xy", "colspan": 4}, None, None, None],
        ],
    )

    # ---- Row 0: KPI 仪表盘 ----
    fig.add_trace(go.Indicator(
        mode="number", value=ann_ret*100,
        number=dict(suffix="%", font=dict(size=36, color=C["green"] if ann_ret>0 else C["red"])),
        title=dict(text="<b>Ann.Return</b>", font=dict(size=13, color=C["muted"])),
        domain=dict(row=0, column=0),
    ), row=1, col=1)
    fig.add_trace(go.Indicator(
        mode="number", value=mdd_val*100,
        number=dict(suffix="%", font=dict(size=36, color=C["red"])),
        title=dict(text="<b>Max DD</b>", font=dict(size=13, color=C["muted"])),
        domain=dict(row=0, column=0),
    ), row=1, col=2)
    fig.add_trace(go.Indicator(
        mode="number", value=shp_val,
        number=dict(font=dict(size=36, color=C["blue"])),
        title=dict(text="<b>Sharpe</b>", font=dict(size=13, color=C["muted"])),
        domain=dict(row=0, column=0),
    ), row=1, col=3)
    fig.add_trace(go.Indicator(
        mode="number", value=tot_ret*100,
        number=dict(suffix="%", font=dict(size=36, color=C["green"] if tot_ret>0 else C["red"])),
        title=dict(text="<b>Total Return</b>", font=dict(size=13, color=C["muted"])),
        domain=dict(row=0, column=0),
    ), row=1, col=4)

    # ---- Row 1: 净值对比 ----
    fig.add_trace(go.Scatter(
        x=nav.index, y=nav_ratio, mode="lines", name="Strategy",
        line=dict(color=C["blue"], width=2.5),
        hovertemplate="Strategy: %{customdata:+.1f}%<extra></extra>",
        customdata=nav_pct,
    ), row=2, col=1)
    if benchmark is not None:
        fig.add_trace(go.Scatter(
            x=bench_nav.index, y=bench_ratio, mode="lines",
            name=benchmark_label, line=dict(color=C["muted"], width=1.5, dash="dot"),
            hovertemplate=f"{benchmark_label}: %{{customdata:+.1f}}%<extra></extra>",
            customdata=bench_pct,
        ), row=2, col=1)

    # ---- Row 2: 回撤 (左) + 年度收益柱状图 (右) ----
    fig.add_trace(go.Scatter(
        x=dd.index, y=dd, mode="lines", name="Drawdown",
        fill="tozeroy", fillcolor=f"rgba(248,81,73,0.15)",
        line=dict(color=C["red"], width=1.2),
        hovertemplate="DD: %{y:.1f}%<extra></extra>",
    ), row=3, col=1)
    fig.add_shape(type="line", x0=dd.index[0], x1=dd.index[-1],
                  y0=dd.min(), y1=dd.min(), line=dict(dash="dot", color=C["red"]),
                  row=3, col=1)
    fig.add_annotation(x=dd.index[0], y=dd.min() + 2, text=f"Max DD: {dd.min():.1f}%",
                       showarrow=False, font=dict(color=C["orange"], size=12, family="monospace"),
                       xanchor="left", yanchor="bottom", row=3, col=1)

    # 年度收益柱状图
    years_str = [str(d.year) for d in annual_ret.index]
    fig.add_trace(go.Bar(
        x=years_str, y=annual_ret.values * 100, name="Strategy",
        marker=dict(color=[C["green"] if v>0 else C["red"] for v in annual_ret.values]),
        hovertemplate="%{y:+.1f}%<extra></extra>",
        text=[f"{v*100:+.1f}%" for v in annual_ret.values],
        textposition="outside", textfont=dict(size=10),
    ), row=3, col=3)

    # ---- Row 3: 月度热力图 (左) + 绩效表 (右) ----
    if monthly_matrix is not None:
        yrs = list(monthly_matrix.keys())
        z_data = []
        for y in yrs:
            row_data = []
            for i in range(12):
                v = monthly_matrix[y].get(i, None)
                row_data.append(v if v is not None else np.nan)
            z_data.append(row_data)
        fig.add_trace(go.Heatmap(
            z=z_data, x=MONTHS, y=[str(y) for y in yrs],
            colorscale=[[0, C["red"]], [0.5, C["card"]], [1, C["green"]]],
            zmid=0, zmin=-0.10, zmax=0.10,
            text=[[f"{v*100:+.1f}%" if not np.isnan(v) else "" for v in row] for row in z_data],
            texttemplate="%{text}", textfont=dict(size=9),
            showscale=False, hoverongaps=False,
        ), row=4, col=1)

    # 绩效表
    header = ["<b>Metric</b>", "<b>Strategy</b>"]
    bench_col = None
    if benchmark is not None:
        header.append(f"<b>{benchmark_label}</b>")
        b_ann = _calc_annual_return(bench_nav)
        b_mdd = _calc_max_dd(bench_nav)
        b_shp = _calc_sharpe(bench_nav)
        b_tot = bench_nav.iloc[-1]/bench_nav.iloc[0]-1
        b_wr = _calc_win_rate(bench_nav)
        bench_col = [
            f"{b_ann*100:+.1f}%", f"{b_mdd*100:.1f}%", f"{b_shp:.2f}",
            f"{b_ann/b_mdd:.2f}" if b_mdd>0 else "-", f"{b_wr*100:.1f}%",
            f"{b_tot*100:+.1f}%", str(len(bench_nav)),
        ]

    strat_cols = [
        f"{metrics.get('annual_return',0)*100:+.1f}%",
        f"{metrics.get('max_drawdown',0)*100:.1f}%",
        f"{metrics.get('sharpe',0):.2f}",
        f"{metrics.get('calmar',0):.2f}",
        f"{metrics.get('win_rate',0)*100:.1f}%",
        f"{metrics.get('total_return',0)*100:+.1f}%",
        f"{metrics.get('n_days',0)}",
    ]
    cells_vals = [
        ["Annual Return", "Max Drawdown", "Sharpe", "Calmar", "Win Rate", "Total Return", "Trading Days"],
        strat_cols,
    ]
    if bench_col:
        cells_vals.append(bench_col)

    fig.add_trace(go.Table(
        header=dict(values=header, fill_color=C["card"], font=dict(color=C["text"], size=12),
                     line=dict(color=C["border"])),
        cells=dict(
            values=cells_vals,
            fill_color=C["bg"],
            font=dict(color=C["text"], size=11),
            line=dict(color=C["border"]),
            align="left",
        ),
    ), row=4, col=3)

    # ---- Row 4: 滚动1年收益 (比值+log刻度) ----
    roll_ratio = (rolling_1y / 100) + 1   # +300% → 4.0, -50% → 0.5
    fig.add_trace(go.Scatter(
        x=rolling_1y.index, y=roll_ratio, mode="lines", name="Rolling 1Y Return",
        fill="tozeroy", fillcolor=f"rgba(88,166,255,0.08)",
        line=dict(color=C["blue"], width=1.2),
        hovertemplate="%{customdata:+.1f}%<extra></extra>",
        customdata=rolling_1y,
    ), row=5, col=1)
    fig.add_shape(type="line", x0=rolling_1y.index[0], x1=rolling_1y.index[-1],
                  y0=1, y1=1, line=dict(dash="solid", color=C["border"]), row=5, col=1)

    # ---- 全局样式 ----
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=C["bg"],
        plot_bgcolor=C["bg"],
        title=dict(text=f"<b>{title}</b>", font=dict(size=22, color=C["text"]), x=0.5, y=0.99),
        height=1400,
        showlegend=True,
        legend=dict(orientation="h", y=1.06, x=0.5, xanchor="center",
                     font=dict(color=C["text"], size=11)),
        margin=dict(l=40, r=40, t=120, b=40),
        hovermode="x unified",
        hoverlabel=dict(bgcolor=C["card"], font=dict(color=C["text"])),
    )

    # 各子图样式
    for r in range(2, 6):
        fig.update_xaxes(gridcolor=C["border"], zerolinecolor=C["border"], row=r, col=1)
        fig.update_yaxes(gridcolor=C["border"], zerolinecolor=C["border"], row=r, col=1)

    # Row1 Y轴 log + 百分比
    tick_vals = [0.3, 0.5, 1, 2, 5, 10, 20, 50]
    tick_labels = ["-70%", "-50%", "0%", "+100%", "+400%", "+900%", "+1900%", "+4900%"]
    fig.update_yaxes(type="log", tickvals=tick_vals, ticktext=tick_labels,
                      title_text="", row=2, col=1)
    fig.update_xaxes(title_text="", row=2, col=1)
    # 热力图：强制显示12个月
    fig.update_xaxes(tickmode="array", tickvals=list(range(12)), ticktext=MONTHS,
                     nticks=12, row=4, col=1)

    # 回撤子图
    fig.update_yaxes(title_text="DD %", ticksuffix="%", row=3, col=1)
    fig.update_xaxes(title_text="", row=3, col=1)

    # 年度收益
    fig.update_yaxes(title_text="Yearly Return", ticksuffix="%", row=3, col=3)
    fig.update_xaxes(title_text="", row=3, col=3)
    fig.add_shape(type="line", x0=-0.5, x1=len(years_str)-0.5, y0=0, y1=0,
                  line=dict(dash="solid", color=C["border"]), row=3, col=3)

    # 滚动收益 (log + 百分比标签)
    roll_tick_vals = [0.3, 0.5, 1, 2, 5]
    roll_tick_labels = ["-70%", "-50%", "0%", "+100%", "+400%"]
    fig.update_yaxes(title_text="Rolling 1Y", type="log", row=5, col=1,
                     tickvals=roll_tick_vals, ticktext=roll_tick_labels)
    fig.update_xaxes(title_text="", row=5, col=1)

    # 保存
    path = Path(save_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(path, include_plotlyjs="cdn", full_html=True)
    return str(path)


def _monthly_heatmap_data(monthly_ret: pd.Series) -> dict | None:
    if len(monthly_ret) == 0:
        return None
    data: dict[int, dict[int, float]] = {}
    for dt, ret in monthly_ret.items():
        y = dt.year
        m = dt.month - 1
        if y not in data:
            data[y] = {}
        data[y][m] = float(ret)
    return data


def _calc_annual_return(nav: pd.Series) -> float:
    years = (nav.index[-1] - nav.index[0]).days / 365.25
    total = nav.iloc[-1] / nav.iloc[0] - 1
    return float((1 + total) ** (1 / years) - 1) if years > 0.01 else 0.0


def _calc_max_dd(nav: pd.Series) -> float:
    return float(abs(((nav - nav.expanding().max()) / nav.expanding().max()).min()))


def _calc_sharpe(nav: pd.Series, risk_free: float = 0.02) -> float:
    daily = nav.pct_change().dropna()
    if len(daily) < 2 or daily.std() == 0:
        return 0.0
    return float((daily.mean()*252 - risk_free) / (daily.std()*np.sqrt(252)))


def _calc_win_rate(nav: pd.Series) -> float:
    monthly = nav.resample("ME").last().pct_change().dropna()
    return float((monthly > 0).sum() / len(monthly)) if len(monthly) > 0 else 0.0
