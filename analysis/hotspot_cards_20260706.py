"""20260706 热点卡片 — 高股息防御 vs 成长分化.

数据源: output/hotspot/20260706/summary.json (手动拉取核心数据)
产物: output/2026-07-06/today-hotspot/xhs_cards_v1/
"""

from __future__ import annotations
import json
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
DATE = "20260706"
DAY_HUM = "2026-07-06"
VERSION = 1

RAW = json.loads((ROOT / f"output/hotspot/{DATE}/summary.json").read_text(encoding="utf-8"))

# 加载胜率基准数据（如存在）
WR_PATH = ROOT / "output/hotspot/winrate_benchmark.json"
WINRATE_RAW = json.loads(WR_PATH.read_text(encoding="utf-8")) if WR_PATH.exists() else {}

OUT = ROOT / f"output/{DATE[:4]}-{DATE[4:6]}-{DATE[6:8]}/today-hotspot/xhs_cards_v{VERSION}"
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


# ─── 数据处理 ──────────────────────
# 概念板块排序
concepts = sorted(RAW.get("concept_board", []), key=lambda x: x["pct_chg"], reverse=True)
# 涨停行业分布
zt_pool = RAW.get("zt_pool", [])
zt_industries = {}
for z in zt_pool:
    ind = z.get("所属行业", "其他")
    zt_industries[ind] = zt_industries.get(ind, 0) + 1
zt_ind_sorted = sorted(zt_industries.items(), key=lambda x: -x[1])

# 人气榜
hot_rank = RAW.get("em_hot_rank", [])

# 快讯
news = RAW.get("em_global_news", [])


def new_card():
    fig, ax = plt.subplots(figsize=(CARD_W, CARD_H), facecolor=C["bg"])
    ax.set_facecolor(C["bg"])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)
    return fig, ax


def add_footer(ax, page, total=6):
    ax.text(0.5, 0.025, "* 数据: 东方财富 · 收盘复盘 · 不构成投资建议",
            ha="center", va="center", fontsize=7, color=C["muted"], transform=ax.transAxes)
    ax.text(0.95, 0.025, f"{page}/{total}", ha="right", va="center",
            fontsize=8, color=C["muted"], transform=ax.transAxes)
    ax.text(0.05, 0.025, "复旦杰伦", ha="left", va="center",
            fontsize=8, color=C["dim"], transform=ax.transAxes)


def pill(ax, x, y, txt, fc, fs=10):
    ax.text(x, y, txt, ha="center", va="center", fontsize=fs, fontweight="bold",
            color=C["bg"], bbox=dict(boxstyle="round,pad=0.4", fc=fc, ec="none"),
            transform=ax.transAxes)


def card_bg(ax, x, y, w, h, fc=None, ec=None):
    fc = fc or C["card"]; ec = ec or C["border"]
    ax.add_patch(FancyBboxPatch((x - w/2, y - h/2), w, h,
                                boxstyle="round,pad=0.005,rounding_size=0.02",
                                fc=fc, ec=ec, lw=0.8, transform=ax.transAxes))


def save(fig, page):
    p = OUT / f"page_{page:02d}.png"
    fig.savefig(p, dpi=DPI, bbox_inches="tight",
                facecolor=C["bg"], edgecolor="none", pad_inches=0.15)
    plt.close(fig)
    print(f"  ✓ saved {p}")


def pct_str(v):
    return f"{float(v):+.2f}%"


