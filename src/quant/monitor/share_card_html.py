"""HTML/CSS分享卡片 — 自动排版，无需调坐标"""

import base64
import io
import weasyprint
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def share_card_html(
    nav,
    metrics: dict,
    benchmark=None,
    benchmark_label: str = "",
    strategy_name: str = "",
    period: str = "",
    theme: str = "dark",
    save_path: str = "./output/share_card.html",
    dpi: int = 200,
) -> str:
    """HTML+CSS自动排版 → 自包含HTML文件，浏览器打开即可截图"""

    ann_ret = metrics.get("annual_return", 0)
    mdd_val = metrics.get("max_drawdown", 0)
    shp_val = metrics.get("sharpe", 0)
    tot_ret = metrics.get("total_return", 0)
    bench_ann = metrics.get("bench_annual")
    bench_tot = metrics.get("bench_total", 0)
    n_days = metrics.get("n_days", 0)
    yrs = n_days / 252

    # ---- NAV迷你图 (base64) ----
    nav_chart_b64 = _nav_chart_b64(nav, benchmark, benchmark_label, theme, dpi)

    # ---- 配色 ----
    if theme == "dark":
        css, hero_color = _dark_theme()
    else:
        css, hero_color = _light_theme()

    hero_cls = "green" if tot_ret > 0 else "red"

    # ---- 对比条 ----
    bench_pct_w = int(min(100, abs((1+bench_tot)/(1+tot_ret)*100))) if tot_ret != 0 else 0
    compare_html = f"""
    <div class="compare-row">
      <span class="compare-label">{benchmark_label}</span>
      <div class="compare-bar-wrap"><div class="compare-bar bench" style="width:{bench_pct_w}%"></div></div>
      <span class="compare-pct">{bench_tot*100:+.1f}%</span>
    </div>
    <div class="compare-row">
      <span class="compare-label strategy">Strategy</span>
      <div class="compare-bar-wrap"><div class="compare-bar strat" style="width:100%"></div></div>
      <span class="compare-pct strat">{tot_ret*100:+.1f}%</span>
    </div>
    """ if bench_tot else ""

    # ---- HTML ----
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{css}</style></head>
<body>
<div class="card">
  <h1>{strategy_name}</h1>
  <p class="period">{period}</p>

  <div class="hero">
    <span class="hero-num {hero_cls}">{tot_ret*100:+.1f}%</span>
    <span class="hero-label">Total Return</span>
    {f'<span class="hero-vs">Ann. {ann_ret*100:+.1f}% vs {benchmark_label} {bench_ann*100:+.1f}%</span>' if bench_ann else ''}
  </div>

  <div class="kpi-row">
    <div class="kpi"><span class="kpi-val">Sharpe</span><span class="kpi-num">{shp_val:.2f}</span></div>
    <div class="kpi"><span class="kpi-val">Max DD</span><span class="kpi-num red">{mdd_val*100:.1f}%</span></div>
    <div class="kpi"><span class="kpi-val">Win Rate</span><span class="kpi-num">{metrics.get('win_rate',0)*100:.0f}%</span></div>
  </div>

  <div class="chart"><img src="data:image/png;base64,{nav_chart_b64}"></div>

  <div class="bottom-bar">
    {compare_html}
    <p class="footer">{n_days} trading days · ~{yrs:.1f} years · for reference only</p>
  </div>
