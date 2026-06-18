"""20260618 散户热点小红书 6 页深色卡片

数据源: output/hotspot/20260618/summary.json
产出:   output/hotspot/20260618/cards/page_1.png ... page_6.png

调色板与字体规范沿用 a-share-quant-research skill (深色 GitHub 风).
"""

from __future__ import annotations
import json
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

# ─── 路径 ───────────────────────────
ROOT = Path("/das/user/QYJI/quant")
DATE = "20260618"
DAY_HUM = "2026-06-18"
SUMMARY = json.loads((ROOT / f"output/hotspot/{DATE}/summary.json").read_text())
OUT = ROOT / f"output/hotspot/{DATE}/cards"
OUT.mkdir(parents=True, exist_ok=True)

# ─── 调色板 (沿用 quant skill) ──────
C = {
    "bg": "#0d1117", "card": "#161b22", "border": "#30363d",
    "text": "#c9d1d9", "muted": "#8b949e",
    "blue": "#58a6ff", "green": "#3fb950", "red": "#f85149",
    "orange": "#d2991d", "purple": "#bc8cff", "gold": "#f0c040",
    "cyan": "#56d4dd",
}
CARD_W, CARD_H, DPI = 7.2, 9.6, 200

# 字体
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


def add_footer(ax, page, total=6):
    ax.text(0.5, 0.025, "* 数据来源: 东方财富/雪球 · 历史不代表未来 · 不构成投资建议",
            ha="center", va="center", fontsize=7, color=C["muted"], transform=ax.transAxes)
    ax.text(0.95, 0.025, f"{page}/{total}", ha="right", va="center",
            fontsize=8, color=C["muted"], transform=ax.transAxes)


def pill(ax, x, y, txt, fc, w=0.12, h=0.04, fs=10):
    """文字药丸"""
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
# Page 1 — 封面: "今日热搜不会撒谎"
# ═══════════════════════════════════════════
def page1():
    fig, ax = new_card()
    # 顶部日期 pill
    pill(ax, 0.5, 0.95, f"  {DAY_HUM} · 盘中速报  ", C["gold"], fs=10)

    # 主标题
    ax.text(0.5, 0.85, "今日 A 股", ha="center", va="center",
            fontsize=36, fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.78, "高低切换", ha="center", va="center",
            fontsize=42, fontweight="bold", color=C["green"], transform=ax.transAxes)
    ax.text(0.5, 0.71, "现场图", ha="center", va="center",
            fontsize=36, fontweight="bold", color=C["text"], transform=ax.transAxes)

    # 三个核心数字 (横排)
    nums = [
        (SUMMARY["zt_count"], "涨停", C["red"]),
        (SUMMARY["zt_max_board"], "最高连板", C["orange"]),
        (SUMMARY["zb_count"], "炸板", C["muted"]),
    ]
    xs = [0.18, 0.50, 0.82]
    for i, (n, lbl, col) in enumerate(nums):
        ax.text(xs[i], 0.50, str(n), ha="center", va="center",
                fontsize=52, fontweight="bold", color=col, transform=ax.transAxes)
        ax.text(xs[i], 0.40, lbl, ha="center", va="center",
                fontsize=14, color=C["muted"], transform=ax.transAxes)

    # 一句话钩子 - 放在卡片中部居中, 别压脚注
    ax.text(0.5, 0.27, "算力链涨停潮 vs 保险煤炭血崩",
            ha="center", va="center", fontsize=18, fontweight="bold",
            color=C["cyan"], transform=ax.transAxes,
            bbox=dict(boxstyle="round,pad=0.6", fc=C["card"], ec=C["border"]))
    ax.text(0.5, 0.18, "这是\"切换日\"的标准教科书剧本",
            ha="center", va="center", fontsize=12, color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.13, "翻到下一页 → 看今天到底谁在涨",
            ha="center", va="center", fontsize=10, color=C["muted"],
            style="italic", transform=ax.transAxes)

    add_footer(ax, 1)
    save(fig, 1)