# ═══════════════════════════════════════════
# Page 1 — 封面
# ═══════════════════════════════════════════
def page1():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, f"  {DAY_HUM} · 收盘复盘  ", C["gold"], fs=10)

    ax.text(0.5, 0.88, "避险升温", ha="center", fontsize=34, fontweight="bold",
            color=C["orange"], transform=ax.transAxes)
    ax.text(0.5, 0.81, "煤炭银行大涨 · 创业板跌 1.77%", ha="center", fontsize=20,
            fontweight="bold", color=C["text"], transform=ax.transAxes)

    # 核心数字
    nums = [
        ("64", "涨停", C["red"]),
        ("5 板", "最高连板", C["gold"]),
        ("150亿", "南向净买", C["cyan"]),
    ]
    for i, (n, lbl, col) in enumerate(nums):
        x = 0.185 + i * 0.315
        card_bg(ax, x, 0.62, 0.27, 0.16)
        ax.text(x, 0.648, n, ha="center", fontsize=28, fontweight="bold",
                color=col, transform=ax.transAxes)
        ax.text(x, 0.572, lbl, ha="center", fontsize=11, color=C["muted"],
                transform=ax.transAxes)

    # 主线标签
    pill(ax, 0.25, 0.45, "  煤炭 +7% 银行齐涨  ", C["red"], fs=11)
    pill(ax, 0.55, 0.45, "  通用设备 7 只涨停  ", C["orange"], fs=11)
    pill(ax, 0.82, 0.45, "  恒尚节能 5 连板  ", C["gold"], fs=11)

    # 一句话总结
    ax.text(0.5, 0.32, "市场在避险：高股息吸金，科技成长承压", ha="center", fontsize=15,
            fontweight="bold", color=C["cyan"], transform=ax.transAxes)
    ax.text(0.5, 0.25, "资金南下 150 亿，存量博弈格局", ha="center", fontsize=13,
            color=C["muted"], transform=ax.transAxes)

    ax.text(0.5, 0.12, "→ 翻页看涨停天梯 & 行业拆解", ha="center", fontsize=11,
            color=C["cyan"], fontstyle="italic", transform=ax.transAxes)

    add_footer(ax, 1)
    save(fig, 1)


# ═══════════════════════════════════════════
# Page 2 — 涨停天梯 TOP10
# ═══════════════════════════════════════════
def page2():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  P2 · 涨停天梯  ", C["cyan"], fs=10)

    ax.text(0.5, 0.885, "今日涨停天梯 TOP10", ha="center", fontsize=22,
            fontweight="bold", color=C["text"], transform=ax.transAxes)

    # 表头
    headers = ["代码", "名称", "连板", "行业", "涨幅"]
    col_x = [0.08, 0.28, 0.52, 0.66, 0.88]
    for j, (hdr, cx) in enumerate(zip(headers, col_x)):
        ax.text(cx, 0.81, hdr, ha="left" if j < 2 else "center", fontsize=9,
                color=C["muted"], fontweight="bold", transform=ax.transAxes)

    ax.axhline(y=0.795, xmin=0.04, xmax=0.96, color=C["border"], lw=0.5)

    # 按连板数排序
    zt_sorted = sorted(zt_pool, key=lambda x: -x.get("连板数", 0))
    for i, item in enumerate(zt_sorted[:10]):
        y = 0.76 - i * 0.065
        boards = item.get("连板数", 0)
        bcolor = C["gold"] if boards >= 4 else (C["red"] if boards >= 3 else C["text"])
        row = [
            item.get("代码", ""),
            item.get("名称", ""),
            str(boards),
            item.get("所属行业", ""),
            pct_str(item.get("涨跌幅", 0)),
        ]
        aligns = ["left", "left", "center", "center", "center"]
        for j, (val, cx) in enumerate(zip(row, col_x)):
            c = bcolor if j == 2 else (C["text"] if j == 1 else C["muted"])
            fs = 11 if j == 1 else 10
            ax.text(cx, y, val, ha=aligns[j], fontsize=fs, color=c,
                    fontweight="bold" if j in (1, 2) else "normal",
                    transform=ax.transAxes)

    # 底部信息
    card_bg(ax, 0.5, 0.09, 0.88, 0.1, fc=C["card2"])
    ax.text(0.5, 0.11, "恒尚节能 5 连板领跑 · 贤丰控股 3 连板 · 多家 2 连板",
            ha="center", fontsize=10, color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.07, "涨停宽度 64 只尚可，高度仅 5 板，投机情绪未过热",
            ha="center", fontsize=9, color=C["dim"], transform=ax.transAxes)

    add_footer(ax, 2)
    save(fig, 2)


