"""
创新药/生物医药 — 主题可行性首看分析
=====================================
验证"医药量化研究"主题是否富矿:全周期、子板块轮动、政策事件、当前定位。
纯价格数据,结论可复现。产出 figures/ + data/ + 控制台 findings。

Usage:
    conda activate research
    python analysis/biopharma_explore.py
"""
import sys
sys.path.insert(0, "src")

import numpy as np
import pandas as pd
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Droid Sans Fallback", "WenQuanYi Micro Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

from quant.data.cache import Cache
from quant.backtest.metrics import annual_return, max_drawdown, sharpe, calmar

ROOT = Path("./output/2026-06-09/biopharma-explore")
FIGS = ROOT / "figures"
DATA = ROOT / "data"
for d in (FIGS, DATA):
    d.mkdir(parents=True, exist_ok=True)

cache = Cache("./data/cache")

UNIVERSE = {
    "159929": "医药(汇添富,长序列)",
    "512010": "医药卫生(宽基)",
    "159992": "创新药",
    "512170": "医疗(器械/服务/CXO)",
    "512290": "生物医药",
    "513120": "港股创新药",
}
BENCH = "510300"  # 沪深300

# 政策/事件时间线(领域框架,用于标注)
EVENTS = [
    ("2018-12-06", "第一批集采(4+7)", "policy_neg"),
    ("2021-06-30", "第五批集采+CDE新政", "policy_neg"),
    ("2022-11-01", "医保谈判常态化", "policy_neu"),
    ("2024-09-24", "政策+流动性反转", "policy_pos"),
    ("2025-01-01", "创新药出海兑现", "policy_pos"),
]

LC = {"text": "#1a1a2e", "sub": "#555", "grid": "#e6e6e6", "blue": "#2563eb",
      "green": "#16a34a", "red": "#dc2626", "orange": "#ea580c", "purple": "#7c3aed",
      "gold": "#b8860b", "muted": "#999", "cyan": "#0891b2"}
EVC = {"policy_neg": LC["red"], "policy_neu": LC["gold"], "policy_pos": LC["green"]}

print("=" * 64)
print("创新药/生物医药 — 主题可行性首看")
print("=" * 64)

# ── 加载 ──
close = {}
for code, name in UNIVERSE.items():
    df = cache.load("etf", code)
    if df is None:
        print(f"  !! {code} {name} 无缓存"); continue
    close[code] = df["close"].dropna()
    print(f"  {code} {name:20s} {close[code].index[0].date()}~{close[code].index[-1].date()} n={len(close[code])}")
bench = cache.load("etf", BENCH)["close"].dropna()

# ════════════════════════════════════════════════════════════════
# 1. 全周期:长序列医药 vs 沪深300 + 事件标注
# ════════════════════════════════════════════════════════════════
long_code = "159929"
lc = close[long_code]
common = lc.index.intersection(bench.index)
lc2 = lc.reindex(common).dropna()
bm = bench.reindex(lc2.index).dropna()
lc2 = lc2.reindex(bm.index)
nav_med = lc2 / lc2.iloc[0]
nav_b = bm / bm.iloc[0]

fig, ax = plt.subplots(figsize=(11, 4.2), facecolor="white")
ax.plot(nav_med.index, nav_med.values, color=LC["red"], lw=1.4, label="医药ETF(159929)")
ax.plot(nav_b.index, nav_b.values, color=LC["muted"], lw=1.2, label="沪深300")
for d, lab, kind in EVENTS:
    dt = pd.Timestamp(d)
    if dt < nav_med.index[0] or dt > nav_med.index[-1]:
        continue
    ax.axvline(dt, color=EVC[kind], ls="--", lw=1, alpha=0.7)
    ax.text(dt, ax.get_ylim()[1] * 0.96, lab, rotation=90, fontsize=8,
            color=EVC[kind], va="top", ha="right")
ax.set_title("医药全周期 vs 沪深300 — 政策驱动的牛熊轮回", fontsize=13,
             color=LC["text"], fontweight="bold")