# ═══════════════════════════════════════════
# Page 2 — 行业涨跌冠亚军 双柱对比
# ═══════════════════════════════════════════
def page2():
    fig, ax = new_card()

    pill(ax, 0.5, 0.95, "  行业冠亚军  ", C["blue"], fs=10)
    ax.text(0.5, 0.89, "今天买啥赚 / 买啥亏", ha="center", va="center",
            fontsize=18, fontweight="bold", color=C["text"], transform=ax.transAxes)

    # 左侧: 涨幅 TOP5
    ax.text(0.27, 0.83, "涨幅榜 TOP5", ha="center", fontsize=14, fontweight="bold",
            color=C["green"], transform=ax.transAxes)
    top5 = SUMMARY["industry_top5"]
    bot5 = SUMMARY["industry_bottom5"]
    y_starts = [0.74, 0.66, 0.58, 0.50, 0.42]
    for i, (yt, t, b) in enumerate(zip(y_starts, top5, bot5)):
        # 左
        ax.text(0.05, yt, t["name"][:6], ha="left", va="center",
                fontsize=12, color=C["text"], transform=ax.transAxes)
        ax.text(0.50, yt, f"+{t['pct_chg']:.2f}%", ha="right", va="center",
                fontsize=14, fontweight="bold", color=C["green"], transform=ax.transAxes)
        # 右
        ax.text(0.55, yt, b["name"][:6], ha="left", va="center",
                fontsize=12, color=C["text"], transform=ax.transAxes)
        ax.text(0.97, yt, f"{b['pct_chg']:.2f}%", ha="right", va="center",
                fontsize=14, fontweight="bold", color=C["red"], transform=ax.transAxes)

    ax.text(0.78, 0.83, "跌幅榜 TOP5", ha="center", fontsize=14, fontweight="bold",
            color=C["red"], transform=ax.transAxes)

    # 中间分割线
    ax.plot([0.525, 0.525], [0.40, 0.80], color=C["border"], lw=0.8, transform=ax.transAxes)

    # 资金流: 龙头主力净流入对比
    ax.text(0.5, 0.32, "主力资金动向", ha="center", fontsize=13, fontweight="bold",
            color=C["text"], transform=ax.transAxes)

    ax.text(0.27, 0.25, f"半导体 +{top5[3]['pct_chg']:.2f}%", ha="center", fontsize=11,
            color=C["text"], transform=ax.transAxes)
    ax.text(0.27, 0.20, f"+{top5[3]['main_net_in']/1e8:.1f}亿", ha="center", fontsize=22,
            fontweight="bold", color=C["green"], transform=ax.transAxes)
    ax.text(0.27, 0.14, "主力净流入", ha="center", fontsize=10,
            color=C["muted"], transform=ax.transAxes)

    ax.text(0.78, 0.25, f"电力 {bot5[2]['pct_chg']:.2f}%", ha="center", fontsize=11,
            color=C["text"], transform=ax.transAxes)
    ax.text(0.78, 0.20, f"{bot5[2]['main_net_in']/1e8:.1f}亿", ha="center", fontsize=22,
            fontweight="bold", color=C["red"], transform=ax.transAxes)
    ax.text(0.78, 0.14, "主力净流出", ha="center", fontsize=10,
            color=C["muted"], transform=ax.transAxes)

    # 一句话评论
    ax.text(0.5, 0.075, "钱从\"红利防御\"向\"算力进攻\"流", ha="center", va="center",
            fontsize=12, fontweight="bold", color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.4", fc=C["card"], ec=C["border"]),
            transform=ax.transAxes)

    add_footer(ax, 2)
    save(fig, 2)


# ═══════════════════════════════════════════
# Page 3 — 涨停天梯
# ═══════════════════════════════════════════
def page3():
    fig, ax = new_card()
    pill(ax, 0.5, 0.95, "  涨停天梯  ", C["red"], fs=10)
    ax.text(0.5, 0.89, f"今日 {SUMMARY['zt_count']} 只涨停 · 最高 {SUMMARY['zt_max_board']} 连板",
            ha="center", va="center", fontsize=14, color=C["text"], transform=ax.transAxes)

    top6 = SUMMARY["zt_top10"][:6]
    y_pos = [0.78, 0.69, 0.60, 0.51, 0.42, 0.33]
    for y, x in zip(y_pos, top6):
        # 连板数大字
        ax.text(0.10, y, f"{x['连板数']}", ha="center", va="center",
                fontsize=28, fontweight="bold", color=C["red"], transform=ax.transAxes)
        ax.text(0.10, y - 0.045, "连板", ha="center", va="center",
                fontsize=8, color=C["muted"], transform=ax.transAxes)
        # 名称
        ax.text(0.21, y + 0.015, x["名称"], ha="left", va="center",
                fontsize=15, fontweight="bold", color=C["text"], transform=ax.transAxes)
        ax.text(0.21, y - 0.030, f"{x['代码']} · {x['所属行业']}", ha="left", va="center",
                fontsize=10, color=C["muted"], transform=ax.transAxes)
        # 涨幅
        try:
            pct = float(x["涨跌幅"])
        except (TypeError, ValueError):
            pct = 0
        ax.text(0.93, y, f"+{pct:.2f}%", ha="right", va="center",
                fontsize=14, fontweight="bold", color=C["green"], transform=ax.transAxes)

    # 行业分布 mini
    ax.text(0.5, 0.255, "涨停最密集的行业", ha="center", fontsize=12,
            fontweight="bold", color=C["text"], transform=ax.transAxes)
    inds = SUMMARY["zt_top_industries"]
    for i, ind in enumerate(inds[:5]):
        x = 0.10 + i * 0.20
        ax.text(x, 0.20, ind["行业"][:5], ha="center", fontsize=10,
                color=C["text"], transform=ax.transAxes)
        ax.text(x, 0.155, f"{ind['涨停数']}", ha="center", fontsize=20,
                fontweight="bold", color=C["orange"], transform=ax.transAxes)
        ax.text(x, 0.115, "只", ha="center", fontsize=8,
                color=C["muted"], transform=ax.transAxes)

    ax.text(0.5, 0.07, "通用设备+汽车零部当头, 老经济+新制造混搭",
            ha="center", va="center", fontsize=11, color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.4", fc=C["card"], ec=C["border"]),
            transform=ax.transAxes)

    add_footer(ax, 3)
    save(fig, 3)


