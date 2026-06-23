"""20260623 小红书 7 页卡片 — 医药狂飙 vs 有色血崩.

故事线: 今日 A 股最大反差日 — 医药 5 板块齐飞 (化学制药+3.45% 等) vs
有色金属全线跳水 (贵金属-9.33% / 小金属-5.62% / 能源金属-5.59%),
主力从周期搬家到防御.

页面规划:
  P1 封面 — 双柱反差 + 三大数字
  P2 行业冠亚军 — 医药 5 板 vs 有色 5 板
  P3 涨停天梯 — 江钨装备 5 连板 + 化学制药 8 只密集
  P4 散户雷达 — 雪球 5 只新热点
  P5 龙头快报 — 4 张子卡 (实涨派 vs 嘴炮派)
  P6 总结 + 风险提示
  P7 求关注 CTA (新增, 区别于评论区互动)
"""

from __future__ import annotations
import json
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

# ─── 路径 ───────────────────────────────
ROOT = Path("/das/user/QYJI/quant")
DATE = "20260623"
DAY_HUM = "2026-06-23"
PREV_DATE = "20260618"   # 上一份快照, 用于"较前次"对比

SUMMARY = json.loads((ROOT / f"output/hotspot/{DATE}/summary.json").read_text())
PREV_SUMMARY = json.loads((ROOT / f"output/hotspot/{PREV_DATE}/summary.json").read_text())
OUT = ROOT / f"output/hotspot/{DATE}/xhs_pharma_vs_metals_v4"
OUT.mkdir(parents=True, exist_ok=True)

# ─── 调色板 (沿用) ────────────────────────
C = {
    "bg": "#0d1117", "card": "#161b22", "card2": "#1c2129", "border": "#30363d",
    "text": "#c9d1d9", "muted": "#8b949e", "dim": "#6e7681",
    "blue": "#58a6ff", "green": "#3fb950", "red": "#f85149",
    "orange": "#d2991d", "purple": "#bc8cff", "gold": "#f0c040",
    "cyan": "#56d4dd", "rose": "#ff7b72",
}
CARD_W, CARD_H, DPI = 7.2, 9.6, 200
TOTAL_PAGES = 7

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "Droid Sans Fallback", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.weight"] = "regular"


def new_card():
    fig, ax = plt.subplots(figsize=(CARD_W, CARD_H), facecolor=C["bg"])
    ax.set_facecolor(C["bg"])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    return fig, ax


def add_footer(ax, page, total=TOTAL_PAGES):
    # "懂哥说" 人设标签 (左下) - vision v2 建议
    ax.text(0.05, 0.025, "懂哥说", ha="left", va="center",
            fontsize=7, fontweight="bold", color=C["bg"],
            bbox=dict(boxstyle="round,pad=0.25", fc=C["cyan"], ec="none"),
            transform=ax.transAxes)
    ax.text(0.5, 0.025, "数据: 东方财富/雪球 · 非投资建议",
            ha="center", va="center", fontsize=7, color=C["muted"], transform=ax.transAxes)
    ax.text(0.95, 0.025, f"{page}/{total}", ha="right", va="center",
            fontsize=8, color=C["muted"], transform=ax.transAxes)


def pill(ax, x, y, txt, fc, fs=10):
    ax.text(x, y, txt, ha="center", va="center", fontsize=fs, fontweight="bold",
            color=C["bg"],
            bbox=dict(boxstyle="round,pad=0.4", fc=fc, ec="none"),
            transform=ax.transAxes)


def save(fig, page):
    p = OUT / f"page_{page}.png"
    fig.savefig(p, dpi=DPI, bbox_inches="tight",
                facecolor=C["bg"], edgecolor="none", pad_inches=0.15)
    plt.close(fig)
    print(f"  ✓ saved {p}")


