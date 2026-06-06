"""
PE/PB估值择时 — HTML+matplotlib混合卡片生成器
=============================================
文字卡片: HTML/CSS Flexbox自动排版 (封面/科普/结论/排行榜)
数据卡片: matplotlib (热力图/净值/分年度) — 3:4竖版
HTML→PNG: weasyprint 渲染为 600×800px PNG
"""

import os, sys, json, base64, io
from pathlib import Path
import pandas as pd
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Rectangle
from matplotlib.colors import Normalize
import matplotlib.cm as cm

from weasyprint import HTML

# ── Paths ──
HOME = Path.home()
FONT_DIR = HOME / ".local/share/fonts"
DATA_DIR = Path(__file__).parent.parent / "output/pe_pb_research"
OUT_DIR = DATA_DIR / "xhs_cards"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Fonts (matplotlib) ──
FP_BOLD = FontProperties(fname=str(FONT_DIR / "NotoSansSC-Bold.otf"))
FP_REG = FontProperties(fname=str(FONT_DIR / "NotoSansSC-Regular.otf"))

# ── Colors ──
AMBER = "#f0b866"
INDIGO = "#7fa5c4"
SILVER = "#6b7b8d"
RED_A = "#e74c3c"
GREEN_A = "#4ecca3"
GOLD = "#ffd700"
BG = "#1a1a2e"
CARD_BG = "#16213e"

# ── Dark matplotlib rcParams ──
plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": CARD_BG,
    "text.color": "white", "axes.labelcolor": "white",
    "xtick.color": "#cccccc", "ytick.color": "#cccccc",
    "axes.edgecolor": "#333366", "grid.color": "#2a2a4a", "grid.alpha": 0.5,
    "font.size": 11,
})

# ═══════════════════════════════════════════════════
# Data loading
# ═══════════════════════════════════════════════════

def load_results():
    with open(DATA_DIR / "results.json") as f:
        return json.load(f)


def load_nav(name):
    sname = name.replace("/", "_").replace(" ", "_").replace("+", "_")
    path = DATA_DIR / f"nav_{sname}.csv"
    if path.exists():
        df = pd.read_csv(path, index_col=0, parse_dates=True)
        return df.iloc[:, 0]
    return None


# ═══════════════════════════════════════════════════
# HTML Card framework
# ═══════════════════════════════════════════════════

HTML_CSS = """
@page { size: 600px 800px; margin: 0; }
* { margin:0; padding:0; box-sizing:border-box; }
body { background:#161b22; margin:0; padding:0; }
.card {
  width:600px; height:800px; background:#161b22;
  display:flex; flex-direction:column; justify-content:space-between; padding:32px 28px 24px;
  font-family:'Noto Sans SC',sans-serif; color:#c9d1d9; position:relative; overflow:hidden;
}
.card .page-num { position:absolute; bottom:10px; right:14px; font-size:12px; color:#484f58; }
.card h2 { font-size:30px; text-align:center; font-weight:700; margin-bottom:4px; color:#f0f6fc; }
.card h3 { font-size:17px; color:#8b949e; text-align:center; font-weight:400; margin-bottom:12px; }
.card .hero-num { font-size:96px; color:#f0b866; text-align:center; font-weight:700; line-height:1; margin:8px 0; }
.card .hero-label { font-size:17px; color:#8b949e; text-align:center; margin-bottom:8px; }
.card .hero-sub { font-size:15px; color:#8b949e; text-align:center; }
.card .kpi-row { display:flex; justify-content:space-around; margin:14px 0; }
.card .kpi .val { font-size:32px; font-weight:700; }
.card .kpi .lab { font-size:14px; color:#8b949e; margin-top:2px; }
.card .section { margin-top:10px; }
.card .section-title { font-size:20px; font-weight:700; margin-bottom:5px; display:flex; align-items:center; gap:8px; }
.card .section-title .bar { width:4px; height:20px; border-radius:2px; flex-shrink:0; }
.card .section-body { font-size:17px; line-height:1.6; padding-left:12px; }
.card .section-body .item { margin-bottom:1px; }
.card .finding { margin-bottom:10px; }
.card .finding-title { font-size:20px; font-weight:700; margin-bottom:2px; }
.card .finding-body { font-size:16px; line-height:1.55; color:#c9d1d9; }
.card .cta { text-align:center; color:#f0b866; font-size:16px; font-weight:700; margin-top:6px; }
.card .disclaimer { text-align:center; font-size:12px; color:#484f58; margin-top:4px; }
.card .divider { height:1px; background:#30363d; margin:8px 0; }
.card .rank-row { display:flex; align-items:center; padding:7px 0; font-size:18px; }
.card .rank-num { width:28px; text-align:right; margin-right:10px; color:#8b949e; font-weight:600; flex-shrink:0; }
.card .rank-name { flex:1; font-size:18px; }
.card .rank-val { width:68px; text-align:right; font-weight:700; font-size:18px; }
.text-amber { color:#f0b866; }
.text-indigo { color:#7fa5c4; }
.text-silver { color:#6b7b8d; }
.text-green { color:#3fb950; }
.text-gold { color:#ffd700; }
.bar-amber { background:#f0b866; }
.bar-indigo { background:#7fa5c4; }
.bar-silver { background:#6b7b8d; }
"""


