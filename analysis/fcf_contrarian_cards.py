"""现金流反共识 8 页深色卡片渲染 — 2026-06-26."""

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

OUT = Path("/das/user/QYJI/quant/output/2026-06-26/fcf-contrarian")
CARD_DIR = OUT / "cards"
DATA_DIR = OUT / "data"
CARD_DIR.mkdir(parents=True, exist_ok=True)

with open(DATA_DIR / "summary.json", "r", encoding="utf-8") as f:
    S = json.load(f)

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
    # A 股配色: 红 = 涨/正, 绿 = 跌/负 (与美股相反)
    "up":     "#f85149",  # 涨幅 / 正值 / 利好
    "down":   "#3fb950",  # 跌幅 / 负值 / 警示
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
    # 撑满 figure (干掉默认 matplotlib 的 ~12% margin), 让 transAxes 坐标真到边
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    return fig, ax


def header(ax, eyebrow: str, title: str, subtitle: str | None = None):
    ax.text(0.06, 0.955, eyebrow, fontsize=13, color=C["muted"], transform=ax.transAxes,
            fontweight="bold")
    ax.text(0.06, 0.905, title, fontsize=26, color=C["text"], transform=ax.transAxes,
            fontweight="bold")
    if subtitle:
        ax.text(0.06, 0.865, subtitle, fontsize=14.5, color=C["muted"], transform=ax.transAxes)


def footer(ax, page: int):
    ax.axhline(0.04, xmin=0.06, xmax=0.94, color=C["border"], lw=0.5, alpha=0.5)
    ax.text(0.06, 0.018,
            "* 历史回测不代表未来 · 不构成投资建议",
            fontsize=10, color=C["muted"], transform=ax.transAxes)
    ax.text(0.94, 0.018, f"{page}/{TOTAL_PAGES}",
            fontsize=10.5, color=C["muted"], transform=ax.transAxes, ha="right")
    ax.text(0.94, 0.038, f"@{BRAND}",
            fontsize=10, color=C["muted"], transform=ax.transAxes, ha="right",
            fontstyle="italic")


def pill(ax, x, y, text, fc, fg="#0d1117", fontsize=13):
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


def fmt_pct(v, plus=True):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "N/A"
    if plus:
        return f"{v:+.2%}"
    return f"{v:.2%}"


def save(fig, name):
    p = CARD_DIR / name
    fig.savefig(p, dpi=DPI, facecolor=C["bg"], bbox_inches=None, pad_inches=0)
    plt.close(fig)
    print(f"[OK] {p}")


