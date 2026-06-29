"""FCF 反共识帖 — page2 (5 只 ETF 横向条形图) 排版修复.

视觉问题
--------
1. 负值百分比标签 (-8.9% / -16.8% / -16.8%) 压在绿色柱体左端,
   且同色, 几乎看不清.
2. 顶部副标题和图表小标题 "近 60 日涨跌幅" 垂直距离过近, 视觉拥挤.

修复
----
- 负值标签从柱体外左侧改为柱体右侧 (紧贴 mid_x 右边的空白区),
  和柱体分离, 不再撞色.
- mid_x 右移 (0.55 -> 0.60), 给柱子留更多左侧空间.
- bar_max_w 缩窄 (0.32 -> 0.26).
- "近 60 日涨跌幅" 小标题上移到 0.86, 避开 header 副标题.
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

C = {
    "bg":     "#0d1117",
    "card":   "#161b22",
    "border": "#30363d",
    "text":   "#c9d1d9",
    "muted":  "#8b949e",
    "gold":   "#f0c040",
    "up":     "#f85149",  # 红 = 涨
    "down":   "#3fb950",  # 绿 = 跌
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


def save(fig, name):
    p = CARD_DIR / name
    fig.savefig(p, dpi=DPI, facecolor=C["bg"], bbox_inches=None, pad_inches=0)
    plt.close(fig)
    print(f"[OK] {p}")


# ============ PAGE 2: 5 只现金流 ETF ============
def page_2():
    fig, ax = new_card()
    header(ax, "PAGE 02 · 现金流 ETF 横向对比",
           "5 只产品走势高度趋同",
           "近 60 日基本都落在 -15%~-17%")

    # "近 60 日涨跌幅" 小标题: 对齐到 mid_x (零轴) 正上方而非整卡居中
    ax.text(0.52, 0.805, "近 60 日涨跌幅", fontsize=13, color=C["muted"],
            transform=ax.transAxes, ha="center")

    etfs = [
        ("563390", "全指现金流", "华泰柏瑞"),
        ("159201", "自由现金流", "华夏"),
        ("159222", "自由现金流", "易方达"),
        ("159221", "现金流", "嘉实"),
        ("159223", "现金流", "永赢"),
    ]
    SYM_KEY = {"563390": "sh563390", "159201": "sz159201", "159222": "sz159222",
               "159221": "sz159221", "159223": "sz159223"}

    data = [(c, name, brand, S["fcf_etfs"][SYM_KEY[c]]["ret_60d"]) for c, name, brand in etfs]
    data.sort(key=lambda x: -x[3])

    y_top = 0.76
    y_bot = 0.36
    y_step = (y_top - y_bot) / (len(data) - 1)
    max_abs = max(abs(d[3]) for d in data)

    # 关键改动: mid_x 在卡片中央偏左 (0.52), 柱子收窄
    # 让 ETF 名字栏 (左侧 0.06~0.40 区) 不会过空, 右侧 +17.6% 也不贴边
    mid_x = 0.52
    bar_max_w = 0.26
    rank_colors = ["#58a6ff", "#56d4dd", C["gold"], "#d2991d", "#ff7b72"]
    rank_tags = ["相对抗跌", "接近均值", "接近均值", "偏弱", "偏弱"]

    for i, (code, name, brand, ret) in enumerate(data):
        y = y_top - i * y_step
        # 左侧 ETF 名 + 代码 (右对齐到 mid_x 之前)
        ax.text(0.06, y + 0.012, f"{name}", fontsize=15, color=C["text"],
                transform=ax.transAxes, fontweight="bold")
        ax.text(0.06, y - 0.018, f"{code} · {brand}", fontsize=11, color=C["muted"],
                transform=ax.transAxes)

        # 中线 (0%)
        ax.plot([mid_x, mid_x], [y - 0.02, y + 0.02], color=C["border"], lw=1, transform=ax.transAxes)

        # 灰色轨道 + 组内排名色, 避免全负收益时整页只有一种绿色
        bar_w = (abs(ret) / max_abs) * bar_max_w
        color = rank_colors[i]
        track = Rectangle((mid_x - bar_max_w, y - 0.014), bar_max_w, 0.028,
                  fc="#21262d", ec=C["border"], lw=0.5,
                  transform=ax.transAxes)
        ax.add_patch(track)
        rect = Rectangle((mid_x - bar_w, y - 0.012), bar_w, 0.024, fc=color, ec="none",
                 transform=ax.transAxes)
        ax.add_patch(rect)
        ax.text(mid_x + 0.018, y, rank_tags[i], fontsize=10.5, color=color,
            transform=ax.transAxes, va="center", ha="left", fontweight="bold")
        ax.text(0.88, y, f"{ret:+.1%}", fontsize=15, color=color,
            transform=ax.transAxes, va="center", ha="right", fontweight="bold")

    # 底部点睛卡
    card_box(ax, 0.06, 0.16, 0.88, 0.13, fc="#1a1f26", ec=C["gold"], lw=1.2)
    top = data[0]
    bot = data[-1]
    gap_pp = (top[3] - bot[3]) * 100
    ax.text(0.5, 0.252, f"组内最强 vs 最弱 差距 {gap_pp:.1f} 个百分点",
            fontsize=16, color=C["gold"], transform=ax.transAxes,
            ha="center", fontweight="bold")
    ax.text(0.5, 0.212, f"{top[1]} {top[3]*100:+.1f}%   vs   {bot[1]} {bot[3]*100:+.1f}%",
            fontsize=13, color=C["text"], transform=ax.transAxes, ha="center")
    ax.text(0.5, 0.180, "组内走势接近, 差异主要看规模/流动性/折溢价",
            fontsize=11.5, color=C["muted"], transform=ax.transAxes, ha="center")

    footer(ax, 2)
    save(fig, "02_5etfs.png")


if __name__ == "__main__":
    page_2()
    print("done.")
