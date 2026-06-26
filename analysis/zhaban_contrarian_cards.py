"""炸板潮反共识帖 · 8 页深色小红书卡片 — 2026-06-26 早盘"""

from __future__ import annotations

import json
import os
from pathlib import Path

for _k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
    os.environ.pop(_k, None)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np
import pandas as pd

plt.rcParams["font.sans-serif"] = ["Droid Sans Fallback", "WenQuanYi Micro Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

OUT = Path("/das/user/QYJI/quant/output/2026-06-26/morning-card")
CARD_DIR = OUT / "cards"
CARD_DIR.mkdir(parents=True, exist_ok=True)

with open(OUT / "summary.json", "r", encoding="utf-8") as f:
    S = json.load(f)

H = S["headline_numbers"]
LB = S["lb_distribution"]
ZTO = S["zt_open_top10"]
ZBA = S["zb_amp_top10"]
MACRO = S["macro"]
INDL = S["industry_loss_top"]
ZT_IND = S["zt_industry_top"]

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


def header(ax, eyebrow: str, title: str, subtitle: str | None = None):
    ax.text(0.06, 0.955, eyebrow, fontsize=10, color=C["muted"], transform=ax.transAxes,
            fontweight="bold")
    ax.text(0.06, 0.905, title, fontsize=22, color=C["text"], transform=ax.transAxes,
            fontweight="bold")
    if subtitle:
        ax.text(0.06, 0.865, subtitle, fontsize=11.5, color=C["muted"], transform=ax.transAxes)


def footer(ax, page: int):
    ax.axhline(0.04, xmin=0.06, xmax=0.94, color=C["border"], lw=0.5, alpha=0.5)
    ax.text(0.06, 0.018,
            "* 数据为 2026-06-26 早盘 11:30 快照 · 不构成投资建议",
            fontsize=7.5, color=C["muted"], transform=ax.transAxes)
    ax.text(0.94, 0.018, f"{page}/{TOTAL_PAGES}",
            fontsize=8, color=C["muted"], transform=ax.transAxes, ha="right")
    ax.text(0.94, 0.038, f"@{BRAND}",
            fontsize=7.5, color=C["muted"], transform=ax.transAxes, ha="right",
            fontstyle="italic")


def pill(ax, x, y, text, fc, fg="#0d1117", fontsize=10):
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
            color=fg, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.35", fc=fc, ec="none"),
            transform=ax.transAxes)


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


