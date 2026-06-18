"""20260618 散户热点 6 页小红书叙事卡 v2 — 排版可视化优化版.

改进点:
- page_1: 双柱反差视觉 + 数字超大字号 + 钩子配色更"狠"
- page_2: 加水平条形图 (柱长 = 涨跌幅), 数据感拉满
- page_3: 阶梯感涨停天梯 + 行业分布柱图升级
- page_4: 讨论数简化为 w 单位, 字号拉大, HOT 标识更醒目
- page_5: 4 卡瘦身 (0.38x0.22) + 中间留十字带 + 圆角加边框
- page_6: 风险提示瘦身, CTA 放大, 01/02/03 加分隔
"""

from __future__ import annotations
import json
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

ROOT = Path("/das/user/QYJI/quant")
DATE = "20260618"
DAY_HUM = "2026-06-18"

SUMMARY = json.loads((ROOT / f"output/hotspot/{DATE}/summary.json").read_text())
OUT = ROOT / f"output/hotspot/{DATE}/cards"
OUT.mkdir(parents=True, exist_ok=True)

C = {
    "bg": "#0d1117", "card": "#161b22", "card2": "#1c2129", "border": "#30363d",
    "text": "#c9d1d9", "muted": "#8b949e", "dim": "#6e7681",
    "blue": "#58a6ff", "green": "#3fb950", "red": "#f85149",
    "orange": "#d2991d", "purple": "#bc8cff", "gold": "#f0c040",
    "cyan": "#56d4dd", "rose": "#ff7b72",
}
CARD_W, CARD_H, DPI = 7.2, 9.6, 200

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
            ha="center", va="center", fontsize=7, color=C["dim"], transform=ax.transAxes)
    ax.text(0.95, 0.025, f"{page}/{total}", ha="right", va="center",
            fontsize=8, color=C["dim"], transform=ax.transAxes)


def pill(ax, x, y, txt, fc, fs=10, color=None):
    ax.text(x, y, txt, ha="center", va="center", fontsize=fs, fontweight="bold",
            color=color if color else C["bg"],
            bbox=dict(boxstyle="round,pad=0.4", fc=fc, ec="none"),
            transform=ax.transAxes)


def hbar(ax, x_left, x_right, y, val, max_val, color, height=0.018):
    """水平条形图 — val 越大柱子越长. 从 x_left 起,最长到 x_right."""
    width = (x_right - x_left) * (abs(val) / max_val)
    rect = Rectangle((x_left, y - height/2), width, height,
                     facecolor=color, edgecolor="none", transform=ax.transAxes,
                     alpha=0.85)
    ax.add_patch(rect)


def save(fig, page):
    p = OUT / f"page_{page}.png"
    fig.savefig(p, dpi=DPI, bbox_inches="tight",
                facecolor=C["bg"], edgecolor="none", pad_inches=0.15)
    plt.close(fig)
    print(f"  saved {p}")


