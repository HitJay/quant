"""哈药5连板 + 医药链反击 — 6 页深色卡片.

数据源: output/hotspot/20260716/summary.json
产出:   output/hotspot/20260716/xhs_hayao_v1/
视觉:   matplotlib 深色 GitHub 风, 7.2×9.6 dpi=200, 禁 emoji
"""

from __future__ import annotations
import json
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path("/das/user/QYJI/quant")
DATE = "20260716"
DAY_HUM = "2026-07-16"

SUMMARY = json.loads((ROOT / f"output/hotspot/{DATE}/summary.json").read_text())
OUT = ROOT / f"output/hotspot/{DATE}/xhs_hayao_v1"
OUT.mkdir(parents=True, exist_ok=True)

# ─── 调色板 (沿用 quant 规范) ───────────────
C = {
    "bg": "#0d1117", "card": "#161b22", "border": "#30363d",
    "text": "#c9d1d9", "muted": "#8b949e",
    "blue": "#58a6ff", "green": "#3fb950", "red": "#f85149",
    "orange": "#d2991d", "purple": "#bc8cff", "gold": "#f0c040",
    "cyan": "#56d4dd",
    # A 股语义: 红=涨, 绿=跌
    "up": "#f85149", "down": "#3fb950",
}
CARD_W, CARD_H, DPI = 7.2, 9.6, 200

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "Droid Sans Fallback", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def new_card():
    fig, ax = plt.subplots(figsize=(CARD_W, CARD_H), facecolor=C["bg"])
    ax.set_facecolor(C["bg"])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    return fig, ax


def add_footer(ax, page, total=6):
    ax.text(0.5, 0.025, "* 数据来源: 东方财富/雪球 · 历史不代表未来 · 不构成投资建议",
            ha="center", va="center", fontsize=9, color=C["muted"], transform=ax.transAxes)
    ax.text(0.95, 0.025, f"{page}/{total}", ha="right", va="center",
            fontsize=10, color=C["muted"], transform=ax.transAxes)


def pill(ax, x, y, txt, fc, fs=11):
    ax.text(x, y, txt, ha="center", va="center", fontsize=fs, fontweight="bold",
            color=C["bg"],
            bbox=dict(boxstyle="round,pad=0.4", fc=fc, ec="none"),
            transform=ax.transAxes)


def card_bg(ax, cx, cy, w, h):
    """添加卡片底."""
    p = FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                        boxstyle="round,pad=0.01", fc=C["card"], ec=C["border"], lw=0.8)
    ax.add_patch(p)


def save(fig, page):
    p = OUT / f"page_{page}.png"
    fig.savefig(p, dpi=DPI, bbox_inches=None, pad_inches=0,
                facecolor=C["bg"], edgecolor="none")
    plt.close(fig)
    print(f"  ✓ saved {p}")