# ============ PAGE 1: 封面 — 反共识 hero ============
def page_1():
    fig, ax = new_card()
    # 顶部 eyebrow
    ax.text(0.06, 0.94, "反共识 · 自由现金流 ETF 真相", fontsize=14,
            color=C["red"], transform=ax.transAxes, fontweight="bold")

    # 主标题 (大字, 两行)
    ax.text(0.5, 0.83, "自由现金流",
            fontsize=46, color=C["text"], transform=ax.transAxes,
            ha="center", fontweight="bold")
    ax.text(0.5, 0.755, "不是红利的升级版",
            fontsize=34, color=C["red"], transform=ax.transAxes,
            ha="center", fontweight="bold")

    # 副标题
    ax.text(0.5, 0.700, "五只产品走势接近 · 风险集中在持仓",
            fontsize=15.5, color=C["muted"], transform=ax.transAxes,
            ha="center")

    # Hero 数字对比卡 (双数字)
    # 左: 国证自由现金流指数 3 个月跌幅
    card_box(ax, 0.07, 0.42, 0.41, 0.21, fc="#1a1f26")
    ax.text(0.275, 0.605, "国证自由现金流指数", fontsize=13, color=C["muted"],
            transform=ax.transAxes, ha="center")
    ax.text(0.275, 0.555, "近 60 日", fontsize=13, color=C["muted"],
            transform=ax.transAxes, ha="center")
    fcf60 = S["headline"]["fcf_index_60d"]
    ax.text(0.275, 0.475, fmt_pct(fcf60), fontsize=38, color=C["down"],
            transform=ax.transAxes, ha="center", fontweight="bold")

    # 右: 中证红利低波同期
    card_box(ax, 0.52, 0.42, 0.41, 0.21, fc="#1a1f26")
    ax.text(0.725, 0.605, "中证红利低波 100", fontsize=13, color=C["muted"],
            transform=ax.transAxes, ha="center")
    ax.text(0.725, 0.555, "近 60 日", fontsize=13, color=C["muted"],
            transform=ax.transAxes, ha="center")
    dvd60 = S["headline"]["dvd_lowvol_60d"]
    dvd_color = C["up"] if dvd60 >= 0 else C["down"]
    ax.text(0.725, 0.475, fmt_pct(dvd60), fontsize=38, color=dvd_color,
            transform=ax.transAxes, ha="center", fontweight="bold")

    # 中部箭头 + gap
    gap = (fcf60 - dvd60) * 100
    ax.text(0.5, 0.475, "→", fontsize=26, color=C["muted"],
            transform=ax.transAxes, ha="center")
    ax.text(0.5, 0.385, f"差距 {abs(gap):.1f} 个百分点",
            fontsize=15.5, color=C["gold"], transform=ax.transAxes,
            ha="center", fontweight="bold")

    # TL;DR 三条 (下半救援)
    ax.text(0.06, 0.330, "TL;DR · 你需要先知道的 3 件事",
            fontsize=14, color=C["text"], transform=ax.transAxes,
            fontweight="bold")
    tldr = [
                                ("01", "五只现金流 ETF 走势接近, 不是红利低波替代品", C["red"]),
        ("02", "国证现金流指数 2024 年 12 月才发布 · ETF 集中 2025 上市 → 发布即顶点", C["orange"]),
                ("03", "现金流 ETF 近 60 日集体 -15%~-17% · 风格 ≠ 红利低波", C["gold"]),
    ]
    yy = 0.270
    for num, text, color in tldr:
        ax.text(0.085, yy, num, fontsize=22, color=color,
                transform=ax.transAxes, fontweight="bold")
        ax.text(0.155, yy + 0.005, text, fontsize=13, color=C["text"],
                transform=ax.transAxes)
        yy -= 0.060

    # 底部时间戳
    ax.text(0.5, 0.075, "数据截至 2026-06-25 · 共 8 页深度复盘",
            fontsize=11.5, color=C["muted"], transform=ax.transAxes, ha="center")

    footer(ax, 1)
    save(fig, "01_cover.png")

page_1()


# ============ PAGE 2: 5 只现金流 ETF ============
def page_2():
    fig, ax = new_card()
    header(ax, "PAGE 02 · 现金流 ETF 横向对比",
                                   "5 只产品走势高度趋同",
                   "近 60 日基本都落在 -15%~-17%")

    # 5 只 ETF 60 日表现条形图
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
    data.sort(key=lambda x: -x[3])  # 高到低

    y_top = 0.78
    y_bot = 0.36
    y_step = (y_top - y_bot) / (len(data) - 1)
    max_abs = max(abs(d[3]) for d in data)
    bar_max_w = 0.32
    rank_colors = [C["blue"], C["cyan"], C["gold"], C["orange"], C["pink"]]
    rank_tags = ["相对抗跌", "接近均值", "接近均值", "偏弱", "偏弱"]

    for i, (code, name, brand, ret) in enumerate(data):
        y = y_top - i * y_step
        # 左侧 ETF 名 + 代码
        ax.text(0.06, y + 0.012, f"{name}", fontsize=15, color=C["text"],
                transform=ax.transAxes, fontweight="bold")
        ax.text(0.06, y - 0.018, f"{code} · {brand}", fontsize=11, color=C["muted"],
                transform=ax.transAxes)

        # 中线 (0%)
        mid_x = 0.55
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

        ax.text(0.5, 0.825, "近 60 日涨跌幅", fontsize=13, color=C["muted"],
            transform=ax.transAxes, ha="center")

    # 底部点睛 (上移让节奏更连贯)
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

page_2()