# ═══════════════════════════════════════════
# Page 1 — 封面 (双柱反差)
# ═══════════════════════════════════════════
def page1():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, f"  {DAY_HUM} · 周四盘中速报  ", C["gold"], fs=11)

    # 主标题区 — 三行,字号差异拉开
    ax.text(0.5, 0.88, "今天 A 股", ha="center", fontsize=24,
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.5, 0.81, "两个世界", ha="center", fontsize=56, fontweight="bold",
            color=C["text"], transform=ax.transAxes)

    # 双柱反差 — 左红右绿
    # 左列: 保险崩
    ax.add_patch(Rectangle((0.05, 0.46), 0.42, 0.30,
                           facecolor=C["card"], edgecolor=C["red"], lw=1.5,
                           transform=ax.transAxes, alpha=0.6))
    ax.text(0.26, 0.72, "保险板块", ha="center", fontsize=13,
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.26, 0.665, "-22亿", ha="center", fontsize=46, fontweight="bold",
            color=C["red"], transform=ax.transAxes)
    ax.text(0.26, 0.595, "主力一日撤出", ha="center", fontsize=10,
            color=C["dim"], transform=ax.transAxes)
    ax.text(0.26, 0.55, "跌 5.42%", ha="center", fontsize=14, fontweight="bold",
            color=C["red"], transform=ax.transAxes)
    ax.text(0.26, 0.50, "全场最惨", ha="center", fontsize=10,
            color=C["muted"], transform=ax.transAxes)

    # VS 标识
    ax.text(0.5, 0.61, "VS", ha="center", fontsize=22, fontweight="bold",
            color=C["gold"],
            bbox=dict(boxstyle="circle,pad=0.4", fc=C["card"], ec=C["gold"], lw=2),
            transform=ax.transAxes)

    # 右列: 蓝宝石嗨
    ax.add_patch(Rectangle((0.53, 0.46), 0.42, 0.30,
                           facecolor=C["card"], edgecolor=C["green"], lw=1.5,
                           transform=ax.transAxes, alpha=0.6))
    ax.text(0.74, 0.72, "蓝宝石概念", ha="center", fontsize=13,
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.74, 0.665, "+11亿", ha="center", fontsize=46, fontweight="bold",
            color=C["green"], transform=ax.transAxes)
    ax.text(0.74, 0.595, "主力净流入", ha="center", fontsize=10,
            color=C["dim"], transform=ax.transAxes)
    ax.text(0.74, 0.55, "涨 4.17%", ha="center", fontsize=14, fontweight="bold",
            color=C["green"], transform=ax.transAxes)
    ax.text(0.74, 0.50, "题材狂欢", ha="center", fontsize=10,
            color=C["muted"], transform=ax.transAxes)

    # 三大数字带
    ax.text(0.5, 0.37, "今日盘中数据", ha="center", fontsize=11,
            color=C["dim"], transform=ax.transAxes)
    nums = [
        (str(SUMMARY["zt_count"]), "涨停", C["red"]),
        (f"{SUMMARY['zt_max_board']}板", "最高连板", C["orange"]),
        (str(SUMMARY["zb_count"]), "炸板", C["muted"]),
    ]
    for i, (n, lbl, col) in enumerate(nums):
        x = [0.18, 0.50, 0.82][i]
        ax.text(x, 0.30, n, ha="center", fontsize=44, fontweight="bold",
                color=col, transform=ax.transAxes)
        ax.text(x, 0.235, lbl, ha="center", fontsize=12,
                color=C["muted"], transform=ax.transAxes)

    # 底部钩子
    ax.text(0.5, 0.155, "你站哪边? 翻到下一页看现场",
            ha="center", fontsize=14, fontweight="bold", color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.5", fc=C["card2"], ec=C["cyan"], lw=0.8),
            transform=ax.transAxes)
    ax.text(0.5, 0.10, "→ 后面5页全是干货 别划走", ha="center",
            fontsize=10, color=C["muted"], style="italic", transform=ax.transAxes)

    add_footer(ax, 1)
    save(fig, 1)