# ═══════════════════════════════════════════════
# P1 — 封面: 哈药5连板 + 三大数字
# ═══════════════════════════════════════════════
def page1():
    fig, ax = new_card()
    pill(ax, 0.5, 0.95, f"  {DAY_HUM} · 盘中速报  ", C["gold"])

    # 主标题
    ax.text(0.5, 0.82, "哈药股份", ha="center", fontsize=46, fontweight="bold",
            color=C["up"], transform=ax.transAxes)
    ax.text(0.5, 0.74, "5 连板", ha="center", fontsize=44, fontweight="bold",
            color=C["up"], transform=ax.transAxes)

    # 副标题
    ax.text(0.5, 0.65, "医药链全线反击", ha="center", fontsize=28, fontweight="bold",
            color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.60, "化学制药 / 生物疫苗 / 医疗器械 / 医疗服务 四线齐发",
            ha="center", fontsize=13, color=C["muted"], transform=ax.transAxes)

    # 三大数字 — 紧凑下移
    nums = [
        (SUMMARY["zt_count"], "涨停", C["up"]),
        (SUMMARY["zt_max_board"], "最高连板", C["orange"]),
        (SUMMARY["zb_count"], "炸板", C["muted"]),
    ]
    for i, (n, lbl, col) in enumerate(nums):
        x = [0.18, 0.50, 0.82][i]
        ax.text(x, 0.48, str(n), ha="center", fontsize=54, fontweight="bold",
                color=col, transform=ax.transAxes)
        ax.text(x, 0.395, lbl, ha="center", fontsize=14,
                color=C["muted"], transform=ax.transAxes)

    # 过渡金句 (填补空白)
    ax.text(0.5, 0.33, "↓ 一条主线, 四条子线同步激活 ↓", ha="center",
            fontsize=11, color=C["muted"], transform=ax.transAxes)

    # VS 双栏对比 — 紧凑上移
    ax.plot([0.50, 0.50], [0.29, 0.19], color=C["border"], lw=0.8, transform=ax.transAxes)
    ax.text(0.25, 0.24, "医药涨停9只", ha="center", fontsize=16, fontweight="bold",
            color=C["up"], transform=ax.transAxes)
    ax.text(0.25, 0.20, "化学制药+生物疫苗+医疗器械+医疗服务", ha="center",
            fontsize=10, color=C["muted"], transform=ax.transAxes)
    ax.text(0.75, 0.24, "蓝宝石-2.28%", ha="center", fontsize=16, fontweight="bold",
            color=C["down"], transform=ax.transAxes)
    ax.text(0.75, 0.20, "概念跌幅最大, 寒锐/蓝思领跌", ha="center",
            fontsize=10, color=C["muted"], transform=ax.transAxes)

    # 翻页引导
    ax.text(0.5, 0.11, "翻到下一页 → 看医药链涨停全景",
            ha="center", fontsize=11, color=C["muted"], style="italic",
            transform=ax.transAxes)

    add_footer(ax, 1)
    save(fig, 1)