# ═══════════════════════════════════════════
# Page 1 — 封面: 医药 +3.45% vs 有色 -9.33% 双柱反差
# ═══════════════════════════════════════════
def page1():
    fig, ax = new_card()
    pill(ax, 0.5, 0.95, f"  {DAY_HUM} · 周二复盘  ", C["gold"])

    # 主标题三行
    ax.text(0.5, 0.865, "今日 A 股", ha="center", fontsize=30, fontweight="bold",
            color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.795, "最魔幻一幕", ha="center", fontsize=42, fontweight="bold",
            color=C["gold"], transform=ax.transAxes)

    # 双柱反差: 左红 (有色崩) vs 右绿 (医药涨)
    # 左柱
    rect_l = Rectangle((0.08, 0.49), 0.36, 0.22, fc=C["red"], alpha=0.18,
                       ec=C["red"], lw=1.5, transform=ax.transAxes)
    ax.add_patch(rect_l)
    ax.text(0.26, 0.665, "有色金属", ha="center", fontsize=14,
            color=C["text"], transform=ax.transAxes)
    ax.text(0.26, 0.60, "-9.33%", ha="center", fontsize=40, fontweight="bold",
            color=C["red"], transform=ax.transAxes)
    ax.text(0.26, 0.535, "贵金属领跌", ha="center", fontsize=10,
            color=C["muted"], transform=ax.transAxes)

    # VS 中圆
    ax.text(0.50, 0.60, "VS", ha="center", va="center", fontsize=18, fontweight="bold",
            color=C["bg"],
            bbox=dict(boxstyle="circle,pad=0.5", fc=C["gold"], ec="none"),
            transform=ax.transAxes)

    # 右柱
    rect_r = Rectangle((0.56, 0.49), 0.36, 0.22, fc=C["green"], alpha=0.18,
                       ec=C["green"], lw=1.5, transform=ax.transAxes)
    ax.add_patch(rect_r)
    ax.text(0.74, 0.665, "化学制药", ha="center", fontsize=14,
            color=C["text"], transform=ax.transAxes)
    ax.text(0.74, 0.60, "+3.45%", ha="center", fontsize=40, fontweight="bold",
            color=C["green"], transform=ax.transAxes)
    ax.text(0.74, 0.535, "医药 5 板齐飞", ha="center", fontsize=10,
            color=C["muted"], transform=ax.transAxes)

    # 三大数字 + 较 6/18 delta (vision v2 建议)
    PREV_LBL = "6/18"
    nums = [
        (SUMMARY["zt_count"], PREV_SUMMARY["zt_count"], "涨停", C["red"]),
        (SUMMARY["zt_max_board"], PREV_SUMMARY["zt_max_board"], "最高连板", C["orange"]),
        (SUMMARY["zb_count"], PREV_SUMMARY["zb_count"], "炸板", C["muted"]),
    ]
    for i, (n, prev, lbl, col) in enumerate(nums):
        x = [0.20, 0.50, 0.80][i]
        ax.text(x, 0.39, str(n), ha="center", fontsize=42, fontweight="bold",
                color=col, transform=ax.transAxes)
        ax.text(x, 0.325, lbl, ha="center", fontsize=12,
                color=C["muted"], transform=ax.transAxes)
        # delta vs PREV
        diff = n - prev
        sign = "+" if diff > 0 else ""
        # 颜色: 涨停/连板增 = 绿 (热度), 炸板增 = 红 (风险), 反之亦然
        if lbl == "炸板":
            d_col = C["red"] if diff > 0 else C["green"]
        else:
            d_col = C["green"] if diff > 0 else C["red"]
        if diff == 0:
            d_col = C["muted"]
        ax.text(x, 0.285, f"较 {PREV_LBL} {sign}{diff}", ha="center", fontsize=9,
                color=d_col, transform=ax.transAxes)

    # 钩子句
    ax.text(0.5, 0.22, "医药狂飙日 · 金子股血崩日",
            ha="center", fontsize=17, fontweight="bold", color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.55", fc=C["card"], ec=C["border"]),
            transform=ax.transAxes)
    ax.text(0.5, 0.135, "卖了金子买药明康德的姐妹今晚加菜",
            ha="center", fontsize=11, color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.085, "翻到下一页 → 看资金到底搬到哪了",
            ha="center", fontsize=9.5, color=C["muted"], style="italic",
            transform=ax.transAxes)

    add_footer(ax, 1)
    save(fig, 1)