# ═══════════════════════════════════════════
# Page 2 — 行业冠亚军 (加条形图)
# ═══════════════════════════════════════════
def page2():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  钱去哪了  ", C["blue"], fs=11)
    ax.text(0.5, 0.895, "今日行业涨幅榜 vs 跌幅榜", ha="center",
            fontsize=18, fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.86, "条形长度 = 涨跌幅大小", ha="center",
            fontsize=9, color=C["dim"], style="italic", transform=ax.transAxes)

    # 涨幅榜 TOP5 (横向条形图)
    ax.text(0.5, 0.81, "涨幅榜 TOP5", ha="center", fontsize=13, fontweight="bold",
            color=C["green"], transform=ax.transAxes,
            bbox=dict(boxstyle="round,pad=0.3", fc=C["card"], ec="none"))

    top5 = SUMMARY["industry_top5"]
    bot5 = SUMMARY["industry_bottom5"]
    max_pct = max(top5[0]["pct_chg"], abs(bot5[0]["pct_chg"]))

    for yt, t in zip([0.74, 0.685, 0.63, 0.575, 0.52], top5):
        ax.text(0.05, yt, t["name"][:8], ha="left", fontsize=11.5,
                color=C["text"], transform=ax.transAxes, va="center")
        # 条形从 0.32 起向右伸到 0.78
        hbar(ax, 0.33, 0.78, yt, t["pct_chg"], max_pct, C["green"])
        ax.text(0.95, yt, f"+{t['pct_chg']:.2f}%", ha="right", fontsize=12.5,
                fontweight="bold", color=C["green"], transform=ax.transAxes, va="center")

    # 跌幅榜 TOP5
    ax.text(0.5, 0.475, "跌幅榜 TOP5", ha="center", fontsize=13, fontweight="bold",
            color=C["red"], transform=ax.transAxes,
            bbox=dict(boxstyle="round,pad=0.3", fc=C["card"], ec="none"))

    for yt, b in zip([0.40, 0.345, 0.29, 0.235, 0.18], bot5):
        ax.text(0.05, yt, b["name"][:8], ha="left", fontsize=11.5,
                color=C["text"], transform=ax.transAxes, va="center")
        hbar(ax, 0.33, 0.78, yt, b["pct_chg"], max_pct, C["red"])
        ax.text(0.95, yt, f"{b['pct_chg']:.2f}%", ha="right", fontsize=12.5,
                fontweight="bold", color=C["red"], transform=ax.transAxes, va="center")

    # 底部金句
    ax.text(0.5, 0.10, "钱从大金融跑到小盘题材",
            ha="center", fontsize=13, fontweight="bold", color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.5", fc=C["card2"], ec=C["cyan"], lw=0.8),
            transform=ax.transAxes)

    add_footer(ax, 2)
    save(fig, 2)


# ═══════════════════════════════════════════
# Page 3 — 涨停天梯 (阶梯感)
# ═══════════════════════════════════════════
def page3():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  涨停天梯  ", C["red"], fs=11)
    ax.text(0.5, 0.895, f"今日 {SUMMARY['zt_count']} 只涨停 · 最高 {SUMMARY['zt_max_board']} 连板",
            ha="center", fontsize=15, fontweight="bold", color=C["text"], transform=ax.transAxes)

    # 6 行涨停股 - 阶梯感: 连板数大的左侧 indent 少, 视觉上像往上爬
    rows_y = [0.80, 0.725, 0.65, 0.575, 0.50, 0.425]
    for y, x in zip(rows_y, SUMMARY["zt_top10"][:6]):
        # 左侧大数字 - 连板数
        lb = x['连板数']
        # 不同连板数用不同颜色
        if lb >= 4:
            col = C["red"]
        elif lb >= 3:
            col = C["orange"]
        else:
            col = C["gold"]
        ax.text(0.10, y, f"{lb}", ha="center", fontsize=36,
                fontweight="bold", color=col, transform=ax.transAxes, va="center")
        ax.text(0.10, y - 0.045, "连板", ha="center", fontsize=8,
                color=C["dim"], transform=ax.transAxes)

        # 中部信息 - 卡片背景
        ax.add_patch(Rectangle((0.21, y-0.035), 0.55, 0.060,
                               facecolor=C["card"], edgecolor=C["border"], lw=0.5,
                               transform=ax.transAxes))
        ax.text(0.235, y + 0.012, x["名称"], ha="left", fontsize=14.5,
                fontweight="bold", color=C["text"], transform=ax.transAxes, va="center")
        ax.text(0.235, y - 0.018, f"{x['代码']}  ·  {x['所属行业']}", ha="left",
                fontsize=9.5, color=C["muted"], transform=ax.transAxes, va="center")

        # 右侧涨幅
        try:
            pct = float(x["涨跌幅"])
        except (TypeError, ValueError):
            pct = 0
        ax.text(0.93, y, f"+{pct:.1f}%", ha="right", fontsize=15,
                fontweight="bold", color=C["green"], transform=ax.transAxes, va="center")

    # 涨停最密集行业 - 柱图
    ax.text(0.5, 0.355, "涨停最密集的 5 个行业", ha="center", fontsize=12,
            fontweight="bold", color=C["text"], transform=ax.transAxes)
    industries = SUMMARY["zt_top_industries"][:5]
    max_cnt = industries[0]["涨停数"] if industries else 1
    for i, ind in enumerate(industries):
        x = 0.10 + i * 0.20
        # 柱
        bar_h = 0.10 * (ind["涨停数"] / max_cnt)
        ax.add_patch(Rectangle((x-0.045, 0.18), 0.09, bar_h,
                               facecolor=C["orange"], edgecolor="none",
                               transform=ax.transAxes, alpha=0.7))
        ax.text(x, 0.18 + bar_h + 0.018, f"{ind['涨停数']}", ha="center", fontsize=14,
                fontweight="bold", color=C["orange"], transform=ax.transAxes)
        ax.text(x, 0.155, ind["行业"][:5], ha="center", fontsize=9,
                color=C["text"], transform=ax.transAxes)

    # 金句
    ax.text(0.5, 0.085, "通用设备+汽车零部当头, 老经济散户基地",
            ha="center", fontsize=11, color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.4", fc=C["card2"], ec=C["cyan"], lw=0.6),
            transform=ax.transAxes)

    add_footer(ax, 3)
    save(fig, 3)