# ═══════════════════════════════════════════════
# P2 — 涨停天梯 + 行业分布
# ═══════════════════════════════════════════════
def page2():
    fig, ax = new_card()
    pill(ax, 0.5, 0.95, "  涨停天梯  ", C["up"])
    ax.text(0.5, 0.89, f"今日 {SUMMARY['zt_count']} 只涨停 · 最高 {SUMMARY['zt_max_board']} 连板",
            ha="center", fontsize=15, color=C["text"], transform=ax.transAxes)

    # 连板梯队 TOP8
    for i, stk in enumerate(SUMMARY["zt_top10"][:8]):
        y = 0.805 - i * 0.085
        board = stk["连板数"]
        board_color = C["up"] if board >= 4 else (C["orange"] if board >= 3 else C["gold"])

        # 连板数大号
        ax.text(0.08, y, f"{board}", ha="center", fontsize=28, fontweight="bold",
                color=board_color, transform=ax.transAxes)
        ax.text(0.08, y - 0.045, "连板", ha="center", fontsize=8,
                color=C["muted"], transform=ax.transAxes)

        # 股票名 + 代码 + 行业
        ax.text(0.19, y + 0.008, stk["名称"], ha="left", fontsize=15, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        ax.text(0.19, y - 0.032, f"{stk['代码']} · {stk['所属行业']}", ha="left",
                fontsize=9, color=C["muted"], transform=ax.transAxes)

        # 涨幅
        pct = float(stk.get("涨跌幅", 0))
        ax.text(0.93, y, f"+{pct:.2f}%", ha="right", fontsize=13, fontweight="bold",
                color=C["up"], transform=ax.transAxes)

        # 行分隔线
        if i < 7:
            ax.plot([0.08, 0.93], [y - 0.072, y - 0.072],
                    color=C["border"], lw=0.5, transform=ax.transAxes)

    # 底部: 涨停最密集行业
    ax.plot([0.08, 0.93], [0.182, 0.182], color=C["border"], lw=0.8, transform=ax.transAxes)
    ax.text(0.5, 0.22, "涨停最密集的行业", ha="center", fontsize=13,
            fontweight="bold", color=C["text"], transform=ax.transAxes)

    for i, ind in enumerate(SUMMARY["zt_top_industries"]):
        x = 0.10 + i * 0.20
        ax.text(x, 0.18, ind["行业"][:5], ha="center", fontsize=11,
                color=C["muted"], transform=ax.transAxes)
        ax.text(x, 0.145, f"{ind['涨停数']}", ha="center", fontsize=24, fontweight="bold",
                color=C["orange"], transform=ax.transAxes)
        ax.text(x, 0.115, "只", ha="center", fontsize=9,
                color=C["muted"], transform=ax.transAxes)

    # 金句
    ax.text(0.5, 0.07, "消费电子5只最多, 化学制药+医疗服务各3只 → 医药是今日主线之一",
            ha="center", fontsize=11, color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.4", fc=C["card"], ec=C["border"]),
            transform=ax.transAxes)

    add_footer(ax, 2)
    save(fig, 2)


# ═══════════════════════════════════════════════
# P3 — 医药链四线全景
# ═══════════════════════════════════════════════
def page3():
    fig, ax = new_card()
    pill(ax, 0.5, 0.95, "  医药链全景  ", C["up"])
    ax.text(0.5, 0.89, "四条子线同步发力", ha="center",
            fontsize=20, fontweight="bold", color=C["text"], transform=ax.transAxes)

    # 四条子线: 化学制药 / 生物疫苗 / 医疗器械 / 医疗服务
    lines = [
        ("化学制药", "哈药 5连板\n永安药业 2连板", 3, C["up"]),
        ("生物疫苗", "贤丰控股 3连板(兼)\n概念 +1.79%", 3, C["up"]),
        ("医疗器械", "九安医疗 3连板\n美诺华 +6.54%", 3, C["orange"]),
        ("医疗服务", "南华生物 2连板\n昭衍新药 +8.49%", 3, C["orange"]),
    ]

    for i, (name, detail, cnt, col) in enumerate(lines):
        y = 0.76 - i * 0.14
        # 卡片底
        card_bg(ax, 0.50, y, 0.88, 0.12)
        # 子线名 pill
        pill(ax, 0.12, y + 0.035, f"  {name}  ", col, fs=11)
        # 涨停数
        ax.text(0.12, y - 0.035, f"涨停{cnt}只", ha="center", fontsize=14,
                fontweight="bold", color=C["text"], transform=ax.transAxes)
        # 详情
        ax.text(0.30, y + 0.015, detail.split("\n")[0], ha="left", fontsize=13,
                fontweight="bold", color=C["text"], transform=ax.transAxes)
        ax.text(0.30, y - 0.030, detail.split("\n")[1], ha="left", fontsize=11,
                color=C["muted"], transform=ax.transAxes)
        # 箭头指示
        ax.text(0.88, y, "→", ha="center", fontsize=18, fontweight="bold",
                color=col, transform=ax.transAxes)

    # 点评金句
    ax.text(0.5, 0.18, "从原料药(美诺华)到CRO(昭衍)到终端(哈药、南华)",
            ha="center", fontsize=12, color=C["muted"], transform=ax.transAxes)
    ax.text(0.5, 0.14, "医药全产业链今天被资金扫了一遍",
            ha="center", fontsize=14, fontweight="bold", color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.4", fc=C["card"], ec=C["border"]),
            transform=ax.transAxes)
    ax.text(0.5, 0.07, "翻到下一页 → 看散户今天在买哪些医药股",
            ha="center", fontsize=10, color=C["muted"], style="italic",
            transform=ax.transAxes)

    add_footer(ax, 3)
    save(fig, 3)


# ═══════════════════════════════════════════════
# P4 — 散户情绪面 (医药股的东财人气 + 雪球热度)
# ═══════════════════════════════════════════════
def page4():
    fig, ax = new_card()
    pill(ax, 0.5, 0.95, "  散户在盯哪些医药股  ", C["purple"])

    ax.text(0.5, 0.89, "今日散户最关注的医药标的", ha="center",
            fontsize=16, fontweight="bold", color=C["text"], transform=ax.transAxes)

    # 从 em_hot 挑医药股 + 从雪球挑药明康德
    med_stocks = [
        ("SH603127", "昭衍新药", 54.92, 8.49, "CRO龙头, 人气#1", C["up"]),
        ("SH600664", "哈药股份", 4.94, 10.02, "5连板龙头", C["up"]),
        ("SZ000566", "海南海药", 5.67, 10.10, "涨停, 人气#8", C["up"]),
        ("SH603538", "美诺华", 41.55, 6.54, "原料药, 人气#9", C["up"]),
        ("SH603259", "药明康德", 129.08, None, "雪球热议 3.1w", C["purple"]),
    ]

    # 表头
    ax.text(0.08, 0.82, "代码", ha="left", fontsize=10, fontweight="bold",
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.28, 0.82, "名称", ha="left", fontsize=10, fontweight="bold",
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.55, 0.82, "涨跌幅", ha="center", fontsize=10, fontweight="bold",
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.68, 0.82, "现价", ha="center", fontsize=10, fontweight="bold",
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.88, 0.82, "标签", ha="right", fontsize=10, fontweight="bold",
            color=C["muted"], transform=ax.transAxes)

    for i, (code, name, price, chg, tag, col) in enumerate(med_stocks):
        y = 0.74 - i * 0.10
        if i % 2 == 0:
            card_bg(ax, 0.50, y, 0.84, 0.085)

        ax.text(0.08, y, code[2:], ha="left", fontsize=11, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        ax.text(0.28, y, name, ha="left", fontsize=13, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        if chg is not None:
            ax.text(0.55, y, f"+{chg:.2f}%", ha="center", fontsize=13, fontweight="bold",
                    color=C["up"], transform=ax.transAxes)
        else:
            ax.text(0.55, y, "讨论热", ha="center", fontsize=13, fontweight="bold",
                    color=C["purple"], transform=ax.transAxes)
        ax.text(0.68, y, f"{price:.2f}", ha="center", fontsize=12,
                color=C["muted"], transform=ax.transAxes)
        # 标签药丸
        ax.text(0.88, y, tag, ha="right", fontsize=9,
                color=col, transform=ax.transAxes)

    # 对比段: 东财人气榜其余非医药 — 紧凑上移
    ax.text(0.5, 0.175, "非医药人气榜上的意外之客", ha="center",
            fontsize=12, fontweight="bold", color=C["text"], transform=ax.transAxes)

    non_med = [
        ("华天科技", -9.13, "半导体暴跌, 散户抄底?"),
        ("紫光股份", 8.92, "IT服务涨停"),
        ("京东方A", -2.66, "面板龙头走弱"),
        ("长电科技", -5.99, "封测领跌"),
    ]

    for i, (nm, chg, note) in enumerate(non_med):
        x = 0.12 + i * 0.24
        ax.text(x, 0.155, nm, ha="center", fontsize=12, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        chg_col = C["down"] if chg < 0 else C["up"]
        ax.text(x, 0.130, f"{chg:+.2f}%", ha="center", fontsize=16, fontweight="bold",
                color=chg_col, transform=ax.transAxes)
        ax.text(x, 0.080, note, ha="center", fontsize=8,
                color=C["muted"], transform=ax.transAxes)

    add_footer(ax, 4)
    save(fig, 4)


# ═══════════════════════════════════════════════
# P5 — 龙头 4 卡 2x2
# ═══════════════════════════════════════════════
def page5():
    fig, ax = new_card()
    pill(ax, 0.5, 0.95, "  医药龙头快报  ", C["orange"])
    ax.text(0.5, 0.89, "今日医药链四大金刚", ha="center",
            fontsize=18, fontweight="bold", color=C["text"], transform=ax.transAxes)

    cards = [
        ("哈药股份", "600664", "5连板", "收盘 +10.02%", "价 4.94", C["up"],
         "化学制药龙头, 全市场最高连板"),
        ("昭衍新药", "603127", "东财#1", "+8.49%", "价 54.92", C["up"],
         "CRO 龙头, 散户人气第一"),
        ("九安医疗", "002432", "3连板", "收盘 +10.00%", "价 47.25", C["up"],
         "医疗器械代表, 疫情记忆股"),
        ("贤丰控股", "002141", "3连板 + 生物疫苗", "+9.98%", "价 6.05", C["orange"],
         "元件+疫苗双概念"),
    ]

    positions = [(0.27, 0.67), (0.73, 0.67), (0.27, 0.38), (0.73, 0.38)]

    for (cx, cy), (name, code, badge, pct, price, col, tag) in zip(positions, cards):
        # 卡片底
        card_bg(ax, cx, cy, 0.40, 0.25)

        # 角标
        ax.text(cx - 0.16, cy + 0.095, badge, ha="center", fontsize=9,
                fontweight="bold", color=C["bg"],
                bbox=dict(boxstyle="round,pad=0.3", fc=col, ec="none"),
                transform=ax.transAxes)

        # 名称
        ax.text(cx, cy + 0.075, name, ha="center", fontsize=16, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        ax.text(cx, cy + 0.040, code, ha="center", fontsize=9,
                color=C["muted"], transform=ax.transAxes)

        # 涨跌幅
        ax.text(cx, cy - 0.010, pct, ha="center", fontsize=18, fontweight="bold",
                color=col, transform=ax.transAxes)
        ax.text(cx, cy - 0.050, price, ha="center", fontsize=11,
                color=C["muted"], transform=ax.transAxes)

        # 一句话点评
        ax.text(cx, cy - 0.095, tag, ha="center", fontsize=9,
                color=C["cyan"], transform=ax.transAxes)

    # 底部总结
    ax.text(0.5, 0.14, "四个方向覆盖了医药链的\n化学制药 → CRO → 器械 → 跨界概念",
            ha="center", fontsize=12, color=C["muted"], transform=ax.transAxes)
    ax.text(0.5, 0.07, "不是单一只票的行情, 是全产业链的资金共识",
            ha="center", fontsize=13, fontweight="bold", color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.4", fc=C["card"], ec=C["border"]),
            transform=ax.transAxes)

    add_footer(ax, 5)
    save(fig, 5)


# ═══════════════════════════════════════════════
# P6 — 总结 + CTA
# ═══════════════════════════════════════════════
def page6():
    fig, ax = new_card()
    pill(ax, 0.5, 0.95, "  今日总结  ", C["gold"])
    ax.text(0.5, 0.89, "三句话看懂今天的医药链行情", ha="center",
            fontsize=18, fontweight="bold", color=C["text"], transform=ax.transAxes)

    points = [
        ("01", "哈药5连板, 医药链全线激活",
         "化学制药/生物疫苗/医疗器械/医疗服务 四条线同步拉涨停"),
        ("02", "散户情绪集中爆发",
         "昭衍新药人气#1, 药明康德雪球热议3.1万, 海南海药+美诺华齐涨停"),
        ("03", "行情结构: 医药为主, 消费电子为辅",
         "消费电子5只涨停最多, 但医药链整体联动更强, 主力逻辑清晰"),
    ]

    for i, (num, title, body) in enumerate(points):
        y = 0.80 - i * 0.14
        # 分隔线
        if i > 0:
            ax.plot([0.10, 0.90], [y + 0.065, y + 0.065],
                    color=C["border"], lw=0.5, transform=ax.transAxes)

        # 大编号
        ax.text(0.10, y + 0.01, num, ha="center", fontsize=36, fontweight="bold",
                color=C["up"], transform=ax.transAxes)
        # 标题
        ax.text(0.22, y + 0.025, title, ha="left", fontsize=16, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        # 正文
        ax.text(0.22, y - 0.035, body, ha="left", fontsize=11,
                color=C["muted"], transform=ax.transAxes)

    # 风险提示 — 紧凑上移
    ax.text(0.5, 0.37, "散户友情提醒", ha="center", fontsize=13, fontweight="bold",
            color=C["bg"],
            bbox=dict(boxstyle="round,pad=0.4", fc=C["orange"], ec="none"),
            transform=ax.transAxes)
    ax.text(0.5, 0.31,
            "哈药5连板后已到高位, 追高风险极大\n涨停48只, 封板率83%偏高, 明日必有分化",
            ha="center", fontsize=11, color=C["text"], transform=ax.transAxes)

    # CTA
    ax.text(0.5, 0.14, "评论区聊聊 → 你今天上车医药了吗?",
            ha="center", fontsize=13, fontweight="bold", color=C["cyan"],
            bbox=dict(boxstyle="round,pad=0.4", fc=C["card"], ec=C["border"]),
            transform=ax.transAxes)

    add_footer(ax, 6)
    save(fig, 6)


if __name__ == "__main__":
    print(f"开始生成 6 页卡片 → {OUT}")
    page1(); page2(); page3(); page4(); page5(); page6()
    print("\n✅ 全部完成!")