# ═══════════════════════════════════════════
# Page 2 — 行业冠亚军: 医药 5 板齐飞 vs 有色 5 板崩
# ═══════════════════════════════════════════
def page2():
    fig, ax = new_card()
    pill(ax, 0.5, 0.95, "  行业冠亚军  ", C["blue"])
    ax.text(0.5, 0.89, "今天买啥赚 / 买啥亏", ha="center",
            fontsize=18, fontweight="bold", color=C["text"], transform=ax.transAxes)

    ax.text(0.27, 0.83, "涨幅榜 TOP5", ha="center", fontsize=13, fontweight="bold",
            color=C["green"], transform=ax.transAxes)
    ax.text(0.78, 0.83, "跌幅榜 TOP5", ha="center", fontsize=13, fontweight="bold",
            color=C["red"], transform=ax.transAxes)

    top5, bot5 = SUMMARY["industry_top5"], SUMMARY["industry_bottom5"]
    max_pct = max(max(t["pct_chg"] for t in top5), abs(min(b["pct_chg"] for b in bot5)))

    for i, (yt, t, b) in enumerate(zip([0.75, 0.67, 0.59, 0.51, 0.43], top5, bot5)):
        # 涨幅条 (从中线左侧延伸到左侧)
        gw = 0.18 * (t["pct_chg"] / max_pct)
        ax.add_patch(Rectangle((0.50 - gw, yt - 0.022), gw, 0.030,
                               fc=C["green"], alpha=0.22, ec="none",
                               transform=ax.transAxes))
        ax.text(0.04, yt, t["name"][:6], ha="left", fontsize=11,
                color=C["text"], transform=ax.transAxes)
        ax.text(0.49, yt, f"+{t['pct_chg']:.2f}%", ha="right", fontsize=13,
                fontweight="bold", color=C["green"], transform=ax.transAxes)

        # 跌幅条
        rw = 0.18 * (abs(b["pct_chg"]) / max_pct)
        ax.add_patch(Rectangle((0.55, yt - 0.022), rw, 0.030,
                               fc=C["red"], alpha=0.22, ec="none",
                               transform=ax.transAxes))
        ax.text(0.96, yt, b["name"][:6], ha="right", fontsize=11,
                color=C["text"], transform=ax.transAxes)
        ax.text(0.56, yt, f"{b['pct_chg']:.2f}%", ha="left", fontsize=13,
                fontweight="bold", color=C["red"], transform=ax.transAxes)

    ax.plot([0.525, 0.525], [0.41, 0.81], color=C["border"], lw=0.8, transform=ax.transAxes)

    # 主力资金动向 — 医药主线龙头 vs 有色重灾区
    ax.text(0.5, 0.34, "主力资金动向", ha="center", fontsize=13,
            fontweight="bold", color=C["text"], transform=ax.transAxes)

    # 改: 选医药生物 (整版块净流入) vs 有色金属 (整版块净流出)
    # industry_top5[3] 是医药生物 +2.70% / industry_bottom5[3] 是有色金属
    win = top5[3]   # 医药生物
    lose = bot5[3]  # 有色金属
    # 字号差视觉化数量级差 (215.9 / 22.1 = 9.8x) - vision v2 建议
    ax.text(0.27, 0.26, f"{win['name']} +{win['pct_chg']:.2f}%", ha="center",
            fontsize=11, color=C["text"], transform=ax.transAxes)
    ax.text(0.27, 0.21, f"+{win['main_net_in']/1e8:.1f}亿", ha="center",
            fontsize=20, fontweight="bold", color=C["green"], transform=ax.transAxes)
    ax.text(0.27, 0.15, "主力净流入", ha="center", fontsize=10,
            color=C["muted"], transform=ax.transAxes)

    ax.text(0.78, 0.26, f"{lose['name']} {lose['pct_chg']:.2f}%", ha="center",
            fontsize=11, color=C["text"], transform=ax.transAxes)
    ax.text(0.78, 0.205, f"{lose['main_net_in']/1e8:.1f}亿", ha="center",
            fontsize=32, fontweight="bold", color=C["red"], transform=ax.transAxes)
    ax.text(0.78, 0.15, "主力净流出 · ~10x", ha="center", fontsize=10,
            color=C["red"], transform=ax.transAxes)

    ax.text(0.5, 0.075, "钱从「周期金属」往「医药防御」搬家",
            ha="center", fontsize=12, fontweight="bold", color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.45", fc=C["card"], ec=C["border"]),
            transform=ax.transAxes)

    add_footer(ax, 2)
    save(fig, 2)