# ============ PAGE 3: 持仓真相 — 同名不同股 ============
def page_3():
    fig, ax = new_card()
    header(ax, "PAGE 03 · 持仓真相",
                                                                   "这 5 只产品高度同质",
                   "核心暴露集中在汽车/石油石化/家电/航运/钢铁")

        # 5 列行业堆叠条
    # 每只 ETF 一个条状结构, 显示前 5 大行业占比
    SECTOR_COLORS = {
        "汽车": C["blue"], "石油石化": "#e6a23c", "家电": C["purple"],
        "航运": C["cyan"], "钢铁": "#8b949e", "有色": C["gold"],
        "机械": "#a0826d", "农牧": "#65a30d", "电子": "#0f766e",
        "物流": "#f97316", "电气设备": C["green"],
        "建筑": "#6f7d8e", "通信": "#5b8def",
        "银行": "#2d8cf0", "医药": "#d63aff", "半导体": "#00d4aa",
        "贸易": "#7f8c8d", "游戏": "#ff7b72", "互联网": "#56d4dd",
        "其他": C["muted"],
    }

    etf_show = [
                ("563390", "全指现金流ETF", "华泰柏瑞"),
                ("159201", "自由现金流ETF", "华夏"),
                ("159222", "自由现金流ETF", "易方达"),
                ("159221", "现金流ETF", "嘉实"),
                ("159223", "现金流ETF", "永赢"),
    ]
    SYM_KEY = {"563390": "sh563390", "159201": "sz159201", "159222": "sz159222",
                           "159221": "sz159221", "159223": "sz159223"}

    y_top = 0.74
    y_step = 0.105
    bar_h = 0.045

    # 图例 (顶部, 最常见 8 个行业)
    legend_items = [
        ("汽车", C["blue"]), ("石油石化", "#e6a23c"), ("家电", C["purple"]),
                ("航运", C["cyan"]), ("钢铁", "#8b949e"), ("有色", C["gold"]),
                ("通信", "#5b8def"), ("机械", "#a0826d"),
    ]
    lg_y = 0.815
    lg_x = 0.06
    for sec, color in legend_items:
        rect = Rectangle((lg_x, lg_y), 0.018, 0.012, fc=color, ec="none", transform=ax.transAxes)
        ax.add_patch(rect)
        ax.text(lg_x + 0.022, lg_y + 0.006, sec, fontsize=10, color=C["text"],
                transform=ax.transAxes, va="center")
        lg_x += 0.115

    for i, (code, name, brand) in enumerate(etf_show):
        y = y_top - i * y_step
        # 名字
        ax.text(0.06, y + bar_h + 0.005, f"{name} · {code}",
                fontsize=13, color=C["text"],
                transform=ax.transAxes, fontweight="bold")
        # 持仓数据
        sym_key = SYM_KEY[code]
        sectors = S["holdings"][sym_key]["sectors"]
        # 按"占净值比例"绝对值 (不归一化) — 条长=100%, 没覆盖到的是\"未披露/其他持仓\"
        sectors_sorted = sorted(sectors.items(), key=lambda x: -x[1])
        # 排除 \"其他\" (来自映射 fallback), 把它当未覆盖
        coverage = sum(w for s, w in sectors_sorted if s != "其他")
        unmapped = sum(w for s, w in sectors_sorted if s == "其他")
        x = 0.06
        bar_total_w = 0.88
        for sec, w in sectors_sorted:
            if sec == "其他":
                continue
            seg_w = (w / 100.0) * bar_total_w
            color = SECTOR_COLORS.get(sec, C["muted"])
            rect = Rectangle((x, y), seg_w, bar_h, fc=color, ec="none", transform=ax.transAxes)
            ax.add_patch(rect)
            # >= 8% 内部标百分比
            if w >= 8:
                ax.text(x + seg_w/2, y + bar_h/2, f"{sec} {w:.0f}%",
                        fontsize=10, color="#0d1117",
                        transform=ax.transAxes, ha="center", va="center", fontweight="bold")
            x += seg_w
        # 未覆盖段 (未披露 + 已映射但小)
        rest_w = bar_total_w - (x - 0.06)
        if rest_w > 0.005:
            rect = Rectangle((x, y), rest_w, bar_h, fc="#21262d", ec=C["border"],
                             lw=0.5, transform=ax.transAxes)
            ax.add_patch(rect)
            if rest_w > 0.10:
                ax.text(x + rest_w/2, y + bar_h/2, "未披露/其他",
                        fontsize=10, color=C["muted"],
                        transform=ax.transAxes, ha="center", va="center")

        # 右侧标注 top1 行业 + 占比
        top_sec, top_w = sectors_sorted[0] if sectors_sorted[0][0] != "其他" else (sectors_sorted[1] if len(sectors_sorted) > 1 else sectors_sorted[0])
        ax.text(0.94, y - 0.012, f"TOP1 {top_sec} {top_w:.0f}%",
                fontsize=10.5, color=C["gold"], transform=ax.transAxes,
                ha="right")

    # 底部反共识结论
    card_box(ax, 0.06, 0.07, 0.88, 0.09, fc="#2a1f1f", ec=C["red"])
    ax.text(0.5, 0.13, "三个持仓结论",
            fontsize=14, color=C["red"], transform=ax.transAxes,
            ha="center", fontweight="bold")
    ax.text(0.5, 0.094, "① 五只产品前十大持仓高度重合",
            fontsize=11, color=C["text"], transform=ax.transAxes, ha="center")
    ax.text(0.5, 0.073, "② 行业集中在周期/价值   ③ 不等于红利低波",
            fontsize=11, color=C["text"], transform=ax.transAxes, ha="center")

    footer(ax, 3)
    save(fig, "03_holdings.png")