</div>
</body></html>"""

    # 保存HTML
    path = Path(save_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return str(path)


def _nav_chart_b64(nav, benchmark, benchmark_label, theme, dpi):
    """生成NAV迷你图并返回base64"""
    if theme == "dark":
        bg, accent, green, red, muted, card_bg = "#0d1117","#58a6ff","#3fb950","#f85149","#8b949e","#21262d"
    else:
        bg, accent, green, red, muted, card_bg = "#fafbfc","#2563eb","#059669","#dc2626","#6b7280","#ffffff"

    fig, ax = plt.subplots(figsize=(5, 2), facecolor=bg)
    nav_ratio = nav / nav.iloc[0]
    ax.fill_between(nav.index, nav_ratio, 1, where=nav_ratio>=1, alpha=0.15, color=green)
    ax.fill_between(nav.index, nav_ratio, 1, where=nav_ratio<1, alpha=0.08, color=red)
    ax.plot(nav.index, nav_ratio, color=accent, linewidth=2, label="Strategy")
    if benchmark is not None:
        br = benchmark.reindex(nav.index).ffill()
        br = br / br.iloc[0]
        ax.plot(br.index, br, color=muted, linewidth=1.2, linestyle="dashed", alpha=0.7, label=benchmark_label)
    ax.axhline(y=1, color=muted, linewidth=0.6, linestyle="--", alpha=0.3)
    ax.set_facecolor(bg)
    leg = ax.legend(loc="upper left", fontsize=7, framealpha=0.6,
                    edgecolor="#30363d" if theme=="dark" else card_bg,
                    facecolor=card_bg)
    if theme == "dark":
        for t in leg.get_texts():
            t.set_color("#c9d1d9")
    for s in ["top","right"]: ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(muted); ax.spines["left"].set_alpha(0.3)
    ax.spines["bottom"].set_color(muted); ax.spines["bottom"].set_alpha(0.3)
    ax.tick_params(colors=muted, labelsize=6)
    ax.set_yscale("log")
    ax.set_yticks([0.3,0.5,1,2,5,10,20,50])
    ax.set_yticklabels(["-70%","-50%","0%","+100%","+400%","+900%","+1900%","+4900%"], fontsize=6, color=muted)
    plt.tight_layout(pad=0.3)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, facecolor=bg, edgecolor="none", pad_inches=0.1)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()


def _dark_theme():
    css = """
    *{margin:0;padding:0;box-sizing:border-box}
    body{background:#0d1117;display:flex;justify-content:center;align-items:center;min-height:100vh}
    .card{width:600px;height:780px;background:#0d1117;padding:30px 36px;display:flex;flex-direction:column;gap:16px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
    h1{font-size:24px;font-weight:800;color:#c9d1d9;text-align:center}
    .period{font-size:11px;color:#8b949e;text-align:center;margin-top:-10px}
    .hero{text-align:center}
    .hero-num{font-size:54px;font-weight:800;line-height:1.1}
    .hero-num.green{color:#3fb950}.hero-num.red{color:#f85149}
    .hero-label{display:block;font-size:12px;color:#8b949e;margin-top:4px}
    .hero-vs{display:block;font-size:10px;color:#8b949e;margin-top:4px}
    .kpi-row{display:flex;gap:12px;justify-content:center}
    .kpi{flex:1;background:#21262d;border:1px solid #30363d;border-radius:10px;padding:12px 8px;text-align:center;display:flex;flex-direction:column;gap:4px}
    .kpi-val{font-size:8px;color:#8b949e;text-transform:uppercase;letter-spacing:0.5px}
    .kpi-num{font-size:18px;font-weight:700;color:#58a6ff}.kpi-num.red{color:#f85149}
    .chart img{width:100%;border-radius:8px}
    .bottom-bar{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:16px 20px;display:flex;flex-direction:column;gap:8px}
    .compare-row{display:flex;align-items:center;gap:10px}
    .compare-label{font-size:9px;font-weight:700;color:#8b949e;width:80px;text-align:right;flex-shrink:0}
    .compare-label.strategy{color:#3fb950}
    .compare-bar-wrap{flex:1;height:14px;background:#21262d;border-radius:7px;overflow:hidden}
    .compare-bar{height:100%;border-radius:7px}
    .compare-bar.bench{background:#484f58}.compare-bar.strat{background:#3fb950}
    .compare-pct{font-size:10px;font-weight:700;color:#8b949e;width:55px;text-align:left;flex-shrink:0}
    .compare-pct.strat{font-size:11px;color:#3fb950}
    .footer{font-size:7px;color:#8b949e;text-align:center;margin-top:4px}
    """
    return css, "#3fb950"


def _light_theme():
    css = """
    *{margin:0;padding:0;box-sizing:border-box}
    body{background:#fafbfc;display:flex;justify-content:center;align-items:center;min-height:100vh}
    .card{width:600px;height:780px;background:#fafbfc;padding:30px 36px;display:flex;flex-direction:column;gap:16px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
    h1{font-size:24px;font-weight:800;color:#111827;text-align:center}
    .period{font-size:11px;color:#6b7280;text-align:center;margin-top:-10px}
    .hero{text-align:center}
    .hero-num{font-size:54px;font-weight:800;line-height:1.1}
    .hero-num.green{color:#059669}.hero-num.red{color:#dc2626}
    .hero-label{display:block;font-size:12px;color:#6b7280;margin-top:4px}
    .hero-vs{display:block;font-size:10px;color:#6b7280;margin-top:4px}
    .kpi-row{display:flex;gap:12px;justify-content:center}
    .kpi{flex:1;background:#ffffff;border:1px solid #e5e7eb;border-radius:10px;padding:12px 8px;text-align:center;display:flex;flex-direction:column;gap:4px;box-shadow:0 1px 3px rgba(0,0,0,0.04)}
    .kpi-val{font-size:8px;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px}
    .kpi-num{font-size:18px;font-weight:700;color:#2563eb}.kpi-num.red{color:#dc2626}
    .chart img{width:100%;border-radius:8px}
    .bottom-bar{background:#ffffff;border:1px solid #e5e7eb;border-radius:12px;padding:16px 20px;display:flex;flex-direction:column;gap:8px;box-shadow:0 1px 3px rgba(0,0,0,0.04)}
    .compare-row{display:flex;align-items:center;gap:10px}
    .compare-label{font-size:9px;font-weight:700;color:#6b7280;width:80px;text-align:right;flex-shrink:0}
    .compare-label.strategy{color:#059669}
    .compare-bar-wrap{flex:1;height:14px;background:#f3f4f6;border-radius:7px;overflow:hidden}
    .compare-bar{height:100%;border-radius:7px}
    .compare-bar.bench{background:#d1d5db}.compare-bar.strat{background:#059669}
    .compare-pct{font-size:10px;font-weight:700;color:#6b7280;width:55px;text-align:left;flex-shrink:0}
    .compare-pct.strat{font-size:11px;color:#059669}
    .footer{font-size:7px;color:#6b7280;text-align:center;margin-top:4px}
    """
    return css, "#059669"
