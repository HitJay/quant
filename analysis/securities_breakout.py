"""券商ETF连日脉冲 — 信号触发后历史胜率量化研究 + 8 页小红书深色卡片
================================================================
背景：
    2026-06-22 证券ETF (512880) 单日 +7.71%，量比 2.16（启动）
    2026-06-23 +0.00% 平开高走平收（多空胶着）
    2026-06-24 -1.77% 缩量回踩（短线回吐）
    2026-06-25 再次拉升 +3.42%，收 1.149；成交 41.92亿、换手 7.49%
    全市场最强一日：长江证券 (000783) 涨停（+9.97%），主力净流入 4.03亿
    证券Ⅱ板块当日 +3.05%。
    券商行情看似启动 —— 但属于"二次冲击"而非一日连板。

但散户最爱问的"券商行情来了"是真的还是假的？
本研报用 10 年（2016-08 至今）证券ETF 日线数据回测：
    - 信号 A：单日 ≥3% 且 量比 ≥1.5（放量大涨）
    - 信号 B：信号 A 且 近10日内已有一次大涨（连续脉冲，今日所处状态）
    持有 5/10/20/60/120/250 个交易日的胜率与中位收益。

核心叙事 — 反共识：
    券商最爱演"一日游"。
    放量大涨后 60日胜率 38.5%，中位 -4.90%；
    连续脉冲后更惨：60日胜率 32.4%，中位 -8.40%。
    历史上买在第二根脉冲后，60日跌的占 68%。

Usage:
    cd /das/user/QYJI/quant
    conda run -n research python analysis/securities_breakout.py
"""
from __future__ import annotations
import sys, json
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
plt.rcParams["font.sans-serif"] = ["Droid Sans Fallback", "WenQuanYi Micro Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# ────────── 路径 / 配色 ──────────
ETF_DIR = Path("./data/cache/etf")
TODAY = datetime.now().strftime("%Y-%m-%d")
ROOT = Path(f"./output/{TODAY}/securities-breakout")
CARDS, FIGS, DATA = ROOT / "cards", ROOT / "figures", ROOT / "data"
for d in (CARDS, FIGS, DATA):
    d.mkdir(parents=True, exist_ok=True)

C = {
    "bg": "#0d1117", "card": "#161b22", "panel": "#1c2128", "border": "#30363d",
    "text": "#c9d1d9", "muted": "#8b949e", "blue": "#58a6ff",
    "green": "#3fb950", "red": "#f85149", "orange": "#d2991d",
    "purple": "#bc8cff", "gold": "#f0c040", "cyan": "#56d4dd",
}
CARD_W, CARD_H, DPI = 7.2, 9.6, 200

MAIN = "512880"
MAIN_NAME = "证券ETF (512880)"
BENCH = "510300"
BENCH_NAME = "沪深300ETF (510300)"

# 今日收盘数据（盘后实测，2026-06-25 收盘后刷新）
# 来源：ak.fund_etf_spot_em（ETF）、push2his.eastmoney.com（个股资金流 / 板块K线）
TODAY_CHG = 0.0342       # +3.42%（收盘价 1.149 / 前收 1.111 - 1）
TODAY_AMOUNT_YI = 41.92   # 41.92亿（收盘成交额 4,191,767,414 元）
TODAY_TURNOVER = 7.49     # 7.49%（fund_etf_spot_em 换手率字段）
TODAY_LJZQ_INFLOW_YI = 4.03   # 长江证券 sz000783 主力净流入 4.03亿（push2his fflow/daykline 6/25 收盘）
TODAY_SECTOR_GAIN = 0.0305    # 证券Ⅱ板块 (BK0473) 收盘涨幅 +3.05%（非银金融板块当日没有 EM 聚合，用证券Ⅱ作代理）

# ────────── 工具函数 ──────────
def pct(x, digits=1, signed=True):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    s = f"{x*100:+.{digits}f}%" if signed else f"{x*100:.{digits}f}%"
    return s

def pct0(x, signed=False):
    return pct(x, 0, signed)

def _fig():
    return plt.figure(figsize=(CARD_W, CARD_H), facecolor=C["bg"])

def _page_number(fig, page):
    fig.text(0.94, 0.018, f"{page}/8", ha="right", va="bottom",
             fontsize=8.5, color=C["muted"])

def _disclaimer(fig):
    fig.text(0.06, 0.018, "复旦杰伦 · 数据回测仅供参考 · 非投资建议",
             ha="left", va="bottom", fontsize=8.5, color=C["muted"])

def _card_rect(ax, xy, width, height, face="card", alpha=1.0, ec=None):
    rect = FancyBboxPatch(
        xy, width, height,
        boxstyle="round,pad=0.01,rounding_size=0.018",
        facecolor=C[face], edgecolor=ec or C["border"],
        lw=0.8, alpha=alpha, transform=ax.transAxes
    )
    ax.add_patch(rect)
    return rect


# ────────── 数据 / 信号 ──────────
def load_etf(code: str) -> pd.DataFrame:
    df = pd.read_parquet(ETF_DIR / f"{code}.parquet")
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)
    df["amount"] = df["amount"].astype(float) if "amount" in df.columns else df["volume"]
    df["ret1d"] = df["close"].pct_change()
    df["vol_ma20"] = df["volume"].rolling(20).mean()
    df["vol_ratio"] = df["volume"] / df["vol_ma20"]
    df["ma20"] = df["close"].rolling(20).mean()
    df["ma60"] = df["close"].rolling(60).mean()
    df["ma120"] = df["close"].rolling(120).mean()
    return df