page_3()


# ============ PAGE 4: 现金流 vs 红利 vs 红利低波 — 不是同一个东西 ============
def page_4():
    fig, ax = new_card()
    header(ax, "PAGE 04 · 你以为现金流 = 红利?",
                   "红利低波也没涨, 只是跌得少",
                   "近 60 日现金流 / 红利 / 沪深300 对比")

    # 4 柱: 现金流指数 / 红利ETF / 红利低波 / 沪深300
    # A 股配色: 跌用绿色阶, 涨用红色阶 (深=程度大, 浅/橙=程度小)
    items = [
        ("国证现金流指数", S["headline"]["fcf_index_60d"], C["down"]),      # 深绿大跌
        ("红利 ETF", S["benchmarks"]["sh510880"]["ret_60d"], "#7ac686"),     # 浅绿小跌
        ("沪深 300", S["headline"]["hs300_60d"], "#ff9580"),                  # 浅红中涨
        ("红利低波 100", S["headline"]["dvd_lowvol_60d"], "#5fbf6b"),          # 中绿下跌
    ]
    items.sort(key=lambda x: x[1])

    # 竖直柱 — 整体上移避免与底部洞察卡重叠
    n = len(items)
    bar_w = 0.13
    gap = (0.82 - n * bar_w) / (n - 1)
    base_y = 0.58
    max_h = 0.19
    vmax = max(abs(v) for _, v, _ in items)

    for i, (name, v, color) in enumerate(items):
        x = 0.10 + i * (bar_w + gap)
        h = abs(v) / vmax * max_h
        if v >= 0:
            rect = Rectangle((x, base_y), bar_w, h, fc=color, ec="none", transform=ax.transAxes)
            ax.add_patch(rect)
            ax.text(x + bar_w/2, base_y + h + 0.020, f"{v:+.1%}",
                    fontsize=17, color=color, transform=ax.transAxes,
                    ha="center", fontweight="bold")
        else:
            rect = Rectangle((x, base_y - h), bar_w, h, fc=color, ec="none", transform=ax.transAxes)
            ax.add_patch(rect)
            ax.text(x + bar_w/2, base_y - h - 0.020, f"{v:+.1%}",
                    fontsize=17, color=color, transform=ax.transAxes,
                    ha="center", va="top", fontweight="bold")
        # 名称
        ax.text(x + bar_w/2, 0.335, name, fontsize=12, color=C["text"],
                transform=ax.transAxes, ha="center")

    # 0 线 (横贯)
    ax.plot([0.07, 0.93], [base_y, base_y], color=C["border"], lw=1, transform=ax.transAxes)
    ax.text(0.06, base_y - 0.005, "0%", fontsize=10.5, color=C["muted"],
            transform=ax.transAxes, ha="right", va="center")

    # 关键洞察卡
    card_box(ax, 0.06, 0.11, 0.88, 0.17, fc="#1a1f26")
    ax.text(0.5, 0.255, "现金流 ≠ 红利 · 现金流 ≠ 红利低波",
            fontsize=16, color=C["gold"], transform=ax.transAxes,
            ha="center", fontweight="bold")
    dvd_total = S["long_term_dvd_vs_300"]["dvd_total"]
    hs300_total = S["long_term_dvd_vs_300"]["hs300_total"]
    years = S["long_term_dvd_vs_30"]["years"] if "long_term_dvd_vs_30" in S else S["long_term_dvd_vs_300"]["years"]
    ax.text(0.5, 0.215, "近 60 日: 现金流跌得更深, 红利低波也不是上涨",
            fontsize=13, color=C["text"], transform=ax.transAxes, ha="center")
    ax.text(0.5, 0.178, "→ 不是红利低波在涨, 是现金流跌得更多",
            fontsize=13, color=C["red"], transform=ax.transAxes, ha="center")
    lowvol_corr = S["correlation_fcf_vs_bench"]["vs_dividend_lowvol"]
    ax.text(0.5, 0.140, f"现金流 vs 红利低波 120日相关性 {lowvol_corr:.2f} · 仍不是同一个风格",
            fontsize=11.5, color=C["muted"], transform=ax.transAxes, ha="center")

    footer(ax, 4)
    save(fig, "04_fcf_vs_dividend.png")