# ═══════════════════════════════════════════
# Page 3 — 涨停天梯: 江钨装备 5 连板 + 化学制药 8 只密集
# ═══════════════════════════════════════════
def page3():
    fig, ax = new_card()
    pill(ax, 0.5, 0.95, "  涨停天梯  ", C["red"])
    ax.text(0.5, 0.89, f"今日 {SUMMARY['zt_count']} 只涨停 · 最高 {SUMMARY['zt_max_board']} 连板",
            ha="center", fontsize=14, color=C["text"], transform=ax.transAxes)

    # 6 只: 5 板江钨装备 + 5 只 3 板
    rows_y = [0.79, 0.705, 0.62, 0.535, 0.45, 0.365]
    for y, x in zip(rows_y, SUMMARY["zt_top10"][:6]):
        n = x["连板数"]
        col_n = C["red"] if n >= 5 else (C["orange"] if n >= 3 else C["gold"])

        # 行卡片底
        ax.add_patch(Rectangle((0.04, y - 0.040), 0.92, 0.075,
                               fc=C["card"], ec=C["border"], lw=0.6,
                               transform=ax.transAxes))

        ax.text(0.10, y + 0.005, f"{n}", ha="center", fontsize=26,
                fontweight="bold", color=col_n, transform=ax.transAxes)
        ax.text(0.10, y - 0.030, "连板", ha="center", fontsize=8,
                color=C["muted"], transform=ax.transAxes)
        ax.text(0.21, y + 0.012, x["名称"], ha="left", fontsize=15,
                fontweight="bold", color=C["text"], transform=ax.transAxes)
        ax.text(0.21, y - 0.022, f"{x['代码']} · {x['所属行业']}", ha="left",
                fontsize=10, color=C["muted"], transform=ax.transAxes)
        try:
            pct = float(x["涨跌幅"])
        except (TypeError, ValueError):
            pct = 0
        ax.text(0.93, y, f"+{pct:.2f}%", ha="right", fontsize=14,
                fontweight="bold", color=C["green"], transform=ax.transAxes)

    # 涨停密集行业 — 柱图
    ax.text(0.5, 0.28, "涨停最密集的行业", ha="center", fontsize=12,
            fontweight="bold", color=C["text"], transform=ax.transAxes)
    inds = SUMMARY["zt_top_industries"][:5]
    max_cnt = max(i["涨停数"] for i in inds)
    bar_max_h = 0.075
    # 医药相关行业用绿色, 其他用 gold (品牌色), 跟整组的红绿语义对齐
    medical_keywords = ("药", "医", "生物", "中药")
    for i, ind in enumerate(inds):
        x = 0.10 + i * 0.20
        h = bar_max_h * (ind["涨停数"] / max_cnt)
        name = ind["行业"]
        is_medical = any(k in name for k in medical_keywords)
        bar_col = C["green"] if is_medical else C["gold"]
        ax.add_patch(Rectangle((x - 0.055, 0.14), 0.11, h,
                               fc=bar_col, alpha=0.38, ec=bar_col, lw=1.0,
                               transform=ax.transAxes))
        ax.text(x, 0.14 + h + 0.013, f"{ind['涨停数']}", ha="center", fontsize=16,
                fontweight="bold", color=bar_col, transform=ax.transAxes)
        ax.text(x, 0.110, name[:5], ha="center", fontsize=10,
                color=C["text"], transform=ax.transAxes)

    ax.text(0.5, 0.07, "连板都在化工医药, 周期金属一只都没进 →",
            ha="center", fontsize=11, color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.4", fc=C["card"], ec=C["border"]),
            transform=ax.transAxes)

    add_footer(ax, 3)
    save(fig, 3)


