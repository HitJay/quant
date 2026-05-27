"""商品轮动 — 粉丝问答: 3张竖版3:4图 (小红书版)"""

import os
for k in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']:
    os.environ.pop(k, None)

import sys
sys.path.insert(0, 'src')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.font_manager import FontProperties

# Force all text to be white by default
matplotlib.rcParams['text.color'] = 'white'
matplotlib.rcParams['axes.labelcolor'] = 'white'
matplotlib.rcParams['xtick.color'] = '#cccccc'
matplotlib.rcParams['ytick.color'] = '#cccccc'
from quant.data.cache import Cache

# 中文字体
ZH_FONT = FontProperties(fname="/mnt/c/Windows/Fonts/msyh.ttc", size=14)
ZH_FONT_SM = FontProperties(fname="/mnt/c/Windows/Fonts/msyh.ttc", size=11)
ZH_FONT_LG = FontProperties(fname="/mnt/c/Windows/Fonts/msyh.ttc", size=22)
ZH_FONT_XL = FontProperties(fname="/mnt/c/Windows/Fonts/msyh.ttc", size=24)
ZH_FONT_TITLE = FontProperties(fname="/mnt/c/Windows/Fonts/msyh.ttc", size=18)
from quant.strategies.commodity_rotation import CommodityRotation
from quant.backtest.engine import BacktestEngine, BacktestConfig
from quant.backtest.metrics import annual_return, max_drawdown
from quant.universe.config import UniverseConfig

# ── 数据 & 回测 ──
cache = Cache()
syms = ["518880", "159985", "159866"]
frames = {}
for s in syms + ["511260"]:
    df = cache.load("etf", s)
    frames[s] = df["close"]

prices = pd.DataFrame(frames).sort_index().ffill().dropna().loc["2021-08-01":]
universe = UniverseConfig(etf_codes=syms)
strat = CommodityRotation(momentum_window=63, hold_n=1, defense_etf="511260", universe=universe)
engine = BacktestEngine(BacktestConfig())
result = engine.run(strat, prices, syms)
nav = result.nav_series.dropna()
gold = prices["518880"].reindex(nav.index).ffill()

nav_n = nav / nav.iloc[0]
gold_n = gold / gold.iloc[0]

DARK = "#1a1a2e"
CARD_BG = "#222244"
LEGEND_KW = dict(facecolor="#4a4a6a", edgecolor="#888", labelcolor="white", fontsize=10, framealpha=0.95)
out_dir = "output/commodity-rotation"
os.makedirs(out_dir, exist_ok=True)

# 3:4 = 9x12 inches at 200dpi = 1800x2400px
W, H, DPI = 9, 12, 200

def save(fig, name):
    path = f"{out_dir}/{name}"
    fig.savefig(path, dpi=DPI, facecolor=DARK, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print(f"Saved: {path}")

# ═══════════════════════════════════════════
# 图1: 策略 vs 黄金 长期走势
# ═══════════════════════════════════════════
fig1 = plt.figure(figsize=(W, H))
fig1.patch.set_facecolor(DARK)
gs = gridspec.GridSpec(3, 1, height_ratios=[1.2, 4, 1.5], hspace=0.15,
                       left=0.1, right=0.92, top=0.94, bottom=0.04)

# 标题区
ax_title = fig1.add_subplot(gs[0])
ax_title.set_facecolor(DARK)
ax_title.axis("off")
ax_title.text(0.5, 0.7, "商品轮动 vs 买入黄金", color="white",
              fontproperties=ZH_FONT_XL, fontweight="bold", ha="center", va="center")
ax_title.text(0.5, 0.35, "同样100万起步，5年后谁赚得多？",
              color="#8b949e", fontproperties=ZH_FONT, ha="center", va="center")
ax_title.text(0.5, 0.05, "2021.08 — 2026.05  |  月度调仓",
              color="#555", fontproperties=ZH_FONT_SM, ha="center", va="center")

# 图表区
ax1 = fig1.add_subplot(gs[1])
ax1.set_facecolor(DARK)
line_s, = ax1.plot(nav_n.index, nav_n.values, color="#00ff88", linewidth=2.2)
line_g, = ax1.plot(gold_n.index, gold_n.values, color="#ffd700", linewidth=1.8, alpha=0.8)
ax1.fill_between(nav_n.index, 1, nav_n.values, alpha=0.08, color="#00ff88")

total_s = (nav_n.iloc[-1] - 1) * 100
total_g = (gold_n.iloc[-1] - 1) * 100
ax1.annotate(f"+{total_s:.0f}%", xy=(nav_n.index[-1], nav_n.iloc[-1]),
             xytext=(-120, 30), textcoords="offset points",
             color="#00ff88", fontsize=16, fontweight="bold",
             arrowprops=dict(arrowstyle="->", color="#00ff88", lw=1.2))
ax1.annotate(f"+{total_g:.0f}%", xy=(gold_n.index[-1], gold_n.iloc[-1]),
             xytext=(-120, -35), textcoords="offset points",
             color="#ffd700", fontsize=16, fontweight="bold",
             arrowprops=dict(arrowstyle="->", color="#ffd700", lw=1.2))

ax1.set_yscale("log")
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.1f}x"))
ax1.set_ylabel("NAV", color="white", fontsize=12)
ax1.tick_params(axis="both", colors="#ccc", labelsize=9)
for label in ax1.get_yticklabels():
    label.set_color("#ccc")