page_4()


# ============ PAGE 5: 跌的真相 — 发布即顶点 ============
def page_5():
    fig, ax = new_card()
    header(ax, "PAGE 05 · 为什么跌这么惨",
           "发布即顶点 · ETF 集中 2025 上市",
           "回测做出来的指数, 散户买完就跌")

    # 时间轴 (从 2024-12 至 2026-06)
    timeline = [
        ("2024-12", "国证自由现金流指数发布"),
                ("2025-02", "159201 上市 (华夏)"),
                ("2025-04", "159222 上市 (易方达)"),
                ("2025-05", "563390/159221 上市"),
                ("2025-07", "159223 上市 (永赢)"),
        ("2026-03", "指数到顶 6227 (距今 -22.9%)"),
        ("2026-06", "今日 4799"),
    ]
    # 垂直时间轴
    line_x = 0.13
    y_start = 0.80
    y_end = 0.22
    y_step = (y_start - y_end) / (len(timeline) - 1)

    # 主轴线
    ax.plot([line_x, line_x], [y_end - 0.01, y_start + 0.01],
            color=C["border"], lw=1.5, transform=ax.transAxes)

    for i, (dt, evt) in enumerate(timeline):
        y = y_start - i * y_step
        # 节点圆点
        # 关键节点(发布, 顶点, 今日)用红
        is_key = i in [0, 5, 6]
        dot_color = C["red"] if is_key else C["blue"]
        ax.scatter([line_x], [y], s=70 if is_key else 40, c=dot_color,
                   transform=ax.transAxes, zorder=3, ec=C["bg"], lw=2)

        # 日期 (左)
        ax.text(line_x - 0.02, y, dt, fontsize=13, color=C["muted"],
                transform=ax.transAxes, ha="right", va="center")
        # 事件 (右)
        text_color = C["red"] if i in (0, 5) else (C["gold"] if i == 6 else C["text"])
        weight = "bold" if is_key else "normal"
        ax.text(line_x + 0.025, y, evt, fontsize=14, color=text_color,
                transform=ax.transAxes, va="center", fontweight=weight)

    # 关键洞察
    card_box(ax, 0.06, 0.06, 0.88, 0.13, fc="#2a1f1f", ec=C["red"])
    ax.text(0.5, 0.155, "「发布即顶点」三连击",
            fontsize=15, color=C["red"], transform=ax.transAxes,
            ha="center", fontweight="bold")
    ax.text(0.5, 0.123, "① 指数 2024-12 发布 (无真实 out-of-sample)",
            fontsize=11.5, color=C["text"], transform=ax.transAxes, ha="center")
    ax.text(0.5, 0.097, "② 2025 全年 ETF 密集上市 · 散户进场",
            fontsize=11.5, color=C["text"], transform=ax.transAxes, ha="center")
    ax.text(0.5, 0.071, "③ 上市后基金抱团推上去 · 2026-03 见顶 · 3 个月跌 22.9%",
            fontsize=11.5, color=C["text"], transform=ax.transAxes, ha="center")

    footer(ax, 5)
    save(fig, "05_publish_peak.png")


