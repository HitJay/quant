"""FCF 反共识帖 — page1 (cover) + page4 (现金流 vs 红利) 数据修复.

背景
----
原 analyze 脚本把 sz159211 误标为 "中证红利低波 100ETF" — 新浪行情核实:
    sz159211 = 富国深证 ETF (跟踪深证 100, 60 日 +21.87%)
真正的红利低波 100ETF 是 sh515100 (景顺长城)、sz159307 等.
真实 60 日数据 (新浪日 K, 截至 2026-06-25):
    sh515100 红利低波 100ETF 景顺 = -9.65%
    sh512890 红利低波 ETF 华泰柏瑞 = -8.35%
    sh510880 红利 ETF 易方达 = -8.02%
    sh510300 沪深 300ETF = +12.48%
    国证现金流指数 980092 = -16.94%

本脚本只重生成 cards/01_cover.png 和 cards/04_fcf_vs_dividend.png,
不动其它 6 页, 不重跑 analyze. 数据更正幅度太大 (+21.9% -> -9.7%),
反共识叙事核心点从 "风格问题 (现金流 vs 红利低波)" 改为
"价值股全线扑街, 只有沪深 300 在涨".

用户决策: 只修 page4 卡片和文案里的数字, 其它页和 PDF 维持
(PDF 内同样有错数据但按用户指示保留).
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle

plt.rcParams["font.sans-serif"] = ["Droid Sans Fallback", "WenQuanYi Micro Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

OUT = Path("/das/user/QYJI/quant/output/2026-06-26/fcf-contrarian")
DATA_DIR = OUT / "data"
CARD_DIR = OUT / "cards"

with open(DATA_DIR / "summary.json", "r", encoding="utf-8") as f:
    S = json.load(f)

# === 真实数据 patch (替代 sz159211 富国深证 ETF 的污染值) ===
# 来源: 新浪日 K http://money.finance.sina.com.cn/.../getKLineData symbol=sh515100
# 截至 2026-06-25 收盘
DVD_LOWVOL_60D_REAL = -0.0965   # 红利低波 100ETF (sh515100 景顺长城)
DVD_LOWVOL_YTD_REAL = -0.0984

# patch headline 仅供本脚本两张卡使用 (不写回 summary.json)
S["headline"]["dvd_lowvol_60d"] = DVD_LOWVOL_60D_REAL
S["headline"]["dvd_lowvol_ytd"] = DVD_LOWVOL_YTD_REAL
S["headline"]["underperf_pp_vs_dvd"] = S["headline"]["fcf_index_60d"] - DVD_LOWVOL_60D_REAL

# ============ 样式工具 (复刻自 fcf_contrarian_cards.py) ============
C = {
    "bg":     "#0d1117",
    "card":   "#161b22",
    "border": "#30363d",
    "text":   "#c9d1d9",
    "muted":  "#8b949e",
    "blue":   "#58a6ff",
    "green":  "#3fb950",
    "red":    "#f85149",
    "orange": "#d2991d",
    "purple": "#bc8cff",
    "gold":   "#f0c040",
    "cyan":   "#56d4dd",
    "pink":   "#ff7b72",
    # A 股配色: 红 = 涨/正, 绿 = 跌/负
    "up":     "#f85149",
    "down":   "#3fb950",
}
CARD_W, CARD_H, DPI = 7.2, 9.6, 200
TOTAL_PAGES = 8
BRAND = "复旦杰伦"


def new_card():
    fig, ax = plt.subplots(figsize=(CARD_W, CARD_H), dpi=DPI)
    fig.patch.set_facecolor(C["bg"])
    ax.set_facecolor(C["bg"])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    return fig, ax


def header(ax, eyebrow, title, subtitle=None):
    ax.text(0.06, 0.955, eyebrow, fontsize=13, color=C["muted"], transform=ax.transAxes, fontweight="bold")
    ax.text(0.06, 0.905, title, fontsize=26, color=C["text"], transform=ax.transAxes, fontweight="bold")
    if subtitle:
        ax.text(0.06, 0.865, subtitle, fontsize=14.5, color=C["muted"], transform=ax.transAxes)


def footer(ax, page):
    ax.axhline(0.04, xmin=0.06, xmax=0.94, color=C["border"], lw=0.5, alpha=0.5)
    ax.text(0.06, 0.018, "* 历史回测不代表未来 · 不构成投资建议",
            fontsize=10, color=C["muted"], transform=ax.transAxes)
    ax.text(0.94, 0.018, f"{page}/{TOTAL_PAGES}",
            fontsize=10.5, color=C["muted"], transform=ax.transAxes, ha="right")
    ax.text(0.94, 0.038, f"@{BRAND}",
            fontsize=10, color=C["muted"], transform=ax.transAxes, ha="right", fontstyle="italic")


def card_box(ax, x, y, w, h, fc=None, ec=None, lw=1.0, alpha=1.0):
    fc = fc or C["card"]
    ec = ec or C["border"]
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.005,rounding_size=0.015",
                         fc=fc, ec=ec, lw=lw, alpha=alpha, transform=ax.transAxes)
    ax.add_patch(box)


def fmt_pct(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "N/A"
    return f"{v:+.2%}"


def save(fig, name):
    p = CARD_DIR / name
    fig.savefig(p, dpi=DPI, facecolor=C["bg"], bbox_inches=None, pad_inches=0)
    plt.close(fig)
    print(f"[OK] {p}")


# ============ PAGE 1: 封面 ============
def page_1():
    fig, ax = new_card()
    ax.text(0.06, 0.94, "反共识 · 自由现金流 ETF 真相", fontsize=14,
            color=C["red"], transform=ax.transAxes, fontweight="bold")

    ax.text(0.5, 0.83, "自由现金流",
            fontsize=46, color=C["text"], transform=ax.transAxes,
            ha="center", fontweight="bold")
    ax.text(0.5, 0.755, "不是红利的升级版",
            fontsize=34, color=C["red"], transform=ax.transAxes,
            ha="center", fontweight="bold")

    ax.text(0.5, 0.700, "五只产品走势接近 · 风险集中在持仓",
            fontsize=15.5, color=C["muted"], transform=ax.transAxes,
            ha="center")

    # Hero: 现金流 vs 沪深 300 (新主对比: 一跌一涨)
    card_box(ax, 0.07, 0.42, 0.41, 0.21, fc="#1a1f26")
    ax.text(0.275, 0.605, "国证自由现金流指数", fontsize=13, color=C["muted"],
            transform=ax.transAxes, ha="center")
    ax.text(0.275, 0.555, "近 60 日", fontsize=13, color=C["muted"],
            transform=ax.transAxes, ha="center")
    fcf60 = S["headline"]["fcf_index_60d"]
    ax.text(0.275, 0.475, fmt_pct(fcf60), fontsize=38, color=C["down"],
            transform=ax.transAxes, ha="center", fontweight="bold")

    card_box(ax, 0.52, 0.42, 0.41, 0.21, fc="#1a1f26")
    ax.text(0.725, 0.605, "沪深 300", fontsize=13, color=C["muted"],
            transform=ax.transAxes, ha="center")
    ax.text(0.725, 0.555, "近 60 日", fontsize=13, color=C["muted"],
            transform=ax.transAxes, ha="center")
    hs300_60 = S["headline"]["hs300_60d"]
    ax.text(0.725, 0.475, fmt_pct(hs300_60), fontsize=38, color=C["up"],
            transform=ax.transAxes, ha="center", fontweight="bold")

    gap = (fcf60 - hs300_60) * 100
    ax.text(0.5, 0.475, "→", fontsize=26, color=C["muted"],
            transform=ax.transAxes, ha="center")
    ax.text(0.5, 0.385, f"差距 {abs(gap):.1f} 个百分点",
            fontsize=15.5, color=C["gold"], transform=ax.transAxes,
            ha="center", fontweight="bold")

    ax.text(0.06, 0.330, "TL;DR · 你需要先知道的 3 件事",
            fontsize=14, color=C["text"], transform=ax.transAxes,
            fontweight="bold")
    dvd_lowvol = S["headline"]["dvd_lowvol_60d"] * 100
    tldr = [
                ("01", "五只现金流 ETF 走势接近, 不是红利低波替代品", C["red"]),
        ("02", "国证现金流指数 2024 年 12 月才发布 · ETF 集中 2025 上市 → 发布即顶点", C["orange"]),
                ("03", f"现金流 ETF 近 60 日集体 -15%~-17% · 风格 ≠ 红利低波", C["gold"]),
    ]
    yy = 0.270
    for num, text, color in tldr:
        ax.text(0.085, yy, num, fontsize=22, color=color,
                transform=ax.transAxes, fontweight="bold")
        ax.text(0.155, yy + 0.005, text, fontsize=13, color=C["text"],
                transform=ax.transAxes)
        yy -= 0.060

    ax.text(0.5, 0.075, "数据截至 2026-06-25 · 共 8 页深度复盘",
            fontsize=11.5, color=C["muted"], transform=ax.transAxes, ha="center")

    footer(ax, 1)
    save(fig, "01_cover.png")


# ============ PAGE 4: 现金流 vs 红利 vs 红利低波 ============
def page_4():
    fig, ax = new_card()
    header(ax, "PAGE 04 · 你以为现金流 = 红利?",
           "现金流跟红利一起跌, 沪深 300 在涨",
           "近 60 日三类\"防御资产\" + 沪深 300 对比")

    # 4 柱: 现金流指数 / 红利ETF / 红利低波 100 / 沪深300
    # A 股配色: 跌用绿色阶 (深=程度大, 浅=程度小), 涨用红色
    items = [
        ("国证现金流指数", S["headline"]["fcf_index_60d"], C["down"]),       # 深绿大跌
        ("红利低波 100", S["headline"]["dvd_lowvol_60d"], "#5fbf6b"),        # 中绿
        ("红利 ETF", S["benchmarks"]["sh510880"]["ret_60d"], "#7ac686"),     # 浅绿
        ("沪深 300", S["headline"]["hs300_60d"], C["up"]),                    # 红涨
    ]
    items.sort(key=lambda x: x[1])

    n = len(items)
    bar_w = 0.13
    gap = (0.82 - n * bar_w) / (n - 1)
    base_y = 0.55
    max_h = 0.22
    vmax = max(abs(v) for _, v, _ in items)

    for i, (name, v, color) in enumerate(items):
        x = 0.10 + i * (bar_w + gap)
        h = abs(v) / vmax * max_h
        if v >= 0:
            rect = Rectangle((x, base_y), bar_w, h, fc=color, ec="none", transform=ax.transAxes)
            ax.add_patch(rect)
            ax.text(x + bar_w / 2, base_y + h + 0.020, f"{v:+.1%}",
                    fontsize=17, color=color, transform=ax.transAxes,
                    ha="center", fontweight="bold")
        else:
            rect = Rectangle((x, base_y - h), bar_w, h, fc=color, ec="none", transform=ax.transAxes)
            ax.add_patch(rect)
            ax.text(x + bar_w / 2, base_y - h - 0.020, f"{v:+.1%}",
                    fontsize=17, color=color, transform=ax.transAxes,
                    ha="center", va="top", fontweight="bold")
        ax.text(x + bar_w / 2, 0.32, name, fontsize=12, color=C["text"],
                transform=ax.transAxes, ha="center")

    # 0 线
    ax.plot([0.07, 0.93], [base_y, base_y], color=C["border"], lw=1, transform=ax.transAxes)
    ax.text(0.06, base_y - 0.005, "0%", fontsize=10.5, color=C["muted"],
            transform=ax.transAxes, ha="right", va="center")

    # 关键洞察卡
    card_box(ax, 0.06, 0.13, 0.88, 0.16, fc="#1a1f26")
    ax.text(0.5, 0.265, "现金流跟红利一起被抛弃 · 资金全在沪深 300",
            fontsize=15.5, color=C["gold"], transform=ax.transAxes,
            ha="center", fontweight="bold")
    fcf = S["headline"]["fcf_index_60d"] * 100
    dvd = S["headline"]["dvd_lowvol_60d"] * 100
    hs = S["headline"]["hs300_60d"] * 100
    ax.text(0.5, 0.225, f"现金流 {fcf:.1f}% · 红利低波 {dvd:.1f}% · 沪深 300 +{hs:.1f}%",
            fontsize=13, color=C["text"], transform=ax.transAxes, ha="center")
    ax.text(0.5, 0.190, "→ 不是\"价值/红利在涨, 现金流在跌\" · 是价值股整体走弱",
            fontsize=13, color=C["red"], transform=ax.transAxes, ha="center")
    ax.text(0.5, 0.155, "现金流跑输沪深 300 整整 29 pp · 跟红利低波也拉开 7 pp",
            fontsize=11.5, color=C["muted"], transform=ax.transAxes, ha="center")

    footer(ax, 4)
    save(fig, "04_fcf_vs_dividend.png")


if __name__ == "__main__":
    print("=" * 60)
    print("FCF page1 + page4 数据修复")
    print(f"  dvd_lowvol_60d: 原 +21.87% (错-用了富国深证 sz159211)")
    print(f"                  实 {DVD_LOWVOL_60D_REAL*100:+.2f}% (红利低波 100ETF sh515100)")
    print("=" * 60)
    page_1()
    page_4()
    print("done.")