# ============ PAGE 1: 封面 — 双数字大对比 ============
def page_1():
    fig, ax = new_card()
    # eyebrow
    ax.text(0.06, 0.945, "反共识 · 早盘炸板潮真相 · 06-26", fontsize=11,
            color=C["red"], transform=ax.transAxes, fontweight="bold")

    # 主标题
    ax.text(0.5, 0.855, "你以为今天涨停板",
            fontsize=24, color=C["text"], transform=ax.transAxes,
            ha="center", fontweight="bold")
    ax.text(0.5, 0.795, "都是赢家?",
            fontsize=32, color=C["red"], transform=ax.transAxes,
            ha="center", fontweight="bold")

    # 副标题
    ax.text(0.5, 0.730, "大盘 -2.14% / 创业板 -3.72% / 4600 只下跌",
            fontsize=11, color=C["muted"], transform=ax.transAxes, ha="center")
    ax.text(0.5, 0.700, "但凑出了 39 个涨停 + 36 个炸板", fontsize=11,
            color=C["muted"], transform=ax.transAxes, ha="center")

    # 双数字大对比卡
    box_y, box_h = 0.34, 0.32
    # 左: 涨停 39
    card_box(ax, 0.08, box_y, 0.40, box_h, fc="#1a2a1a", ec=C["green"], lw=1.5)
    ax.text(0.28, box_y + 0.26, "涨停", ha="center", fontsize=13,
            color=C["green"], transform=ax.transAxes, fontweight="bold")
    ax.text(0.28, box_y + 0.13, f"{H['n_zt']}", ha="center", fontsize=80,
            color=C["green"], transform=ax.transAxes, fontweight="bold")
    ax.text(0.28, box_y + 0.04, "看着像赢家", ha="center", fontsize=11,
            color=C["muted"], transform=ax.transAxes)

    # 右: 炸板 36
    card_box(ax, 0.52, box_y, 0.40, box_h, fc="#2a1a1a", ec=C["red"], lw=1.5)
    ax.text(0.72, box_y + 0.26, "炸板", ha="center", fontsize=13,
            color=C["red"], transform=ax.transAxes, fontweight="bold")
    ax.text(0.72, box_y + 0.13, f"{H['n_zb']}", ha="center", fontsize=80,
            color=C["red"], transform=ax.transAxes, fontweight="bold")
    ax.text(0.72, box_y + 0.04, "上午曾涨停, 没守住", ha="center", fontsize=11,
            color=C["muted"], transform=ax.transAxes)

    # 中间冒号
    ax.text(0.5, box_y + 0.15, "VS", ha="center", fontsize=18,
            color=C["muted"], transform=ax.transAxes, fontweight="bold")

    # 底部 punch
    card_box(ax, 0.06, 0.085, 0.88, 0.225, fc=C["card"], ec=C["border"])
    ax.text(0.5, 0.279, "更扎心:", ha="center", fontsize=12,
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.5, 0.235, f"涨停的 {H['n_zt']} 只里 · {H['n_zt_with_open']} 只当日炸过封板",
            ha="center", fontsize=14.5, color=C["text"], transform=ax.transAxes,
            fontweight="bold")
    # 大号 54% 锚点
    ax.text(0.36, 0.165, f"{H['zt_open_pct']:.0f}%", ha="center", fontsize=44,
            color=C["orange"], transform=ax.transAxes, fontweight="bold")
    ax.text(0.36, 0.117, "涨停股当日炸过", ha="center", fontsize=10,
            color=C["muted"], transform=ax.transAxes)
    # 右侧文本
    ax.text(0.62, 0.190, "= 反复打开、勉强封回",
            ha="left", fontsize=11.5, color=C["text"], transform=ax.transAxes)
    ax.text(0.62, 0.160, "= 看着是涨停, 其实是绞肉机",
            ha="left", fontsize=11.5, color=C["orange"], transform=ax.transAxes,
            fontweight="bold")
    pill(ax, 0.745, 0.115, f"五方光电单日炸板 {H['max_open_count']} 次", C["red"],
         fg="#fff5f5", fontsize=10)

    footer(ax, 1)
    save(fig, "page_1_封面.png")