# ============ PAGE 6: 当前位置诊断 — 抄底还是趋势? ============
def page_6():
    fig, ax = new_card()
    header(ax, "PAGE 06 · 现在该抄底吗?",
           "三个客观信号 · 拒绝拍脑袋",
           "用数据说话, 不用情绪")

    # 三个信号灯卡
    signals = [
        {
            "title": "信号 1 · 回撤深度",
            "val": "-22.9%",
            "note": "国证现金流指数距 ATH",
            "pill": "WARN",
            "pill_color": C["orange"],
            "expl": "已超过指数发布以来\n所有回撤的最深值",
        },
        {
            "title": "信号 2 · 风格相关性",
                        "val": f"{S['correlation_fcf_vs_bench']['vs_dividend_lowvol']:.2f}",
            "note": "现金流 vs 红利低波 (120 日)",
            "pill": "NEUTRAL",
            "pill_color": C["blue"],
                        "expl": "中等相关 · 现金流仍不是\n红利低波替代品",
        },
        {
            "title": "信号 3 · 跟踪行业风险",
            "val": "45%+",
            "note": "汽车/能源/家电/航运/钢铁",
            "pill": "RISK",
            "pill_color": C["red"],
            "expl": "偏周期/价值组合\n不是红利低波替代品",
        },
    ]

    y_top = 0.66
    card_h = 0.16
    gap = 0.025
    for i, s in enumerate(signals):
        y = y_top - i * (card_h + gap)
        card_box(ax, 0.06, y, 0.88, card_h, fc="#1a1f26")
        # 左侧 pill + title
        ax.text(0.10, y + card_h - 0.030, s["title"], fontsize=14,
                color=C["muted"], transform=ax.transAxes, fontweight="bold")
        pill(ax, 0.83, y + card_h - 0.030, s["pill"], s["pill_color"], fontsize=11.5)
        # 大数字
        ax.text(0.10, y + 0.045, s["val"], fontsize=34, color=s["pill_color"],
                transform=ax.transAxes, fontweight="bold")
        ax.text(0.10, y + 0.020, s["note"], fontsize=11.5, color=C["muted"],
                transform=ax.transAxes)
        # 右侧解释
        for j, line in enumerate(s["expl"].split("\n")):
            ax.text(0.60, y + card_h - 0.075 - j*0.025, line,
                    fontsize=13, color=C["text"], transform=ax.transAxes)

    # 结论
    card_box(ax, 0.06, 0.07, 0.88, 0.10, fc="#1a2a1f", ec=C["gold"])
    ax.text(0.5, 0.145, "结论: 现在不是\"无脑抄底\"的位置",
            fontsize=15, color=C["gold"], transform=ax.transAxes,
            ha="center", fontweight="bold")
    ax.text(0.5, 0.115, "回撤深度只代表\"跌了多少\", 不代表\"该买\"",
            fontsize=13, color=C["text"], transform=ax.transAxes, ha="center")
    ax.text(0.5, 0.088, "真正决定收益的是: 持仓行业的景气度 + 你买的是哪一只",
            fontsize=11.5, color=C["muted"], transform=ax.transAxes, ha="center")

    footer(ax, 6)
    save(fig, "06_position.png")

page_5()
page_6()