# ═══════════════════════════════════════════
# Page 3 — 行业 & 概念拆解
# ═══════════════════════════════════════════
def page3():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  P3 · 行业 & 概念拆解  ", C["cyan"], fs=10)

    # 概念涨幅 TOP8
    ax.text(0.5, 0.89, "概念板块涨幅 TOP8", ha="center", fontsize=15,
            fontweight="bold", color=C["purple"], transform=ax.transAxes)
    for i, item in enumerate(concepts[:8]):
        y = 0.84 - i * 0.065
        name = item.get("name", "")
        pct = item.get("pct_chg", 0)
        up = item.get("up_count", 0)
        down = item.get("down_count", 0)
        leader = item.get("leader_name", "")
        # 涨幅条
        bar_w = 0.45 * (pct / max(c["pct_chg"] for c in concepts[:8])) if concepts[:8] else 0
        ax.add_patch(FancyBboxPatch((0.06, y - 0.012), bar_w, 0.025,
                                    boxstyle="round,pad=0.002,rounding_size=0.01",
                                    fc=C["red"], ec="none", alpha=0.6, transform=ax.transAxes))
        ax.text(0.06, y + 0.003, f"{name}", ha="left", fontsize=10,
                fontweight="bold", color=C["text"], transform=ax.transAxes)
        ax.text(0.06 + max(bar_w, 0.25) + 0.03, y + 0.003,
                f"{pct:+.2f}%  ({up}涨/{down}跌)", ha="left", fontsize=8.5,
                color=C["muted"], transform=ax.transAxes)
        ax.text(0.93, y + 0.003, f"领涨:{leader}", ha="right", fontsize=7.5,
                color=C["dim"], transform=ax.transAxes)

    # 下半：涨停行业分布
    ax.text(0.5, 0.34, "涨停行业分布 TOP8", ha="center", fontsize=14,
            fontweight="bold", color=C["text"], transform=ax.transAxes)
    max_zt = max(c for _, c in zt_ind_sorted[:8]) if zt_ind_sorted[:8] else 1
    for i, (ind, cnt) in enumerate(zt_ind_sorted[:8]):
        y = 0.29 - i * 0.038
        bar_w = 0.6 * (cnt / max_zt)
        ax.add_patch(FancyBboxPatch((0.13, y - 0.007), bar_w, 0.025,
                                    boxstyle="round,pad=0.002,rounding_size=0.01",
                                    fc=C["orange"] if cnt >= 5 else C["blue"],
                                    ec="none", alpha=0.7, transform=ax.transAxes))
        ax.text(0.1, y + 0.003, f"{ind}", ha="right", fontsize=9,
                color=C["text"], fontweight="bold", transform=ax.transAxes)
        ax.text(0.15 + bar_w + 0.015, y + 0.003, f"{cnt} 只", ha="left",
                fontsize=9, color=C["muted"], transform=ax.transAxes)

    add_footer(ax, 3)
    save(fig, 3)


# ═══════════════════════════════════════════
# Page 4 — 人气榜 TOP 15
# ═══════════════════════════════════════════
def page4():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  P4 · 人气榜 TOP20  ", C["cyan"], fs=10)

    ax.text(0.5, 0.89, "东方财富人气 TOP 15", ha="center", fontsize=18,
            fontweight="bold", color=C["text"], transform=ax.transAxes)

    headers = ["#", "名称", "最新价", "涨跌幅"]
    col_x = [0.04, 0.12, 0.70, 0.86]
    for j, (hdr, cx) in enumerate(zip(headers, col_x)):
        ax.text(cx, 0.84, hdr, ha="left" if j < 2 else "right", fontsize=8.5,
                color=C["muted"], fontweight="bold", transform=ax.transAxes)

    ax.axhline(y=0.828, xmin=0.03, xmax=0.97, color=C["border"], lw=0.5)

    for i, item in enumerate(hot_rank[:15]):
        y = 0.80 - i * 0.048
        name = item.get("股票名称", "")
        code = item.get("代码", "")
        price = item.get("最新价", 0)
        chg = item.get("涨跌幅", 0)
        chg_col = C["red"] if chg >= 0 else C["green"]
        arrow = "▲" if chg >= 0 else "▼"
        ax.text(0.04, y, f"{i+1}", ha="left", fontsize=10, color=C["dim"],
                transform=ax.transAxes)
        ax.text(0.12, y, f"{name}", ha="left", fontsize=10.5,
                fontweight="bold", color=C["text"], transform=ax.transAxes)
        ax.text(0.70, y, f"{price:.2f}", ha="right", fontsize=10,
                color=C["muted"], transform=ax.transAxes)
        ax.text(0.86, y, f"{arrow} {chg:+.2f}%", ha="right", fontsize=10,
                fontweight="bold", color=chg_col, transform=ax.transAxes)

    # 底部提示
    card_bg(ax, 0.5, 0.06, 0.88, 0.06, fc=C["card2"])
    ax.text(0.5, 0.065, "江波龙 +10.32% 人气第一 · 存储涨价逻辑驱动 · 华大九天 +14% 紧随",
            ha="center", fontsize=9, color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.04, "新股 C华润 -16.58% · 中国巨石 -10% 跌停上榜 · 分化剧烈",
            ha="center", fontsize=8.5, color=C["dim"], transform=ax.transAxes)

    add_footer(ax, 4)
    save(fig, 4)