# ============ PAGE 2: 大盘背景 — 流动性陷阱 ============
def page_2():
    fig, ax = new_card()
    header(ax, "01 · 大盘背景",
           "今天是个什么样的市场?",
           "三大指数齐跌 · 行业普跌 · 资金避险")

    # 三大指数卡
    idx_y = 0.71
    idx_h = 0.10
    items = [
        ("沪指", MACRO["sh_pt"], MACRO["sh_chg_pct"]),
        ("深成指", MACRO["sz_pt"], MACRO["sz_chg_pct"]),
        ("创业板", MACRO["cyb_pt"], MACRO["cyb_chg_pct"]),
    ]
    w = 0.275
    for i, (nm, pt, ch) in enumerate(items):
        x0 = 0.06 + i * (w + 0.015)
        card_box(ax, x0, idx_y, w, idx_h, fc=C["card"], ec=C["red"], lw=1.2)
        ax.text(x0 + w/2, idx_y + idx_h - 0.022, nm, ha="center", fontsize=10.5,
                color=C["muted"], transform=ax.transAxes)
        ax.text(x0 + w/2, idx_y + idx_h - 0.057, f"{pt:.0f}", ha="center",
                fontsize=14, color=C["text"], transform=ax.transAxes, fontweight="bold")
        ax.text(x0 + w/2, idx_y + 0.015, f"{ch:+.2f}%", ha="center",
                fontsize=16, color=C["red"], transform=ax.transAxes, fontweight="bold")

    # 关键数字: 4600 跌
    card_box(ax, 0.06, 0.555, 0.88, 0.13, fc="#2a1a1a", ec=C["red"], lw=1.2)
    ax.text(0.5, 0.640, f"全市场近 {MACRO['n_decline']} 只下跌", ha="center", fontsize=16,
            color=C["red"], transform=ax.transAxes, fontweight="bold")
    ax.text(0.5, 0.598, "两市半日成交 2.43 万亿 · 较前一日放量 33 亿",
            ha="center", fontsize=11, color=C["muted"], transform=ax.transAxes)
    ax.text(0.5, 0.570, "= 一边在跑路, 一边在博弈剩下的题材", ha="center", fontsize=11,
            color=C["orange"], transform=ax.transAxes, fontstyle="italic")

    # 行业跌幅 TOP6
    ax.text(0.06, 0.510, "行业跌幅 TOP6 (主力净流出 · 亿)", fontsize=11.5,
            color=C["muted"], transform=ax.transAxes, fontweight="bold")
    bar_top = 0.475
    bar_h = 0.045
    sub = INDL[:6]
    max_loss = abs(min(r["涨跌幅"] for r in sub))
    for i, r in enumerate(sub):
        y0 = bar_top - i * (bar_h + 0.015)
        nm = r["板块名称"]
        ch = r["涨跌幅"]
        mn = r["主力净流入"]
        # bar (右负向)
        bar_len = abs(ch) / max_loss * 0.45
        ax.add_patch(Rectangle((0.30, y0), bar_len, bar_h - 0.005,
                               fc=C["red"], ec="none", alpha=0.7,
                               transform=ax.transAxes))
        ax.text(0.06, y0 + (bar_h-0.005)/2, nm, ha="left", va="center", fontsize=10.5,
                color=C["text"], transform=ax.transAxes)
        ax.text(0.30 + bar_len + 0.01, y0 + (bar_h-0.005)/2, f"{ch:.2f}%",
                ha="left", va="center", fontsize=10.5, color=C["red"],
                transform=ax.transAxes, fontweight="bold")
        # main net
        mn_yi = mn / 1e8
        col = C["red"] if mn_yi < 0 else C["green"]
        ax.text(0.94, y0 + (bar_h-0.005)/2, f"{mn_yi:+.1f}亿", ha="right",
                va="center", fontsize=10, color=col, transform=ax.transAxes,
                fontweight="bold")

    # 底部 punch
    card_box(ax, 0.06, 0.075, 0.88, 0.075, fc=C["card"], ec=C["orange"], lw=1.0)
    ax.text(0.5, 0.115, "这种环境下『涨停板』≠ 题材爆发", ha="center", fontsize=12,
            color=C["orange"], transform=ax.transAxes, fontweight="bold")
    ax.text(0.5, 0.090, "= 资金避险后的『窄活水』里, 几个游资在博弈剩下的羊毛",
            ha="center", fontsize=10, color=C["muted"], transform=ax.transAxes)

    footer(ax, 2)
    save(fig, "page_2_大盘背景.png")