# ============ PAGE 7: 操作策略 ============
def page_7():
    fig, ax = new_card()
    header(ax, "PAGE 07 · 怎么操作",
           "买之前先认清你买的是什么",
           "5 句话教你避开 90% 的坑")

    strategies = [
                ("01", "买前先看持仓", "别只看名字里的现金流\n真正风险藏在前十大和行业暴露", C["red"]),
                ("02", "五只产品高度同质", "前十大持仓重合度很高\n差异更多在规模/流动性/折溢价", C["blue"]),
                ("03", "风格风险仍然存在", "主要暴露在汽车/海油/家电/航运/钢铁\n不是红利低波替代品", C["orange"]),
        ("04", "不要单笔重仓 · 分批进", "指数发布以来仅 18 个月\n样本不足 · 不知道真正底部在哪\n建议: 现价 50% + 再跌 10% 加 30% + 再跌 10% 补 20%", C["gold"]),
        ("05", "用红利低波控波动", f"现金流和红利低波相关性约 {S['correlation_fcf_vs_bench']['vs_dividend_lowvol']:.2f}\n搭配是降波动, 不是押同一风格", C["green"]),
    ]

    y_top = 0.78
    y_step = 0.128
    for i, (num, title, body, color) in enumerate(strategies):
        y = y_top - i * y_step
        # 编号大字
        ax.text(0.08, y + 0.025, num, fontsize=28, color=color,
                transform=ax.transAxes, fontweight="bold", va="center")
        # 标题
        ax.text(0.18, y + 0.045, title, fontsize=14.5, color=C["text"],
                transform=ax.transAxes, fontweight="bold")
        # body 多行
        for j, line in enumerate(body.split("\n")):
            ax.text(0.18, y + 0.015 - j*0.022, line, fontsize=11, color=C["muted"],
                    transform=ax.transAxes)
        # 横分割线
        if i < len(strategies) - 1:
            ax.plot([0.08, 0.92], [y - 0.070, y - 0.070],
                    color=C["border"], lw=0.4, alpha=0.5, transform=ax.transAxes)

    # 底部口诀总结 (填充留白)
    card_box(ax, 0.06, 0.07, 0.88, 0.08, fc="#1a2a1f", ec=C["gold"])
    ax.text(0.5, 0.118, "核心口诀",
            fontsize=14, color=C["gold"], transform=ax.transAxes,
            ha="center", fontweight="bold")
    ax.text(0.5, 0.085, "看持仓 · 看行业 · 分批进 · 配红利低波",
            fontsize=14, color=C["text"], transform=ax.transAxes, ha="center")

    footer(ax, 7)
    save(fig, "07_strategy.png")


# ============ PAGE 8: 总结 + 免责 ============
def page_8():
    fig, ax = new_card()
    header(ax, "PAGE 08 · 一图总结",
           "自由现金流真相速记卡",
           "存图防止再被名字割韭菜")

    # 大主标
    ax.text(0.5, 0.79, "记住这 4 句", fontsize=19, color=C["gold"],
            transform=ax.transAxes, ha="center", fontweight="bold")

    quotes = [
                ("名字 ≠ 风格", "同类产品也要看持仓和行业暴露", C["red"]),
        ("回测 ≠ 实盘", "国证现金流指数 2024-12 发布 · 散户买进就跌 22.9%", C["orange"]),
        ("现金流 ≠ 红利", f"相关性 {S['correlation_fcf_vs_bench']['vs_dividend_lowvol']:.2f} · 近60日仍跑输 {abs(S['headline']['underperf_pp_vs_dvd'])*100:.1f} pp", C["blue"]),
        ("现在 ≠ 抄底", "样本不足 18 个月 · 不知道真底 · 分批 > 一次性", C["gold"]),
    ]

    y_top = 0.70
    y_step = 0.115
    for i, (h, body, color) in enumerate(quotes):
        y = y_top - i * y_step
        card_box(ax, 0.06, y - 0.05, 0.88, 0.10, fc="#1a1f26", ec=color, lw=1.0)
        ax.text(0.10, y, h, fontsize=17, color=color, transform=ax.transAxes,
                fontweight="bold", va="center")
        ax.text(0.94, y, body, fontsize=12, color=C["text"],
                transform=ax.transAxes, ha="right", va="center")

    # 底部 CTA
    ax.text(0.5, 0.18, "看完点赞收藏",
            fontsize=17, color=C["gold"], transform=ax.transAxes,
            ha="center", fontweight="bold")
    ax.text(0.5, 0.15, "下次再有 ETF 网红主题 · 先看看跟踪指数发布时间",
            fontsize=11.5, color=C["muted"], transform=ax.transAxes, ha="center")
    # 绿色按钮化 CTA
    cta_box = FancyBboxPatch((0.18, 0.080), 0.64, 0.045,
                             boxstyle="round,pad=0.005,rounding_size=0.020",
                             fc=C["green"], ec="none", transform=ax.transAxes)
    ax.add_patch(cta_box)
    ax.text(0.5, 0.102, "想看完整深度研报 PDF · 评论区扣【现金流】",
            fontsize=14, color="#0d1117", transform=ax.transAxes,
            ha="center", va="center", fontweight="bold")

    footer(ax, 8)
    save(fig, "08_summary.png")

page_7()
page_8()
print("\n[ALL 8 CARDS DONE]")