# ═══════════════════════════════════════════
# Page 4 — 雪球散户在聊啥
# ═══════════════════════════════════════════
def page4():
    fig, ax = new_card()
    pill(ax, 0.5, 0.95, "  散户雷达  ", C["purple"], fs=10)
    ax.text(0.5, 0.89, "雪球今天突然热起来的 5 只", ha="center", va="center",
            fontsize=16, fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.85, "(讨论榜入TOP10但平时不在关注榜)", ha="center", va="center",
            fontsize=9, color=C["muted"], style="italic", transform=ax.transAxes)

    # 找新热点
    follow_codes = {x['股票代码'] for x in SUMMARY['xueqiu_follow_top10']}
    new_buzz = [x for x in SUMMARY['xueqiu_tweet_top10'] if x['股票代码'] not in follow_codes][:5]

    y_pos = [0.74, 0.62, 0.50, 0.38, 0.26]
    for y, x in zip(y_pos, new_buzz):
        # 序号 (火药丸代替 emoji)
        ax.text(0.08, y, "HOT", ha="center", va="center", fontsize=10, fontweight="bold",
                color=C["bg"],
                bbox=dict(boxstyle="round,pad=0.3", fc=C["red"], ec="none"),
                transform=ax.transAxes)
        # 名称 + code
        ax.text(0.18, y + 0.02, x["股票简称"], ha="left", va="center",
                fontsize=16, fontweight="bold", color=C["text"], transform=ax.transAxes)
        ax.text(0.18, y - 0.025, x["股票代码"], ha="left", va="center",
                fontsize=10, color=C["muted"], transform=ax.transAxes)
        # 讨论量
        ax.text(0.93, y + 0.02, f"{x['关注']:,}", ha="right", va="center",
                fontsize=14, fontweight="bold", color=C["purple"], transform=ax.transAxes)
        ax.text(0.93, y - 0.025, f"价 {x['最新价']}", ha="right", va="center",
                fontsize=10, color=C["muted"], transform=ax.transAxes)

    ax.text(0.5, 0.165, "AI 算力 + 智驾 = 今日两大共识",
            ha="center", va="center", fontsize=12, fontweight="bold", color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.4", fc=C["card"], ec=C["border"]),
            transform=ax.transAxes)
    ax.text(0.5, 0.10, "寒武纪 1497 · 胜宏科技 369 · 新易盛 578",
            ha="center", va="center", fontsize=10, color=C["muted"],
            transform=ax.transAxes)

    add_footer(ax, 4)
    save(fig, 4)