# ═══════════════════════════════════════════
# Page 4 — 雪球新热点 5 只 (讨论榜∖关注榜)
def page4():
    fig, ax = new_card()
    pill(ax, 0.5, 0.95, "  散户雷达  ", C["purple"])
    ax.text(0.5, 0.89, "雪球讨论榜 · 散户在聊啥",
            ha="center", fontsize=20, fontweight="bold",
            color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.857, "(讨论榜 TOP10 但不在关注榜 = 短期热度过沉淀派)",
            ha="center", fontsize=9.5, color=C["muted"], transform=ax.transAxes)

    follow_codes = {x['股票代码'] for x in SUMMARY['xueqiu_follow_top10']}
    new_buzz = [x for x in SUMMARY['xueqiu_tweet_top10']
                if x['股票代码'] not in follow_codes][:5]
    # 当日讨论榜排名 + 较 6/18 讨论量变化 (真实信号)
    rank_map = {x['股票代码']: i+1 for i, x in enumerate(SUMMARY['xueqiu_tweet_top10'])}
    prev_buzz = {x['股票代码']: x['关注'] for x in PREV_SUMMARY['xueqiu_tweet_top10']}

    # 每条独立卡片底
    rows_y = [0.75, 0.625, 0.50, 0.375, 0.25]
    for y, x in zip(rows_y, new_buzz):
        ax.add_patch(Rectangle((0.04, y - 0.055), 0.92, 0.105,
                               fc=C["card"], ec=C["border"], lw=0.6,
                               transform=ax.transAxes))
        # HOT 药丸
        ax.text(0.10, y, "HOT", ha="center", va="center", fontsize=10, fontweight="bold",
                color=C["bg"],
                bbox=dict(boxstyle="round,pad=0.3", fc=C["red"], ec="none"),
                transform=ax.transAxes)
        # 股票名 + 代码
        ax.text(0.20, y + 0.020, x["股票简称"], ha="left", fontsize=15,
                fontweight="bold", color=C["text"], transform=ax.transAxes)
        # 代码 + 较 5 日前真实变化 (诚实)
        prev_b = prev_buzz.get(x['股票代码'], 0)
        if prev_b > 0:
            pct = (x['关注'] / prev_b - 1) * 100
            if pct > 1:
                delta_str = f"较 6/18 +{pct:.1f}%"
                d_col = C["green"]
            elif pct < -1:
                delta_str = f"较 6/18 {pct:.1f}%"
                d_col = C["muted"]
            else:
                delta_str = f"较 6/18 持平"
                d_col = C["muted"]
        else:
            delta_str = "5 日内首次上榜"
            d_col = C["green"]
        ax.text(0.20, y - 0.025, f"{x['股票代码']}  ·  {delta_str}",
                ha="left", fontsize=9.5, color=d_col, transform=ax.transAxes)
        # 讨论量 (w 单位) + 讨论榜排名
        buzz_w = x['关注'] / 10000
        rank = rank_map.get(x['股票代码'], '?')
        ax.text(0.93, y + 0.020, f"{buzz_w:.1f}w", ha="right", fontsize=17,
                fontweight="bold", color=C["purple"], transform=ax.transAxes)
        ax.text(0.93, y - 0.025, f"讨论榜 #{rank} · 价 {x['最新价']}", ha="right", fontsize=9.5,
                color=C["muted"], transform=ax.transAxes)

    ax.text(0.5, 0.15, "AI 算力 + 智驾 + 医药 CXO = 今日三条共识线",
            ha="center", fontsize=11.5, fontweight="bold", color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.4", fc=C["card"], ec=C["border"]),
            transform=ax.transAxes)
    ax.text(0.5, 0.105, "药明康德正好跨在医药+科技两条线交点上",
            ha="center", fontsize=10, color=C["muted"], transform=ax.transAxes)
    # 真相补刀: 5 只里只有寒武纪在涨, 其余都在散户讨论度上萎缩 — 反差点
    ax.text(0.5, 0.07, "* 只有寒武纪讨论量较 5 日前真增, 其余 4 只其实在退烧",
            ha="center", fontsize=8.5, color=C["orange"], style="italic",
            transform=ax.transAxes)

    add_footer(ax, 4)
    save(fig, 4)