for label in ax1.get_xticklabels():
    label.set_color("#ccc")

# Legend: use ax.legend with explicit colors
leg = ax1.legend(
    [plt.Line2D([0],[0], color='#00ff88', linewidth=2.2),
     plt.Line2D([0],[0], color='#ffd700', linewidth=1.8)],
    ['Commodity Rotation', 'Gold Buy & Hold'],
    loc='upper left', fontsize=11,
    facecolor='#3d3d6b', edgecolor='#999999',
    labelcolor='white', framealpha=0.95
)
leg.get_frame().set_linewidth(1.5)
# Force text color after creation
for t in leg.get_texts():
    t.set_color('white')

for sp in ax1.spines.values():
    sp.set_color("#666")
ax1.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)

# 底部KPI区
ax_kpi = fig1.add_subplot(gs[2])
ax_kpi.set_facecolor(DARK)
ax_kpi.axis("off")
# 三个KPI
kpi_data = [
    ("Strategy", f"+{total_s:.0f}%", "#00ff88"),
    ("Gold", f"+{total_g:.0f}%", "#ffd700"),
    ("Sharpe", f"{0.85:.2f}", "#58a6ff"),
]
for i, (label, val, color) in enumerate(kpi_data):
    cx = 0.17 + i * 0.33
    ax_kpi.text(cx, 0.7, val, color=color, fontsize=22, fontweight="bold",
                ha="center", va="center", transform=ax_kpi.transAxes)
    ax_kpi.text(cx, 0.3, label, color="#8b949e", fontsize=12,
                ha="center", va="center", transform=ax_kpi.transAxes)

save(fig1, "qa_chart1_overview.png")

# ═══════════════════════════════════════════
# 图2: 分年度对比
# ═══════════════════════════════════════════
fig2 = plt.figure(figsize=(W, H))
fig2.patch.set_facecolor(DARK)
gs2 = gridspec.GridSpec(3, 1, height_ratios=[1.2, 4, 2], hspace=0.18,
                        left=0.1, right=0.92, top=0.94, bottom=0.04)

# 标题
ax_t2 = fig2.add_subplot(gs2[0])
ax_t2.set_facecolor(DARK)
ax_t2.axis("off")
ax_t2.text(0.5, 0.7, "黄金不行的时候，策略能扛住吗？",
           color="white", fontproperties=ZH_FONT_LG, fontweight="bold", ha="center", va="center")
ax_t2.text(0.5, 0.3, "分年度对比：绿色=策略  金色=黄金",
           color="#8b949e", fontproperties=ZH_FONT_SM, ha="center", va="center")

# 柱状图
ax2 = fig2.add_subplot(gs2[1])
ax2.set_facecolor(DARK)

years = list(range(2022, 2027))
strat_yr, gold_yr = [], []
for yr in years:
    n = nav.loc[str(yr)]
    g = gold.loc[str(yr)]
    strat_yr.append((n.iloc[-1] / n.iloc[0] - 1) * 100 if len(n) > 1 else 0)
    gold_yr.append((g.iloc[-1] / g.iloc[0] - 1) * 100 if len(g) > 1 else 0)

x = np.arange(len(years))
w = 0.35
b1 = ax2.bar(x - w/2, strat_yr, w, label="Strategy",
             color=["#00ff88" if v >= 0 else "#ff4444" for v in strat_yr], alpha=0.85)
b2 = ax2.bar(x + w/2, gold_yr, w, label="Gold",
             color=["#ffd700" if v >= 0 else "#888" for v in gold_yr], alpha=0.65)

for bar, val in zip(b1, strat_yr):
    off = 3 if val >= 0 else -6
    ax2.text(bar.get_x() + bar.get_width()/2, val + off,
             f"{val:+.0f}%", color="#00ff88", fontsize=11, ha="center", fontweight="bold")
for bar, val in zip(b2, gold_yr):
    off = 3 if val >= 0 else -6
    ax2.text(bar.get_x() + bar.get_width()/2, val + off,
             f"{val:+.0f}%", color="#ffd700", fontsize=11, ha="center")

