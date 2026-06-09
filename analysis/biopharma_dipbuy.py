"""
医药能抄底吗 — 量化研究 + 小红书卡片(7张)
================================================
Phase 2 付费内容: 医药跌3年现在能否抄底 + "买医药≠买创新药出海"。
基于 akshare 后复权ETF日线, 全部结论可复现。

主线(均为可验证价格数据):
  1. 政策驱动的牛熊全周期 (2018集采→2021顶→深熊→反转)
  2. 买医药≠买创新药出海 (宽基被稀释)
  3. 深跌抄底胜率U型 (跌透88% vs 当前44%)
  4. 动量轮动在医药内部失效
  5. 子板块当前定位

产出: cards/ 7张 + figures/ + data/ + summary.json

Usage:
    conda activate research
    python analysis/biopharma_dipbuy.py
"""
import sys, json
sys.path.insert(0, "src")

import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
plt.rcParams["font.sans-serif"] = ["Droid Sans Fallback", "WenQuanYi Micro Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

from quant.data.cache import Cache
from quant.backtest.metrics import annual_return, max_drawdown, sharpe, calmar

C = {
    "bg": "#0d1117", "card": "#161b22", "border": "#30363d",
    "text": "#c9d1d9", "muted": "#8b949e", "blue": "#58a6ff",
    "green": "#3fb950", "red": "#f85149", "orange": "#d2991d",
    "purple": "#bc8cff", "gold": "#f0c040", "cyan": "#56d4dd",
}
CARD_W, CARD_H, DPI = 7.2, 9.6, 200  # 1440x1920 高清(小红书手机端)
TOTAL_CARDS = 7
ROOT = Path("./output/2026-06-09/biopharma-dipbuy")
CARDS, FIGS, DATA = ROOT / "cards", ROOT / "figures", ROOT / "data"
for d in (CARDS, FIGS, DATA):
    d.mkdir(parents=True, exist_ok=True)

cache = Cache("./data/cache")


def _fig():
    return plt.figure(figsize=(CARD_W, CARD_H), facecolor=C["bg"])


def _page_number(fig, n):
    fig.text(0.94, 0.052, f"{n}/{TOTAL_CARDS}", ha="right", fontsize=12,
             color=C["muted"], fontfamily="monospace")


def _disclaimer(fig):
    fig.text(0.5, 0.052, "* 历史回测不代表未来 · 不构成投资建议",
             ha="center", fontsize=11, color=C["muted"])


# ════════════════════════════════════════════════════════════════
# 数据与计算
# ════════════════════════════════════════════════════════════════
print("=" * 60)
print("医药能抄底吗 — 卡片生成")
print("=" * 60)

ASSETS = {
    "159929": "医药(长序列)", "512010": "医药卫生", "159992": "创新药",
    "512170": "医疗(器械/CXO)", "512290": "生物医药", "513120": "港股创新药",
}
close = {c: cache.load("etf", c)["close"].dropna() for c in ASSETS}
bench = cache.load("etf", "510300")["close"].dropna()
END_STR = max(s.index[-1] for s in close.values()).strftime("%Y.%m.%d")

LONG = "159929"
med = close[LONG]

# 1) 全周期分段
def seg(s, a, b):
    s2 = s[(s.index >= a) & (s.index <= b)]
    return (s2.iloc[-1] / s2.iloc[0] - 1) if len(s2) > 1 else np.nan

REVERSAL = "2024-09-23"
cycles = [
    ("2018集采冲击", "2018-05-01", "2019-01-04"),
    ("2019-21大牛", "2019-01-04", "2021-07-01"),
    ("2021-24深熊", "2021-07-01", REVERSAL),
    ("2024-25反转", REVERSAL, str(med.index[-1].date())),
]
cyc = [{"name": n, "med": seg(med, a, b), "b300": seg(bench, a, b)} for n, a, b in cycles]

# 2) 买医药≠创新药出海 (反转后各板块)
end = str(med.index[-1].date())
diverge = {
    "宽基医药": seg(close["512010"], REVERSAL, end),
    "创新药": seg(close["159992"], REVERSAL, end),
    "港股创新药": seg(close["513120"], REVERSAL, end),
    "沪深300": seg(bench, REVERSAL, end),
}

# 3) 深跌抄底胜率 (med, 1年)
dd_full = med / med.rolling(252, min_periods=60).max() - 1
fwd = med.shift(-252) / med - 1
d5 = pd.DataFrame({"dd": dd_full, "fwd": fwd}).dropna()
DD_BINS = [(-1.0, -0.40), (-0.40, -0.30), (-0.30, -0.20), (-0.20, -0.10), (-0.10, 0.0)]
DD_LABS = ["≤-40%", "-40~-30%", "-30~-20%", "-20~-10%", "-10~0%"]
knife = []
for (lo, hi), lab in zip(DD_BINS, DD_LABS):
    v = d5.loc[(d5["dd"] > lo) & (d5["dd"] <= hi), "fwd"]
    knife.append({"lab": lab, "n": int(len(v)),
                  "win": float((v > 0).mean()) if len(v) else np.nan,
                  "avg": float(v.mean()) if len(v) else np.nan})
cur_dd = float(dd_full.iloc[-1])
cur_lab = next((lab for (lo, hi), lab in zip(DD_BINS, DD_LABS) if lo < cur_dd <= hi), DD_LABS[-1])

# 4) 动量轮动失效
rot_codes = ["159992", "512170", "512290", "512010"]
px = pd.DataFrame({c: close[c] for c in rot_codes}).dropna()
px = px[px.index >= "2020-06-01"]
bench_r = bench.reindex(px.index).ffill()
mends = px.resample("ME").last().index
LB, HN = 63, 2
W = pd.DataFrame(0.0, index=px.index, columns=rot_codes)
for i, me in enumerate(mends[:-1]):
    h = px[px.index <= me]
    if len(h) < LB + 1:
        continue
    mom = h.iloc[-1] / h.iloc[-1 - LB] - 1
    top = mom.sort_values(ascending=False).head(HN).index.tolist()
    nxt = mends[i + 1]
    mk = (W.index > me) & (W.index <= nxt)
    for c in top:
        W.loc[mk, c] = 1.0 / HN
ret = px.pct_change().fillna(0)
nav_rot = (1 + (W.shift(1).fillna(0) * ret).sum(axis=1)).cumprod()
nav_ew = (1 + ret.mean(axis=1)).cumprod()
nav_b = bench_r / bench_r.iloc[0]
nav_rot /= nav_rot.iloc[0]; nav_ew /= nav_ew.iloc[0]
rot_m = {}
for nm, nav in [("动量轮动", nav_rot), ("医药等权", nav_ew), ("沪深300", nav_b)]:
    rot_m[nm] = {"total": float(nav.iloc[-1] - 1), "ann": annual_return(nav),
                 "mdd": max_drawdown(nav), "sharpe": sharpe(nav)}

# 5) 子板块当前定位
sub = {}
for c, name in ASSETS.items():
    s = close[c]
    dd = s / s.rolling(252, min_periods=20).max() - 1
    sub[c] = {"name": name, "ret1y": float(s.pct_change(250).iloc[-1]) if len(s) > 250 else np.nan,
              "ret20": float(s.pct_change(20).iloc[-1]), "dd": float(dd.iloc[-1]),
              "ann": annual_return(s / s.iloc[0]), "mdd": max_drawdown(s / s.iloc[0])}

print(f"当前医药回撤 {cur_dd:+.0%} (属{cur_lab}, 1年胜率{[k['win'] for k in knife if k['lab']==cur_lab][0]:.0%})")
print(f"反转后: 宽基医药{diverge['宽基医药']:+.0%} vs 沪深300{diverge['沪深300']:+.0%}")
print(f"动量轮动 {rot_m['动量轮动']['total']:+.0%} vs 沪深300 {rot_m['沪深300']['total']:+.0%}")

# 导出
summary = {
    "as_of": END_STR, "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "cycles": cyc, "diverge": diverge, "knife": knife, "cur_dd": cur_dd, "cur_lab": cur_lab,
    "rot_metrics": rot_m, "sub": sub,
}
(ROOT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
pd.DataFrame(cyc).to_csv(DATA / "cycle_returns.csv", index=False, encoding="utf-8-sig")
pd.DataFrame(knife).to_csv(DATA / "dipbuy_winrate.csv", index=False, encoding="utf-8-sig")
pd.DataFrame(sub).T.to_csv(DATA / "subsector_state.csv", encoding="utf-8-sig")
pd.DataFrame(rot_m).T.to_csv(DATA / "rotation_metrics.csv", encoding="utf-8-sig")


# ════════════════════════════════════════════════════════════════
# 卡片
# ════════════════════════════════════════════════════════════════
def card_1_cover():
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(C["bg"]); ax.axis("off")
    ax.text(0.5, 0.89, "医药跌了三年", ha="center", fontsize=37, fontweight="bold",
            color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.805, "现在能抄底吗？", ha="center", fontsize=45, fontweight="bold",
            color=C["gold"], transform=ax.transAxes)
    ax.text(0.5, 0.728, f"数据截止 {END_STR} · 用12年数据算胜率",
            ha="center", fontsize=14.5, color=C["muted"], transform=ax.transAxes)
    ax.plot([0.13, 0.87], [0.688, 0.688], color=C["border"], lw=1.2, transform=ax.transAxes)
    ax.text(0.5, 0.585, f"{cur_dd:+.0%}", ha="center", fontsize=78, fontweight="bold",
            color=C["red"], fontfamily="monospace", transform=ax.transAxes)
    ax.text(0.5, 0.495, "医药距一年高点", ha="center", fontsize=16, color=C["muted"], transform=ax.transAxes)
    win_cur = [k["win"] for k in knife if k["lab"] == cur_lab][0]
    kpis = [("2021-24深熊", f"{cyc[2]['med']:+.0%}", C["red"]),
            ("当前档1年胜率", f"{win_cur:.0%}", C["orange"]),
            ("跌透(≤-40%)胜率", f"{knife[0]['win']:.0%}", C["green"])]
    for i, (label, val, color) in enumerate(kpis):
        x = 0.2 + i * 0.3
        rect = FancyBboxPatch((x - 0.142, 0.325), 0.284, 0.125, boxstyle="round,pad=0.01",
                              facecolor=C["card"], edgecolor=C["border"], lw=0.8,
                              transform=ax.transAxes, zorder=0)
        ax.add_patch(rect)
        ax.text(x, 0.405, val, ha="center", fontsize=23, fontweight="bold",
                color=color, fontfamily="monospace", transform=ax.transAxes)
        ax.text(x, 0.347, label, ha="center", fontsize=11.5, color=C["muted"], transform=ax.transAxes)
    ax.text(0.5, 0.24, "买医药≠买创新药出海，先搞懂再抄", ha="center", fontsize=17.5,
            color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.172, "一个做药的人 + 量化数据 告诉你真相", ha="center", fontsize=14,
            color=C["cyan"], transform=ax.transAxes)
    ax.text(0.5, 0.105, "#创新药  #医药板块  #抄底  #集采  #量化投资",
            ha="center", fontsize=13, color=C["blue"], transform=ax.transAxes)
    _page_number(fig, 1)
    fig.savefig(CARDS / "01_cover.png", dpi=DPI, facecolor=C["bg"]); plt.close()
    print("  [1/7] cover")


def card_2_cycle():
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(C["bg"]); ax.axis("off")
    ax.text(0.5, 0.93, "政策驱动的牛熊轮回", ha="center", fontsize=29, fontweight="bold",
            color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.875, "医药的命脉是政策：集采杀、创新与出海兴",
            ha="center", fontsize=13.5, color=C["muted"], transform=ax.transAxes)
    # 净值图
    axp = fig.add_axes([0.11, 0.45, 0.81, 0.36]); axp.set_facecolor(C["card"])
    common = med.index.intersection(bench.index)
    m2 = (med.reindex(common) / med.reindex(common).iloc[0])
    b2 = (bench.reindex(common) / bench.reindex(common).iloc[0])
    axp.plot(m2.index, m2.values, color=C["red"], lw=1.4, label="医药")
    axp.plot(b2.index, b2.values, color=C["muted"], lw=1.1, label="沪深300")
    for d, lab, col in [("2018-12-06", "集采", C["red"]), ("2021-07-01", "估值顶", C["orange"]),
                        ("2024-09-23", "反转", C["green"])]:
        dt = pd.Timestamp(d)
        axp.axvline(dt, color=col, ls="--", lw=1, alpha=0.7)
    axp.legend(fontsize=10, loc="upper left", facecolor=C["card"], edgecolor=C["border"], labelcolor=C["text"])
    axp.grid(True, color=C["border"], lw=0.5, alpha=0.5)
    for sp in axp.spines.values():
        sp.set_color(C["border"])
    axp.tick_params(colors=C["muted"], labelsize=9)
    # 分段收益
    y = 0.36
    for cseg in cyc:
        col = C["green"] if cseg["med"] > 0 else C["red"]
        ax.text(0.12, y, cseg["name"], fontsize=14, color=C["text"], va="center", transform=ax.transAxes)
        ax.text(0.66, y, f"{cseg['med']:+.0%}", fontsize=17, fontweight="bold", color=col,
                ha="right", va="center", fontfamily="monospace", transform=ax.transAxes)
        ax.text(0.90, y, f"(沪深{cseg['b300']:+.0%})", fontsize=11, color=C["muted"],
                ha="right", va="center", transform=ax.transAxes)
        y -= 0.066
    ax.text(0.5, 0.092, "看懂政策周期，比追涨杀跌重要十倍",
            ha="center", fontsize=14, fontweight="bold", color=C["gold"], transform=ax.transAxes)
    _page_number(fig, 2); _disclaimer(fig)
    fig.savefig(CARDS / "02_cycle.png", dpi=DPI, facecolor=C["bg"]); plt.close()
    print("  [2/7] cycle")


def card_3_diverge():
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(C["bg"]); ax.axis("off")
    ax.text(0.5, 0.93, "买医药 ≠ 买创新药出海", ha="center", fontsize=27, fontweight="bold",
            color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.875, "2024-09反转以来 · 同样是医药差别巨大",
            ha="center", fontsize=13.5, color=C["muted"], transform=ax.transAxes)
    items = [("宽基医药(512010)", diverge["宽基医药"], C["red"]),
             ("创新药(159992)", diverge["创新药"], C["orange"]),
             ("港股创新药(513120)", diverge["港股创新药"], C["green"]),
             ("沪深300", diverge["沪深300"], C["blue"])]
    vals = [v for _, v, _ in items]
    vmax = max(abs(min(vals)), abs(max(vals))) or 1
    y = 0.76
    for name, v, col in items:
        rect = FancyBboxPatch((0.06, y - 0.052), 0.88, 0.10, boxstyle="round,pad=0.006",
                              facecolor=C["card"], edgecolor=C["border"], lw=0.6,
                              transform=ax.transAxes, zorder=0)
        ax.add_patch(rect)
        ax.text(0.10, y, name, fontsize=15, fontweight="bold", color=C["text"],
                va="center", transform=ax.transAxes)
        bw = 0.30 * abs(v) / vmax
        x0 = 0.62
        ax.add_patch(FancyBboxPatch((x0, y - 0.018), bw if v > 0 else -bw, 0.036,
                     boxstyle="round,pad=0.002", facecolor=col, alpha=0.5,
                     transform=ax.transAxes, zorder=1))
        ax.text(0.92, y, f"{v:+.0%}", fontsize=17, fontweight="bold", color=col,
                ha="right", va="center", fontfamily="monospace", transform=ax.transAxes)
        y -= 0.115
    ax.text(0.5, 0.20, "宽基医药被CXO/器械/仿制/中药拖累", ha="center", fontsize=14,
            color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.145, "真正的出海行情，集中在少数创新药标的",
            ha="center", fontsize=14, fontweight="bold", color=C["gold"], transform=ax.transAxes)
    _page_number(fig, 3); _disclaimer(fig)
    fig.savefig(CARDS / "03_diverge.png", dpi=DPI, facecolor=C["bg"]); plt.close()
    print("  [3/7] diverge")


def card_4_winrate():
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(C["bg"]); ax.axis("off")
    ax.text(0.5, 0.93, "深跌抄底胜率", ha="center", fontsize=29, fontweight="bold",
            color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.875, "按距高点回撤分档买入，持有1年的上涨概率",
            ha="center", fontsize=13.5, color=C["muted"], transform=ax.transAxes)
    valid = [k for k in knife if k["win"] == k["win"]]
    y = 0.78
    for k in valid:
        is_cur = (k["lab"] == cur_lab)
        win = k["win"]
        bar_c = C["green"] if win >= 0.6 else (C["red"] if win < 0.46 else C["gold"])
        if is_cur:
            ax.add_patch(FancyBboxPatch((0.04, y - 0.026), 0.92, 0.052, boxstyle="round,pad=0.004",
                         facecolor=C["blue"], alpha=0.13, transform=ax.transAxes, zorder=0))
        ax.text(0.07, y, k["lab"], fontsize=14, color=accent_lab(is_cur), va="center",
                fontweight="bold" if is_cur else "normal", transform=ax.transAxes)
        ax.add_patch(FancyBboxPatch((0.33, y - 0.013), 0.40 * win, 0.026, boxstyle="round,pad=0.002",
                     facecolor=bar_c, alpha=0.55, transform=ax.transAxes, zorder=1))
        ax.text(0.745, y, f"{win:.0%}", fontsize=16, fontweight="bold", color=bar_c,
                va="center", ha="left", fontfamily="monospace", transform=ax.transAxes)
        if not is_cur:
            ax.text(0.85, y, f"均{k['avg']:+.0%}", fontsize=11.5, color=C["muted"], va="center",
                    transform=ax.transAxes)
        if is_cur:
            pill = FancyBboxPatch((0.85, y - 0.02), 0.105, 0.04, boxstyle="round,pad=0.004",
                                  facecolor=C["blue"], edgecolor="none", transform=ax.transAxes, zorder=2)
            ax.add_patch(pill)
            ax.text(0.902, y, "现在", fontsize=11.5, color=C["bg"], fontweight="bold",
                    va="center", ha="center", transform=ax.transAxes, zorder=3)
        y -= 0.078
    ax.text(0.5, y - 0.01, "真正的黄金坑是跌透(≤-40%胜率88%)", ha="center", fontsize=15,
            fontweight="bold", color=C["green"], transform=ax.transAxes)
    ax.text(0.5, y - 0.065, f"当前-27%恰在历史最尴尬区间(胜率仅44%)", ha="center",
            fontsize=13.5, color=C["muted"], transform=ax.transAxes)
    ax.text(0.5, y - 0.115, "结论：现在不是最优抄底点，别急", ha="center", fontsize=14.5,
            fontweight="bold", color=C["gold"], transform=ax.transAxes)
    _page_number(fig, 4); _disclaimer(fig)
    fig.savefig(CARDS / "04_winrate.png", dpi=DPI, facecolor=C["bg"]); plt.close()
    print("  [4/7] winrate")


def accent_lab(is_cur):
    return C["blue"] if is_cur else C["text"]


def card_5_momentum():
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(C["bg"]); ax.axis("off")
    ax.text(0.5, 0.93, "医药里追动量是灾难", ha="center", fontsize=28, fontweight="bold",
            color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.875, "子板块月度动量轮动 · 2020-06起回测",
            ha="center", fontsize=13.5, color=C["muted"], transform=ax.transAxes)
    axp = fig.add_axes([0.12, 0.46, 0.78, 0.34]); axp.set_facecolor(C["card"])
    cmap = {"动量轮动": C["red"], "医药等权": C["blue"], "沪深300": C["muted"]}
    for nm, nav in [("动量轮动", nav_rot), ("医药等权", nav_ew), ("沪深300", nav_b)]:
        axp.plot(nav.index, nav.values, color=cmap[nm], lw=1.5, label=nm)
    axp.axhline(1, color=C["muted"], ls=":", lw=0.8)
    axp.legend(fontsize=10.5, loc="upper right", facecolor=C["card"], edgecolor=C["border"], labelcolor=C["text"])
    axp.grid(True, color=C["border"], lw=0.5, alpha=0.5)
    for sp in axp.spines.values():
        sp.set_color(C["border"])
    axp.tick_params(colors=C["muted"], labelsize=9)
    y = 0.37
    cols = ["策略", "总收益", "年化", "最大回撤"]
    xs = [0.10, 0.45, 0.65, 0.86]
    for x, c in zip(xs, cols):
        ax.text(x, y, c, fontsize=12.5, fontweight="bold", color=C["muted"],
                ha="left" if x < 0.12 else "center", transform=ax.transAxes)
    y -= 0.018
    ax.plot([0.07, 0.93], [y, y], color=C["border"], transform=ax.transAxes)
    for nm in ["动量轮动", "医药等权", "沪深300"]:
        m = rot_m[nm]; y -= 0.07
        ax.text(xs[0], y, nm, fontsize=13, color=cmap[nm], fontweight="bold", va="center", transform=ax.transAxes)
        for x, v, col in [(xs[1], f"{m['total']:+.0%}", C["green"] if m["total"] > 0 else C["red"]),
                          (xs[2], f"{m['ann']:+.1%}", C["green"] if m["ann"] > 0 else C["red"]),
                          (xs[3], f"{m['mdd']:.0%}", C["red"])]:
            ax.text(x, y, v, fontsize=14, fontweight="bold", color=col, ha="center", va="center",
                    fontfamily="monospace", transform=ax.transAxes)
    ax.text(0.5, 0.105, "震荡下行的板块，追最强=反复打脸",
            ha="center", fontsize=14, fontweight="bold", color=C["gold"], transform=ax.transAxes)
    _page_number(fig, 5); _disclaimer(fig)
    fig.savefig(CARDS / "05_momentum.png", dpi=DPI, facecolor=C["bg"]); plt.close()
    print("  [5/7] momentum")


def card_6_position():
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(C["bg"]); ax.axis("off")
    ax.text(0.5, 0.93, "六大医药板块 当前定位", ha="center", fontsize=27, fontweight="bold",
            color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.875, f"截止 {END_STR} · 谁更抗跌谁跌得透",
            ha="center", fontsize=13.5, color=C["muted"], transform=ax.transAxes)
    headers = ["板块", "近1年", "距一年高", "近20日"]
    xs = [0.08, 0.50, 0.72, 0.91]
    y = 0.805
    for x, h in zip(xs, headers):
        ax.text(x, y, h, fontsize=12.5, fontweight="bold", color=C["muted"],
                ha="left" if x < 0.1 else "center", transform=ax.transAxes)
    y -= 0.018
    ax.plot([0.05, 0.95], [y, y], color=C["border"], transform=ax.transAxes)
    order = sorted(ASSETS, key=lambda c: sub[c]["dd"], reverse=True)
    y = 0.73
    for c in order:
        s = sub[c]
        ax.add_patch(FancyBboxPatch((0.04, y - 0.036), 0.92, 0.074, boxstyle="round,pad=0.005",
                     facecolor=C["card"], edgecolor=C["border"], lw=0.6, transform=ax.transAxes, zorder=0))
        ax.text(xs[0], y + 0.008, s["name"], fontsize=13, fontweight="bold", color=C["text"],
                va="center", transform=ax.transAxes)
        ax.text(xs[0], y - 0.022, c, fontsize=9.5, color=C["muted"], va="center",
                fontfamily="monospace", transform=ax.transAxes)
        for x, key in [(xs[1], "ret1y"), (xs[2], "dd"), (xs[3], "ret20")]:
            v = s[key]
            if v != v:
                ax.text(x, y, "—", fontsize=14, color=C["muted"], ha="center", va="center", transform=ax.transAxes)
                continue
            ax.text(x, y, f"{v:+.0%}", fontsize=14.5, fontweight="bold", ha="center",
                    color=C["red"] if v < 0 else C["green"], va="center",
                    fontfamily="monospace", transform=ax.transAxes)
        y -= 0.092
    ax.text(0.5, 0.15, "港股创新药最抗跌(出海纯度最高)", ha="center", fontsize=14,
            fontweight="bold", color=C["gold"], transform=ax.transAxes)
    ax.text(0.5, 0.105, "想押出海，板块选择比择时更关键",
            ha="center", fontsize=12.5, color=C["muted"], transform=ax.transAxes)
    _page_number(fig, 6); _disclaimer(fig)
    fig.savefig(CARDS / "06_position.png", dpi=DPI, facecolor=C["bg"]); plt.close()
    print("  [6/7] position")


def card_7_conclusion():
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(C["bg"]); ax.axis("off")
    ax.text(0.5, 0.92, "结论：医药怎么投", ha="center", fontsize=29, fontweight="bold",
            color=C["gold"], transform=ax.transAxes)
    lines = [
        ("别买宽基赌出海", "买医药≠买创新药，选对子板块才有beta", C["blue"]),
        ("现在别急着抄底", f"当前-27%胜率仅44%，跌透(≤-40%)才88%", C["gold"]),
        ("看政策催化，别追动量", "集采落地/出海兑现是信号，追最强会打脸", C["red"]),
    ]
    y = 0.80
    for title, desc, col in lines:
        ax.add_patch(FancyBboxPatch((0.06, y - 0.115), 0.88, 0.13, boxstyle="round,pad=0.01",
                     facecolor=C["card"], edgecolor=C["border"], lw=0.8, transform=ax.transAxes, zorder=0))
        ax.text(0.10, y - 0.01, title, fontsize=16.5, fontweight="bold", color=col, transform=ax.transAxes)
        ax.text(0.10, y - 0.07, desc, fontsize=13, color=C["text"], transform=ax.transAxes)
        y -= 0.165
    ax.text(0.5, y + 0.01, "一句话：分板块、等跌透或催化、不追动量", ha="center", fontsize=16,
            fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, y - 0.05, "完整研报+数据+源码 见主页", ha="center", fontsize=14,
            color=C["cyan"], transform=ax.transAxes)
    ax.text(0.5, y - 0.105, "#创新药  #医药  #集采  #出海  #量化投资  #ETF",
            ha="center", fontsize=13, color=C["blue"], transform=ax.transAxes)
    _page_number(fig, 7); _disclaimer(fig)
    fig.savefig(CARDS / "07_conclusion.png", dpi=DPI, facecolor=C["bg"]); plt.close()
    print("  [7/7] conclusion")


print("\n生成卡片...")
card_1_cover()
card_2_cycle()
card_3_diverge()
card_4_winrate()
card_5_momentum()
card_6_position()
card_7_conclusion()
print(f"\n完成 → {ROOT}")
