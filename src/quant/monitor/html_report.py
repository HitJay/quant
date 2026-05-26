"""可视化模块 — 精美交互式 HTML 报告 (Plotly dark theme)"""

import pandas as pd
import numpy as np
from pathlib import Path

# 主题色
C = {
    "bg":       "#0d1117",  "card":     "#161b22",  "border":   "#30363d",
    "text":     "#c9d1d9",  "muted":    "#8b949e",  "blue":     "#58a6ff",
    "green":    "#3fb950",  "red":      "#f85149",  "orange":   "#d2991d",
    "purple":   "#bc8cff",
}


def report_html(
    nav: pd.Series,
    metrics: dict,
    benchmark: pd.Series | None = None,
    benchmark_label: str = "Benchmark",
    positions: pd.DataFrame | None = None,
    title: str = "Backtest Report",
    save_path: str = "./output/report.html",
) -> str:
    """生成精美交互式 HTML 回测报告"""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    # ---- 数据 ----
    nav_ratio = nav / nav.iloc[0]
    nav_pct = (nav_ratio - 1) * 100
    peak = nav.expanding().max()
    dd = (nav - peak) / peak * 100
    monthly_ret = nav.resample("ME").last().pct_change().dropna()
    monthly_matrix = _monthly_heatmap_data(monthly_ret)
    annual_ret = nav.resample("YE").last().pct_change().dropna()
    rolling_1y = nav.pct_change(252).dropna() * 100
    daily_ret = nav.pct_change().dropna()
    MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    # 基准
    bench_nav = bench_ratio = bench_pct = None
    if benchmark is not None:
        bench_nav = benchmark.reindex(nav.index).ffill().dropna()
        bench_ratio = bench_nav / bench_nav.iloc[0]
        bench_pct = (bench_ratio - 1) * 100

    # 滚动夏普 (1年窗口)
    roll_sharpe = daily_ret.rolling(252).apply(
        lambda x: (x.mean()*252 - 0.02) / (x.std()*np.sqrt(252)) if x.std()>0 else np.nan
    ).dropna()

    # KPI
    ann_ret = metrics.get("annual_return", 0)
    mdd_val = metrics.get("max_drawdown", 0)
    shp_val = metrics.get("sharpe", 0)
    tot_ret = metrics.get("total_return", 0)

    # 基准KPI
    b_ann = b_mdd = None
    if bench_nav is not None:
        b_ann = _calc_annual_return(bench_nav)
        b_mdd = _calc_max_dd(bench_nav)

    # ---- 构建图表 ----
    n_rows = 6 if positions is not None else 5
    fig = make_subplots(
        rows=n_rows, cols=4,
        row_heights=([0.10] + [0.26, 0.20, 0.08, 0.20, 0.16][:n_rows-1]) if positions is not None
                    else [0.10, 0.28, 0.22, 0.22, 0.18],
        column_widths=[0.25, 0.25, 0.25, 0.25],
        vertical_spacing=0.05, horizontal_spacing=0.04,
        specs=(
            [[{"type": "indicator"}]*4] +
            [[{"type": "xy", "colspan": 4}, None, None, None]] +
            [[{"type": "xy", "colspan": 2}, None, {"type": "xy", "colspan": 2}, None]] +
            ([[{"type": "xy", "colspan": 4}, None, None, None]] if positions is not None else []) +
            [[{"type": "heatmap", "colspan": 2}, None, {"type": "table", "colspan": 2}, None]] +
            [[{"type": "xy", "colspan": 4}, None, None, None]]
        ),
    )

    # ====== Row 0: KPI Cards ======
    _kpi(fig, 1, 1, "Ann.Return", f"{ann_ret*100:+.1f}%",
         C["green"] if ann_ret>0 else C["red"], delta=_kpi_delta(ann_ret, b_ann, "%"))
    _kpi(fig, 1, 2, "Max DD", f"{mdd_val*100:.1f}%",
         C["red"], delta=_kpi_delta(-mdd_val, -b_mdd, "%") if b_mdd else None)
    _kpi(fig, 1, 3, "Sharpe", f"{shp_val:.2f}",
         C["blue"], delta=None)
    _kpi(fig, 1, 4, "Total Return", f"{tot_ret*100:+.1f}%",
         C["green"] if tot_ret>0 else C["red"], delta=None)

    # ====== Row 1: NAV ======
    fig.add_trace(go.Scatter(
        x=nav.index, y=nav_ratio, mode="lines", name="Strategy",
        line=dict(color=C["blue"], width=2.5),
        hovertemplate="Strategy: %{customdata:+.1f}%<extra></extra>", customdata=nav_pct,
    ), row=2, col=1)
    if bench_ratio is not None:
        fig.add_trace(go.Scatter(
            x=bench_nav.index, y=bench_ratio, mode="lines", name=benchmark_label,
            line=dict(color=C["muted"], width=1.5, dash="dot"),
            hovertemplate=f"{benchmark_label}: %{{customdata:+.1f}}%<extra></extra>",
            customdata=bench_pct,
        ), row=2, col=1)

    # ====== Row 2: Drawdown + Annual Returns ======
    fig.add_trace(go.Scatter(
        x=dd.index, y=dd, mode="lines", name="Drawdown",
        fill="tozeroy", fillcolor=f"rgba(248,81,73,0.15)",
        line=dict(color=C["red"], width=1.2),
        hovertemplate="DD: %{y:.1f}%<extra></extra>",
    ), row=3, col=1)
    fig.add_shape(type="line", x0=dd.index[0], x1=dd.index[-1],
                  y0=dd.min(), y1=dd.min(), line=dict(dash="dot", color=C["red"]), row=3, col=1)
    fig.add_annotation(x=dd.index[-1], y=dd.min(), text=f"Max: {dd.min():.1f}%",
                       showarrow=False, font=dict(color=C["red"], size=11),
                       xanchor="right", row=3, col=1)

    years_str = [str(d.year) for d in annual_ret.index]
    fig.add_trace(go.Bar(
        x=years_str, y=annual_ret.values*100, name="Strategy",
        marker=dict(color=[C["green"] if v>0 else C["red"] for v in annual_ret.values]),
        hovertemplate="%{y:+.1f}%<extra></extra>",
        text=[f"{v*100:+.1f}%" for v in annual_ret.values],
        textposition="outside", textfont=dict(size=10),
    ), row=3, col=3)
    fig.add_shape(type="line", x0=-0.5, x1=len(years_str)-0.5, y0=0, y1=0,
                  line=dict(dash="solid", color=C["border"]), row=3, col=3)

    # ====== Row 3: 持仓时间线 (if positions) ======
    position_row = 4
    if positions is not None:
        pos_symbols = [c for c in positions.columns if c != "CASH"]
        colors = ["#58a6ff","#3fb950","#d2991d","#f85149","#bc8cff","#8b949e","#ff7b72"]
        for j, sym in enumerate(pos_symbols):
            # 找出持有该标的的区间
            held = positions[sym] > 0
            changes = held.astype(int).diff()
            starts = held.index[changes == 1]
            ends = held.index[changes == -1]
            if held.iloc[0]:
                starts = starts.insert(0, held.index[0])
            if held.iloc[-1]:
                ends = ends.append(pd.DatetimeIndex([held.index[-1]]))
            for s, e in zip(starts, ends):
                fig.add_trace(go.Scatter(
                    x=[s, e, e, s], y=[j, j, j+0.8, j+0.8],
                    fill="toself", mode="none",
                    fillcolor=colors[j % len(colors)],
                    opacity=0.7, name=sym,
                    showlegend=(s == starts[0]),
                    hoverinfo="skip",
                ), row=position_row, col=1)
        fig.update_yaxes(
            tickvals=[i+0.4 for i in range(len(pos_symbols))],
            ticktext=pos_symbols, row=position_row, col=1,
        )
        fig.update_xaxes(title_text="", row=position_row, col=1)

    # ====== Row 4: Heatmap + Table ======
    ht_row = position_row + 1 if positions is not None else 4
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
        ), row=ht_row, col=1)

    # 绩效表
    header = ["<b>Metric</b>", "<b>Strategy</b>"]
    bench_col = None
    if bench_nav is not None:
        header.append(f"<b>{benchmark_label}</b>")
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
        ["Annual Return","Max Drawdown","Sharpe","Calmar","Win Rate","Total Return","Trading Days"],
        strat_cols,
    ]
    if bench_col:
        cells_vals.append(bench_col)
    fig.add_trace(go.Table(
        header=dict(values=header, fill_color=C["card"], font=dict(color=C["text"], size=12),
                     line=dict(color=C["border"])),
        cells=dict(values=cells_vals, fill_color=C["bg"], font=dict(color=C["text"], size=11),
                    line=dict(color=C["border"]), align="left"),
    ), row=ht_row, col=3)

    # ====== Row 5: Rolling 1Y + Sharpe ======
    rr_row = ht_row + 1
    roll_ratio = (rolling_1y / 100) + 1
    fig.add_trace(go.Scatter(
        x=rolling_1y.index, y=roll_ratio, mode="lines", name="Rolling 1Y Return",
        fill="tozeroy", fillcolor=f"rgba(88,166,255,0.08)",
        line=dict(color=C["blue"], width=1.2),
        hovertemplate="%{customdata:+.1f}%<extra></extra>", customdata=rolling_1y,
    ), row=rr_row, col=1)
    fig.add_shape(type="line", x0=rolling_1y.index[0], x1=rolling_1y.index[-1],
                  y0=1, y1=1, line=dict(dash="solid", color=C["border"]), row=rr_row, col=1)

    # 滚动夏普 (双Y轴)
    fig.add_trace(go.Scatter(
        x=roll_sharpe.index, y=roll_sharpe, mode="lines", name="Rolling Sharpe",
        line=dict(color=C["orange"], width=1, dash="dot"),
        hovertemplate="Sharpe: %{y:.2f}<extra></extra>",
        yaxis="y2",
    ), row=rr_row, col=1)

    # ====== 全局样式 ======
    fig.update_layout(
        template="plotly_dark", paper_bgcolor=C["bg"], plot_bgcolor=C["bg"],
        title=dict(text=f"<b>{title}</b>", font=dict(size=22, color=C["text"]), x=0.5, y=0.99),
        height=1600 if positions is not None else 1400,
        showlegend=True,
        legend=dict(orientation="h", y=1.06, x=0.5, xanchor="center",
                     font=dict(color=C["text"], size=11)),
        margin=dict(l=40, r=40, t=120, b=40),
        hovermode="x unified",
        hoverlabel=dict(bgcolor=C["card"], font=dict(color=C["text"])),
        # 双Y轴
        yaxis2=dict(overlaying="y", side="right", title=dict(text="Sharpe", font=dict(color=C["orange"])),
                     tickfont=dict(color=C["orange"]), gridcolor=C["border"]),
    )

    for r in range(2, n_rows+1):
        fig.update_xaxes(gridcolor=C["border"], zerolinecolor=C["border"], row=r, col=1)
        fig.update_yaxes(gridcolor=C["border"], zerolinecolor=C["border"], row=r, col=1)

    # NAV Y轴
    fig.update_yaxes(type="log", tickvals=[0.3,0.5,1,2,5,10,20,50],
                      ticktext=["-70%","-50%","0%","+100%","+400%","+900%","+1900%","+4900%"],
                      title_text="", row=2, col=1)
    fig.update_xaxes(title_text="", row=2, col=1)
    # 回撤
    fig.update_yaxes(title_text="DD %", ticksuffix="%", row=3, col=1)
    fig.update_xaxes(title_text="", row=3, col=1)
    # 年度收益
    fig.update_yaxes(title_text="Yearly Return", ticksuffix="%", row=3, col=3)
    fig.update_xaxes(title_text="", row=3, col=3)
    # 热力图
    fig.update_xaxes(tickmode="array", tickvals=list(range(12)), ticktext=MONTHS,
                     nticks=12, row=ht_row, col=1)
    # 滚动收益
    fig.update_yaxes(title_text="Rolling 1Y", type="log", row=rr_row, col=1,
                     tickvals=[0.3,0.5,1,2,5], ticktext=["-70%","-50%","0%","+100%","+400%"])
    fig.update_xaxes(title_text="", row=rr_row, col=1)

    # 保存
    path = Path(save_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(path, include_plotlyjs="cdn", full_html=True)
    return str(path)


def _kpi(fig, row, col, label, value, color, delta=None):
    """添加KPI卡片"""
    import plotly.graph_objects as go
    title_text = f"<b>{label}</b>"
    if delta:
        title_text += f"  <span style='color:{C['muted']};font-size:11px'>({delta})</span>"
    v_str = str(value).replace("%","").replace("+","")
    v_num = float(v_str)
    suffix = "%" if "%" in str(value) else ""
    fig.add_trace(go.Indicator(
        mode="number", value=v_num,
        number=dict(suffix=suffix, font=dict(size=40, color=color)),
        title=dict(text=title_text, font=dict(size=13, color=C["muted"])),
    ), row=row, col=col)


def _kpi_delta(val, bench_val, suffix=""):
    """计算相对基准的差值"""
    if bench_val is None:
        return None
    d = val - bench_val
    sign = "+" if d >= 0 else ""
    return f"vs {sign}{d*100:.1f}{suffix}" if suffix == "%" else f"vs {sign}{d:.1f}{suffix}"


# ---- 辅助函数 ----

def _monthly_heatmap_data(monthly_ret):
    if len(monthly_ret) == 0: return None
    data = {}
    for dt, ret in monthly_ret.items():
        y, m = dt.year, dt.month-1
        data.setdefault(y, {})[m] = float(ret)
    return data

def _calc_annual_return(nav):
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    t = nav.iloc[-1] / nav.iloc[0] - 1
    return float((1+t)**(1/yrs)-1) if yrs>0.01 else 0.0

def _calc_max_dd(nav):
    return float(abs(((nav - nav.expanding().max()) / nav.expanding().max()).min()))

def _calc_sharpe(nav, rf=0.02):
    d = nav.pct_change().dropna()
    if len(d)<2 or d.std()==0: return 0.0
    return float((d.mean()*252-rf)/(d.std()*np.sqrt(252)))

def _calc_win_rate(nav):
    m = nav.resample("ME").last().pct_change().dropna()
    return float((m>0).sum()/len(m)) if len(m)>0 else 0.0