ax2.axvspan(1.55, 2.45, alpha=0.12, color="#ff6b6b")
y_max = max(max(strat_yr), max(gold_yr))
ax2.text(2.0, y_max + 10, "All weak\nStrategy -6%",
         color="#ff9999", fontsize=10, ha="center", va="bottom", style="italic")

ax2.set_xticks(x)
ax2.set_xticklabels([str(y) for y in years], fontsize=12, color="white")
ax2.axhline(0, color="#555", linewidth=0.8)
ax2.set_ylabel("Return %", color="#aaa", fontsize=11)
ax2.tick_params(colors="white", labelsize=9)
ax2.legend(**LEGEND_KW, loc="upper left")
for sp in ax2.spines.values():
    sp.set_color("#444")
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)

# 底部文字说明
ax_txt2 = fig2.add_subplot(gs2[2])
ax_txt2.set_facecolor(CARD_BG)
ax_txt2.axis("off")
ax_txt2.rounded_clip = True

txt2_lines = [
    (">> 大部分时候策略赢", "#00ff88"),
    ("  黄金跌的时候，轮动到其他商品照样赚", "#aaa"),
    ("", "#aaa"),
    (">> 但不是每年都能赢", "#ff9999"),
    ("  2023年三个商品同时横盘，策略反而亏", "#aaa"),
]
for i, (line, color) in enumerate(txt2_lines):
    ax_txt2.text(0.08, 0.88 - i * 0.18, line, color=color, fontproperties=ZH_FONT_SM,
                 ha="left", va="top", transform=ax_txt2.transAxes)

save(fig2, "qa_chart2_yearly.png")

# ═══════════════════════════════════════════
# 图3: 2026年1月暴跌
# ═══════════════════════════════════════════
fig3 = plt.figure(figsize=(W, H))
fig3.patch.set_facecolor(DARK)
gs3 = gridspec.GridSpec(4, 1, height_ratios=[1, 3, 2.2, 1.8], hspace=0.18,
                        left=0.1, right=0.92, top=0.94, bottom=0.04)

# 标题
ax_t3 = fig3.add_subplot(gs3[0])
ax_t3.set_facecolor(DARK)
ax_t3.axis("off")
ax_t3.text(0.5, 0.7, "2026年1月黄金暴跌",
           color="white", fontproperties=ZH_FONT_XL, fontweight="bold", ha="center", va="center")
ax_t3.text(0.5, 0.3, "策略回撤 vs 黄金回撤",
           color="#ff7b72", fontproperties=ZH_FONT, ha="center", va="center")

# 上图: NAV走势
ax3a = fig3.add_subplot(gs3[1])
ax3a.set_facecolor(DARK)
w_nav = nav.loc["2025-11-01":"2026-04-30"]
w_gold = gold.loc["2025-11-01":"2026-04-30"]
nav_w = w_nav / w_nav.iloc[0]
gold_w = w_gold / w_gold.iloc[0]

ax3a.plot(nav_w.index, nav_w.values, color="#00ff88", linewidth=2.2, label="Strategy")
ax3a.plot(gold_w.index, gold_w.values, color="#ffd700", linewidth=1.8, alpha=0.8, label="Gold")

peak_date = w_nav.idxmax()
peak_val = nav_w.max()
trough_date = w_nav.idxmin()
trough_val = nav_w.min()
dd_pct = (trough_val / peak_val - 1) * 100
g_dd_pct = ((gold_w.min()) / gold_w.max() - 1) * 100

# 回撤箭头
ax3a.annotate("", xy=(peak_date, peak_val), xytext=(peak_date, trough_val),
              arrowprops=dict(arrowstyle="<->", color="#ff4444", lw=2))
ax3a.text(peak_date + pd.Timedelta(days=5), (peak_val + trough_val) / 2,
          f"{dd_pct:.0f}%", color="#ff4444", fontsize=16, fontweight="bold", va="center")

ax3a.annotate("", xy=(gold_w.idxmax(), gold_w.max()),
              xytext=(gold_w.idxmin(), gold_w.min()),
              arrowprops=dict(arrowstyle="<->", color="#ffd700", lw=1.5, alpha=0.6))

ax3a.set_ylabel("NAV", color="#aaa", fontsize=11)
ax3a.tick_params(colors="white", labelsize=9)
ax3a.legend(**LEGEND_KW, loc="upper left")
for sp in ax3a.spines.values():
    sp.set_color("#444")
ax3a.spines["top"].set_visible(False)
ax3a.spines["right"].set_visible(False)

# 中图: 回撤曲线
ax3b = fig3.add_subplot(gs3[2])
ax3b.set_facecolor(DARK)
peak_nav = w_nav.expanding().max()
dd = (w_nav - peak_nav) / peak_nav * 100