# ============ PAGE 3: 涨停结构剖析 ============
def page_3():
    fig, ax = new_card()
    header(ax, "02 · 涨停结构拆解",
           f"{H['n_zt']} 个涨停里, 真稳的只有 {H['n_zt'] - H['n_zt_with_open']} 个",
           "拆开『涨停』这张皮, 看里面是稳封还是反复横跳")

    # 三层金字塔条形图
    levels = [
        (f"{H['n_zt']} 涨停 (表面)", H['n_zt'], C["green"], "看着都是赢家"),
        (f"{H['n_zt_with_open']} 当日炸过封板", H['n_zt_with_open'], C["orange"],
         f"占 {H['zt_open_pct']:.0f}% · 封了又开"),
        (f"{H['n_zt_open_3plus']} 炸 ≥3 次 (极不稳)", H['n_zt_open_3plus'], C["red"],
         f"占 {H['n_zt_open_3plus']/H['n_zt']*100:.0f}% · 心跳冲浪手"),
        (f"{H['top_lb']['n']} 板龙头数量: 1", 1, C["pink"],
         f"{H['top_lb']['name']} ({H['top_lb']['code']}) · 唯一真龙"),
    ]

    bar_top = 0.755
    bar_h = 0.105
    max_v = H['n_zt']
    for i, (label, v, col, sub) in enumerate(levels):
        y0 = bar_top - i * (bar_h + 0.025)
        bar_len = v / max_v * 0.66
        # bar
        ax.add_patch(FancyBboxPatch((0.06, y0), bar_len, bar_h,
                                    boxstyle="round,pad=0.002,rounding_size=0.008",
                                    fc=col, ec="none", alpha=0.85,
                                    transform=ax.transAxes))
        # label inside
        ax.text(0.075, y0 + bar_h - 0.025, label, fontsize=11.5,
                color="#0d1117", transform=ax.transAxes, fontweight="bold")
        ax.text(0.075, y0 + 0.022, sub, fontsize=9.5,
                color="#0d1117", transform=ax.transAxes, alpha=0.85)
        # value (right of bar)
        ax.text(0.06 + bar_len + 0.015, y0 + bar_h/2, f"{v}", ha="left", va="center",
                fontsize=20, color=col, transform=ax.transAxes, fontweight="bold")

    # 底部点评
    card_box(ax, 0.06, 0.110, 0.88, 0.110, fc=C["card"], ec=C["red"], lw=1.0)
    ax.text(0.5, 0.190, "翻译人话:", ha="center", fontsize=11,
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.5, 0.155, f"100 个涨停里, 真稳的不到 50 个", ha="center",
            fontsize=14, color=C["text"], transform=ax.transAxes, fontweight="bold")
    ax.text(0.5, 0.122, "剩下一半是『早盘冲上去, 中午被人砸出来, 下午再勉强封住』的伪强势",
            ha="center", fontsize=10.5, color=C["orange"], transform=ax.transAxes)

    footer(ax, 3)
    save(fig, "page_3_涨停结构.png")


# ============ PAGE 4: 涨停股炸板次数 TOP10 ============
def page_4():
    fig, ax = new_card()
    header(ax, "03 · 心跳冲浪手榜",
           "涨停股里, 谁今天炸得最狠?",
           "封板被打开的次数 = 散户的心电图振幅")

    # TOP10 表
    rows = ZTO[:10]
    bar_top = 0.795
    bar_h = 0.048
    row_gap = 0.012
    max_n = max(r["炸板次数"] for r in rows)
    for i, r in enumerate(rows):
        y0 = bar_top - i * (bar_h + row_gap)
        nm = r["名称"]
        code = r["代码"]
        ind_ = r["所属行业"]
        n_open = r["炸板次数"]
        lb = r["连板数"]
        # bg row alternate
        if i % 2 == 0:
            ax.add_patch(Rectangle((0.06, y0), 0.88, bar_h - 0.003,
                                   fc=C["card"], ec="none", alpha=0.4,
                                   transform=ax.transAxes))

        # rank
        ax.text(0.075, y0 + bar_h/2, f"{i+1}", ha="left", va="center", fontsize=11,
                color=C["muted"], transform=ax.transAxes, fontweight="bold")
        # name
        ax.text(0.115, y0 + bar_h/2 + 0.008, nm, ha="left", va="center", fontsize=11,
                color=C["text"], transform=ax.transAxes, fontweight="bold")
        ax.text(0.115, y0 + bar_h/2 - 0.014, f"{code} · {ind_}", ha="left", va="center",
                fontsize=8.5, color=C["muted"], transform=ax.transAxes)
        # bar (炸板次数)
        bar_x0 = 0.42
        bar_len_max = 0.36
        bar_len = n_open / max_n * bar_len_max
        # color: ≥10 红, ≥5 橙, else 黄
        if n_open >= 15:
            col = C["red"]
        elif n_open >= 5:
            col = C["orange"]
        else:
            col = C["gold"]
        ax.add_patch(Rectangle((bar_x0, y0 + 0.005), bar_len, bar_h - 0.013,
                               fc=col, ec="none", alpha=0.85,
                               transform=ax.transAxes))
        # value
        ax.text(bar_x0 + bar_len + 0.008, y0 + bar_h/2, f"{n_open}次",
                ha="left", va="center", fontsize=11, color=col,
                transform=ax.transAxes, fontweight="bold")
        # 连板数
        ax.text(0.93, y0 + bar_h/2, f"{lb}板", ha="right", va="center",
                fontsize=10.5, color=C["cyan"], transform=ax.transAxes,
                fontweight="bold")

    # 表头注解
    ax.text(0.115, 0.844, "股票", fontsize=9, color=C["muted"], transform=ax.transAxes)
    ax.text(0.42, 0.844, "当日炸板次数", fontsize=9, color=C["muted"], transform=ax.transAxes)
    ax.text(0.93, 0.844, "连板", fontsize=9, color=C["muted"], transform=ax.transAxes, ha="right")

    # 底部点评
    card_box(ax, 0.06, 0.085, 0.88, 0.135, fc=C["card"], ec=C["red"], lw=1.0)
    ax.text(0.5, 0.190, f"最炸 · {H['max_open_name']} ({H['max_open_code']})",
            ha="center", fontsize=12.5, color=C["red"], transform=ax.transAxes,
            fontweight="bold")
    ax.text(0.5, 0.158, f"全天封板被打开 {H['max_open_count']} 次", ha="center",
            fontsize=15, color=C["text"], transform=ax.transAxes, fontweight="bold")
    ax.text(0.5, 0.122, "= 反复『封→开→封→开』, 中间每一次开板, 都有人卖出止损 / 有人冲进去接盘",
            ha="center", fontsize=10, color=C["muted"], transform=ax.transAxes)
    ax.text(0.5, 0.098, "这种股看着是涨停, 实际是绞肉机",
            ha="center", fontsize=10.5, color=C["orange"], transform=ax.transAxes,
            fontstyle="italic")

    footer(ax, 4)
    save(fig, "page_4_炸板次数top10.png")