# ═══════════════════════════════════════════
# Page 5 — 明日跟踪框架
# ═══════════════════════════════════════════
def page5():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  P5 · 明日跟踪  ", C["cyan"], fs=10)

    ax.text(0.5, 0.90, "明天看什么？", ha="center", fontsize=20,
            fontweight="bold", color=C["text"], transform=ax.transAxes)

    checks = [
        ("[主线]", "煤炭 / 银行 / 高股息", "继续强=避险延续", "回落=成长回摆"),
        ("[高度]", "恒尚节能能否 6 板", "打开空间", "断板=高低切"),
        ("[回流]", "半导体 / 存储 / AI", "风格回摆买点", "主线吸金继续"),
        ("[资金]", "南向是否持续百亿+", "港股联动行情", "一日游"),
        ("[防御]", "独家药品 / 生态农业", "防御延续信号", "资金回成长"),
    ]

    for i, (icon, target, cont, weak) in enumerate(checks):
        y = 0.79 - i * 0.105
        card_bg(ax, 0.5, y, 0.88, 0.08, fc=C["card"])
        ax.text(0.08, y + 0.01, icon, ha="left", fontsize=12, fontweight="bold",
                color=C["gold"], transform=ax.transAxes)
        ax.text(0.22, y + 0.01, target, ha="left", fontsize=10.5, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        ax.text(0.22, y - 0.018, f"[+] {cont}", ha="left", fontsize=8.5,
                color=C["red"], transform=ax.transAxes)
        ax.text(0.62, y - 0.018, f"[-] {weak}", ha="left", fontsize=8.5,
                color=C["green"], transform=ax.transAxes)

    # 金句
    card_bg(ax, 0.5, 0.18, 0.88, 0.08, fc=C["card2"])
    ax.text(0.5, 0.195, "存量博弈格局下，追高煤炭不如等成长回调",
            ha="center", fontsize=11, fontweight="bold", color=C["gold"],
            transform=ax.transAxes)
    ax.text(0.5, 0.165, "高股息持续强 = 避险情绪没释放完",
            ha="center", fontsize=9, color=C["muted"], transform=ax.transAxes)

    ax.text(0.5, 0.08, "[!] 本报告仅供个人复盘，不构成投资建议",
            ha="center", fontsize=7.5, color=C["dim"], transform=ax.transAxes)

    add_footer(ax, 5)
    save(fig, 5)


# ═══════════════════════════════════════════
# Page 6 — 快讯 & 收尾
# ═══════════════════════════════════════════
def page6():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  P6 · 盘中快讯  ", C["cyan"], fs=10)

    ax.text(0.5, 0.90, "今日重要快讯", ha="center", fontsize=18,
            fontweight="bold", color=C["orange"], transform=ax.transAxes)

    key_news = [
        "南向资金净买入 150 亿港元",
        "煤炭板块集体爆发，陕西煤业飙涨 7%",
        "DRAM / NAND 价格全面上修（集邦咨询）",
        "瑞银上调迈威尔科技目标价至 340 美元",
        "创业板指跌 1.77%，沪指微跌 0.06%",
        "沙利文报告：阿里云 AI 占比 40.1% 居首",
        "红利 ETF 涨 2.11%，高股息全面走强",
        "联电 6 月销售额 231 亿台币，同比 +23%",
    ]

    for i, n in enumerate(key_news):
        y = 0.82 - i * 0.075
        ax.text(0.08, y, "●", ha="center", fontsize=8, color=C["blue"],
                transform=ax.transAxes)
        ax.text(0.14, y, n, ha="left", fontsize=10, color=C["text"],
                transform=ax.transAxes)

    # 总结卡
    card_bg(ax, 0.5, 0.18, 0.88, 0.12, fc=C["card2"])
    ax.text(0.5, 0.21, "今日小结", ha="center", fontsize=13,
            fontweight="bold", color=C["gold"], transform=ax.transAxes)
    ax.text(0.5, 0.175, "64 只涨停 + 5 连板 + 150 亿南下 → 宽度可高度一般",
            ha="center", fontsize=9.5, color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.145, "煤炭银行涨 = 避险；通用设备 7 只涨停 = 制造业暗线",
            ha="center", fontsize=9.5, color=C["text"], transform=ax.transAxes)

    ax.text(0.5, 0.07, "[!] 本报告仅供个人复盘，不构成投资建议",
            ha="center", fontsize=7.5, color=C["dim"], transform=ax.transAxes)

    add_footer(ax, 6)
    save(fig, 6)


# ═══════════════════════════════════════════
# Page 7 — 胜率量化
# ═══════════════════════════════════════════
WINRATE = {
    "创业板大跌后20d": {"win": 52.3, "mean": 1.37, "n": 619},
    "煤炭大涨后20d": {"win": 57.1, "mean": 6.00, "n": 140},
    "煤炭大涨→创业板20d": {"win": 54.3, "mean": 2.81, "n": 140},
    "银行大涨→创业板20d": {"win": 58.0, "mean": 2.64, "n": 162},
    "红利大涨→创业板20d": {"win": 59.2, "mean": 2.05, "n": 147},
    "红利大涨后20d": {"win": 59.8, "mean": 1.85, "n": 346},
    "极端分化后创业板20d": {"win": 55.6, "mean": 2.22, "n": 18},
}

def page7():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  P7 · 胜率量化  ", C["purple"], fs=10)

    ax.text(0.5, 0.90, "历史回测：今日行情怎么走？", ha="center", fontsize=17,
            fontweight="bold", color=C["text"], transform=ax.transAxes)

    ax.text(0.5, 0.855, "基于申万煤炭(801950)/创业板指/银行/中证红利的实战回测",
            ha="center", fontsize=8.5, color=C["dim"], transform=ax.transAxes)

    headers = ["条件", "持有", "胜率", "均值", "样本"]
    col_x = [0.06, 0.43, 0.62, 0.77, 0.90]
    for j, (hdr, cx) in enumerate(zip(headers, col_x)):
        ax.text(cx, 0.81, hdr, ha="left" if j < 1 else "center", fontsize=8.5,
                color=C["muted"], fontweight="bold", transform=ax.transAxes)
    ax.axhline(y=0.795, xmin=0.03, xmax=0.97, color=C["border"], lw=0.5)

    rows = [
        ("创业板大跌 >1.5%", "20日", 52.3, 1.37, 619),
        ("→ 创业板自身", "", "", "", ""),
        ("煤炭大涨 >3%", "20日", 57.1, 6.00, 140),
        ("→ 煤炭自身", "", "", "", ""),
        ("煤炭大涨 >3%", "20日", 54.3, 2.81, 140),
        ("→ 创业板后续", "", "", "", ""),
        ("银行大涨 >2%", "20日", 58.0, 2.64, 162),
        ("→ 创业板后续", "", "", "", ""),
        ("红利大涨 >2%", "20日", 59.2, 2.05, 147),
        ("→ 创业板后续", "", "", "", ""),
        ("红利大涨 >2%", "20日", 59.8, 1.85, 346),
        ("→ 红利自身", "", "", "", ""),
        ("极端分化※", "20日", 55.6, 2.22, 18),
        ("→ 创业板后续", "", "", "", ""),
    ]

    for i, (cond, hold, win, mean, n) in enumerate(rows):
        y = 0.77 - i * 0.048
        if i % 2 == 0:
            # 条件行
            ax.text(col_x[0], y, cond, ha="left", fontsize=9,
                    fontweight="bold", color=C["cyan"], transform=ax.transAxes)
            if isinstance(win, (int, float)) and win > 0:
                win_col = C["red"] if win >= 55 else C["text"]
                mean_col = C["red"] if mean > 0 else C["green"]
                ax.text(col_x[2], y, f"{win:.1f}%", ha="center", fontsize=11,
                        fontweight="bold", color=win_col, transform=ax.transAxes)
                ax.text(col_x[3], y, f"{mean:+.2f}%", ha="center", fontsize=10,
                        fontweight="bold", color=mean_col, transform=ax.transAxes)
                ax.text(col_x[1], y, hold, ha="center", fontsize=9, color=C["muted"], transform=ax.transAxes)
                ax.text(col_x[4], y, f"n={n}", ha="center", fontsize=8.5, color=C["dim"], transform=ax.transAxes)
        else:
            # 说明行（灰色小字）
            ax.text(col_x[0] + 0.02, y, cond, ha="left", fontsize=7.5,
                    color=C["dim"], fontstyle="italic", transform=ax.transAxes)

    # 底部注释
    card_bg(ax, 0.5, 0.055, 0.88, 0.06, fc=C["card2"])
    ax.text(0.5, 0.07, "※ 极端分化 = 创业板跌>1.5% + 煤炭涨>2% 同日发生（历史仅19次）",
            ha="center", fontsize=7.5, color=C["muted"], transform=ax.transAxes)
    ax.text(0.5, 0.045, "数据：2014-2026 申万/中证指数日线回测 · 不构成投资建议",
            ha="center", fontsize=7, color=C["dim"], transform=ax.transAxes)

    add_footer(ax, 7)
    save(fig, 7)


# ═══════════════════════════════════════════
# Page 8 — 量化结论 & 策略
# ═══════════════════════════════════════════
def page8():
    fig, ax = new_card()
    pill(ax, 0.5, 0.955, "  P8 · 量化结论  ", C["purple"], fs=10)

    ax.text(0.5, 0.89, "数据告诉我们的 5 件事", ha="center", fontsize=18,
            fontweight="bold", color=C["text"], transform=ax.transAxes)

    conclusions = [
        ("1", "银行大涨后别慌",
         "银行涨>2%后，创业板20日胜率58%，均值+2.64%",
         "资金最终会从高股息轮动到成长，耐心等待"),
        ("2", "煤炭有动量，追高需谨慎",
         "煤炭涨>3%后，自身20日胜率57%，均值+6%",
         "但煤炭大涨后创业板也有54%胜率，无需恐慌"),
        ("3", "红利大涨是高胜率信号",
         "中证红利涨>2%后，20日胜率59.8%",
         "高股息大涨本身是个看多信号，而非见顶"),
        ("4", "极端分化≠灾难",
         "创业板跌1.5%+煤炭涨2%同日发生仅19次",
         "后续创业板20日胜率55.6%，均值+2.2%"),
        ("5", "创业板大跌是中性信号",
         "单日跌>1.5%后20日胜率仅52.3%",
         "不要因为单日大跌就抄底，等确认更稳妥"),
    ]

    for i, (num, title, stat, takeaway) in enumerate(conclusions):
        y = 0.80 - i * 0.125
        card_bg(ax, 0.5, y, 0.90, 0.10, fc=C["card"])
        # 编号
        ax.add_patch(plt.Circle((0.06, y), 0.025, color=C["purple"], alpha=0.8,
                                 transform=ax.transAxes))
        ax.text(0.06, y, num, ha="center", va="center", fontsize=10,
                fontweight="bold", color=C["bg"], transform=ax.transAxes)
        # 标题
        ax.text(0.14, y + 0.018, title, ha="left", fontsize=11,
                fontweight="bold", color=C["text"], transform=ax.transAxes)
        # 数据
        ax.text(0.14, y - 0.008, stat, ha="left", fontsize=8.5,
                color=C["cyan"], transform=ax.transAxes)
        # 结论
        ax.text(0.60, y - 0.008, takeaway, ha="left", fontsize=8,
                color=C["muted"], transform=ax.transAxes)

    # 总结金句
    card_bg(ax, 0.5, 0.14, 0.88, 0.07, fc=C["card2"])
    ax.text(0.5, 0.158, "数据回测不能预测未来，但能帮我们管理预期",
            ha="center", fontsize=10, fontweight="bold", color=C["gold"],
            transform=ax.transAxes)
    ax.text(0.5, 0.128, "今天的分化其实没那么可怕 — 耐心等待风格轮动",
            ha="center", fontsize=9, color=C["muted"], transform=ax.transAxes)

    ax.text(0.5, 0.06, "[!] 本报告仅供个人复盘，回测基于申万/中证历史指数，不构成投资建议",
            ha="center", fontsize=7, color=C["dim"], transform=ax.transAxes)

    add_footer(ax, 8)
    save(fig, 8)


def main():
    print(f"生成 XHS 卡片到 {OUT}")
    page1()
    page2()
    page3()
    page4()
    page5()
    page6()
    page7()
    page8()
    print(f"完成！共 8 页 → {OUT}")


if __name__ == "__main__":
    main()