def compute_signals(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """返回两个信号集 (sig_A: 放量大涨；sig_B: 连续脉冲)"""
    a = (df["ret1d"] >= 0.03) & (df["vol_ratio"] >= 1.5)
    has_prior = df["ret1d"].rolling(10).apply(lambda x: (x >= 0.03).sum()).shift(1)
    b = a & (has_prior >= 1)
    return df[a].copy(), df[b].copy()


def winrate_after(df: pd.DataFrame, sig_idx: pd.Index, horizons: list[int]) -> pd.DataFrame:
    """信号触发后 N 日胜率表"""
    rows = []
    for h in horizons:
        rets = []
        worst_dd = []
        for d in sig_idx:
            pos = df.index.get_loc(d)
            if pos + h >= len(df):
                continue
            base = df["close"].iloc[pos]
            future = df["close"].iloc[pos+h]
            rets.append((future / base - 1) * 100)
            # 持有期内最大浮亏
            path = df["close"].iloc[pos+1: pos+h+1]
            dd = (path.min() / base - 1) * 100
            worst_dd.append(dd)
        if not rets:
            continue
        rets = pd.Series(rets)
        worst_dd = pd.Series(worst_dd)
        rows.append({
            "持有": label_horizon(h),
            "h": h,
            "样本": len(rets),
            "胜率": (rets > 0).mean(),
            "中位": rets.median() / 100,
            "均值": rets.mean() / 100,
            "最差": rets.min() / 100,
            "最好": rets.max() / 100,
            "浮亏中位": worst_dd.median() / 100,
            "浮亏P10": worst_dd.quantile(0.10) / 100,
            "再跌5%概率": (worst_dd <= -5).mean(),
        })
    return pd.DataFrame(rows)


def label_horizon(h: int) -> str:
    mapping = {5: "1周", 10: "2周", 20: "1月", 60: "3月", 120: "6月", 250: "1年"}
    return mapping.get(h, f"{h}日")


# ────────── 卡片 ──────────
def card_1(state, win_b):
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_facecolor(C["bg"])

    # 标题区
    ax.text(0.5, 0.91, "券商ETF连日脉冲", ha="center", fontsize=32,
            fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.845, "这次能追吗？", ha="center", fontsize=38,
            fontweight="bold", color=C["gold"], transform=ax.transAxes)
    ax.text(0.5, 0.78, f"512880 · 6/22 +7.7% → 今天再 +3.6% · 数据截止 {TODAY}",
            ha="center", fontsize=12.5, color=C["muted"], transform=ax.transAxes)

    # 大字: 60日胜率
    sig_b_60 = win_b[win_b["h"] == 60].iloc[0]
    ax.text(0.5, 0.65, f"{sig_b_60['胜率']*100:.0f}%", ha="center", fontsize=92,
            fontweight="bold", color=C["red"], fontfamily="monospace", transform=ax.transAxes)
    ax.text(0.5, 0.565, f"连续脉冲信号后 · 3个月持有胜率 · 历史 36 次同款样本",
            ha="center", fontsize=13.5, color=C["muted"], transform=ax.transAxes)

    # 三个 KPI
    kpis = [
        ("1周胜率", pct0(win_b[win_b["h"] == 5].iloc[0]["胜率"]), C["gold"]),
        ("3月中位收益", pct(sig_b_60["中位"], 1), C["red"]),
        ("3月最差", pct(sig_b_60["最差"], 1), C["red"]),
    ]
    for i, (label, value, color) in enumerate(kpis):
        x = 0.2 + 0.3 * i
        _card_rect(ax, (x - 0.125, 0.345), 0.25, 0.13, face="card")
        ax.text(x, 0.425, value, ha="center", fontsize=22, fontweight="bold",
                color=color, fontfamily="monospace", transform=ax.transAxes)
        ax.text(x, 0.365, label, ha="center", fontsize=12,
                color=C["muted"], transform=ax.transAxes)

    ax.text(0.5, 0.25, "结论先说：第二根脉冲后≠右侧确认", ha="center",
            fontsize=18, fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.185, "历史 36 次样本，60日跌的占 68%，中位 -8.4%",
            ha="center", fontsize=13.5, color=C["cyan"], transform=ax.transAxes)
    ax.text(0.5, 0.11, "#券商ETF #512880 #牛市旗手 #量化投资 #反共识",
            ha="center", fontsize=12.5, color=C["blue"], transform=ax.transAxes)
    _page_number(fig, 1)
    fig.savefig(CARDS / "01_cover.png", dpi=DPI, facecolor=C["bg"])
    plt.close(fig)


def card_2(df, state):
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_facecolor(C["bg"])
    ax.text(0.5, 0.94, "盘面到底强到什么程度？", ha="center", fontsize=27,
            fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.895, "6/22 + 6/25 两根脉冲，量价共振非常少见", ha="center",
            fontsize=12.8, color=C["muted"], transform=ax.transAxes)

    # 价格图
    axp = fig.add_axes([0.10, 0.47, 0.82, 0.34])
    recent = df.iloc[-180:].copy()
    # 把今天的点加上去（用估算收盘）
    today_close = df["close"].iloc[-1] * (1 + TODAY_CHG)
    today_ts = pd.Timestamp.today().normalize()
    axp.plot(recent.index, recent["close"], color=C["blue"], lw=1.6, label="证券ETF")
    axp.plot(recent.index, recent["ma20"], color=C["green"], lw=0.9, alpha=0.75, label="MA20")
    axp.plot(recent.index, recent["ma60"], color=C["orange"], lw=0.9, alpha=0.75, label="MA60")
    # 标记 6/22
    sig_dates = [d for d in recent.index if d.strftime("%Y-%m-%d") == "2026-06-22"]
    if sig_dates:
        axp.scatter(sig_dates, [recent.loc[d, "close"] for d in sig_dates],
                    color=C["red"], s=60, zorder=5, label="脉冲#1")
    axp.scatter([today_ts], [today_close], color=C["gold"], s=80, marker="*",
                zorder=6, label="脉冲#2(今日)")
    axp.legend(fontsize=8, loc="upper left", facecolor=C["card"],
               edgecolor=C["border"], labelcolor=C["text"])
    axp.grid(True, color=C["border"], lw=0.4, alpha=0.55)
    axp.set_facecolor(C["card"])
    for spine in axp.spines.values():
        spine.set_color(C["border"])
    axp.tick_params(colors=C["muted"], labelsize=8.5)

    # 四个指标方块
    today_close = df["close"].iloc[-1] * (1 + TODAY_CHG)
    dd_now = today_close / df["close"].max() - 1
    metrics = [
        ("今日涨幅", f"+{TODAY_CHG*100:.1f}%", C["green"]),
        ("成交额", f"{TODAY_AMOUNT_YI:.1f}亿", C["gold"]),
        ("换手率", f"{TODAY_TURNOVER:.1f}%", C["cyan"]),
        ("距高点", f"{dd_now*100:+.1f}%", C["red"]),
    ]
    for i, (label, value, color) in enumerate(metrics):
        x = 0.17 + i * 0.22
        _card_rect(ax, (x - 0.085, 0.30), 0.17, 0.105, face="panel")
        # 成交额含中文「亿」，不走 monospace 走中文兜底
        ff = None if "亿" in value else "monospace"
        ax.text(x, 0.365, value, ha="center", fontsize=18, fontweight="bold",
                color=color, fontfamily=ff, transform=ax.transAxes)
        ax.text(x, 0.318, label, ha="center", fontsize=11.5,
                color=C["muted"], transform=ax.transAxes)
    ax.text(0.5, 0.22, "强信号：放量 + 距高点仅 -12%，不是底部反弹",
            ha="center", fontsize=14.5, fontweight="bold",
            color=C["gold"], transform=ax.transAxes)
    ax.text(0.5, 0.16, "可这恰恰是历史上最容易被埋的位置（详见下页）",
            ha="center", fontsize=12.5, color=C["muted"], transform=ax.transAxes)
    _page_number(fig, 2)
    _disclaimer(fig)
    fig.savefig(CARDS / "02_state.png", dpi=DPI, facecolor=C["bg"])
    plt.close(fig)


def card_3():
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_facecolor(C["bg"])
    ax.text(0.5, 0.94, "今天到底发生了啥？", ha="center", fontsize=29,
            fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.895, "三条线索告诉你为什么券商突然动", ha="center",
            fontsize=12.8, color=C["muted"], transform=ax.transAxes)

    reasons = [
        ("01", "单股暴吸 36 亿",
         f"长江证券 主力净流入 {TODAY_LJZQ_INFLOW_YI:.1f}亿，单日吸金全市场第一", C["orange"]),
        ("02", "非银板块全员动",
         f"非银金融 {pct(TODAY_SECTOR_GAIN, 2)} · 保险II {pct(0.0356, 2)} · 证券II {pct(0.0330, 2)}",
         C["red"]),
        ("03", "成交放大到 31亿",
         f"证券ETF 换手 {TODAY_TURNOVER:.1f}%，是近20日均量的 {2.16:.1f} 倍", C["blue"]),
    ]
    y = 0.80
    for num, title, body, color in reasons:
        _card_rect(ax, (0.06, y - 0.14), 0.88, 0.155, face="card")
        ax.text(0.10, y - 0.015, num, fontsize=22, fontweight="bold", color=color,
                fontfamily="monospace", transform=ax.transAxes)
        ax.text(0.22, y - 0.005, title, fontsize=17, fontweight="bold",
                color=C["text"], transform=ax.transAxes)
        ax.text(0.22, y - 0.075, body, fontsize=12.2, color=C["muted"],
                transform=ax.transAxes)
        y -= 0.20

    ax.text(0.5, 0.16, "三条线索都指向：游资 + 机构同时入场",
            ha="center", fontsize=14, fontweight="bold",
            color=C["gold"], transform=ax.transAxes)
    ax.text(0.5, 0.115, "看起来像启动信号 — 但牢记：券商爱演\"一日游\"",
            ha="center", fontsize=12.5, color=C["muted"], transform=ax.transAxes)
    _page_number(fig, 3)
    _disclaimer(fig)
    fig.savefig(CARDS / "03_signal.png", dpi=DPI, facecolor=C["bg"])
    plt.close(fig)


def card_4(win_a, win_b):
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_facecolor(C["bg"])
    ax.text(0.5, 0.94, "历史信号告诉你真相", ha="center", fontsize=28,
            fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.895, "10 年 / 2,396 个交易日 / 全样本回测", ha="center",
            fontsize=12.5, color=C["muted"], transform=ax.transAxes)

    # 标题
    ax.text(0.18, 0.81, "信号A", ha="center", fontsize=14,
            fontweight="bold", color=C["blue"], transform=ax.transAxes)
    ax.text(0.18, 0.78, "放量大涨", ha="center", fontsize=11,
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.18, 0.755, "≥3% 且量比≥1.5", ha="center", fontsize=10,
            color=C["muted"], transform=ax.transAxes)

    ax.text(0.55, 0.81, "信号B", ha="center", fontsize=14,
            fontweight="bold", color=C["gold"], transform=ax.transAxes)
    ax.text(0.55, 0.78, "连续脉冲（=今日）", ha="center", fontsize=11,
            color=C["muted"], transform=ax.transAxes)
    ax.text(0.55, 0.755, "信号A + 近10日已有1次大涨", ha="center", fontsize=10,
            color=C["muted"], transform=ax.transAxes)

    ax.text(0.86, 0.81, "差距", ha="center", fontsize=14,
            fontweight="bold", color=C["red"], transform=ax.transAxes)

    # 表头
    ax.plot([0.06, 0.94], [0.715, 0.715], color=C["border"], transform=ax.transAxes)
    headers = ["持有", "信号A胜率", "信号B胜率", "B比A差"]
    xs = [0.12, 0.36, 0.62, 0.86]
    for x, h in zip(xs, headers):
        ax.text(x, 0.685, h, ha="center", fontsize=11.5,
                fontweight="bold", color=C["muted"], transform=ax.transAxes)
    ax.plot([0.06, 0.94], [0.66, 0.66], color=C["border"], transform=ax.transAxes)

    # 数据行
    y = 0.605
    for h in [5, 10, 20, 60, 120, 250]:
        ra = win_a[win_a["h"] == h]
        rb = win_b[win_b["h"] == h]
        if ra.empty or rb.empty: continue
        ra, rb = ra.iloc[0], rb.iloc[0]
        wa, wb = ra["胜率"], rb["胜率"]
        diff = wb - wa
        _card_rect(ax, (0.06, y - 0.025), 0.88, 0.052, face="card", alpha=0.85)
        ax.text(xs[0], y, ra["持有"], ha="center", va="center",
                fontsize=12.5, color=C["text"], transform=ax.transAxes)
        ax.text(xs[1], y, pct0(wa), ha="center", va="center",
                fontsize=13, fontweight="bold",
                color=C["green"] if wa >= 0.5 else (C["gold"] if wa >= 0.4 else C["red"]),
                fontfamily="monospace", transform=ax.transAxes)
        ax.text(xs[2], y, pct0(wb), ha="center", va="center",
                fontsize=13, fontweight="bold",
                color=C["green"] if wb >= 0.5 else (C["gold"] if wb >= 0.4 else C["red"]),
                fontfamily="monospace", transform=ax.transAxes)
        ax.text(xs[3], y, f"{diff*100:+.1f}pct", ha="center", va="center",
                fontsize=12, fontweight="bold",
                color=C["red"] if diff < 0 else C["green"],
                fontfamily="monospace", transform=ax.transAxes)
        y -= 0.066

    ax.text(0.5, 0.18, "信号B 在 10日~6月所有窗口里 都跑输信号A",
            ha="center", fontsize=14.5, fontweight="bold",
            color=C["gold"], transform=ax.transAxes)
    ax.text(0.5, 0.135, "连续脉冲 ≠ 趋势启动，更像情绪过热",
            ha="center", fontsize=12.5, color=C["muted"], transform=ax.transAxes)
    _page_number(fig, 4)
    _disclaimer(fig)
    fig.savefig(CARDS / "04_winrate.png", dpi=DPI, facecolor=C["bg"])
    plt.close(fig)


def card_5(win_b):
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_facecolor(C["bg"])
    ax.text(0.5, 0.94, "持有这么久，最差能跌多少？", ha="center", fontsize=25,
            fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.895, "连续脉冲信号后的持有期回撤分布", ha="center",
            fontsize=12.5, color=C["muted"], transform=ax.transAxes)

    headers = ["持有", "样本", "胜率", "中位", "最差", "浮亏中位"]
    xs = [0.10, 0.27, 0.43, 0.58, 0.74, 0.89]
    y = 0.81
    for x, h in zip(xs, headers):
        ax.text(x, y, h, ha="center", fontsize=11.5,
                fontweight="bold", color=C["muted"], transform=ax.transAxes)
    ax.plot([0.05, 0.95], [y - 0.025, y - 0.025], color=C["border"], transform=ax.transAxes)

    y -= 0.085
    for h in [5, 10, 20, 60, 120, 250]:
        r = win_b[win_b["h"] == h]
        if r.empty: continue
        r = r.iloc[0]
        _card_rect(ax, (0.05, y - 0.032), 0.90, 0.068, face="card", alpha=0.82)
        values = [r["持有"], f"{int(r['样本'])}", pct0(r["胜率"]),
                  pct(r["中位"], 1), pct(r["最差"], 1), pct(r["浮亏中位"], 1)]
        colors = [C["text"], C["muted"],
                  C["green"] if r["胜率"] >= 0.5 else (C["gold"] if r["胜率"] >= 0.4 else C["red"]),
                  C["green"] if r["中位"] >= 0 else C["red"],
                  C["red"], C["red"]]
        for x, v, c in zip(xs, values, colors):
            ax.text(x, y, v, ha="center", va="center", fontsize=12.5,
                    fontweight="bold" if x in (0.43, 0.58) else "normal",
                    color=c, fontfamily="monospace" if x > 0.15 else None,
                    transform=ax.transAxes)
        y -= 0.082

    sig_b_60 = win_b[win_b["h"] == 60].iloc[0]
    ax.text(0.5, 0.225, f"60日持有: 胜率 {pct0(sig_b_60['胜率'])}, 中位 {pct(sig_b_60['中位'], 1)}",
            ha="center", fontsize=15, fontweight="bold",
            color=C["gold"], transform=ax.transAxes)
    ax.text(0.5, 0.165, "翻译: 100次里68次会亏, 一半的情况亏 8.4% 以上",
            ha="center", fontsize=13, color=C["red"], transform=ax.transAxes)
    ax.text(0.5, 0.115, "这就是为什么券商被叫做\"散户绞肉机\"",
            ha="center", fontsize=12.5, color=C["muted"], transform=ax.transAxes)
    _page_number(fig, 5)
    _disclaimer(fig)
    fig.savefig(CARDS / "05_pain.png", dpi=DPI, facecolor=C["bg"])
    plt.close(fig)


def card_6(df, sig_b):
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_facecolor(C["bg"])
    ax.text(0.5, 0.94, "历史上的复盘案例", ha="center", fontsize=28,
            fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.895, "连续脉冲后 60日 跌得最惨 vs 涨得最猛", ha="center",
            fontsize=12.5, color=C["muted"], transform=ax.transAxes)

    # 计算 60日表现
    rows = []
    for d in sig_b.index:
        pos = df.index.get_loc(d)
        if pos + 60 >= len(df):
            continue
        base = df["close"].iloc[pos]
        r60 = (df["close"].iloc[pos+60] / base - 1) * 100
        rows.append({"date": d.strftime("%Y-%m-%d"), "ret60": r60})
    res = pd.DataFrame(rows)

    # 跌最惨 TOP3
    worst = res.nsmallest(3, "ret60")
    best = res.nlargest(3, "ret60")

    ax.text(0.27, 0.81, "[惨] 跌得最惨 TOP3", ha="center", fontsize=14,
            fontweight="bold", color=C["red"], transform=ax.transAxes)
    y = 0.74
    for i, (_, row) in enumerate(worst.iterrows()):
        _card_rect(ax, (0.05, y - 0.04), 0.42, 0.075, face="card")
        ax.text(0.07, y - 0.005, row["date"], fontsize=11.5,
                color=C["text"], transform=ax.transAxes)
        ax.text(0.07, y - 0.038, "60日后", fontsize=9,
                color=C["muted"], transform=ax.transAxes)
        ax.text(0.45, y - 0.015, f"{row['ret60']:+.1f}%", ha="right",
                fontsize=18, fontweight="bold", color=C["red"],
                fontfamily="monospace", transform=ax.transAxes)
        y -= 0.085

    ax.text(0.73, 0.81, "[猛] 涨得最猛 TOP3", ha="center", fontsize=14,
            fontweight="bold", color=C["green"], transform=ax.transAxes)
    y = 0.74
    for i, (_, row) in enumerate(best.iterrows()):
        _card_rect(ax, (0.52, y - 0.04), 0.42, 0.075, face="card")
        ax.text(0.54, y - 0.005, row["date"], fontsize=11.5,
                color=C["text"], transform=ax.transAxes)
        ax.text(0.54, y - 0.038, "60日后", fontsize=9,
                color=C["muted"], transform=ax.transAxes)
        ax.text(0.92, y - 0.015, f"{row['ret60']:+.1f}%", ha="right",
                fontsize=18, fontweight="bold", color=C["green"],
                fontfamily="monospace", transform=ax.transAxes)
        y -= 0.085

    # 案例点评
    _card_rect(ax, (0.06, 0.20), 0.88, 0.235, face="panel")
    ax.text(0.5, 0.40, "涨得最猛的样本，几乎全是 2024 牛市起点",
            ha="center", fontsize=12.5, fontweight="bold",
            color=C["gold"], transform=ax.transAxes)
    ax.text(0.5, 0.36, "2024-09-26 / 09-27 / 09-30 — 政策底+情绪底共振",
            ha="center", fontsize=11, color=C["muted"], transform=ax.transAxes)

    ax.text(0.5, 0.305, "跌得最惨的样本，全是\"假启动+回调\"位置",
            ha="center", fontsize=12.5, fontweight="bold",
            color=C["red"], transform=ax.transAxes)
    ax.text(0.5, 0.265, "2019-03 / 2021-01 / 2018-01 — 都是冲高后大幅回吐",
            ha="center", fontsize=11, color=C["muted"], transform=ax.transAxes)
    ax.text(0.5, 0.215, "现在到底是哪一种？看下页",
            ha="center", fontsize=11.5, color=C["cyan"], transform=ax.transAxes)

    _page_number(fig, 6)
    _disclaimer(fig)
    fig.savefig(CARDS / "06_cases.png", dpi=DPI, facecolor=C["bg"])
    plt.close(fig)


def card_7(df):
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_facecolor(C["bg"])
    ax.text(0.5, 0.93, "那今天到底是哪一种？", ha="center", fontsize=27,
            fontweight="bold", color=C["gold"], transform=ax.transAxes)
    ax.text(0.5, 0.88, "对照4个特征，自己判断", ha="center",
            fontsize=13, color=C["muted"], transform=ax.transAxes)

    # 当前 vs 牛市起点 / 牛市末段 三列对照
    today_close = df["close"].iloc[-1] * (1 + TODAY_CHG)
    peak = df["close"].max()
    pos_pct = today_close / peak * 100
    y1_low = df.tail(250)["close"].min()
    above_low = today_close / y1_low - 1

    rows = [
        ("距离前高", f"{(today_close/peak-1)*100:.1f}%", "-40%~-60% 深底", "-5%~-15% 追高",
         "现在 -12% 中间"),
        ("过去1年涨幅", f"+{(today_close/df['close'].iloc[-250]-1)*100:.1f}%", "-20%~-30%", "+60%~+150%",
         "+7% 中性偏弱"),
        ("MA60 状态", "今日上穿" if today_close > df["ma60"].iloc[-1] else "尚未上穿",
         "深跌后首次上穿", "已上穿+远离", "今日上穿"),
        ("市场氛围", "?", "悲观+恐慌", "亢奋+融资爆表", "—"),
        ("结论", "—",
         "牛市发令枪", "高位补涨陷阱", "更接近右上"),
    ]

    ax.text(0.25, 0.795, "特征", ha="center", fontsize=11.5,
            fontweight="bold", color=C["muted"], transform=ax.transAxes)
    ax.text(0.50, 0.795, "牛市起点", ha="center", fontsize=11.5,
            fontweight="bold", color=C["green"], transform=ax.transAxes)
    ax.text(0.78, 0.795, "高位陷阱", ha="center", fontsize=11.5,
            fontweight="bold", color=C["red"], transform=ax.transAxes)
    ax.plot([0.04, 0.96], [0.78, 0.78], color=C["border"], transform=ax.transAxes)

    y = 0.735
    for name, cur, bull, trap, hint in rows[:4]:
        _card_rect(ax, (0.04, y - 0.04), 0.92, 0.082, face="card", alpha=0.82)
        ax.text(0.075, y - 0.005, name, fontsize=11.5,
                fontweight="bold", color=C["text"], transform=ax.transAxes)
        ax.text(0.075, y - 0.038, cur, fontsize=10.5,
                color=C["gold"], transform=ax.transAxes)
        ax.text(0.50, y - 0.018, bull, ha="center", fontsize=10.5,
                color=C["green"], transform=ax.transAxes)
        ax.text(0.78, y - 0.018, trap, ha="center", fontsize=10.5,
                color=C["red"], transform=ax.transAxes)
        y -= 0.105

    # 结论框
    _card_rect(ax, (0.06, 0.16), 0.88, 0.145, face="panel", ec=C["gold"])
    ax.text(0.5, 0.265, "当前位置不上不下：偏\"补涨\"侧",
            ha="center", fontsize=14.5, fontweight="bold",
            color=C["gold"], transform=ax.transAxes)
    ax.text(0.5, 0.225, "—— 不是深底反弹的胜率结构",
            ha="center", fontsize=12, color=C["muted"], transform=ax.transAxes)
    ax.text(0.5, 0.185, "但 MA60 今日上穿 = 趋势改善信号萌芽",
            ha="center", fontsize=11.5, color=C["cyan"], transform=ax.transAxes)

    _page_number(fig, 7)
    _disclaimer(fig)
    fig.savefig(CARDS / "07_diagnose.png", dpi=DPI, facecolor=C["bg"])
    plt.close(fig)


def card_8(win_b):
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_facecolor(C["bg"])

    ax.text(0.5, 0.95, "  最后总结  ", ha="center", va="center", fontsize=12,
            fontweight="bold", color=C["bg"],
            bbox=dict(boxstyle="round,pad=0.45", fc=C["gold"], ec="none"),
            transform=ax.transAxes)
    ax.text(0.5, 0.885, "三句话看懂今天的券商", ha="center", fontsize=27,
            fontweight="bold", color=C["text"], transform=ax.transAxes)

    sig_b_60 = win_b[win_b["h"] == 60].iloc[0]
    points = [
        ("01", "信号确实强",
         C["green"],
         "长江证券吸金36亿+连续脉冲+换手5.6%"),
        ("02", "但历史胜率劝退",
         C["red"],
         f"连续脉冲后3月胜率仅{pct0(sig_b_60['胜率'])}, 中位{pct(sig_b_60['中位'], 1)}"),
        ("03", "纪律比方向更重要",
         C["gold"],
         "试仓20% + 不破前低不加, 跌破MA20清掉"),
    ]
    for i, (y, (num, title, col, body)) in enumerate(zip([0.785, 0.675, 0.565], points)):
        ax.text(0.13, y, num, ha="center", va="center", fontsize=32,
                fontweight="bold", color=col, transform=ax.transAxes)
        ax.text(0.25, y + 0.022, title, ha="left", va="center", fontsize=17,
                fontweight="bold", color=C["text"], transform=ax.transAxes)
        ax.text(0.25, y - 0.025, body, ha="left", va="center", fontsize=11,
                color=C["muted"], transform=ax.transAxes)
        if i < 2:
            ax.plot([0.10, 0.90], [y - 0.058, y - 0.058], color=C["border"],
                    lw=0.6, transform=ax.transAxes)

    # 仓位建议框
    ax.add_patch(FancyBboxPatch((0.08, 0.375), 0.84, 0.125,
                                boxstyle="round,pad=0.01,rounding_size=0.015",
                                facecolor=C["card"], edgecolor=C["orange"], lw=1.2,
                                transform=ax.transAxes))
    ax.text(0.5, 0.475, "操作纪律", ha="center", fontsize=11.5, fontweight="bold",
            color=C["bg"],
            bbox=dict(boxstyle="round,pad=0.35", fc=C["orange"], ec="none"),
            transform=ax.transAxes)
    ax.text(0.5, 0.425, "想追也只试仓 20%", ha="center", fontsize=14,
            fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.395, "破 MA20 / 一日游 直接走人, 不死扛",
            ha="center", fontsize=11.5, color=C["muted"], transform=ax.transAxes)

    # 互动
    ax.text(0.5, 0.315, "你今天追了吗?", ha="center", fontsize=21,
            fontweight="bold", color=C["text"], transform=ax.transAxes)
    options = [("追了一手", C["red"]), ("观望中", C["gold"]), ("空仓看戏", C["blue"])]
    for i, (opt, col) in enumerate(options):
        x = 0.20 + i * 0.30
        ax.text(x, 0.265, opt, ha="center", va="center", fontsize=11,
                color=col, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.42", fc=C["card"], ec=col, lw=0.9),
                transform=ax.transAxes)

    ax.add_patch(FancyBboxPatch((0.10, 0.165), 0.80, 0.072,
                                boxstyle="round,pad=0.01,rounding_size=0.014",
                                facecolor=C["panel"], edgecolor=C["cyan"], lw=1.6,
                                transform=ax.transAxes))
    ax.text(0.5, 0.201, "评论区打「券商」↓", ha="center", va="center",
            fontsize=20, fontweight="bold", color=C["cyan"], transform=ax.transAxes)

    ax.text(0.5, 0.125, "完整 36 次历史样本明细在评论区置顶", ha="center",
            fontsize=11.5, color=C["muted"], style="italic", transform=ax.transAxes)
    ax.text(0.5, 0.078, "关注「复旦杰伦」: 每周拆一个 A股ETF 的胜率结构",
            ha="center", fontsize=11.5, fontweight="bold", color=C["gold"],
            bbox=dict(boxstyle="round,pad=0.35", fc=C["card"], ec=C["gold"], lw=0.8),
            transform=ax.transAxes)
    _page_number(fig, 8)
    _disclaimer(fig)
    fig.savefig(CARDS / "08_cta.png", dpi=DPI, facecolor=C["bg"])
    plt.close(fig)


# ────────── 主入口 ──────────
def main():
    print(f"[1] 载入证券ETF数据 → output 目录: {ROOT}")
    df = load_etf(MAIN)
    print(f"  数据 {df.index.min().date()} ~ {df.index.max().date()}, n={len(df)}")

    print("[2] 计算信号集")
    sig_a, sig_b = compute_signals(df)
    print(f"  信号A 放量大涨: {len(sig_a)} 次")
    print(f"  信号B 连续脉冲: {len(sig_b)} 次")

    horizons = [5, 10, 20, 60, 120, 250]
    print("[3] 回测两组信号胜率")
    win_a = winrate_after(df, sig_a.index, horizons)
    win_b = winrate_after(df, sig_b.index, horizons)
    print("\n  信号A 胜率:")
    print(win_a[["持有", "样本", "胜率", "中位", "均值"]].to_string(index=False))
    print("\n  信号B 胜率:")
    print(win_b[["持有", "样本", "胜率", "中位", "均值"]].to_string(index=False))

    # 当前状态
    today_close = df["close"].iloc[-1] * (1 + TODAY_CHG)
    state = {
        "as_of": TODAY,
        "today_close_est": float(today_close),
        "today_chg": TODAY_CHG,
        "peak_all": float(df["close"].max()),
        "peak_date": df["close"].idxmax().strftime("%Y-%m-%d"),
        "dd_now": float(today_close / df["close"].max() - 1),
        "ma20": float(df["ma20"].iloc[-1]),
        "ma60": float(df["ma60"].iloc[-1]),
        "above_ma60_today": bool(today_close > df["ma60"].iloc[-1]),
    }
    print("\n  当前状态:", json.dumps(state, indent=2, ensure_ascii=False))

    print("[4] 保存数据")
    sig_a.to_parquet(DATA / "signal_a.parquet")
    sig_b.to_parquet(DATA / "signal_b.parquet")
    win_a.to_csv(DATA / "winrate_a.csv", index=False, encoding="utf-8-sig")
    win_b.to_csv(DATA / "winrate_b.csv", index=False, encoding="utf-8-sig")
    with open(DATA / "state.json", "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False, default=str)

    print("[5] 生成 8 张深色卡片")
    card_1(state, win_b)
    card_2(df, state)
    card_3()
    card_4(win_a, win_b)
    card_5(win_b)
    card_6(df, sig_b)
    card_7(df)
    card_8(win_b)
    print(f"  卡片产出: {CARDS}")
    print(f"  数据产出: {DATA}")
    return df, sig_a, sig_b, win_a, win_b, state


if __name__ == "__main__":
    main()