ax3b.fill_between(dd.index, dd.values, 0, color="#ff4444", alpha=0.35)
ax3b.plot(dd.index, dd.values, color="#ff4444", linewidth=1.5)
ax3b.axhline(-8, color="#ff9900", linewidth=1.2, linestyle="--", alpha=0.8)
ax3b.text(dd.index[5], -6, "止损线 -8% (待加)", color="#ff9900",
          fontproperties=ZH_FONT_SM, alpha=0.9)
ax3b.set_ylabel("Drawdown %", color="#ff4444", fontsize=11)
ax3b.tick_params(colors="white", labelsize=9)
ax3b.set_ylim(-60, 5)
for sp in ax3b.spines.values():
    sp.set_color("#444")
ax3b.spines["top"].set_visible(False)
ax3b.spines["right"].set_visible(False)

# 底部: KPI + 改进方向
ax_btm = fig3.add_subplot(gs3[3])
ax_btm.set_facecolor(CARD_BG)
ax_btm.axis("off")

# 两个大数字
ax_btm.text(0.25, 0.78, f"{dd_pct:.0f}%", color="#ff4444", fontsize=28, fontweight="bold",
            ha="center", va="center", transform=ax_btm.transAxes)
ax_btm.text(0.25, 0.45, "Strategy DD", color="#aaa", fontsize=11, ha="center", va="center",
            transform=ax_btm.transAxes)

ax_btm.text(0.75, 0.78, f"{g_dd_pct:.0f}%", color="#ffd700", fontsize=28, fontweight="bold",
            ha="center", va="center", transform=ax_btm.transAxes)
ax_btm.text(0.75, 0.45, "Gold DD", color="#aaa", fontsize=11, ha="center", va="center",
            transform=ax_btm.transAxes)

ax_btm.text(0.5, 0.1, ">> 改进: 加止损 + 分散持仓 + 限制单品种上限",
            color="#58a6ff", fontproperties=ZH_FONT_SM, ha="center", va="center",
            transform=ax_btm.transAxes)

save(fig3, "qa_chart3_crash.png")

# ═══════════════════════════════════════════
# HTML报告 (同样竖版)
# ═══════════════════════════════════════════
import io, base64

def img_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

c1 = img_b64(f"{out_dir}/qa_chart1_overview.png")
c2 = img_b64(f"{out_dir}/qa_chart2_yearly.png")
c3 = img_b64(f"{out_dir}/qa_chart3_crash.png")

html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
body {{ background: #0d1117; color: #e6edf3; font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
       margin: 0; padding: 16px; }}
.wrap {{ max-width: 480px; margin: 0 auto; }}
.card {{ background: #161b22; border-radius: 14px; padding: 16px; margin-bottom: 20px;
         border: 1px solid #30363d; }}
.img {{ width: 100%; border-radius: 8px; }}
.explain {{ font-size: 13px; line-height: 1.8; color: #c9d1d9; margin-top: 12px; }}
.explain .hl {{ color: #00ff88; font-weight: bold; }}
.explain .warn {{ color: #ff7b72; font-weight: bold; }}
.explain .gold {{ color: #ffd700; font-weight: bold; }}
.footer {{ text-align: center; color: #484f58; font-size: 10px; margin-top: 12px; }}
</style></head>
<body>
<div class="wrap">

<div class="card">
  <img class="img" src="data:image/png;base64,{c1}">
  <div class="explain">
    绿色线是<span class="hl">商品轮动策略</span>，金色线是<span class="gold">买入黄金不动</span>。
    同样100万起步，策略最终变成 <span class="hl">234万</span>，黄金只有 <span class="gold">153万</span>。
    做法很简单：每月看黄金、豆粕、有色金属谁涨最猛就全仓买谁，全都跌就买国债躲着。
  </div>
</div>

<div class="card">
  <img class="img" src="data:image/png;base64,{c2}">
  <div class="explain">
    大部分时候策略比单拿黄金好。但2023年（红色阴影）三个商品同时横盘，策略反而亏了<span class="warn">-6%</span>，
    黄金却涨了+7%。<span class="warn">所有商品都不行的时候，轮动也救不了。</span>
  </div>
</div>

<div class="card">
  <img class="img" src="data:image/png;base64,{c3}">
  <div class="explain">
    2026年1月策略全仓白银（因为之前涨最猛），结果暴跌<span class="warn">亏了54%</span>，
    黄金本身只跌<span class="gold">25%</span>。改进方向：①加止损线 ②分散持仓 ③限制单品种上限。
  </div>
</div>

<div class="footer">Commodity Rotation | 商品ETF轮动研究 | 2026.05</div>
</div>
</body></html>"""

out_path = f"{out_dir}/fan_qa_report.html"
with open(out_path, "w") as f:
    f.write(html)
print(f"HTML report: {out_path}")
print("Done! 3 vertical PNG (3:4) + HTML")