# ═══════════════════════════════════════════
# Page 4 — 雪球新热点
# ═══════════════════════════════════════════
def page4():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  散户雷达  ", C["purple"], fs=11)
    ax.text(0.5, 0.895, "雪球今天突然热起来的 5 只", ha="center",
            fontsize=17, fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.86, "讨论榜入TOP10  但平时不在长期关注榜", ha="center",
            fontsize=9.5, color=C["dim"], style="italic", transform=ax.transAxes)

    follow_codes = {x['股票代码'] for x in SUMMARY['xueqiu_follow_top10']}
    new_buzz = [x for x in SUMMARY['xueqiu_tweet_top10']
                if x['股票代码'] not in follow_codes][:5]

    rows_y = [0.77, 0.66, 0.55, 0.44, 0.33]
    for y, x in zip(rows_y, new_buzz):
        # 卡片底
        ax.add_patch(Rectangle((0.05, y-0.045), 0.90, 0.085,
                               facecolor=C["card"], edgecolor=C["border"], lw=0.5,
                               transform=ax.transAxes))
        # HOT 红药丸
        ax.text(0.115, y, "HOT", ha="center", fontsize=11, fontweight="bold",
                color=C["bg"],
                bbox=dict(boxstyle="round,pad=0.35", fc=C["red"], ec="none"),
                transform=ax.transAxes, va="center")
        # 名字
        ax.text(0.20, y + 0.018, x["股票简称"], ha="left", fontsize=16.5,
                fontweight="bold", color=C["text"], transform=ax.transAxes, va="center")
        ax.text(0.20, y - 0.022, x["股票代码"], ha="left", fontsize=10,
                color=C["muted"], transform=ax.transAxes, va="center")
        # 讨论数 (转换成 w)
        followers = float(x['关注'])
        if followers >= 10000:
            disp = f"{followers/10000:.1f}w"
        else:
            disp = f"{int(followers):,}"
        ax.text(0.92, y + 0.018, disp, ha="right", fontsize=18,
                fontweight="bold", color=C["purple"], transform=ax.transAxes, va="center")
        ax.text(0.92, y - 0.022, f"讨论 · 价{x['最新价']}", ha="right", fontsize=9.5,
                color=C["muted"], transform=ax.transAxes, va="center")

    # 金句
    ax.text(0.5, 0.21, "AI算力 + 智驾 = 散户今天两大共识",
            ha="center", fontsize=13, fontweight="bold", color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.5", fc=C["card2"], ec=C["cyan"], lw=0.8),
            transform=ax.transAxes)
    ax.text(0.5, 0.135, "讨论量 ≠ 涨幅\n是\"嘴上炒\" 还是真买入 看明天就知道", ha="center",
            fontsize=10, color=C["muted"], transform=ax.transAxes)

    add_footer(ax, 4)
    save(fig, 4)