# ============ PAGE 5: 连板分布金字塔 ============
def page_5():
    fig, ax = new_card()
    header(ax, "04 · 连板天梯结构",
           "题材无龙头 · 全是『一日游』",
           f"{H['n_zt']} 涨停 · {H['first_board']} 首板 ({H['first_board_pct']:.0f}%) · 只 1 个 6 板")

    # 金字塔条形 (从 6 板到 1 板)
    sorted_lb = sorted(LB.items(), key=lambda x: -int(x[0]))
    bar_top = 0.770
    bar_h = 0.085
    max_v = max(LB.values())

    for i, (lvl, cnt) in enumerate(sorted_lb):
        y0 = bar_top - i * (bar_h + 0.022)
        lvl = int(lvl)
        bar_len = cnt / max_v * 0.66
        if lvl >= 4:
            col = C["pink"]
        elif lvl == 3:
            col = C["orange"]
        elif lvl == 2:
            col = C["gold"]
        else:
            col = C["cyan"]
        # bar (右对齐, 居中视觉 — 但这里左对齐展示金字塔)
        ax.add_patch(FancyBboxPatch((0.20, y0), bar_len, bar_h,
                                    boxstyle="round,pad=0.002,rounding_size=0.008",
                                    fc=col, ec="none", alpha=0.85,
                                    transform=ax.transAxes))
        # label left
        ax.text(0.06, y0 + bar_h/2, f"{lvl} 板", ha="left", va="center",
                fontsize=14, color=col, transform=ax.transAxes, fontweight="bold")
        # count inside bar
        ax.text(0.21, y0 + bar_h/2, f"{cnt} 只", ha="left", va="center", fontsize=12,
                color="#0d1117", transform=ax.transAxes, fontweight="bold")
        # right side: 占比 + 代表
        pct = cnt / H['n_zt'] * 100
        ax.text(0.94, y0 + bar_h/2 + 0.008, f"占 {pct:.0f}%", ha="right", va="center",
                fontsize=11, color=C["text"], transform=ax.transAxes, fontweight="bold")
        if lvl == H['top_lb']['n']:
            ax.text(0.94, y0 + bar_h/2 - 0.018, f"{H['top_lb']['name']}",
                    ha="right", va="center", fontsize=9, color=C["pink"],
                    transform=ax.transAxes)

    # 底部对比
    card_box(ax, 0.06, 0.090, 0.88, 0.155, fc=C["card"], ec=C["orange"], lw=1.0)
    ax.text(0.5, 0.220, "什么叫『健康的涨停潮』?", ha="center", fontsize=11.5,
            color=C["muted"], transform=ax.transAxes, fontweight="bold")
    ax.text(0.5, 0.180, "上一轮 AI 高潮: 5 个龙头, 个个 8-10 板, 题材接力",
            ha="center", fontsize=10.5, color=C["green"], transform=ax.transAxes)
    ax.text(0.5, 0.150, "今天: 82% 首板, 6 板就 1 只 (兴业科技, 还是冷门纺织制造)",
            ha="center", fontsize=10.5, color=C["red"], transform=ax.transAxes)
    ax.text(0.5, 0.115, "= 资金没共识 · 各打各的 · 不接力 = 题材活不过 2 天",
            ha="center", fontsize=11, color=C["orange"], transform=ax.transAxes,
            fontweight="bold", fontstyle="italic")

    footer(ax, 5)
    save(fig, "page_5_连板分布.png")