ax.set_ylabel("净值(归一)", color=LC["sub"])
ax.legend(loc="upper left", fontsize=9)
ax.grid(True, color=LC["grid"], lw=0.6)
for s in ax.spines.values():
    s.set_color(LC["grid"])
ax.tick_params(colors=LC["sub"])
fig.tight_layout()
fig.savefig(FIGS / "fig_full_cycle.png", dpi=150, facecolor="white")
plt.close()

# 关键周期段收益
def seg_ret(s, a, b):
    s2 = s[(s.index >= a) & (s.index <= b)]
    return (s2.iloc[-1] / s2.iloc[0] - 1) if len(s2) > 1 else np.nan

cycles = [
    ("2018集采冲击", "2018-05-01", "2019-01-04"),
    ("2019-21医药大牛", "2019-01-04", "2021-07-01"),
    ("2021-24深熊", "2021-07-01", "2024-09-23"),
    ("2024-25出海反转", "2024-09-23", str(lc2.index[-1].date())),
]
print("\n--- 全周期分段收益(159929医药) ---")
cyc_rows = []
for name, a, b in cycles:
    r = seg_ret(lc2, a, b)
    rb = seg_ret(bm, a, b)
    cyc_rows.append({"周期": name, "区间": f"{a[:7]}~{b[:7]}", "医药": r, "沪深300": rb, "超额": r - rb})
    print(f"  {name:16s} {a[:7]}~{b[:7]}  医药{r:+.0%}  沪深300{rb:+.0%}  超额{r-rb:+.0%}")
pd.DataFrame(cyc_rows).to_csv(DATA / "cycle_returns.csv", index=False, encoding="utf-8-sig")

# ════════════════════════════════════════════════════════════════
# 2. 子板块表现 + 当前定位
# ════════════════════════════════════════════════════════════════
print("\n--- 子板块绩效(各自上市以来) + 当前定位 ---")
sub_rows = []
for code, name in UNIVERSE.items():
    c = close[code]
    nav = c / c.iloc[0]
    dd = c / c.rolling(252, min_periods=20).max() - 1
    sub_rows.append({
        "代码": code, "名称": name, "起始": str(c.index[0].date()),
        "年化": annual_return(nav), "最大回撤": max_drawdown(nav), "夏普": sharpe(nav),
        "近1年": c.pct_change(250).iloc[-1] if len(c) > 250 else np.nan,
        "近20日": c.pct_change(20).iloc[-1], "距一年高": dd.iloc[-1],
    })
    print(f"  {code} {name:20s} 年化{sub_rows[-1]['年化']:+.1%} MDD{sub_rows[-1]['最大回撤']:.0%} "
          f"近1年{sub_rows[-1]['近1年']:+.0%} 距高{sub_rows[-1]['距一年高']:+.0%}")
pd.DataFrame(sub_rows).to_csv(DATA / "subsector_metrics.csv", index=False, encoding="utf-8-sig")

# ════════════════════════════════════════════════════════════════
# 3. 创新药 vs 沪深300 滚动相对强弱
# ════════════════════════════════════════════════════════════════
inno = close["159992"]
common2 = inno.index.intersection(bench.index)
ri = inno.reindex(common2).dropna()
rb = bench.reindex(ri.index).dropna()
ri = ri.reindex(rb.index)
rs = (ri / ri.iloc[0]) / (rb / rb.iloc[0])  # 相对强弱(>1=跑赢)

fig, ax = plt.subplots(figsize=(11, 3.6), facecolor="white")
ax.plot(rs.index, rs.values, color=LC["purple"], lw=1.3)
ax.axhline(1, color=LC["muted"], ls=":", lw=1)
ax.fill_between(rs.index, rs.values, 1, where=(rs.values >= 1), color=LC["green"], alpha=0.15)
ax.fill_between(rs.index, rs.values, 1, where=(rs.values < 1), color=LC["red"], alpha=0.15)
ax.set_title("创新药ETF 相对沪深300 强弱 (>1=跑赢)", fontsize=13, color=LC["text"], fontweight="bold")
ax.grid(True, color=LC["grid"], lw=0.6)
for s in ax.spines.values():
    s.set_color(LC["grid"])
