"""可视化模块 — 交互式 HTML 报告 (Plotly)"""

import pandas as pd
import numpy as np
from pathlib import Path


def report_html(
    nav: pd.Series,
    metrics: dict,
    benchmark: pd.Series | None = None,
    benchmark_label: str = "Benchmark",
    title: str = "Backtest Report",
    save_path: str = "./output/report.html",
) -> str:
    """
    生成自包含交互式 HTML 回测报告

    包含:
      - 净值曲线（策略 vs 基准，可缩放悬停）
      - 回撤曲线
      - 月度收益热力图
      - 绩效指标表 + 策略参数
    """
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    # ---- 数据准备 ----
    nav_ratio = nav / nav.iloc[0]               # 净值倍数（始终>0），用于log轴
    nav_pct = (nav_ratio - 1) * 100             # 百分比，用于表格
    peak = nav.expanding().max()
    dd = (nav - peak) / peak * 100

    monthly_ret = nav.resample("ME").last().pct_change().dropna()
    monthly_matrix = _monthly_heatmap_data(monthly_ret)

    # ---- 构建图表 ----
    fig = make_subplots(
        rows=3, cols=2,
        row_heights=[0.45, 0.30, 0.25],
        column_widths=[0.55, 0.45],
        subplot_titles=(
            "Strategy vs Benchmark", "Performance Metrics",
            "Drawdown", "Monthly Returns Heatmap",
        ),
        vertical_spacing=0.08,
        horizontal_spacing=0.06,
        specs=[
            [{"type": "xy"}, {"type": "table"}],
            [{"type": "xy"}, {"type": "heatmap"}],
            [{"type": "xy", "colspan": 2}, None],
        ],
    )

    # 1. 净值曲线（log刻度，百分比标签）
    fig.add_trace(
        go.Scatter(x=nav.index, y=nav_ratio, mode="lines", name="Strategy",
                   line=dict(color="#1f77b4", width=2),
                   hovertemplate="%{customdata:+.1f}%",
                   customdata=nav_pct),
        row=1, col=1,
    )
    if benchmark is not None:
        bench_norm = benchmark.reindex(nav.index).ffill()
        bench_ratio = bench_norm / bench_norm.iloc[0]
        bench_pct = (bench_ratio - 1) * 100
        fig.add_trace(
            go.Scatter(x=bench_norm.index, y=bench_ratio, mode="lines",
                       name=benchmark_label, line=dict(color="gray", width=1.5, dash="dash"),
                       hovertemplate="%{customdata:+.1f}%",
                       customdata=bench_pct),
            row=1, col=1,
        )

    # 2. 回撤曲线
    fig.add_trace(
        go.Scatter(x=dd.index, y=dd, mode="lines", name="Drawdown",
                   fill="tozeroy", fillcolor="rgba(200,0,0,0.15)",
                   line=dict(color="darkred", width=1)),
        row=2, col=1,
    )
    max_dd = dd.min()
    fig.add_hline(y=max_dd, line_dash="dot", line_color="red", row=2, col=1,
                  annotation_text=f"Max DD: {max_dd:.1f}%")

    # 3. 月度收益热力图
    if monthly_matrix is not None:
        years = list(monthly_matrix.keys())
        months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        z_data = []
        annotations = []
        for y in years:
            row_data = []
            for i, m in enumerate(months):
                v = monthly_matrix[y].get(i, None)
                row_data.append(v if v is not None else np.nan)
                if v is not None:
                    annotations.append(dict(
                        x=i, y=years.index(y), text=f"{v*100:+.1f}%",
                        showarrow=False, font=dict(size=8, color="white" if abs(v)>0.03 else "black")
                    ))
            z_data.append(row_data)

        fig.add_trace(
            go.Heatmap(
                z=z_data, x=months, y=[str(y) for y in years],
                colorscale="RdYlGn", zmid=0,
                text=[[f"{v*100:+.1f}%" if not np.isnan(v) else "" for v in row] for row in z_data],
                texttemplate="%{text}", textfont=dict(size=8),
                showscale=False,
            ),
            row=2, col=2,
        )

    # 4. 绩效指标表
    header = ["Metric", "Strategy"]
    benchmark_col = None
    if benchmark is not None:
        header.append(benchmark_label)
        bench_nav = benchmark.reindex(nav.index).ffill().dropna()
        # 用传入的 metrics 如果有，否则从 benchmark 数列算
        bench_ann = metrics.get("bench_annual") or _calc_annual_return(bench_nav)
        bench_mdd = metrics.get("bench_max_dd") or _calc_max_dd(bench_nav)
        bench_shp = metrics.get("bench_sharpe") or _calc_sharpe(bench_nav)
        bench_tot = metrics.get("bench_total") or (bench_nav.iloc[-1] / bench_nav.iloc[0] - 1)
        bench_wr = metrics.get("bench_win_rate") or _calc_win_rate(bench_nav)
        benchmark_col = [
            f"{bench_ann*100:+.1f}%",
            f"{bench_mdd*100:.1f}%",
            f"{bench_shp:.2f}",
            _calc_calmar(bench_ann, bench_mdd),
            f"{bench_wr*100:.1f}%",
            f"{bench_tot*100:+.1f}%",
            f"{len(bench_nav)}",
        ]

    cells = [
        ["Annual Return", "Max Drawdown", "Sharpe", "Calmar", "Win Rate", "Total Return", "Trading Days"],
        [
            f"{metrics.get('annual_return', 0)*100:+.1f}%",
            f"{metrics.get('max_drawdown', 0)*100:.1f}%",
            f"{metrics.get('sharpe', 0):.2f}",
            f"{metrics.get('calmar', 0):.2f}",
            f"{metrics.get('win_rate', 0)*100:.1f}%",
            f"{metrics.get('total_return', 0)*100:+.1f}%",
            f"{metrics.get('n_days', 0)}",
        ],
    ]
    if benchmark_col:
        cells.append(benchmark_col)

    fig.add_trace(
        go.Table(
            header=dict(values=header, fill_color="#1f77b4", font=dict(color="white"), align="left"),
            cells=dict(values=cells, fill_color=[["white","#f0f0f0"]*4], align="left",
                       font=dict(size=12)),
        ),
        row=1, col=2,
    )

    # 5. 底部策略参数（可选，留给调用者通过 metrics 传入）
    if metrics.get("strategy_name"):
        fig.add_annotation(
            text=f"Strategy: {metrics['strategy_name']}",
            xref="paper", yref="paper", x=0.01, y=0.01,
            showarrow=False, font=dict(size=10, color="gray"),
        )

    # ---- 布局 ----
    fig.update_layout(
        title=dict(text=title, font=dict(size=18), x=0.5),
        height=900,
        showlegend=True,
        hovermode="x unified",
    )
    fig.update_xaxes(title_text="Date", row=1, col=1)
    # log刻度 + 百分比标签
    tick_vals = [0.5, 1, 2, 5, 10, 20]
    tick_labels = ["-50%", "0%", "+100%", "+400%", "+900%", "+1900%"]
    fig.update_yaxes(
        title_text="Return", row=1, col=1, type="log",
        tickvals=tick_vals, ticktext=tick_labels,
    )
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="%", row=2, col=1)

    # 保存
    path = Path(save_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(path, include_plotlyjs="cdn", full_html=True)

    return str(path)


def _monthly_heatmap_data(monthly_ret: pd.Series) -> dict | None:
    """将月度收益序列转为热力图数据结构 {year: {month_index: return}}"""
    if len(monthly_ret) == 0:
        return None
    data: dict[int, dict[int, float]] = {}
    for dt, ret in monthly_ret.items():
        y = dt.year
        m = dt.month - 1  # 0-indexed
        if y not in data:
            data[y] = {}
        data[y][m] = float(ret)
    return data


# ---- 内部辅助：从净值序列计算指标 ----

def _calc_annual_return(nav: pd.Series) -> float:
    years = (nav.index[-1] - nav.index[0]).days / 365.25
    total = nav.iloc[-1] / nav.iloc[0] - 1
    return float((1 + total) ** (1 / years) - 1) if years > 0.01 else 0.0


def _calc_max_dd(nav: pd.Series) -> float:
    peak = nav.expanding().max()
    return float(abs(((nav - peak) / peak).min()))


def _calc_sharpe(nav: pd.Series, risk_free: float = 0.02) -> float:
    daily = nav.pct_change().dropna()
    if len(daily) < 2 or daily.std() == 0:
        return 0.0
    excess = daily.mean() * 252 - risk_free
    vol = daily.std() * np.sqrt(252)
    return float(excess / vol)


def _calc_win_rate(nav: pd.Series) -> float:
    monthly = nav.resample("ME").last().pct_change().dropna()
    if len(monthly) == 0:
        return 0.0
    return float((monthly > 0).sum() / len(monthly))


def _calc_calmar(ann_ret: float, mdd: float) -> str:
    if mdd > 0:
        return f"{ann_ret / mdd:.2f}"
    return "-"