# ============ PAGE 6: 炸板池振幅 TOP10 ============
def page_6():
    fig, ax = new_card()
    header(ax, "05 · 早盘追涨停的散户在哪",
           f"{H['n_zb']} 只『早盘冲到涨停, 没守住』的股",
           f"振幅 TOP10 · {H['zb_amp_gt10']} 只振幅 >10% · 套人最深的现场")

    rows = ZBA[:10]
    bar_top = 0.795
    bar_h = 0.048
    row_gap = 0.012
    max_amp = max(r["振幅"] for r in rows)

    for i, r in enumerate(rows):
        y0 = bar_top - i * (bar_h + row_gap)
        nm = r["名称"]
        code = r["代码"]
        ind_ = r["所属行业"]
        amp = r["振幅"]
        cur = r["涨跌幅"]
        if i % 2 == 0:
            ax.add_patch(Rectangle((0.06, y0), 0.88, bar_h - 0.003,
                                   fc=C["card"], ec="none", alpha=0.4,
                                   transform=ax.transAxes))
        ax.text(0.075, y0 + bar_h/2, f"{i+1}", ha="left", va="center", fontsize=11,
                color=C["muted"], transform=ax.transAxes, fontweight="bold")
        ax.text(0.115, y0 + bar_h/2 + 0.008, nm, ha="left", va="center", fontsize=11,
                color=C["text"], transform=ax.transAxes, fontweight="bold")
        ax.text(0.115, y0 + bar_h/2 - 0.014, f"{code} · {ind_}", ha="left", va="center",
                fontsize=8.5, color=C["muted"], transform=ax.transAxes)
        # bar 振幅
        bar_x0 = 0.42
        bar_len_max = 0.32
        bar_len = amp / max_amp * bar_len_max
        col = C["red"] if amp >= 15 else C["orange"] if amp >= 10 else C["gold"]
        ax.add_patch(Rectangle((bar_x0, y0 + 0.005), bar_len, bar_h - 0.013,
                               fc=col, ec="none", alpha=0.85,
                               transform=ax.transAxes))
        ax.text(bar_x0 + bar_len + 0.008, y0 + bar_h/2, f"{amp:.1f}%",
                ha="left", va="center", fontsize=10.5, color=col,
                transform=ax.transAxes, fontweight="bold")
        # 当下涨幅 (右)
        cur_col = C["green"] if cur > 0 else C["red"]
        ax.text(0.935, y0 + bar_h/2, f"{cur:+.1f}%", ha="right", va="center",
                fontsize=10.5, color=cur_col, transform=ax.transAxes, fontweight="bold")

    # 表头
    ax.text(0.115, 0.844, "股票", fontsize=9, color=C["muted"], transform=ax.transAxes)
    ax.text(0.42, 0.844, "全日振幅", fontsize=9, color=C["muted"], transform=ax.transAxes)
    ax.text(0.935, 0.844, "当下涨幅", fontsize=9, color=C["muted"], transform=ax.transAxes,
            ha="right")

    # 底部点评 — 关键解读
    card_box(ax, 0.06, 0.085, 0.88, 0.135, fc=C["card"], ec=C["orange"], lw=1.0)
    ax.text(0.5, 0.190, f"最惨现场 · {H['zb_amp_max_name']}", ha="center", fontsize=12.5,
            color=C["red"], transform=ax.transAxes, fontweight="bold")
    ax.text(0.5, 0.158, f"全日振幅 {H['zb_amp_max']:.1f}% (从最高到最低跨度)", ha="center",
            fontsize=12, color=C["text"], transform=ax.transAxes, fontweight="bold")
    ax.text(0.5, 0.122, "= 上午冲到涨停 → 中午被砸下来十几个点, 追在涨停板的散户当下账面腰斩",
            ha="center", fontsize=10, color=C["muted"], transform=ax.transAxes)
    ax.text(0.5, 0.098, f"36 只里 {H['zb_amp_gt10']} 只振幅 >10% · 这是炸板潮的真实代价",
            ha="center", fontsize=10.5, color=C["orange"], transform=ax.transAxes,
            fontstyle="italic")

    footer(ax, 6)
    save(fig, "page_6_炸板振幅.png")