# ═══════════════════════════════════════════
# Page 5 — 龙头快报 (4 卡瘦身)
# ═══════════════════════════════════════════
def page5():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  4 只散户最关注  ", C["orange"], fs=11)
    ax.text(0.5, 0.895, "实涨 vs 嘴上炒", ha="center",
            fontsize=18, fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.86, "上排 = 真涨幅 / 下排 = 雪球讨论热度", ha="center",
            fontsize=9.5, color=C["dim"], style="italic", transform=ax.transAxes)

    # 4 卡片瘦身: 0.38 x 0.22, 留更多间距
    cards_data = [
        # 上排 - 实涨派
        ("兆易创新", "SH603986", "+8.11%", "633.58", C["green"], "存储芯片龙头", "REAL"),
        ("国瓷材料", "SZ300285", "+13.90%", "89.41",  C["red"],   "蓝宝石+材料", "REAL"),
        # 下排 - 嘴上炒派
        ("寒武纪",   "SH688256", "讨论 3.6w",  "1495.7", C["purple"], "AI算力一哥", "BUZZ"),
        ("赛力斯",   "SH601127", "讨论 7.7w",  "64.55",  C["purple"], "今日突然爆热", "BUZZ"),
    ]
    positions = [(0.27, 0.65), (0.73, 0.65), (0.27, 0.40), (0.73, 0.40)]
    cw, ch = 0.38, 0.20
    for (cx, cy), (name, code, pct, price, col, tag, kind) in zip(positions, cards_data):
        # 主卡
        rect = FancyBboxPatch(
            (cx - cw/2, cy - ch/2), cw, ch,
            boxstyle="round,pad=0.005,rounding_size=0.012",
            fc=C["card"], ec=C["border"], lw=1.2,
            transform=ax.transAxes,
        )
        ax.add_patch(rect)
        # 角标 - 类型
        kind_col = C["green"] if kind == "REAL" else C["purple"]
        ax.text(cx - cw/2 + 0.045, cy + ch/2 - 0.025, kind, ha="center", fontsize=8,
                fontweight="bold", color=C["bg"],
                bbox=dict(boxstyle="round,pad=0.25", fc=kind_col, ec="none"),
                transform=ax.transAxes)
        # 名字
        ax.text(cx, cy + 0.055, name, ha="center", fontsize=15.5, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        # 代码
        ax.text(cx, cy + 0.022, code, ha="center", fontsize=9.5,
                color=C["dim"], transform=ax.transAxes)
        # 主指标
        ax.text(cx, cy - 0.020, pct, ha="center", fontsize=18, fontweight="bold",
                color=col, transform=ax.transAxes)
        # 价
        ax.text(cx, cy - 0.055, f"价 {price}", ha="center", fontsize=10,
                color=C["muted"], transform=ax.transAxes)
        # 标签
        ax.text(cx, cy - 0.080, tag, ha="center", fontsize=10, fontweight="bold",
                color=C["cyan"], transform=ax.transAxes)

    # 中间分隔标识
    ax.text(0.5, 0.525, "─ ─ ─", ha="center", fontsize=12,
            color=C["dim"], transform=ax.transAxes)

    # 底部点评
    ax.text(0.5, 0.245, "一句话点评", ha="center", fontsize=11, fontweight="bold",
            color=C["bg"],
            bbox=dict(boxstyle="round,pad=0.35", fc=C["gold"], ec="none"),
            transform=ax.transAxes)
    ax.text(0.5, 0.175,
            "兆易/国瓷是真金白银涨\n寒武/赛力斯是雪球嘴炮 股价没跟上",
            ha="center", fontsize=11, color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.105, "明天看谁的故事讲得下去",
            ha="center", fontsize=11, fontweight="bold", color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.4", fc=C["card2"], ec=C["cyan"], lw=0.6),
            transform=ax.transAxes)

    add_footer(ax, 5)
    save(fig, 5)


# ═══════════════════════════════════════════
# Page 6 — 总结 + CTA (CTA 放大)
# ═══════════════════════════════════════════
def page6():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  今日总结  ", C["gold"], fs=11)
    ax.text(0.5, 0.895, "三句话看懂今天 A 股", ha="center",
            fontsize=18, fontweight="bold", color=C["text"], transform=ax.transAxes)

    points = [
        ("01", "保险崩塌", C["red"],    "保险板块跌5.42%, 主力一日撤22亿"),
        ("02", "题材狂欢", C["green"],  "蓝宝石+4.17% 净流入11亿 国瓷材料封涨"),
        ("03", "散户进场", C["purple"], "雪球突然在聊赛力斯/寒武纪 5只新热点"),
    ]
    for i, (y, (num, title, col, body)) in enumerate(zip([0.79, 0.69, 0.59], points)):
        # 数字大圆
        ax.text(0.13, y, num, ha="center", fontsize=32, fontweight="bold",
                color=col, transform=ax.transAxes, va="center")
        # 标题 + 内容
        ax.text(0.25, y + 0.020, title, ha="left", fontsize=17, fontweight="bold",
                color=C["text"], transform=ax.transAxes, va="center")
        ax.text(0.25, y - 0.025, body, ha="left", fontsize=11,
                color=C["muted"], transform=ax.transAxes, va="center")
        # 分隔线 (除最后一行)
        if i < 2:
            ax.plot([0.10, 0.90], [y - 0.052, y - 0.052], color=C["border"], lw=0.5,
                    transform=ax.transAxes)

    # 风险提示 - 瘦身
    ax.add_patch(FancyBboxPatch((0.08, 0.36), 0.84, 0.13,
                                boxstyle="round,pad=0.01,rounding_size=0.012",
                                facecolor=C["card"], edgecolor=C["orange"], lw=1,
                                transform=ax.transAxes))
    ax.text(0.5, 0.46, "散户友情提醒", ha="center", fontsize=11, fontweight="bold",
            color=C["bg"],
            bbox=dict(boxstyle="round,pad=0.3", fc=C["orange"], ec="none"),
            transform=ax.transAxes)
    ax.text(0.5, 0.41, "今天炸板 30 只 = 30 个被埋的散户群",
            ha="center", fontsize=11.5, color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.378, "切换日抢热点 = 容易接最后一棒",
            ha="center", fontsize=10.5, color=C["muted"], transform=ax.transAxes)

    # CTA 放大
    ax.text(0.5, 0.27, "你今天怎么操作的?", ha="center", fontsize=20, fontweight="bold",
            color=C["text"], transform=ax.transAxes)
    ax.add_patch(FancyBboxPatch((0.08, 0.13), 0.84, 0.10,
                                boxstyle="round,pad=0.01,rounding_size=0.012",
                                facecolor=C["card2"], edgecolor=C["cyan"], lw=1.2,
                                transform=ax.transAxes))
    ax.text(0.5, 0.205, "买保险被埋   抢到蓝宝石   还在观望", ha="center",
            fontsize=12, color=C["muted"], transform=ax.transAxes)
    ax.text(0.5, 0.158, "评论区报上你的战绩", ha="center",
            fontsize=15, fontweight="bold", color=C["cyan"], transform=ax.transAxes)
    ax.text(0.5, 0.10, "(说被埋的我陪你)", ha="center",
            fontsize=10, color=C["muted"], style="italic", transform=ax.transAxes)

    add_footer(ax, 6)
    save(fig, 6)


if __name__ == "__main__":
    print(f"开始生成 v2 优化版 6 页卡片到 {OUT}")
    page1(); page2(); page3(); page4(); page5(); page6()
    print(f"\n全部完成. 6 张 PNG 在 {OUT}")