# ═══════════════════════════════════════════
# Page 5 — 龙头快报 4 卡: 实涨派 vs 嘴炮派
# ═══════════════════════════════════════════
def page5():
    fig, ax = new_card()
    pill(ax, 0.5, 0.95, "  龙头快报  ", C["orange"])
    ax.text(0.5, 0.89, "今日 4 只代表股", ha="center",
            fontsize=18, fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.85, "↑ 实涨派 (上排) | 嘴炒派 (下排) ↓", ha="center",
            fontsize=10, color=C["muted"], style="italic", transform=ax.transAxes)

    # 4 卡: 上排 = 今日真涨 (医药主线龙头), 下排 = 雪球热议但价位高/未跟涨
    # 海南海药 +N% 化学制药龙头 (industry leader)
    # 赛升药业 +N% 生物制品龙头
    # 寒武纪 — 嘴炒派 (价 1424, 雪球讨论 3.8w)
    # 药明康德 — 双修 (医药+CXO 雪球新热点)
    cards_data = [
        ("海南海药", "SZ000566", "化学制药领涨", "净流入 12.71亿", C["green"], "REAL", "医药主线龙头"),
        ("赛升药业", "SZ300485", "生物制品领涨", "净流入 5.33亿", C["green"], "REAL", "生物制品一哥"),
        ("寒武纪", "SH688256", "雪球 3.8w", "价 1424.69", C["purple"], "BUZZ", "AI算力, 高位嘴炒"),
        ("药明康德", "SH603259", "雪球 3.2w", "价 106.56", C["cyan"], "DUAL", "医药+CXO 双修"),
    ]
    positions = [(0.27, 0.665), (0.73, 0.665), (0.27, 0.36), (0.73, 0.36)]
    badge_col_map = {"REAL": C["green"], "BUZZ": C["purple"], "DUAL": C["cyan"]}

    for (cx, cy), (name, code, pct, price, col, badge, tag) in zip(positions, cards_data):
        # 瘦身卡片 (按 §13 v2)
        rect = FancyBboxPatch(
            (cx - 0.19, cy - 0.10), 0.38, 0.20,
            boxstyle="round,pad=0.01", fc=C["card"], ec=C["border"], lw=1,
            transform=ax.transAxes,
        )
        ax.add_patch(rect)
        # 角标
        ax.text(cx - 0.165, cy + 0.075, badge, ha="left", va="center",
                fontsize=8, fontweight="bold", color=C["bg"],
                bbox=dict(boxstyle="round,pad=0.25", fc=badge_col_map[badge], ec="none"),
                transform=ax.transAxes)
        ax.text(cx, cy + 0.075, name, ha="center", fontsize=14, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        ax.text(cx, cy + 0.040, code, ha="center", fontsize=9,
                color=C["muted"], transform=ax.transAxes)
        ax.text(cx, cy - 0.005, pct, ha="center", fontsize=14, fontweight="bold",
                color=col, transform=ax.transAxes)
        ax.text(cx, cy - 0.045, price, ha="center", fontsize=10,
                color=C["muted"], transform=ax.transAxes)
        ax.text(cx, cy - 0.083, tag, ha="center", fontsize=9.5,
                color=C["cyan"], transform=ax.transAxes)

    # 十字分隔
    ax.plot([0.08, 0.92], [0.51, 0.51], color=C["border"], lw=0.6, transform=ax.transAxes)
    ax.plot([0.50, 0.50], [0.24, 0.78], color=C["border"], lw=0.6, transform=ax.transAxes)

    # 一句话点评卡
    ax.add_patch(FancyBboxPatch(
        (0.07, 0.07), 0.86, 0.15,
        boxstyle="round,pad=0.01", fc=C["card2"], ec=C["border"], lw=1,
        transform=ax.transAxes,
    ))
    ax.text(0.5, 0.18, "懂哥短评", ha="center", fontsize=12, fontweight="bold",
            color=C["cyan"], transform=ax.transAxes)
    ax.text(0.5, 0.115,
            "实涨派吃的是真金白银, 嘴炒派吃的是关注度\n"
            "1400 块的寒武纪只能远观, 药明康德是医药+科技双修",
            ha="center", fontsize=9.5, color=C["text"], transform=ax.transAxes)

    add_footer(ax, 5)
    save(fig, 5)


# ═══════════════════════════════════════════
# Page 6 — 总结 (3 句) + 风险提示
# ═══════════════════════════════════════════
def page6():
    fig, ax = new_card()
    pill(ax, 0.5, 0.95, "  今日总结  ", C["gold"])
    ax.text(0.5, 0.89, "三句话看懂今天 A 股", ha="center",
            fontsize=18, fontweight="bold", color=C["text"], transform=ax.transAxes)

    points = [
        ("01", "医药狂飙", C["green"], "5 板块齐飞, 化学制药 +3.45% 领涨, 海南海药净流入 12 亿"),
        ("02", "金子股血崩", C["red"], "贵金属 -9.33% 全军覆没, 有色金属一个板块流出 215 亿"),
        ("03", "炸板 46 只", C["orange"], "97 涨停里 46 只炸了一次, 47% 失败率, 追高者一片狼藉"),
    ]
    for y, (num, title, col, body) in zip([0.76, 0.61, 0.46], points):
        ax.text(0.10, y, num, ha="center", fontsize=36, fontweight="bold",
                color=col, transform=ax.transAxes)
        ax.text(0.22, y + 0.025, title, ha="left", fontsize=18, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        ax.text(0.22, y - 0.035, body, ha="left", fontsize=10.5,
                color=C["muted"], transform=ax.transAxes)
        # 编号间隔线
        if num != "03":
            ax.plot([0.08, 0.92], [y - 0.075, y - 0.075],
                    color=C["border"], lw=0.5, transform=ax.transAxes)

    # 风险提示卡片 — 放大炸板 46 警示数据 (vision v2 建议)
    ax.add_patch(FancyBboxPatch(
        (0.07, 0.14), 0.86, 0.20,
        boxstyle="round,pad=0.01", fc=C["card2"], ec=C["red"], lw=1.2,
        transform=ax.transAxes,
    ))
    ax.text(0.5, 0.31, "散户友情提醒", ha="center", fontsize=11.5, fontweight="bold",
            color=C["bg"],
            bbox=dict(boxstyle="round,pad=0.35", fc=C["red"], ec="none"),
            transform=ax.transAxes)
    # 大字号警示 - 47% 失败率
    ax.text(0.50, 0.245, "47%", ha="center", fontsize=32, fontweight="bold",
            color=C["red"], transform=ax.transAxes)
    ax.text(0.50, 0.195, "今日涨停失败率", ha="center", fontsize=10,
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.5, 0.155,
            "今天追高的, 明天大概率裂开",
            ha="center", fontsize=11, fontweight="bold", color=C["text"],
            transform=ax.transAxes)

    # 引导下一页
    ax.text(0.5, 0.075, "翻到下一页 → 收下这个市场温度计", ha="center",
            fontsize=11, fontweight="bold", color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.4", fc=C["card"], ec=C["border"]),
            transform=ax.transAxes)

    add_footer(ax, 6)
    save(fig, 6)


# ═══════════════════════════════════════════
# Page 7 — 求关注 CTA (大字 + 价值钩 + 卖点)
# ═══════════════════════════════════════════
def page7():
    fig, ax = new_card()
    pill(ax, 0.5, 0.95, "  关注我  ", C["rose"])

    # 顶部回扣前文 — 跟封面医药 vs 有色色块呼应
    ax.text(0.5, 0.895, "今天的医药狂飙明天还能续命吗?",
            ha="center", fontsize=12.5, color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.4", fc=C["card"], ec=C["border"]),
            transform=ax.transAxes)

    # 顶部价值主张 — 让用户秒懂"关注你能拿到啥"
    ax.text(0.5, 0.81, "每天 3 分钟", ha="center", fontsize=28, fontweight="bold",
            color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.74, "看懂 A 股", ha="center", fontsize=40, fontweight="bold",
            color=C["gold"], transform=ax.transAxes)

    # 三大卖点 — 卡片化
    sells = [
        ("01", "每日复盘", "涨停天梯 / 行业冠亚军 / 炸板预警", C["red"]),
        ("02", "散户雷达", "雪球今天突然在聊啥, 主力搬家路径", C["purple"]),
        ("03", "数据可视", "纯数据驱动, 拒绝小作文, 拒绝喊单", C["cyan"]),
    ]
    for i, (num, title, body, col) in enumerate(sells):
        y = 0.64 - i * 0.105
        # 子卡片
        ax.add_patch(FancyBboxPatch(
            (0.07, y - 0.042), 0.86, 0.085,
            boxstyle="round,pad=0.01", fc=C["card"], ec=C["border"], lw=0.8,
            transform=ax.transAxes,
        ))
        ax.text(0.13, y, num, ha="center", va="center", fontsize=22,
                fontweight="bold", color=col, transform=ax.transAxes)
        ax.text(0.22, y + 0.018, title, ha="left", fontsize=14, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        ax.text(0.22, y - 0.020, body, ha="left", fontsize=10,
                color=C["muted"], transform=ax.transAxes)

    # 主 CTA — 大字 + 高对比卡
    ax.add_patch(FancyBboxPatch(
        (0.07, 0.22), 0.86, 0.105,
        boxstyle="round,pad=0.01", fc=C["gold"], ec="none", lw=0,
        transform=ax.transAxes,
    ))
    ax.text(0.5, 0.285, "点关注 + 收藏 不迷路", ha="center", fontsize=20,
            fontweight="bold", color=C["bg"], transform=ax.transAxes)
    ax.text(0.5, 0.243, "明天盘中继续给你递数据", ha="center", fontsize=11,
            color=C["bg"], transform=ax.transAxes)

    # 互动钩子
    ax.text(0.5, 0.17, "评论区告诉我", ha="center", fontsize=12, fontweight="bold",
            color=C["cyan"], transform=ax.transAxes)
    ax.text(0.5, 0.13,
            "今天你是 \"医药党\" 还是 \"金子党\"?",
            ha="center", fontsize=12, color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.09,
            "明天想看 哪只票 的盘后追踪? 评论区点名 →",
            ha="center", fontsize=10, color=C["muted"], transform=ax.transAxes)

    add_footer(ax, 7)
    save(fig, 7)


if __name__ == "__main__":
    print(f"开始生成 7 页卡片到 {OUT}")
    page1(); page2(); page3(); page4(); page5(); page6(); page7()
    print(f"\n✅ 全部完成. 7 张 PNG 在 {OUT}")