# ============ PAGE 7: 涨停行业分布 — 没主线 ============
def page_7():
    fig, ax = new_card()
    header(ax, "06 · 涨停行业地图",
           "题材散乱 · 没有主线",
           "热门赛道全部缺席 · 都在冷门赛道里捡羊毛")

    # 涨停行业 TOP6 vs 炸板行业 TOP5
    zt_items = list(ZT_IND.items())[:6]

    ax.text(0.06, 0.795, "今天涨停股的行业分布 (TOP6)", fontsize=12,
            color=C["muted"], transform=ax.transAxes, fontweight="bold")

    bar_top = 0.745
    bar_h = 0.058
    max_v = max(v for _, v in zt_items)

    for i, (ind_name, cnt) in enumerate(zt_items):
        y0 = bar_top - i * (bar_h + 0.013)
        bar_len = cnt / max_v * 0.55
        col = C["cyan"]
        ax.add_patch(FancyBboxPatch((0.25, y0), bar_len, bar_h,
                                    boxstyle="round,pad=0.002,rounding_size=0.008",
                                    fc=col, ec="none", alpha=0.85,
                                    transform=ax.transAxes))
        ax.text(0.06, y0 + bar_h/2, ind_name, ha="left", va="center", fontsize=11,
                color=C["text"], transform=ax.transAxes, fontweight="bold")
        ax.text(0.25 + bar_len + 0.012, y0 + bar_h/2, f"{cnt} 只",
                ha="left", va="center", fontsize=11, color=col,
                transform=ax.transAxes, fontweight="bold")

    # 中间分隔
    ax.axhline(0.355, xmin=0.06, xmax=0.94, color=C["border"], lw=0.5, alpha=0.6)

    # 对比 — 缺席的热门
    card_box(ax, 0.06, 0.090, 0.88, 0.255, fc=C["card"], ec=C["red"], lw=1.0)
    ax.text(0.5, 0.320, "对比 · 散户最热门 / 雪球讨论榜上的赛道, 今天全部缺席",
            ha="center", fontsize=11, color=C["muted"], transform=ax.transAxes,
            fontweight="bold")

    absent = [
        ("AI · CPO / 算力", "今天 -4.70% (通信领跌, 主力流出 347 亿)"),
        ("锂电 · 电池", "今天 -4.33% (主力流出 84 亿)"),
        ("贵金属 · 有色", "今天 -5.03% (主力流出 7.9 亿)"),
        ("白酒 · 消费", "茅台 / 五粮液 雪球讨论第一/六, 但价格走平"),
    ]
    yy = 0.282
    for nm, note in absent:
        ax.text(0.10, yy, "//", fontsize=11, color=C["red"], transform=ax.transAxes,
                fontweight="bold")
        ax.text(0.13, yy, nm, fontsize=11, color=C["text"], transform=ax.transAxes,
                fontweight="bold")
        ax.text(0.13, yy - 0.027, note, fontsize=9.5, color=C["muted"],
                transform=ax.transAxes)
        yy -= 0.052

    ax.text(0.5, 0.108, "涨停在哪? 专用设备 / 电力 / 光学光电 / 化学制品 — 全是冷门轮动",
            ha="center", fontsize=10.5, color=C["orange"], transform=ax.transAxes,
            fontstyle="italic")

    footer(ax, 7)
    save(fig, "page_7_行业地图.png")