ax.tick_params(colors=LC["sub"])
fig.tight_layout()
fig.savefig(FIGS / "fig_innodrug_rs.png", dpi=150, facecolor="white")
plt.close()

# ════════════════════════════════════════════════════════════════
# 4. 子板块动量轮动回测 (月频,持有最强2个) vs 等权 vs 沪深300
# ════════════════════════════════════════════════════════════════
rot_codes = ["159992", "512170", "512290", "512010"]  # 创新药/医疗/生物医药/医药卫生
px = pd.DataFrame({c: close[c] for c in rot_codes}).dropna()
px = px[px.index >= "2020-06-01"]
bench_r = bench.reindex(px.index).ffill()

month_ends = px.resample("ME").last().index
LOOKBACK = 63  # 3月动量
HOLD_N = 2

def run_rotation():
    weights = pd.DataFrame(0.0, index=px.index, columns=rot_codes)
    cur = []
    for i, me in enumerate(month_ends[:-1]):
        hist = px[px.index <= me]
        if len(hist) < LOOKBACK + 1:
            continue
        mom = hist.iloc[-1] / hist.iloc[-1 - LOOKBACK] - 1
        top = mom.sort_values(ascending=False).head(HOLD_N).index.tolist()
        nxt = month_ends[i + 1]
        mask = (weights.index > me) & (weights.index <= nxt)
        for c in top:
            weights.loc[mask, c] = 1.0 / HOLD_N
    ret = px.pct_change().fillna(0)
    strat_ret = (weights.shift(1).fillna(0) * ret).sum(axis=1)
    return (1 + strat_ret).cumprod()

nav_rot = run_rotation()
nav_ew = (1 + px.pct_change().fillna(0).mean(axis=1)).cumprod()
nav_b300 = bench_r / bench_r.iloc[0]
nav_rot = nav_rot / nav_rot.iloc[0]
nav_ew = nav_ew / nav_ew.iloc[0]

fig, ax = plt.subplots(figsize=(11, 4.0), facecolor="white")
ax.plot(nav_rot.index, nav_rot.values, color=LC["red"], lw=1.5, label="动量轮动(持最强2)")
ax.plot(nav_ew.index, nav_ew.values, color=LC["blue"], lw=1.3, label="医药等权")
ax.plot(nav_b300.index, nav_b300.values, color=LC["muted"], lw=1.2, label="沪深300")
ax.set_title("医药子板块动量轮动 vs 等权 vs 沪深300", fontsize=13, color=LC["text"], fontweight="bold")
ax.set_ylabel("净值", color=LC["sub"])
ax.legend(loc="upper left", fontsize=9)
ax.grid(True, color=LC["grid"], lw=0.6)
for s in ax.spines.values():
    s.set_color(LC["grid"])
ax.tick_params(colors=LC["sub"])
fig.tight_layout()
fig.savefig(FIGS / "fig_rotation.png", dpi=150, facecolor="white")
plt.close()

print("\n--- 子板块动量轮动回测 (2020-06起) ---")
rot_metrics = {}
for nm, nav in [("动量轮动", nav_rot), ("医药等权", nav_ew), ("沪深300", nav_b300)]:
    rot_metrics[nm] = {"总收益": float(nav.iloc[-1] - 1), "年化": annual_return(nav),
                       "最大回撤": max_drawdown(nav), "夏普": sharpe(nav), "卡玛": calmar(nav)}
    m = rot_metrics[nm]
    print(f"  {nm:10s} 总{m['总收益']:+.0%} 年化{m['年化']:+.1%} MDD{m['最大回撤']:.0%} "
          f"Sharpe{m['夏普']:.2f} Calmar{m['卡玛']:.2f}")
pd.DataFrame(rot_metrics).T.to_csv(DATA / "rotation_metrics.csv", encoding="utf-8-sig")
pd.DataFrame({"动量轮动": nav_rot, "医药等权": nav_ew, "沪深300": nav_b300}).to_csv(
    DATA / "rotation_nav.csv", encoding="utf-8-sig")