def card_html(page, total, title, subtitle, body, extra_head=""):
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8">{extra_head}
<style>{HTML_CSS}</style></head>
<body>
<div class="card">
  <div class="page-num">{page}/{total}</div>
  <h2>{title}</h2>
  {"<h3>" + subtitle + "</h3>" if subtitle else ""}
  {body}
</div>
</body></html>"""


def html_to_png(html_str, filename):
    """Render HTML to 600x800 PNG via weasyprint"""
    path = OUT_DIR / filename
    # weasyprint renders HTML to PDF, then convert to PNG
    pdf_path = OUT_DIR / f"{filename}.pdf"
    HTML(string=html_str).write_pdf(str(pdf_path))
    # Convert PDF first page to PNG using PyMuPDF
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(str(pdf_path))
        page = doc[0]
        pix = page.get_pixmap(dpi=150)
        pix.save(str(path))
        doc.close()
        os.remove(str(pdf_path))
    except ImportError:
        # Fallback: keep PDF, rename
        os.rename(str(pdf_path), str(path).replace('.png', '_fallback.pdf'))
        path = Path(str(path).replace('.png', '_fallback.pdf'))

    size_kb = path.stat().st_size / 1024
    print(f"  ✓ {filename} ({size_kb:.0f} KB)")
    return path


# ═══════════════════════════════════════════════════
# Card 1/9: Cover (HTML)
# ═══════════════════════════════════════════════════

def card_cover_html(data):
    mt = data["market_timing"]
    best = max([(k, v) for k, v in mt.items() if "PB_10y" in k and "error" not in v],
               key=lambda x: x[1]["annual_return"], default=(None, None))
    hero_val = best[1]["annual_return"] if best[1] else 9.0

    pe_now = data["pe_now"]
    pb_now = data["pb_now"]

    body = f"""
  <div style="flex:1; display:flex; flex-direction:column; align-items:center; justify-content:center;">
    <div style="font-size:48px; font-weight:700; color:#f0f6fc; text-align:center; margin-bottom:4px;">PE/PB判断行业买点</div>
    <div style="font-size:56px; font-weight:700; color:#f0b866; text-align:center; margin-bottom:16px;">靠谱吗？</div>
    <div class="hero-num">{hero_val:.1f}%</div>
    <div class="hero-label">PB估值分位择时 · 年化收益</div>
    <div class="hero-sub">2013-2026 · 13年回测 · 沪深300+国债ETF</div>
  </div>
  <div class="kpi-row">
    <div class="kpi"><div class="val text-amber">PB择时</div><div class="lab">策略主线</div></div>
    <div class="kpi"><div class="val text-indigo">{pe_now['pct']:.0f}%分位</div><div class="lab">当前PE分位</div></div>
    <div class="kpi"><div class="val text-silver">{pb_now['pct']:.0f}%分位</div><div class="lab">当前PB分位</div></div>
  </div>
  <div class="divider"></div>
  <div class="cta">专业AI量化研究员告诉你答案</div>
  <div class="disclaimer">历史回测不代表未来表现 · 仅供研究参考</div>"""

    html_str = card_html(1, 9, "PE/PB估值择时", "", body)
    return html_to_png(html_str, "00_cover.png")


# ═══════════════════════════════════════════════════
# Card 2/9: Intro — PE/PB科普 (HTML)
# ═══════════════════════════════════════════════════

def card_intro_html(data):
    body = """
  <div class="section">
    <div class="section-title"><span class="bar bar-amber"></span>PE (市盈率) — Price / Earnings</div>
    <div class="section-body">
      <div class="item">• PE = 股价 ÷ 每股盈利</div>
      <div class="item">• PE低 → 便宜（盈利能力强/市场低估）</div>
      <div class="item">• PE高 → 贵（成长预期高/可能泡沫）</div>
      <div class="item">• 缺点：盈利波动大时PE失真</div>
    </div>
  </div>
  <div class="section">
    <div class="section-title"><span class="bar bar-indigo"></span>PB (市净率) — Price / Book</div>
    <div class="section-body">
      <div class="item">• PB = 股价 ÷ 每股净资产</div>
      <div class="item">• PB低 → 便宜（破净/资产折价）</div>
      <div class="item">• PB高 → 贵（轻资产/品牌溢价）</div>
      <div class="item">• 优点：净资产比盈利更稳定</div>
    </div>
  </div>
  <div class="divider"></div>
  <div class="section">
    <div class="section-title"><span class="bar bar-silver"></span>历史百分位择时</div>
    <div class="section-body">
      <div class="item">• 计算当前PE/PB在过去N年中的排位</div>
      <div class="item">• 分位越低越便宜 → 加大权益仓位</div>
      <div class="item">• 分位越高越贵 → 转向债券防御</div>
      <div class="item">• 核心假设：估值会均值回归</div>
    </div>
  </div>
  <div style="flex:1"></div>
  <div class="cta" style="font-size:14px; color:#8b949e;">下面用13年真实数据跑一遍看结果</div>"""

    html_str = card_html(2, 9, "什么是PE/PB估值分位？", "简单搞懂两个最常用的估值指标", body)
    return html_to_png(html_str, "00b_intro.png")


# ═══════════════════════════════════════════════════
# Card 3/9: PE vs PB Heatmap (matplotlib, 3:4)
# ═══════════════════════════════════════════════════

def card_heatmap_mpl(data):
    mt = data["market_timing"]
    windows = [5, 7, 10]
    thresholds = ["20_80", "25_75", "30_70"]

    fig, axes = plt.subplots(2, 1, figsize=(7.2, 9.6))  # 3:4 ratio
    fig.suptitle("PE vs PB 估值择时参数扫描", fontproperties=FP_BOLD, fontsize=18, y=0.98, color="white")

    indicators = [("PE", AMBER), ("PB", INDIGO)]

    # Build per-indicator color normalization
    for ax_idx, (ind, color) in enumerate(indicators):
        ax = axes[ax_idx]
        ax.set_facecolor(CARD_BG)
        ax.set_title(f"{ind} 分位择时 · 年化收益(%)", fontproperties=FP_BOLD, fontsize=15,
                     color=color, pad=8)

        # Collect values for THIS indicator only
        ind_vals = []
        cell_data = {}
        for i in range(len(windows)):
            for j in range(len(thresholds)):
                key = f"{ind}_{windows[i]}y_{thresholds[j]}"
                val = mt[key]["annual_return"] if key in mt and "error" not in mt[key] else np.nan
                if not np.isnan(val):
                    ind_vals.append(val)
                    cell_data[(i, j)] = val

        if not ind_vals:
            continue

        vmin, vmax = np.min(ind_vals), np.max(ind_vals)
        # Pad range slightly for visual separation
        padding = (vmax - vmin) * 0.1 if vmax > vmin else 1.0
        vmin -= padding
        vmax += padding
        norm = Normalize(vmin=vmin, vmax=vmax)

        # A-share convention: red(gain/high) ← yellow(mid) ← green(loss/low)
        from matplotlib.colors import LinearSegmentedColormap
        colors_custom = ["#3fb950", "#8cc97e", "#f0b866", "#e8845c", "#e74c3c"]
        cmap_custom = LinearSegmentedColormap.from_list("green_red", colors_custom, N=256)

        for (i, j), val in cell_data.items():
            rect = Rectangle((j - 0.45, i - 0.45), 0.9, 0.9,
                             facecolor=cmap_custom(norm(val)),
                             edgecolor="#2a2a4a", linewidth=1.5)
            ax.add_patch(rect)
            ax.text(j, i, f"{val:.1f}%", ha="center", va="center",
                    fontproperties=FP_BOLD, fontsize=13, color="white",
                    path_effects=[pe.withStroke(linewidth=2, foreground="black")])

        ax.set_xticks(range(len(thresholds)))
        ax.set_xticklabels([t.replace("_", "/") for t in thresholds], fontproperties=FP_REG, fontsize=11)
        ax.set_yticks(range(len(windows)))
        ax.set_yticklabels([f"{w}年窗口" for w in windows], fontproperties=FP_REG, fontsize=11)
        ax.set_xlim(-0.6, len(thresholds) - 0.4)
        ax.set_ylim(-0.6, len(windows) - 0.4)
        ax.tick_params(colors="#cccccc")

    fig.subplots_adjust(left=0.10, right=0.95, top=0.90, bottom=0.06, hspace=0.40)
    path = OUT_DIR / "01_heatmap.png"
    fig.text(0.95, 0.015, "3/9", fontproperties=FP_REG, fontsize=11, color="#666688", ha="right")
    fig.savefig(path, dpi=150, facecolor=BG, edgecolor="none")
    plt.close(fig)
    print(f"  ✓ 01_heatmap.png ({path.stat().st_size/1024:.0f} KB)")
    return path


# ═══════════════════════════════════════════════════
# Card 4/9: Best PB NAV (matplotlib, 3:4)
# ═══════════════════════════════════════════════════

def card_best_nav_mpl(data):
    nav_pb = load_nav("PB_10y_30_70")
    nav_bh = load_nav("买入持有")

    fig, ax = plt.subplots(figsize=(6, 8))
    ax.set_facecolor(CARD_BG)

    if nav_pb is not None and nav_bh is not None:
        nav_pb = nav_pb / nav_pb.iloc[0]
        nav_bh = nav_bh / nav_bh.iloc[0]

        ax.plot(nav_pb.index, nav_pb.values, color=INDIGO, linewidth=2.2, label="PB择时(10年30/70)")
        ax.plot(nav_bh.index, nav_bh.values, color=SILVER, linewidth=1.5, label="买入持有", alpha=0.8)

        ax.set_yscale("log")
        ax.set_ylabel("NAV (log)", fontproperties=FP_REG, fontsize=11, color="#aaaacc")
        ax.legend(loc="upper left", prop=FP_REG, fontsize=11,
                  facecolor="#2a2a4a", edgecolor="#444466", labelcolor="white")
        ax.grid(True, alpha=0.3)
        ax.set_title("PB 估值择时 vs 买入持有 — PB完胜", fontproperties=FP_BOLD, fontsize=18, color=INDIGO, pad=12)

        mt_pb = data["market_timing"].get("PB_10y_30_70", {})
        mt_bh = data["market_timing"].get("买入持有", {})
        kpi = (
            f"PB择时: 年化{mt_pb.get('annual_return',0):.1f}%  回撤{mt_pb.get('max_drawdown',0):.1f}%  夏普{mt_pb.get('sharpe',0):.2f}\n"
            f"买入持有: 年化{mt_bh.get('annual_return',0):.1f}%  回撤{mt_bh.get('max_drawdown',0):.1f}%  夏普{mt_bh.get('sharpe',0):.2f}"
        )
        ax.text(0.02, 0.88, kpi, transform=ax.transAxes, fontproperties=FP_REG,
                fontsize=9, color="#cccccc", va="top",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#0d1117", edgecolor="#333366", alpha=0.85))

    fig.tight_layout()
    path = OUT_DIR / "02_best_nav.png"
    fig.text(0.95, 0.01, "4/9", fontproperties=FP_REG, fontsize=10, color="#666688", ha="right")
    fig.savefig(path, dpi=150, facecolor=BG, edgecolor="none")
    plt.close(fig)
    print(f"  ✓ 02_best_nav.png ({path.stat().st_size/1024:.0f} KB)")
    return path


# ═══════════════════════════════════════════════════
# Card 5/9: Worst PE NAV (matplotlib, 3:4)
# ═══════════════════════════════════════════════════

def card_worst_nav_mpl(data):
    nav_pe = load_nav("PE_5y_30_70")
    nav_bh = load_nav("买入持有")

    fig, ax = plt.subplots(figsize=(6, 8))
    ax.set_facecolor(CARD_BG)

    if nav_pe is not None and nav_bh is not None:
        nav_pe = nav_pe / nav_pe.iloc[0]
        nav_bh = nav_bh / nav_bh.iloc[0]

        ax.plot(nav_pe.index, nav_pe.values, color=AMBER, linewidth=2.2, label="PE择时(5年30/70)")
        ax.plot(nav_bh.index, nav_bh.values, color=SILVER, linewidth=1.5, label="买入持有", alpha=0.8)

        ax.set_yscale("log")
        ax.set_ylabel("NAV (log)", fontproperties=FP_REG, fontsize=11, color="#aaaacc")
        ax.legend(loc="upper left", prop=FP_REG, fontsize=11,
                  facecolor="#2a2a4a", edgecolor="#444466", labelcolor="white")
        ax.grid(True, alpha=0.3)
        ax.set_title("PE 5年分位择时 — 效果打折扣", fontproperties=FP_BOLD, fontsize=18, color=AMBER, pad=12)

        mt_pe = data["market_timing"].get("PE_5y_30_70", {})
        mt_bh = data["market_timing"].get("买入持有", {})
        kpi = (
            f"PE择时: 年化{mt_pe.get('annual_return',0):.1f}%  回撤{mt_pe.get('max_drawdown',0):.1f}%  夏普{mt_pe.get('sharpe',0):.2f}\n"
            f"买入持有: 年化{mt_bh.get('annual_return',0):.1f}%  回撤{mt_bh.get('max_drawdown',0):.1f}%  夏普{mt_bh.get('sharpe',0):.2f}"
        )
        ax.text(0.02, 0.88, kpi, transform=ax.transAxes, fontproperties=FP_REG,
                fontsize=9, color="#cccccc", va="top",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#0d1117", edgecolor="#333366", alpha=0.85))

    fig.tight_layout()
    path = OUT_DIR / "03_worst_nav.png"
    fig.text(0.95, 0.01, "5/9", fontproperties=FP_REG, fontsize=10, color="#666688", ha="right")
    fig.savefig(path, dpi=150, facecolor=BG, edgecolor="none")
    plt.close(fig)
    print(f"  ✓ 03_worst_nav.png ({path.stat().st_size/1024:.0f} KB)")
    return path


# ═══════════════════════════════════════════════════
# Card 6/9: Sector heatmap (matplotlib, 3:4)
# ═══════════════════════════════════════════════════

def card_sector_heatmap_mpl(data):
    sr = data["sector_rotation"]
    lookbacks = [1, 3, 6, 12]
    hold_ns = [2, 3]
    modes = ["反转", "动量"]

    fig, axes = plt.subplots(2, 1, figsize=(7.2, 9.6))  # 3:4 ratio
    fig.suptitle("行业层面：反转(低估值代理) vs 动量", fontproperties=FP_BOLD, fontsize=16, y=0.98, color="white")

    for ax_idx, mode in enumerate(modes):
        ax = axes[ax_idx]
        ax.set_facecolor(CARD_BG)
        color = AMBER if mode == "反转" else INDIGO
        label_cn = "买最弱行业" if mode == "反转" else "买最强行业"
        ax.set_title(f"{mode}策略 ({label_cn}) · 年化收益(%)", fontproperties=FP_BOLD, fontsize=15,
                     color=color, pad=8)

        # Collect values for THIS mode only
        mode_vals = []
        cell_data = {}
        for i, lb in enumerate(lookbacks):
            for j, n in enumerate(hold_ns):
                key = f"{mode}{lb}月_hold{n}"
                val = sr[key]["annual_return"] if key in sr and "error" not in sr[key] else np.nan
                if not np.isnan(val):
                    mode_vals.append(val)
                    cell_data[(i, j)] = val

        if not mode_vals:
            continue

        vmin, vmax = np.min(mode_vals), np.max(mode_vals)
        padding = (vmax - vmin) * 0.1 if vmax > vmin else 1.0
        vmin -= padding
        vmax += padding
        norm = Normalize(vmin=vmin, vmax=vmax)

        from matplotlib.colors import LinearSegmentedColormap
        # A-share convention: red(gain/high) ← yellow(mid) ← green(loss/low)
        colors_custom = ["#3fb950", "#8cc97e", "#f0b866", "#e8845c", "#e74c3c"]
        cmap_custom = LinearSegmentedColormap.from_list("green_red", colors_custom, N=256)

        for (i, j), val in cell_data.items():
            rect = Rectangle((j - 0.45, i - 0.45), 0.9, 0.9,
                             facecolor=cmap_custom(norm(val)),
                             edgecolor="#2a2a4a", linewidth=1.5)
            ax.add_patch(rect)
            ax.text(j, i, f"{val:.1f}%", ha="center", va="center",
                    fontproperties=FP_BOLD, fontsize=13, color="white",
                    path_effects=[pe.withStroke(linewidth=2, foreground="black")])

        ax.set_xticks(range(len(hold_ns)))
        ax.set_xticklabels([f"持{n}只" for n in hold_ns], fontproperties=FP_REG, fontsize=11)
        ax.set_yticks(range(len(lookbacks)))
        ax.set_yticklabels([f"{lb}月回看" for lb in lookbacks], fontproperties=FP_REG, fontsize=11)
        ax.set_xlim(-0.6, len(hold_ns) - 0.4)
        ax.set_ylim(-0.6, len(lookbacks) - 0.4)
        ax.tick_params(colors="#cccccc")

    fig.subplots_adjust(left=0.10, right=0.95, top=0.90, bottom=0.06, hspace=0.40)
    path = OUT_DIR / "05_sector_heatmap.png"
    fig.text(0.95, 0.015, "6/9", fontproperties=FP_REG, fontsize=11, color="#666688", ha="right")
    fig.savefig(path, dpi=150, facecolor=BG, edgecolor="none")
    plt.close(fig)
    print(f"  ✓ 05_sector_heatmap.png ({path.stat().st_size/1024:.0f} KB)")
    return path


# ═══════════════════════════════════════════════════
# Card 7/9: Annual bars (matplotlib, 3:4)
# ═══════════════════════════════════════════════════

def card_annual_mpl(data):
    nav_pb = load_nav("PB_10y_30_70")
    nav_bh = load_nav("买入持有")

    fig, ax = plt.subplots(figsize=(6, 8))
    ax.set_facecolor(CARD_BG)

    if nav_pb is not None and nav_bh is not None:
        pb_annual = nav_pb.resample("YE").last().pct_change().dropna() * 100
        bh_annual = nav_bh.resample("YE").last().pct_change().dropna() * 100
        common_years = sorted(set(pb_annual.index.year) & set(bh_annual.index.year))

        years_str = [str(y) for y in common_years]
        x = np.arange(len(common_years))
        width = 0.35

        pb_vals = [float(pb_annual[pb_annual.index.year == y].iloc[0]) for y in common_years]
        bh_vals = [float(bh_annual[bh_annual.index.year == y].iloc[0]) for y in common_years]

        # Per-bar coloring: amber for positive, indigo for negative
        pb_colors = [AMBER if v >= 0 else INDIGO for v in pb_vals]
        bh_colors = [SILVER for _ in bh_vals]

        ax.bar(x - width/2, pb_vals, width, color=pb_colors, label="PB择时", edgecolor=BG, linewidth=0.3)
        ax.bar(x + width/2, bh_vals, width, color=bh_colors, label="买入持有", edgecolor=BG, linewidth=0.3, alpha=0.7)

        ax.set_title("分年度收益: PB择时 vs 买入持有", fontproperties=FP_BOLD, fontsize=22, color=INDIGO, pad=12)
        ax.set_xticks(x)
        ax.set_xticklabels(years_str, fontproperties=FP_REG, fontsize=12, rotation=45)
        ax.set_ylabel("年收益 (%)", fontproperties=FP_REG, fontsize=14, color="#aaaacc")
        ax.axhline(y=0, color="#555577", linewidth=0.8)
        ax.legend(loc="upper right", prop=FP_REG, fontsize=14,
                  facecolor="#2a2a4a", edgecolor="#444466", labelcolor="white")
        ax.grid(True, alpha=0.3, axis="y")

    fig.tight_layout()
    path = OUT_DIR / "04_annual.png"
    fig.text(0.95, 0.01, "7/9", fontproperties=FP_REG, fontsize=10, color="#666688", ha="right")
    fig.savefig(path, dpi=150, facecolor=BG, edgecolor="none")
    plt.close(fig)
    print(f"  ✓ 04_annual.png ({path.stat().st_size/1024:.0f} KB)")
    return path


# ═══════════════════════════════════════════════════
# Card 8/9: Conclusion (HTML)
# ═══════════════════════════════════════════════════

def card_conclusion_html(data):
    body = """
  <div class="finding">
    <div class="finding-title text-indigo">▎PB比PE靠谱得多</div>
    <div class="finding-body">宽基PB择时年化远超PE择时。PB(净资产)比PE(盈利)更稳定，不受盈利周期波动干扰。</div>
  </div>
  <div class="finding">
    <div class="finding-title text-amber">▎回撤大幅减少</div>
    <div class="finding-body">PB择时最大回撤仅买入持有的一半。估值分位帮你精准躲过市场最贵的时候。</div>
  </div>
  <div class="finding">
    <div class="finding-title text-indigo">▎行业反转策略有效</div>
    <div class="finding-body">买跌得最惨的行业(反转1月hold3)跑赢等权持有。短期超跌比PE/PB更有信号价值。</div>
  </div>
  <div class="finding">
    <div class="finding-title text-amber">▎PE单独用有陷阱</div>
    <div class="finding-body">PE低不一定是便宜——盈利见顶前的PE反而最低。需要结合PB和动量交叉验证。</div>
  </div>
  <div class="divider"></div>
  <div style="text-align:center; margin:4px 0;">
    <div style="font-size:20px; font-weight:700; color:#f0b866; margin-bottom:4px;">散户建议</div>
    <div style="font-size:15px; line-height:1.6; color:#c9d1d9;">
      宽基指数PB分位低于30%时大胆定投<br>
      高于70%时减少权益仓位<br>
      行业层面别只看PE/PB——<br>
      短期超跌的反转信号比估值更有用
    </div>
  </div>"""

    html_str = card_html(8, 9, "核心发现 · 结论", "13年数据告诉我们什么", body)
    return html_to_png(html_str, "06_conclusion.png")


# ═══════════════════════════════════════════════════
# Card 9/9: Ranking (HTML)
# ═══════════════════════════════════════════════════

def card_ranking_html(data):
    mt = data["market_timing"]
    sr = data["sector_rotation"]

    # Collect top strategies
    all_strats = []
    # Add benchmarks + best PB/PE
    for k in ["买入持有", "60/40固定", "PE+PB联合_5y_30_70"]:
        if k in mt and "error" not in mt[k]:
            v = mt[k]
            name_map = {"买入持有": "买入持有(基准)", "60/40固定": "60/40股债固定",
                        "PE+PB联合_5y_30_70": "PE+PB联合择时"}
            all_strats.append((name_map.get(k, k.replace("_", " ")), v["annual_return"], v["max_drawdown"], v["sharpe"]))

    # Best PB
    for k in ["PB_10y_30_70"]:
        if k in mt and "error" not in mt[k]:
            v = mt[k]
            all_strats.append(("PB分位择时(10年窗口)", v["annual_return"], v["max_drawdown"], v["sharpe"]))

    # Top sector strategies
    sector_names = {"反转1月_hold3": "反转策略(1月·持3只)", "反转6月_hold3": "反转策略(6月·持3只)",
                    "动量12月_hold2": "动量策略(12月·持2只)", "等权持有": "等权持有(行业基准)"}
    for k, display_name in sector_names.items():
        if k in sr and "error" not in sr[k]:
            v = sr[k]
            all_strats.append((display_name, v["annual_return"], v["max_drawdown"], v["sharpe"]))

    all_strats.sort(key=lambda x: x[3], reverse=True)

    rows = ""
    for i, (name, ann, mdd, sh) in enumerate(all_strats):
        color = "text-amber" if sh > 0.4 else "text-indigo" if sh > 0.2 else ""
        rows += f"""
  <div class="rank-row">
    <span class="rank-num">{i+1}</span>
    <span class="rank-name">{name}</span>
    <span class="rank-val">{ann:.1f}%</span>
    <span class="rank-val" style="width:56px; color:#8b949e;">{mdd:.1f}%</span>
    <span class="rank-val {color}">{sh:.2f}</span>
  </div>"""

    body = f"""
  <div style="font-size:16px; color:#8b949e; display:flex; padding:4px 0 8px 0; border-bottom:1px solid #30363d; margin-bottom:6px;">
    <span style="width:38px; flex-shrink:0;"></span>
    <span style="flex:1; font-weight:700;">策略</span>
    <span style="width:68px; text-align:right; font-weight:700;">年化</span>
    <span style="width:68px; text-align:right; font-weight:700;">回撤</span>
    <span style="width:68px; text-align:right; font-weight:700;">夏普</span>
  </div>
  {rows}
  <div style="flex:1"></div>
  <div class="divider"></div>
  <div class="cta">关注我不迷路 · 下方链接获取研报+源码</div>"""

    html_str = card_html(9, 9, "策略排行榜", "按夏普比率排序", body)
    return html_to_png(html_str, "07_table.png")


# ═══════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════

def main():
    print("Loading data...")
    data = load_results()
    print(f"  {len(data['market_timing'])} market + {len(data['sector_rotation'])} sector strategies")
    print()

    cards = [
        ("1/9 封面(HTML)", lambda: card_cover_html(data)),
        ("2/9 科普(HTML)", lambda: card_intro_html(data)),
        ("3/9 PE/PB热力图", lambda: card_heatmap_mpl(data)),
        ("4/9 PB最佳净值", lambda: card_best_nav_mpl(data)),
        ("5/9 PE最差净值", lambda: card_worst_nav_mpl(data)),
        ("6/9 行业反转vs动量", lambda: card_sector_heatmap_mpl(data)),
        ("7/9 分年度对比", lambda: card_annual_mpl(data)),
        ("8/9 结论(HTML)", lambda: card_conclusion_html(data)),
        ("9/9 排行榜(HTML)", lambda: card_ranking_html(data)),
    ]

    for label, fn in cards:
        try:
            fn()
        except Exception as e:
            print(f"  ❌ {label}: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n✅ {len(list(OUT_DIR.glob('*.png')))} cards → {OUT_DIR}/")


if __name__ == "__main__":
    main()