# ============ PAGE 8: 总结 + 三条警示 ============
def page_8():
    fig, ax = new_card()
    header(ax, "07 · 总结 · 给散户的三条警示",
           "今天的涨停板, 不是机会 · 是绞肉机",
           "数据为 2026-06-26 11:30 早盘快照, 收盘可能变化")

    # 5 个核心数字回顾
    card_box(ax, 0.06, 0.715, 0.88, 0.115, fc=C["card"], ec=C["border"], lw=1.0)
    ax.text(0.5, 0.815, "今日 5 个核心数字", ha="center", fontsize=11,
            color=C["muted"], transform=ax.transAxes, fontweight="bold")
    # 5 column mini stats — 等距居中, 每列 center_x 固定
    nums = [
        (f"{H['n_zt']}", "涨停", C["green"]),
        (f"{H['n_zb']}", "炸板", C["red"]),
        (f"{H['zt_open_pct']:.0f}%", "涨停股炸过", C["orange"]),
        (f"{H['max_open_count']}", "单日炸板纪录", C["red"]),
        (f"{H['first_board_pct']:.0f}%", "首板占比", C["pink"]),
    ]
    # 5 列居中分布, 占 0.10 - 0.90 区间
    centers = [0.14, 0.30, 0.50, 0.70, 0.86]
    for cx, (v, lab, col) in zip(centers, nums):
        ax.text(cx, 0.770, v, ha="center", va="center", fontsize=22, color=col,
                transform=ax.transAxes, fontweight="bold")
        ax.text(cx, 0.733, lab, ha="center", va="center", fontsize=9, color=C["muted"],
                transform=ax.transAxes)

    # 三条警示卡
    warnings = [
        ("01", "看『涨停股池』而不是看『涨停板』",
         f"东财涨停池标记『炸板次数』 — 今天 {H['n_zt_with_open']}/{H['n_zt']} 涨停股炸过封板. "
         f"封板≠稳, 看次数比看名单重要."),
        ("02", "首板 ≠ 龙头, 别一上来就追",
         f"今天 {H['first_board']} 首板 ({H['first_board_pct']:.0f}%), "
         f"统计上首板续板成功率 ~30%. 龙头要 3 板+确认, 不是 1 板就上车."),
        ("03", "大盘环境 > 个股逻辑",
         "创业板 -3.72% / 4600 跌的日子里, 涨停股 = 资金避险后博弈剩余羊毛. "
         "周末若没增量, 下周一涨停股容易高开低走."),
    ]
    yy = 0.660
    for tag, title, body in warnings:
        card_box(ax, 0.06, yy - 0.135, 0.88, 0.135, fc=C["card"], ec=C["border"], lw=1.0)
        ax.text(0.085, yy - 0.030, tag, fontsize=18, color=C["orange"],
                transform=ax.transAxes, fontweight="bold")
        ax.text(0.145, yy - 0.028, title, fontsize=12.5, color=C["text"],
                transform=ax.transAxes, fontweight="bold")
        ax.text(0.145, yy - 0.062, body, fontsize=9.5, color=C["muted"],
                transform=ax.transAxes, wrap=True)
        yy -= 0.145

    # 底部品牌 + 数据来源
    card_box(ax, 0.06, 0.075, 0.88, 0.080, fc="#1a1a2e", ec=C["purple"], lw=1.0)
    ax.text(0.5, 0.125, "本期数据 · 东方财富涨停池 / 炸板池 / 行业板块 (sina + push2)",
            ha="center", fontsize=9.5, color=C["muted"], transform=ax.transAxes)
    ax.text(0.5, 0.097, f"反共识不是反对, 是把『散户共识』和『数据真相』摆一起 — @{BRAND}",
            ha="center", fontsize=10, color=C["purple"], transform=ax.transAxes,
            fontweight="bold", fontstyle="italic")

    footer(ax, 8)
    save(fig, "page_8_总结.png")


if __name__ == "__main__":
    page_1()
    page_2()
    page_3()
    page_4()
    page_5()
    page_6()
    page_7()
    page_8()
    print(f"\n[DONE] 8 张卡 -> {CARD_DIR}")