# ════════════════════════════════════════════════════════════════
# 5. 深跌抄底胜率: 长序列医药,按距高点回撤分档,持有1年前向收益
# ════════════════════════════════════════════════════════════════
lc_full = close["159929"]
dd_full = lc_full / lc_full.rolling(252, min_periods=60).max() - 1
fwd252 = lc_full.shift(-252) / lc_full - 1
df5 = pd.DataFrame({"dd": dd_full, "fwd": fwd252}).dropna()

DD_BINS = [(-1.0, -0.40), (-0.40, -0.30), (-0.30, -0.20), (-0.20, -0.10), (-0.10, 0.0)]
DD_LABELS = ["≤-40%", "-40~-30%", "-30~-20%", "-20~-10%", "-10~0%"]
print("\n--- 深跌抄底胜率(159929医药,持有1年) ---")
knife_rows = []
for (lo, hi), lab in zip(DD_BINS, DD_LABELS):
    m = (df5["dd"] > lo) & (df5["dd"] <= hi)
    v = df5.loc[m, "fwd"]
    if len(v) < 20:
        knife_rows.append({"回撤档": lab, "样本": len(v), "胜率": np.nan, "均值": np.nan, "中位": np.nan})
        continue
    knife_rows.append({"回撤档": lab, "样本": int(len(v)), "胜率": float((v > 0).mean()),
                       "均值": float(v.mean()), "中位": float(v.median())})
    r = knife_rows[-1]
    print(f"  {lab:9s} n={r['样本']:4d} 胜率{r['胜率']:.0%} 1年均值{r['均值']:+.0%} 中位{r['中位']:+.0%}")
cur_dd = float(dd_full.iloc[-1])
cur_lab = next((lab for (lo, hi), lab in zip(DD_BINS, DD_LABELS) if lo < cur_dd <= hi), DD_LABELS[-1])
print(f"  >> 当前回撤 {cur_dd:+.0%} (属 {cur_lab} 档)")
pd.DataFrame(knife_rows).to_csv(DATA / "dipbuy_winrate.csv", index=False, encoding="utf-8-sig")

fig, ax = plt.subplots(figsize=(9, 3.8), facecolor="white")
labs = [r["回撤档"] for r in knife_rows if r["胜率"] == r["胜率"]]
wins = [r["胜率"] * 100 for r in knife_rows if r["胜率"] == r["胜率"]]
avgs = [r["均值"] * 100 for r in knife_rows if r["胜率"] == r["胜率"]]
x = np.arange(len(labs))
bars = ax.bar(x, wins, color=[LC["green"] if w >= 60 else (LC["red"] if w < 45 else LC["gold"]) for w in wins])
ax.axhline(50, color=LC["muted"], ls=":", lw=1)
for i, (w, a) in enumerate(zip(wins, avgs)):
    ax.text(i, w + 1.5, f"{w:.0f}%\n均{a:+.0f}%", ha="center", fontsize=9, color=LC["text"])
if cur_lab in labs:
    ci = labs.index(cur_lab)
    ax.text(ci, 6, "当前", ha="center", fontsize=10, color=LC["blue"], fontweight="bold")
ax.set_xticks(x); ax.set_xticklabels(labs, fontsize=10, color=LC["sub"])
ax.set_ylabel("持有1年上涨概率 %", color=LC["sub"])
ax.set_title("医药深跌后抄底胜率(2013至今,持有1年)", fontsize=13, color=LC["text"], fontweight="bold")
ax.grid(True, axis="y", color=LC["grid"], lw=0.6)
for s in ax.spines.values():
    s.set_color(LC["grid"])
ax.tick_params(colors=LC["sub"])
fig.tight_layout()
fig.savefig(FIGS / "fig_dipbuy_winrate.png", dpi=150, facecolor="white")
plt.close()

print(f"\n图表 → {FIGS}")
print(f"数据 → {DATA}")
print("\n首看结论: 见控制台 findings")