# ═══════════════════════════════════════════
# Page 5 — 龙头个股快报
# ═══════════════════════════════════════════
def page5():
    fig, ax = new_card()
    pill(ax, 0.5, 0.95, "  龙头快报  ", C["orange"], fs=10)
    ax.text(0.5, 0.89, "算力链 4 只代表股", ha="center", va="center",
            fontsize=18, fontweight="bold", color=C["text"], transform=ax.transAxes)

    # 4 只代表股, 2x2 网格 (从 em_hot_top10 + xueqiu 取)
    em = {x["代码"]: x for x in SUMMARY["em_hot_top10"]}
    cards_data = [
        ("兆易创新", "SH603986", "+8.06%", "633.29", C["green"], "存储芯片龙头"),
        ("中京电子", "SZ002579", "+10.02%", "20.32", C["red"], "PCB涨停"),
        ("寒武纪", "SH688256", "雪球讨论 36k+", "1497", C["purple"], "AI算力一哥"),
        ("胜宏科技", "SZ300476", "雪球讨论 35k+", "369", C["purple"], "PCB+AI 双线"),
    ]
    positions = [(0.27, 0.66), (0.73, 0.66), (0.27, 0.36), (0.73, 0.36)]
    for (cx, cy), (name, code, pct, price, col, tag) in zip(positions, cards_data):
        # 卡片背景
        rect = FancyBboxPatch(
            (cx - 0.21, cy - 0.13), 0.42, 0.26,
            boxstyle="round,pad=0.01", fc=C["card"], ec=C["border"], lw=1,
            transform=ax.transAxes,
        )
        ax.add_patch(rect)
        ax.text(cx, cy + 0.085, name, ha="center", va="center",
                fontsize=15, fontweight="bold", color=C["text"], transform=ax.transAxes)
        ax.text(cx, cy + 0.045, code, ha="center", va="center",
                fontsize=9, color=C["muted"], transform=ax.transAxes)
        ax.text(cx, cy - 0.005, pct, ha="center", va="center",
                fontsize=18, fontweight="bold", color=col, transform=ax.transAxes)
        ax.text(cx, cy - 0.05, f"价 {price}", ha="center", va="center",
                fontsize=10, color=C["muted"], transform=ax.transAxes)
        ax.text(cx, cy - 0.10, tag, ha="center", va="center",
                fontsize=10, color=C["cyan"], transform=ax.transAxes)

    ax.text(0.5, 0.18, "一句话点评", ha="center", fontsize=12,
            fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.115,
            "AI 算力今天又是\"涨完一波接一波\"\n但寒武纪 1497, 胜宏 369 都已\"贵到只能远观\"",
            ha="center", va="center", fontsize=10, color=C["muted"],
            transform=ax.transAxes)

    add_footer(ax, 5)
    save(fig, 5)


# ═══════════════════════════════════════════
# Page 6 — 总结 + 选题钩子
# ═══════════════════════════════════════════
def page6():
    fig, ax = new_card()
    pill(ax, 0.5, 0.95, "  今日总结  ", C["gold"], fs=10)
    ax.text(0.5, 0.89, "三句话看懂今天 A 股", ha="center", va="center",
            fontsize=18, fontweight="bold", color=C["text"], transform=ax.transAxes)

    points = [
        ("01", "高低切换", C["red"],
         "保险/电力/煤炭血崩, 主力撤出红利防御"),
        ("02", "算力主线", C["green"],
         "半导体净流入 29 亿, 寒武纪/胜宏/新易盛在雪球封神"),
        ("03", "妖股回归", C["orange"],
         "62 涨停 4 连板, 旭光电子领头, 通用设备/汽车零部混战"),
    ]
    y_starts = [0.76, 0.60, 0.44]
    for y, (num, title, col, body) in zip(y_starts, points):
        # 大数字
        ax.text(0.10, y, num, ha="center", va="center",
                fontsize=36, fontweight="bold", color=col, transform=ax.transAxes)
        # 标题
        ax.text(0.22, y + 0.025, title, ha="left", va="center",
                fontsize=18, fontweight="bold", color=C["text"], transform=ax.transAxes)
        # 正文
        ax.text(0.22, y - 0.035, body, ha="left", va="center",
                fontsize=11, color=C["muted"], transform=ax.transAxes,
                wrap=True)

    # 风险提示
    ax.text(0.5, 0.30, "散户友情提醒", ha="center", va="center",
            fontsize=12, fontweight="bold", color=C["bg"],
            bbox=dict(boxstyle="round,pad=0.4", fc=C["orange"], ec="none"),
            transform=ax.transAxes)
    ax.text(0.5, 0.22,
            "30 只炸板今天高位接货的散户已被埋\n"
            "高位股追涨 = 吃别人剩下的, 切换日尤其危险",
            ha="center", va="center", fontsize=10.5, color=C["text"],
            transform=ax.transAxes)

    # CTA
    ax.text(0.5, 0.10, "你今天买啥了? 评论区聊聊",
            ha="center", va="center", fontsize=12, fontweight="bold", color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.4", fc=C["card"], ec=C["border"]),
            transform=ax.transAxes)

    add_footer(ax, 6)
    save(fig, 6)


# ═══════════════════════════════════════════
if __name__ == "__main__":
    print(f"开始生成 6 页卡片到 {OUT}")
    page1(); page2(); page3(); page4(); page5(); page6()
    print(f"\n✅ 全部完成. 6 张 PNG 在 {OUT}")
