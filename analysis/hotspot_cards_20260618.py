"""20260618 散户热点 6 页小红书叙事卡 v3 — 修叠字 + 排版精修.

v3 改动 (基于 vision 复检):
- page_1: "今天A股" 上移避让大字, 板块名上移到双柱卡上方,
          "今日盘中数据" 与三大数字拉开间距, 字号层级重排
- page_2: 跌幅榜标题上下间距修匀, 底部 CTA 留白拉大
- page_3: 阶梯左移 (0.10 → 0.07), 卡片右移 (0.21 → 0.25),
          "连板"小字下移, 行间距加大
- page_4: 主标题/副标题间距拉大, 卡内右下副信息字号下调
- page_5: 上下两排 y 间距拉到 ~0.20, 加 "↑真涨 / ↓嘴炒" 分隔标
- page_6: CTA 主句放大、三选项改胶囊小标签, 增加关注钩子
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
# Page 1 — 封面 (双柱反差) — v3 修叠字
# ═══════════════════════════════════════════
def page1():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, f"  {DAY_HUM} · 周四盘中速报  ", C["gold"], fs=11)

    # 主标题区 — v3.1 修: 改成"上下两行 + 加大间距 + 副标小字号"避免叠
    # 关键: 大字 fontsize 改为 44 (从 52 降), y=0.81; 副标 y=0.895,
    # 间距从 0.07 拉到 0.085, 大字字高 (44pt @200dpi ≈ 0.045 axes), 安全
    ax.text(0.5, 0.895, "今天 A 股", ha="center", fontsize=20,
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.5, 0.81, "两个世界", ha="center", fontsize=44, fontweight="bold",
            color=C["text"], transform=ax.transAxes)

    # 双柱反差 — 板块名挪到卡片"上方外侧" (修: 不再压在大数字底下)
    # 卡片 y 范围 0.46~0.74 (高 0.28), 板块名放在 0.78 上方
    ax.text(0.26, 0.78, "保险板块", ha="center", fontsize=13, fontweight="bold",
            color=C["red"], transform=ax.transAxes)
    ax.text(0.74, 0.78, "蓝宝石概念", ha="center", fontsize=13, fontweight="bold",
            color=C["green"], transform=ax.transAxes)

    # 左列: 保险崩
    ax.add_patch(Rectangle((0.05, 0.46), 0.42, 0.30,
                           facecolor=C["card"], edgecolor=C["red"], lw=1.5,
                           transform=ax.transAxes, alpha=0.6))
    ax.text(0.26, 0.66, "-22亿", ha="center", fontsize=46, fontweight="bold",
            color=C["red"], transform=ax.transAxes)
    ax.text(0.26, 0.585, "主力一日撤出", ha="center", fontsize=10,
            color=C["dim"], transform=ax.transAxes)
    ax.text(0.26, 0.535, "跌 5.42%", ha="center", fontsize=14, fontweight="bold",
            color=C["red"], transform=ax.transAxes)
    ax.text(0.26, 0.49, "全场最惨", ha="center", fontsize=10,
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
    ax.text(0.74, 0.66, "+11亿", ha="center", fontsize=46, fontweight="bold",
            color=C["green"], transform=ax.transAxes)
    ax.text(0.74, 0.585, "主力净流入", ha="center", fontsize=10,
            color=C["dim"], transform=ax.transAxes)
    ax.text(0.74, 0.535, "涨 4.17%", ha="center", fontsize=14, fontweight="bold",
            color=C["green"], transform=ax.transAxes)
    ax.text(0.74, 0.49, "题材狂欢", ha="center", fontsize=10,
            color=C["muted"], transform=ax.transAxes)

    # 三大数字带 — 修: 标签往上挪开数字, 数字下移留呼吸
    # 之前 "今日盘中数据" 0.37, 大数字 0.30 -> 大数字 44pt 高度约 0.06 直接撞标题
    ax.text(0.5, 0.405, "今日盘中数据", ha="center", fontsize=10.5,
            color=C["dim"], transform=ax.transAxes,
            bbox=dict(boxstyle="round,pad=0.25", fc=C["card"], ec="none"))
    nums = [
        (str(SUMMARY["zt_count"]), "涨停", C["red"]),
        (f"{SUMMARY['zt_max_board']}板", "最高连板", C["orange"]),
        (str(SUMMARY["zb_count"]), "炸板", C["muted"]),
    ]
    for i, (n, lbl, col) in enumerate(nums):
        x = [0.18, 0.50, 0.82][i]
        ax.text(x, 0.32, n, ha="center", fontsize=40, fontweight="bold",
                color=col, transform=ax.transAxes)
        ax.text(x, 0.255, lbl, ha="center", fontsize=11,
                color=C["muted"], transform=ax.transAxes)

    # 底部钩子
    ax.text(0.5, 0.165, "你站哪边? 翻到下一页看现场",
            ha="center", fontsize=14, fontweight="bold", color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.5", fc=C["card2"], ec=C["cyan"], lw=0.8),
            transform=ax.transAxes)
    ax.text(0.5, 0.105, "→ 后面5页全是干货 别划走", ha="center",
            fontsize=10, color=C["muted"], style="italic", transform=ax.transAxes)

    add_footer(ax, 1)
    save(fig, 1)


# ═══════════════════════════════════════════
# Page 2 — 行业冠亚军 — v3 修分组间距
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

    for yt, t in zip([0.745, 0.69, 0.635, 0.58, 0.525], top5):
        ax.text(0.05, yt, t["name"][:8], ha="left", fontsize=11.5,
                color=C["text"], transform=ax.transAxes, va="center")
        hbar(ax, 0.33, 0.78, yt, t["pct_chg"], max_pct, C["green"])
        ax.text(0.95, yt, f"+{t['pct_chg']:.2f}%", ha="right", fontsize=12.5,
                fontweight="bold", color=C["green"], transform=ax.transAxes, va="center")

    # 跌幅榜 TOP5 — 修: 标题与上方涨幅榜末尾的间距拉到 0.07 (之前 0.045)
    ax.text(0.5, 0.45, "跌幅榜 TOP5", ha="center", fontsize=13, fontweight="bold",
            color=C["red"], transform=ax.transAxes,
            bbox=dict(boxstyle="round,pad=0.3", fc=C["card"], ec="none"))

    for yt, b in zip([0.385, 0.33, 0.275, 0.22, 0.165], bot5):
        ax.text(0.05, yt, b["name"][:8], ha="left", fontsize=11.5,
                color=C["text"], transform=ax.transAxes, va="center")
        hbar(ax, 0.33, 0.78, yt, b["pct_chg"], max_pct, C["red"])
        ax.text(0.95, yt, f"{b['pct_chg']:.2f}%", ha="right", fontsize=12.5,
                fontweight="bold", color=C["red"], transform=ax.transAxes, va="center")

    # 底部金句 — 修: 上方留白拉大 (0.10 → 0.085, 上方多 24px 呼吸)
    ax.text(0.5, 0.085, "钱从大金融跑到小盘题材",
            ha="center", fontsize=13, fontweight="bold", color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.5", fc=C["card2"], ec=C["cyan"], lw=0.8),
            transform=ax.transAxes)

    add_footer(ax, 2)
    save(fig, 2)


# ═══════════════════════════════════════════
# Page 3 — 涨停天梯 — v3 修阶梯叠卡片
# ═══════════════════════════════════════════
def page3():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  涨停天梯  ", C["red"], fs=11)
    ax.text(0.5, 0.895, f"今日 {SUMMARY['zt_count']} 只涨停 · 最高 {SUMMARY['zt_max_board']} 连板",
            ha="center", fontsize=15, fontweight="bold", color=C["text"], transform=ax.transAxes)

    # 6 行涨停股 — v3.1 修: 行距从 0.075 拉到 0.092, 大数字字号 32→28
    # "连板"小字往下挪到大数字下方-0.038 (之前 -0.052 不够)
    rows_y = [0.81, 0.718, 0.626, 0.534, 0.442, 0.35]
    for y, x in zip(rows_y, SUMMARY["zt_top10"][:6]):
        # 左侧大数字 — 字号小一档
        lb = x['连板数']
        if lb >= 4:
            col = C["red"]
        elif lb >= 3:
            col = C["orange"]
        else:
            col = C["gold"]
        ax.text(0.07, y + 0.008, f"{lb}", ha="center", fontsize=28,
                fontweight="bold", color=col, transform=ax.transAxes, va="center")
        ax.text(0.07, y - 0.038, "连板", ha="center", fontsize=8,
                color=C["dim"], transform=ax.transAxes, va="center")

        # 中部信息卡 — 修: x 从 0.21 → 0.18, 宽 0.55 → 0.60 (左右各调)
        ax.add_patch(Rectangle((0.18, y-0.030), 0.62, 0.060,
                               facecolor=C["card"], edgecolor=C["border"], lw=0.5,
                               transform=ax.transAxes))
        ax.text(0.205, y + 0.012, x["名称"], ha="left", fontsize=14,
                fontweight="bold", color=C["text"], transform=ax.transAxes, va="center")
        ax.text(0.205, y - 0.015, f"{x['代码']}  ·  {x['所属行业']}", ha="left",
                fontsize=9.5, color=C["muted"], transform=ax.transAxes, va="center")

        # 右侧涨幅
        try:
            pct = float(x["涨跌幅"])
        except (TypeError, ValueError):
            pct = 0
        ax.text(0.93, y, f"+{pct:.1f}%", ha="right", fontsize=14,
                fontweight="bold", color=C["green"], transform=ax.transAxes, va="center")

    # 涨停最密集行业 — 柱图 (v3.1 下移避让加大行距后的列表)
    ax.text(0.5, 0.295, "涨停最密集的 5 个行业", ha="center", fontsize=12,
            fontweight="bold", color=C["text"], transform=ax.transAxes)
    industries = SUMMARY["zt_top_industries"][:5]
    max_cnt = industries[0]["涨停数"] if industries else 1
    for i, ind in enumerate(industries):
        x = 0.10 + i * 0.20
        bar_h = 0.075 * (ind["涨停数"] / max_cnt)
        ax.add_patch(Rectangle((x-0.045, 0.155), 0.09, bar_h,
                               facecolor=C["orange"], edgecolor="none",
                               transform=ax.transAxes, alpha=0.7))
        ax.text(x, 0.155 + bar_h + 0.015, f"{ind['涨停数']}", ha="center", fontsize=13,
                fontweight="bold", color=C["orange"], transform=ax.transAxes)
        ax.text(x, 0.135, ind["行业"][:5], ha="center", fontsize=9,
                color=C["text"], transform=ax.transAxes)

    # 金句 — v3.2 改更狠的人话点评 (vision 反馈: 这页情绪浓度偏低)
    ax.text(0.5, 0.085, "通用设备+汽车零部 = 老散户的最后阵地",
            ha="center", fontsize=12, fontweight="bold", color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.45", fc=C["card2"], ec=C["cyan"], lw=0.8),
            transform=ax.transAxes)

    add_footer(ax, 3)
    save(fig, 3)


# ═══════════════════════════════════════════
# Page 4 — 雪球新热点 — v3 修主副标题间距
# ═══════════════════════════════════════════
def page4():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  散户雷达  ", C["purple"], fs=11)
    # 修: 主副标题间距从 0.035 拉到 0.05
    ax.text(0.5, 0.895, "雪球今天突然热起来的 5 只", ha="center",
            fontsize=17, fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.845, "讨论榜入TOP10  但平时不在长期关注榜", ha="center",
            fontsize=9.5, color=C["dim"], style="italic", transform=ax.transAxes)

    follow_codes = {x['股票代码'] for x in SUMMARY['xueqiu_follow_top10']}
    new_buzz = [x for x in SUMMARY['xueqiu_tweet_top10']
                if x['股票代码'] not in follow_codes][:5]

    rows_y = [0.755, 0.645, 0.535, 0.425, 0.315]
    for y, x in zip(rows_y, new_buzz):
        ax.add_patch(Rectangle((0.05, y-0.045), 0.90, 0.085,
                               facecolor=C["card"], edgecolor=C["border"], lw=0.5,
                               transform=ax.transAxes))
        ax.text(0.115, y, "HOT", ha="center", fontsize=11, fontweight="bold",
                color=C["bg"],
                bbox=dict(boxstyle="round,pad=0.35", fc=C["red"], ec="none"),
                transform=ax.transAxes, va="center")
        # v3.2: HOT 与名字间距 0.20 → 0.215
        ax.text(0.215, y + 0.018, x["股票简称"], ha="left", fontsize=16.5,
                fontweight="bold", color=C["text"], transform=ax.transAxes, va="center")
        ax.text(0.215, y - 0.022, x["股票代码"], ha="left", fontsize=10,
                color=C["muted"], transform=ax.transAxes, va="center")

        followers = float(x['关注'])
        if followers >= 10000:
            disp = f"{followers/10000:.1f}w"
        else:
            disp = f"{int(followers):,}"
        ax.text(0.92, y + 0.018, disp, ha="right", fontsize=18,
                fontweight="bold", color=C["purple"], transform=ax.transAxes, va="center")
        # v3.2: 8.5pt → 9pt, 颜色用 dim (更暗) 拉层级而非字号
        ax.text(0.92, y - 0.022, f"讨论 · 价 {x['最新价']}", ha="right", fontsize=9,
                color=C["dim"], transform=ax.transAxes, va="center")

    # 金句 — 修: 上移聚拢底部 (0.21 → 0.215, 不要飘)
    ax.text(0.5, 0.21, "AI算力 + 智驾 = 散户今天两大共识",
            ha="center", fontsize=13, fontweight="bold", color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.5", fc=C["card2"], ec=C["cyan"], lw=0.8),
            transform=ax.transAxes)
    ax.text(0.5, 0.135, "讨论量 ≠ 涨幅\n是\"嘴上炒\" 还是真买入 看明天就知道", ha="center",
            fontsize=10, color=C["muted"], transform=ax.transAxes)

    add_footer(ax, 4)
    save(fig, 4)


# ═══════════════════════════════════════════
# Page 5 — 龙头快报 — v3 修上下两排分隔
# ═══════════════════════════════════════════
def page5():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  4 只散户最关注  ", C["orange"], fs=11)
    ax.text(0.5, 0.895, "实涨 vs 嘴上炒", ha="center",
            fontsize=18, fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.86, "上排 = 真涨幅 / 下排 = 雪球讨论热度", ha="center",
            fontsize=9.5, color=C["dim"], style="italic", transform=ax.transAxes)

    # 4 卡片 — 修: 上排 y=0.69, 下排 y=0.385, 间距 0.305 (之前 0.25)
    cards_data = [
        ("兆易创新", "SH603986", "+8.11%", "633.58", C["green"], "存储芯片龙头", "REAL"),
        ("国瓷材料", "SZ300285", "+13.90%", "89.41",  C["red"],   "蓝宝石+材料", "REAL"),
        ("寒武纪",   "SH688256", "讨论 3.6w",  "1495.7", C["purple"], "AI算力一哥", "BUZZ"),
        ("赛力斯",   "SH601127", "讨论 7.7w",  "64.55",  C["purple"], "今日突然爆热", "BUZZ"),
    ]
    positions = [(0.27, 0.69), (0.73, 0.69), (0.27, 0.385), (0.73, 0.385)]
    cw, ch = 0.38, 0.20
    for (cx, cy), (name, code, pct, price, col, tag, kind) in zip(positions, cards_data):
        rect = FancyBboxPatch(
            (cx - cw/2, cy - ch/2), cw, ch,
            boxstyle="round,pad=0.005,rounding_size=0.012",
            fc=C["card"], ec=C["border"], lw=1.2,
            transform=ax.transAxes,
        )
        ax.add_patch(rect)
        kind_col = C["green"] if kind == "REAL" else C["purple"]
        ax.text(cx - cw/2 + 0.045, cy + ch/2 - 0.025, kind, ha="center", fontsize=8,
                fontweight="bold", color=C["bg"],
                bbox=dict(boxstyle="round,pad=0.25", fc=kind_col, ec="none"),
                transform=ax.transAxes)
        ax.text(cx, cy + 0.055, name, ha="center", fontsize=15.5, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        ax.text(cx, cy + 0.022, code, ha="center", fontsize=9.5,
                color=C["dim"], transform=ax.transAxes)
        ax.text(cx, cy - 0.020, pct, ha="center", fontsize=18, fontweight="bold",
                color=col, transform=ax.transAxes)
        ax.text(cx, cy - 0.055, f"价 {price}", ha="center", fontsize=10,
                color=C["muted"], transform=ax.transAxes)
        ax.text(cx, cy - 0.080, tag, ha="center", fontsize=10, fontweight="bold",
                color=C["cyan"], transform=ax.transAxes)

    # 中间分隔标识 — 修: 替换 "─ ─ ─" 为强语义"↑真涨 ｜ ↓嘴炒↓"
    # 加贯穿细线 + 中央带文字胶囊
    ax.plot([0.10, 0.42], [0.5375, 0.5375], color=C["border"], lw=0.6,
            transform=ax.transAxes)
    ax.plot([0.58, 0.90], [0.5375, 0.5375], color=C["border"], lw=0.6,
            transform=ax.transAxes)
    ax.text(0.5, 0.5375, "↑ 真涨 ｜ 嘴炒 ↓",
            ha="center", va="center", fontsize=10, fontweight="bold",
            color=C["text"],
            bbox=dict(boxstyle="round,pad=0.4", fc=C["card2"], ec=C["dim"], lw=0.5),
            transform=ax.transAxes)

    # 底部点评 — 修: 整体下移到底部, 留白拉匀
    ax.text(0.5, 0.215, "一句话点评", ha="center", fontsize=11, fontweight="bold",
            color=C["bg"],
            bbox=dict(boxstyle="round,pad=0.35", fc=C["gold"], ec="none"),
            transform=ax.transAxes)
    ax.text(0.5, 0.155,
            "兆易/国瓷是真金白银涨\n寒武/赛力斯是雪球嘴炮 股价没跟上",
            ha="center", fontsize=11, color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.085, "明天看谁的故事讲得下去",
            ha="center", fontsize=11, fontweight="bold", color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.4", fc=C["card2"], ec=C["cyan"], lw=0.6),
            transform=ax.transAxes)

    add_footer(ax, 5)
    save(fig, 5)


# ═══════════════════════════════════════════
# Page 6 — 总结 + CTA — v3 修 CTA 层级 + 关注钩子
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
    for i, (y, (num, title, col, body)) in enumerate(zip([0.81, 0.71, 0.61], points)):
        ax.text(0.13, y, num, ha="center", fontsize=32, fontweight="bold",
                color=col, transform=ax.transAxes, va="center")
        ax.text(0.25, y + 0.020, title, ha="left", fontsize=17, fontweight="bold",
                color=C["text"], transform=ax.transAxes, va="center")
        ax.text(0.25, y - 0.025, body, ha="left", fontsize=11,
                color=C["muted"], transform=ax.transAxes, va="center")
        if i < 2:
            ax.plot([0.10, 0.90], [y - 0.052, y - 0.052], color=C["border"], lw=0.5,
                    transform=ax.transAxes)

    # 风险提示
    ax.add_patch(FancyBboxPatch((0.08, 0.39), 0.84, 0.13,
                                boxstyle="round,pad=0.01,rounding_size=0.012",
                                facecolor=C["card"], edgecolor=C["orange"], lw=1,
                                transform=ax.transAxes))
    ax.text(0.5, 0.49, "散户友情提醒", ha="center", fontsize=11, fontweight="bold",
            color=C["bg"],
            bbox=dict(boxstyle="round,pad=0.3", fc=C["orange"], ec="none"),
            transform=ax.transAxes)
    ax.text(0.5, 0.44, "今天炸板 30 只 = 30 个被埋的散户群",
            ha="center", fontsize=11.5, color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.408, "切换日抢热点 = 容易接最后一棒",
            ha="center", fontsize=10.5, color=C["muted"], transform=ax.transAxes)

    # CTA 提问
    ax.text(0.5, 0.32, "你今天怎么操作的?", ha="center", fontsize=18, fontweight="bold",
            color=C["text"], transform=ax.transAxes)

    # 三选项 → 改成胶囊小标签 (降低视觉重量)
    options = [
        ("买保险被埋", C["red"]),
        ("抢到蓝宝石", C["green"]),
        ("还在观望",   C["muted"]),
    ]
    for i, (opt, col) in enumerate(options):
        x = 0.20 + i * 0.30
        ax.text(x, 0.275, opt, ha="center", va="center", fontsize=10.5,
                color=col, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.4", fc=C["card"], ec=col, lw=0.8),
                transform=ax.transAxes)

    # 主 CTA — 放大 + 加粗 + 唯一焦点
    ax.add_patch(FancyBboxPatch((0.10, 0.175), 0.80, 0.065,
                                boxstyle="round,pad=0.01,rounding_size=0.012",
                                facecolor=C["card2"], edgecolor=C["cyan"], lw=1.5,
                                transform=ax.transAxes))
    ax.text(0.5, 0.207, "评论区报上你的战绩 ↓", ha="center", va="center",
            fontsize=17, fontweight="bold", color=C["cyan"], transform=ax.transAxes)

    # 情绪尾注
    ax.text(0.5, 0.135, "(说被埋的我陪你)", ha="center",
            fontsize=10, color=C["muted"], style="italic", transform=ax.transAxes)

    # 关注钩子 — v3 新增 (vision 建议)
    ax.text(0.5, 0.085, "明天继续盘 → 关注我, 每晚 8 点更新", ha="center",
            fontsize=11, fontweight="bold", color=C["gold"],
            bbox=dict(boxstyle="round,pad=0.35", fc=C["card"], ec=C["gold"], lw=0.8),
            transform=ax.transAxes)

    add_footer(ax, 6)
    save(fig, 6)


if __name__ == "__main__":
    print(f"开始生成 v3 排版精修版 6 页卡片到 {OUT}")
    page1(); page2(); page3(); page4(); page5(); page6()
    print(f"\n全部完成. 6 张 PNG 在 {OUT}")
