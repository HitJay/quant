"""有色金属 (周期之王) 长线胜率 + 周期位置量化研究 + 7 页小红书深色卡片
================================================================
主代理:  801050   申万有色金属指数 (1999-12 起, 26 年, ~319 月)  ★长历史
ETF 交叉: 159866   有色金属ETF (2021-04 起)
基准:    sh000300  沪深 300

方法:
  1. 滚动起点回测: 月末入场, 持有 1/2/3/5 年, 一次性 vs 定投
  2. 当前位置评估: 回撤 / 200日均线 / 12月动量 / 价格历史分位
  3. 条件胜率: 不同回撤深度入场 (≤-30/-40/-50/-60%), 后续 1/3/5 年胜率与中位
  4. 风险对照: 有色 vs 沪深300 的年化波动 / 最大回撤 (强周期的代价)

核心叙事: 有色是「周期之王」—— 强周期、高波动、与全球商品/美元/地产基建挂钩。
          不是躺赢品种, 但深度回撤(周期底部)入场是历史最肥右尾。

Usage:
    cd /home/QYJI/das/quant && unset http_proxy https_proxy
    conda run -n research python analysis/nonferrous_fetch.py
    conda run -n research python analysis/nonferrous_winrate.py
"""
import sys, json
sys.path.insert(0, "src")
from pathlib import Path
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.lines import Line2D
plt.rcParams["font.sans-serif"] = ["Droid Sans Fallback", "WenQuanYi Micro Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# ────────── 路径 / 配色 ──────────
INDEX_DIR = Path("./data/cache/index")
ETF_DIR = Path("./data/cache/etf")
ROOT = Path("./output/2026-06-17/nonferrous-metals")
CARDS, FIGS, DATA = ROOT / "cards", ROOT / "figures", ROOT / "data"
for d in (CARDS, FIGS, DATA):
    d.mkdir(parents=True, exist_ok=True)

C = {
    "bg": "#0d1117", "card": "#161b22", "border": "#30363d",
    "text": "#c9d1d9", "muted": "#8b949e", "blue": "#58a6ff",
    "green": "#3fb950", "red": "#f85149", "orange": "#d2991d",
    "purple": "#bc8cff", "gold": "#f0c040", "cyan": "#56d4dd",
}
CARD_W, CARD_H, DPI = 7.2, 9.6, 200
TOTAL_CARDS = 8
HORIZONS = [(12, "1年"), (24, "2年"), (36, "3年"), (60, "5年")]

# ── 第8页(付费研报引流)配置: 按需修改 ──────────────────────────────
SALE = {
    "price": "9.9",           # 现价
    "price_orig": "39",       # 原价(划线), 留空字符串则不显示
    "channel": "点击本帖下方的个人售卖链接购买",  # 主入口(帖子底部挂的售卖链接)
    "keyword": "有色",        # 私信关键词(备用入口)
    "title": "完整10页·量化深度研报",
}

# ════════════════════════════════════════════════════════════════
# 1. 载入数据
# ════════════════════════════════════════════════════════════════
print("=" * 60)
print("有色金属 长线胜率 + 周期位置研究 — 计算")
print("=" * 60)

nf_d = pd.read_parquet(INDEX_DIR / "sw801050.parquet")["close"].astype(float)
nf_d.index = pd.to_datetime(nf_d.index)
hs300_d = pd.read_parquet(INDEX_DIR / "sh000300.parquet")["close"].astype(float)
hs300_d.index = pd.to_datetime(hs300_d.index)
etf_d = pd.read_parquet(ETF_DIR / "159866.parquet")["close"].astype(float)
etf_d.index = pd.to_datetime(etf_d.index)

# 基准对齐到有色起始 (取二者重叠区间, 沪深300 从 2002 起)
common_start = max(nf_d.index[0], hs300_d.index[0])
hs300_align = hs300_d[hs300_d.index >= common_start]
nf_align = nf_d[nf_d.index >= common_start]

# 月末序列
nf_m = nf_d.resample("ME").last().dropna()
hs300_m = hs300_align.resample("ME").last().dropna()

AS_OF = nf_d.index[-1].strftime("%Y.%m.%d")
N_MONTH = len(nf_m)
N_YEAR = round((nf_d.index[-1] - nf_d.index[0]).days / 365.25, 1)

print(f"  申万有色 (801050): {nf_d.index[0].date()} → {nf_d.index[-1].date()}, {N_MONTH} 月 / {N_YEAR} 年")
print(f"  沪深300 同期对照: {len(hs300_m)} 月 (自 {common_start.date()})")
print(f"  有色金属ETF (159866): {etf_d.index[0].date()} → {etf_d.index[-1].date()}, {len(etf_d)} 日")
print(f"  AS_OF = {AS_OF}")

# ════════════════════════════════════════════════════════════════
# 2. 核心计算函数
# ════════════════════════════════════════════════════════════════
def lumpsum_returns(m, H):
    n = len(m)
    if n <= H: return np.array([])
    i = np.arange(0, n - H)
    return m[i + H] / m[i] - 1.0


def dca_returns(m, H):
    n = len(m)
    if n <= H: return np.array([])
    out = []
    inv_cum = np.cumsum(1.0 / m)
    for i in range(0, n - H):
        s = inv_cum[i + H - 1] - (inv_cum[i - 1] if i > 0 else 0.0)
        out.append(m[i + H] * (s / H) - 1.0)
    return np.array(out)


def stats(r):
    if len(r) == 0:
        return {k: float("nan") for k in ["n","win","med","mean","p10","p90","loss30","loss50","worst","best"]}
    return {
        "n": int(len(r)),
        "win": float((r > 0).mean()),
        "med": float(np.median(r)),
        "mean": float(r.mean()),
        "p10": float(np.percentile(r, 10)),
        "p90": float(np.percentile(r, 90)),
        "loss30": float((r < -0.30).mean()),
        "loss50": float((r < -0.50).mean()),
        "worst": float(r.min()),
        "best": float(r.max()),
    }


def ann_vol(daily_close):
    ret = daily_close.pct_change().dropna()
    return float(ret.std() * np.sqrt(252))


def max_dd(daily_close):
    s = daily_close / daily_close.iloc[0]
    return float((s / s.expanding().max() - 1).min())


def ann_ret(daily_close):
    yrs = (daily_close.index[-1] - daily_close.index[0]).days / 365.25
    return float((daily_close.iloc[-1] / daily_close.iloc[0]) ** (1 / yrs) - 1)


# ════════════════════════════════════════════════════════════════
# 3. 滚动起点 — 有色 vs 沪深300
# ════════════════════════════════════════════════════════════════
print("\n[2] 滚动起点回测 ...")
results = {"有色": {}, "沪深300": {}}
for name, mser in [("有色", nf_m), ("沪深300", hs300_m)]:
    mv = mser.values.astype(float)
    for method in ("dca", "lump"):
        results[name][method] = {}
        for H, hlab in HORIZONS:
            r = (dca_returns if method == "dca" else lumpsum_returns)(mv, H)
            results[name][method][H] = stats(r)
            print(f"  {name} {method} {hlab}: n={len(r):>4} "
                  f"胜率={stats(r)['win']*100:5.1f}% 中位={stats(r)['med']*100:+7.1f}% "
                  f"亏50%+={stats(r)['loss50']*100:4.1f}%")

# ════════════════════════════════════════════════════════════════
# 4. 风险对照 (重叠区间) — 强周期的代价
# ════════════════════════════════════════════════════════════════
print("\n[3] 风险对照 (重叠区间) ...")
risk = {
    "as_of": AS_OF,
    "common_start": common_start.strftime("%Y-%m-%d"),
    "有色": {"ann_ret": ann_ret(nf_align), "ann_vol": ann_vol(nf_align), "max_dd": max_dd(nf_align)},
    "沪深300": {"ann_ret": ann_ret(hs300_align), "ann_vol": ann_vol(hs300_align), "max_dd": max_dd(hs300_align)},
}
for k in ("有色", "沪深300"):
    print(f"  {k}: 年化{risk[k]['ann_ret']*100:+.1f}% 波动{risk[k]['ann_vol']*100:.1f}% 最大回撤{risk[k]['max_dd']*100:.0f}%")

# ════════════════════════════════════════════════════════════════
# 5. 当前位置评估
# ════════════════════════════════════════════════════════════════
print("\n[4] 当前位置评估 ...")
peak_d = nf_d.expanding().max()
dd_d = nf_d / peak_d - 1
ma200 = nf_d.rolling(200).mean()
current = {
    "as_of": AS_OF,
    "price": float(nf_d.iloc[-1]),
    "peak_price": float(nf_d.max()),
    "peak_date": nf_d.idxmax().strftime("%Y-%m-%d"),
    "drawdown": float(dd_d.iloc[-1]),
    "days_since_peak": int((nf_d.index[-1] - nf_d.idxmax()).days),
    "ma200": float(ma200.iloc[-1]),
    "vs_ma200": float(nf_d.iloc[-1] / ma200.iloc[-1] - 1),
    "mom_6m": float(nf_d.iloc[-1] / nf_d.iloc[-126] - 1),
    "mom_12m": float(nf_d.iloc[-1] / nf_d.iloc[-252] - 1),
    "price_pctile": float((nf_d <= nf_d.iloc[-1]).mean()),
}
for k, v in current.items():
    print(f"  {k}: {v}")

# ════════════════════════════════════════════════════════════════
# 6. 条件胜率: 不同回撤深度入场后的前瞻收益
# ════════════════════════════════════════════════════════════════
print("\n[5] 条件胜率 (历史不同回撤深度入场) ...")
mv_b = nf_m.values.astype(float)
mpeak = pd.Series(mv_b, index=nf_m.index).expanding().max().values
mdd = mv_b / mpeak - 1


def fwd_lump(mv, H):
    n = len(mv); out = np.full(n, np.nan)
    for i in range(n - H):
        out[i] = mv[i + H] / mv[i] - 1
    return out


def fwd_dca(mv, H):
    n = len(mv); out = np.full(n, np.nan)
    inv_cum = np.cumsum(1.0 / mv)
    for i in range(n - H):
        s = inv_cum[i + H - 1] - (inv_cum[i - 1] if i > 0 else 0.0)
        out[i] = mv[i + H] * (s / H) - 1.0
    return out


cond = {}
for thr_label, thr in [("dd30", -0.30), ("dd40", -0.40), ("dd50", -0.50), ("dd60", -0.60)]:
    cond[thr_label] = {"threshold": thr, "n_obs": int((mdd <= thr).sum())}
    for H, hlab in HORIZONS:
        for method, fn in [("lump", fwd_lump), ("dca", fwd_dca)]:
            f = fn(mv_b, H)
            mask = (mdd <= thr) & ~np.isnan(f)
            sub = f[mask]
            cond[thr_label][f"{method}_{H}m"] = stats(sub)

for k in ("dd30", "dd50", "dd60"):
    c = cond[k]
    print(f"  回撤≤{int(c['threshold']*100)}% 入场: n={c['n_obs']} | "
          f"5y定投 胜率={c['dca_60m']['win']*100:.0f}% 中位={c['dca_60m']['med']*100:+.0f}%")

# ════════════════════════════════════════════════════════════════
# 6b. 分位条件胜率: 买在历史「高位 vs 低位」(expanding 分位, 无未来函数)
#     直接回答「现在 99 分位高位还能不能追」
# ════════════════════════════════════════════════════════════════
print("\n[5b] 分位条件胜率 (买在不同历史分位) ...")
# 每个月末: 用截至当时的全部历史算价格分位 (expanding rank, 只用过去信息)
nf_pctile = np.full(len(mv_b), np.nan)
for i in range(len(mv_b)):
    nf_pctile[i] = (mv_b[: i + 1] <= mv_b[i]).mean()

pcond = {}
PBUCKETS = [("low", 0.0, 0.30, "低位 ≤30分位"),
            ("mid", 0.30, 0.70, "中位 30-70分位"),
            ("high", 0.70, 0.90, "高位 70-90分位"),
            ("vhigh", 0.90, 1.01, "极高位 ≥90分位")]
for key, lo, hi, lab in PBUCKETS:
    sel = (nf_pctile >= lo) & (nf_pctile < hi)
    pcond[key] = {"label": lab, "lo": lo, "hi": hi, "n_obs": int(sel.sum())}
    for H, hlab in HORIZONS:
        for method, fn in [("lump", fwd_lump), ("dca", fwd_dca)]:
            f = fn(mv_b, H)
            mask = sel & ~np.isnan(f)
            pcond[key][f"{method}_{H}m"] = stats(f[mask])

for key, lo, hi, lab in PBUCKETS:
    p = pcond[key]
    print(f"  {lab}: n={p['n_obs']:>3} | 3y一次性 胜率={p['lump_36m']['win']*100:>3.0f}% 中位={p['lump_36m']['med']*100:+5.0f}% "
          f"| 5y一次性 胜率={p['lump_60m']['win']*100:>3.0f}% 中位={p['lump_60m']['med']*100:+5.0f}%")
cur_pct_bucket = ("vhigh" if current["price_pctile"] >= 0.90 else
                  "high" if current["price_pctile"] >= 0.70 else
                  "mid" if current["price_pctile"] >= 0.30 else "low")
print(f"  → 当前价格分位 {current['price_pctile']*100:.0f}% 落在: {pcond[cur_pct_bucket]['label']}")

# ════════════════════════════════════════════════════════════════
# 7. 导出 summary.json + CSV
# ════════════════════════════════════════════════════════════════
summary = {
    "as_of": AS_OF,
    "n_months": int(N_MONTH),
    "n_years": N_YEAR,
    "horizons": [{"months": H, "label": lab} for H, lab in HORIZONS],
    "results": results,
    "risk": risk,
    "current": current,
    "conditional_winrate": cond,
    "percentile_winrate": pcond,
    "current_pctile_bucket": cur_pct_bucket,
}
(ROOT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n[6] 写出 {ROOT}/summary.json")

rows = []
for name in ("有色", "沪深300"):
    for method, mlab in (("dca", "定投"), ("lump", "一次性")):
        for H, hlab in HORIZONS:
            st = results[name][method][H]
            rows.append({"标的": name, "方法": mlab, "持有期": hlab, "样本数": st["n"],
                         "胜率": st["win"], "中位收益": st["med"], "均值收益": st["mean"],
                         "P10": st["p10"], "P90": st["p90"],
                         "亏30%+概率": st["loss30"], "亏50%+概率": st["loss50"],
                         "最差": st["worst"], "最好": st["best"]})
pd.DataFrame(rows).to_csv(DATA / "winrate_table.csv", index=False, encoding="utf-8-sig")

cond_rows = []
for thr_label, thr in [("dd30", -0.30), ("dd40", -0.40), ("dd50", -0.50), ("dd60", -0.60)]:
    for method, mlab in (("lump", "一次性"), ("dca", "定投")):
        for H, hlab in HORIZONS:
            st = cond[thr_label][f"{method}_{H}m"]
            cond_rows.append({"回撤阈值": f"≤{int(thr*100)}%", "方法": mlab, "持有期": hlab,
                              "n": st["n"], "胜率": st["win"], "中位": st["med"], "p10": st["p10"], "p90": st["p90"]})
pd.DataFrame(cond_rows).to_csv(DATA / "conditional_winrate.csv", index=False, encoding="utf-8-sig")
print(f"     winrate_table.csv + conditional_winrate.csv")

pcond_rows = []
for key, lo, hi, lab in PBUCKETS:
    for method, mlab in (("lump", "一次性"), ("dca", "定投")):
        for H, hlab in HORIZONS:
            st = pcond[key][f"{method}_{H}m"]
            pcond_rows.append({"入场分位": lab, "方法": mlab, "持有期": hlab,
                               "n": st["n"], "胜率": st["win"], "中位": st["med"],
                               "p10": st["p10"], "p90": st["p90"]})
pd.DataFrame(pcond_rows).to_csv(DATA / "percentile_winrate.csv", index=False, encoding="utf-8-sig")
print(f"     percentile_winrate.csv")


# 便捷取值
def W(name, method, H):  return results[name][method][H]["win"] * 100
def MED(name, method, H): return results[name][method][H]["med"] * 100
def P10(name, method, H): return results[name][method][H]["p10"] * 100
def P90(name, method, H): return results[name][method][H]["p90"] * 100
def L50(name, method, H): return results[name][method][H]["loss50"] * 100

# 分位条件取值: PW(bucket, method, H, key)
def PWIN(key, method, H): return pcond[key][f"{method}_{H}m"]["win"] * 100
def PMED(key, method, H): return pcond[key][f"{method}_{H}m"]["med"] * 100


# ════════════════════════════════════════════════════════════════
# 7b. 浅色研报图 (figures/, PDF 用)
# ════════════════════════════════════════════════════════════════
LC = {"navy": "#10243e", "green": "#16a34a", "red": "#dc2626",
      "orange": "#ea580c", "blue": "#2563eb", "gray": "#666",
      "teal": "#0e7490", "gold": "#b8860b", "purple": "#7c3aed",
      "light": "#eef2f7"}


def save_lightfig(fig, name):
    fig.savefig(FIGS / name, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def fig_winrate():
    labs = [l for _, l in HORIZONS]
    x = np.arange(len(labs)); w = 0.35
    fig, ax = plt.subplots(figsize=(8.4, 4.2))
    dca_v = [W("有色", "dca", H) for H, _ in HORIZONS]
    lump_v = [W("有色", "lump", H) for H, _ in HORIZONS]
    ax.bar(x - w/2, dca_v, w, label="定投", color=LC["green"])
    ax.bar(x + w/2, lump_v, w, label="一次性", color=LC["blue"])
    for xi in range(len(labs)):
        ax.text(xi - w/2, dca_v[xi] + 1.5, f"{dca_v[xi]:.0f}", ha="center", fontsize=9.5, color="#333")
        ax.text(xi + w/2, lump_v[xi] + 1.5, f"{lump_v[xi]:.0f}", ha="center", fontsize=9.5, color="#333")
    ax.axhline(50, color=LC["gray"], lw=0.8, ls="--", alpha=0.6)
    ax.set_xticks(x); ax.set_xticklabels(labs, fontsize=11)
    ax.set_ylabel("胜率 (%)", fontsize=11); ax.set_ylim(0, 105)
    ax.set_title("申万有色: 持有不同年限的赚钱概率(胜率)", fontsize=13, color=LC["navy"], fontweight="bold")
    ax.legend(fontsize=10, ncol=2, loc="lower right", frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    save_lightfig(fig, "fig_winrate.png")


def fig_distribution():
    cats = ["有色\n定投5年", "有色\n一次性5年", "沪深300\n定投5年", "沪深300\n一次性5年"]
    keys = [("有色","dca"), ("有色","lump"), ("沪深300","dca"), ("沪深300","lump")]
    p10 = [results[g][m][60]["p10"] * 100 for g, m in keys]
    med = [results[g][m][60]["med"] * 100 for g, m in keys]
    p90 = [results[g][m][60]["p90"] * 100 for g, m in keys]
    x = np.arange(len(cats))
    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    for i in range(len(cats)):
        ax.plot([x[i], x[i]], [p10[i], p90[i]], color=LC["gray"], lw=2, zorder=1)
        ax.scatter([x[i]], [p10[i]], color=LC["red"], s=70, zorder=2, label="P10(差)" if i == 0 else "")
        ax.scatter([x[i]], [med[i]], color=LC["navy"], s=100, zorder=3, marker="D", label="中位数" if i == 0 else "")
        ax.scatter([x[i]], [p90[i]], color=LC["green"], s=70, zorder=2, label="P90(好)" if i == 0 else "")
        ax.text(x[i] + 0.10, p10[i], f"{p10[i]:+.0f}%", fontsize=9, va="center", color=LC["red"])
        ax.text(x[i] + 0.10, med[i], f"{med[i]:+.0f}%", fontsize=9.5, va="center", color=LC["navy"], fontweight="bold")
        ax.text(x[i] + 0.10, p90[i], f"{p90[i]:+.0f}%", fontsize=9, va="center", color=LC["green"])
    ax.axhline(0, color=LC["gray"], lw=0.8, ls="--", alpha=0.6)
    ax.set_xticks(x); ax.set_xticklabels(cats, fontsize=10)
    ax.set_xlim(-0.4, len(cats) - 0.4)
    ax.set_ylabel("5 年总收益 %", fontsize=11)
    ax.set_title("5年收益分布: P10 / 中位 / P90", fontsize=13, color=LC["navy"], fontweight="bold")
    ax.legend(fontsize=9, frameon=False, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    save_lightfig(fig, "fig_distribution.png")


def fig_drawdown():
    s = nf_d / nf_d.iloc[0]
    pk = s.expanding().max()
    dd = s / pk - 1
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.6, 5.6), sharex=True,
                                   gridspec_kw={"height_ratios": [2, 1]})
    ax1.plot(s.index, s.values, color=LC["navy"], lw=1.1)
    ax1.fill_between(s.index, s.values, color=LC["navy"], alpha=0.10)
    ax1.set_yscale("log")
    ax1.set_ylabel("归一化净值 (对数, 起点=1)", fontsize=10.5)
    ax1.set_title(f"申万有色金属指数 (801050) — {N_YEAR:.0f}年净值 + 回撤", fontsize=13, color=LC["navy"], fontweight="bold")
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.grid(alpha=0.25)

    ax2.fill_between(dd.index, dd.values * 100, 0, color=LC["red"], alpha=0.55)
    ax2.plot(dd.index, dd.values * 100, color=LC["red"], lw=0.7)
    ax2.axhline(current["drawdown"] * 100, color=LC["orange"], lw=1.0, ls="--", alpha=0.7)
    ax2.text(s.index[40], current["drawdown"] * 100 - 6,
             f"当前 {current['drawdown']*100:.0f}%", color=LC["orange"], fontsize=9.5, fontweight="bold")
    ax2.set_ylabel("回撤 (%)", fontsize=11)
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.grid(alpha=0.25)
    fig.tight_layout()
    save_lightfig(fig, "fig_drawdown.png")


def fig_conditional():
    labels = ["≤-30%", "≤-40%", "≤-50%", "≤-60%"]
    keys = ["dd30", "dd40", "dd50", "dd60"]
    win5 = [cond[k]["dca_60m"]["win"] * 100 if not np.isnan(cond[k]["dca_60m"]["win"]) else 0 for k in keys]
    med5 = [cond[k]["dca_60m"]["med"] * 100 if not np.isnan(cond[k]["dca_60m"]["med"]) else 0 for k in keys]
    n_obs = [cond[k]["n_obs"] for k in keys]
    x = np.arange(len(labels))
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 4.0))
    palette = [LC["green"], LC["teal"], LC["orange"], LC["purple"]]
    b1 = axes[0].bar(x, win5, color=palette)
    for i, (b, v, n) in enumerate(zip(b1, win5, n_obs)):
        axes[0].text(b.get_x() + b.get_width()/2, v + 1.5, f"{v:.0f}%\nn={n}", ha="center", fontsize=9.5, color="#333")
    axes[0].set_xticks(x); axes[0].set_xticklabels(labels, fontsize=10)
    axes[0].set_ylim(0, 118); axes[0].set_ylabel("5年定投胜率 %")
    axes[0].set_title("不同回撤深度入场 → 5年定投胜率", fontsize=11.5, color=LC["navy"], fontweight="bold")
    axes[0].spines[["top","right"]].set_visible(False)

    b2 = axes[1].bar(x, med5, color=palette)
    for b, v in zip(b2, med5):
        axes[1].text(b.get_x() + b.get_width()/2, v + 4, f"+{v:.0f}%", ha="center", fontsize=9.5, color="#333")
    axes[1].set_xticks(x); axes[1].set_xticklabels(labels, fontsize=10)
    axes[1].set_ylabel("5年定投中位收益 %")
    axes[1].set_title("不同回撤深度入场 → 5年中位收益", fontsize=11.5, color=LC["navy"], fontweight="bold")
    axes[1].spines[["top","right"]].set_visible(False)
    fig.tight_layout()
    save_lightfig(fig, "fig_conditional.png")


def fig_riskreturn():
    """风险-收益: 有色 vs 沪深300 (年化收益/波动/最大回撤)"""
    cats = ["年化收益", "年化波动", "最大回撤"]
    nf_v = [risk["有色"]["ann_ret"]*100, risk["有色"]["ann_vol"]*100, abs(risk["有色"]["max_dd"])*100]
    hs_v = [risk["沪深300"]["ann_ret"]*100, risk["沪深300"]["ann_vol"]*100, abs(risk["沪深300"]["max_dd"])*100]
    x = np.arange(len(cats)); w = 0.35
    fig, ax = plt.subplots(figsize=(8.4, 4.2))
    ax.bar(x - w/2, nf_v, w, label="有色金属", color=LC["orange"])
    ax.bar(x + w/2, hs_v, w, label="沪深300", color=LC["navy"])
    for xi in range(len(cats)):
        ax.text(xi - w/2, nf_v[xi] + 1.5, f"{nf_v[xi]:.0f}", ha="center", fontsize=10, color="#333")
        ax.text(xi + w/2, hs_v[xi] + 1.5, f"{hs_v[xi]:.0f}", ha="center", fontsize=10, color="#333")
    ax.set_xticks(x); ax.set_xticklabels(cats, fontsize=11)
    ax.set_ylabel("%", fontsize=11)
    ax.set_title(f"有色 vs 沪深300: 风险-收益 (自 {risk['common_start'][:4]} 年)", fontsize=12.5, color=LC["navy"], fontweight="bold")
    ax.legend(fontsize=10, ncol=2, loc="upper left", frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    save_lightfig(fig, "fig_riskreturn.png")


def fig_percentile():
    """图: 买在不同历史分位 → 3年/5年一次性前瞻收益 (中位)"""
    keys = ["low", "mid", "high", "vhigh"]
    labels = ["低位\n≤30分位", "中位\n30-70", "高位\n70-90", "极高位\n≥90分位"]
    med3 = [PMED(k, "lump", 36) for k in keys]
    med5 = [PMED(k, "lump", 60) for k in keys]
    x = np.arange(len(keys)); w = 0.36
    fig, ax = plt.subplots(figsize=(8.6, 4.3))
    b1 = ax.bar(x - w/2, med3, w, label="3年", color=LC["teal"])
    b2 = ax.bar(x + w/2, med5, w, label="5年", color=LC["orange"])
    for bs, vs in [(b1, med3), (b2, med5)]:
        for b, v in zip(bs, vs):
            ax.text(b.get_x() + b.get_width()/2, v + (2 if v >= 0 else -6),
                    f"{v:+.0f}%", ha="center", fontsize=9.5,
                    color="#333", va="bottom" if v >= 0 else "top")
    ax.axhline(0, color=LC["gray"], lw=0.9, ls="--", alpha=0.7)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=10.5)
    ax.set_ylabel("一次性买入·前瞻中位收益 %", fontsize=11)
    ax.set_title("买在不同历史分位 → 未来收益 (一次性)", fontsize=13, color=LC["navy"], fontweight="bold")
    ax.legend(fontsize=10, ncol=2, loc="upper right", frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    cur_idx = {"low": 0, "mid": 1, "high": 2, "vhigh": 3}[cur_pct_bucket]
    ax.annotate("当前位置", xy=(cur_idx, med5[cur_idx]), xytext=(cur_idx, max(med5) * 0.6 + 20),
                ha="center", fontsize=10, color=LC["red"], fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=LC["red"], lw=1.4))
    save_lightfig(fig, "fig_percentile.png")


print("\n[6b] 渲染浅色研报图 ...")
fig_winrate(); print("    fig_winrate.png")
fig_distribution(); print("    fig_distribution.png")
fig_drawdown(); print("    fig_drawdown.png")
fig_conditional(); print("    fig_conditional.png")
fig_riskreturn(); print("    fig_riskreturn.png")
fig_percentile(); print("    fig_percentile.png")


# ════════════════════════════════════════════════════════════════
# 8. 小红书深色卡片 (7 张)
# ════════════════════════════════════════════════════════════════
def _fig():
    return plt.figure(figsize=(CARD_W, CARD_H), facecolor=C["bg"])

def _pageno(fig, n):
    fig.text(0.945, 0.045, f"{n}/{TOTAL_CARDS}", ha="right", fontsize=12,
             color=C["muted"], fontfamily="monospace")

def _disc(fig):
    fig.text(0.5, 0.045, "* 历史回测不代表未来 · 不构成投资建议",
             ha="center", fontsize=10.5, color=C["muted"])

def _save(fig, name):
    fig.savefig(CARDS / name, dpi=DPI, facecolor=C["bg"])
    plt.close(fig)

def _header(fig, kicker, title, tcolor=None):
    fig.text(0.08, 0.925, kicker, fontsize=15, color=C["gold"], fontweight="bold")
    fig.text(0.08, 0.862, title, fontsize=24, color=tcolor or C["text"], fontweight="bold")
    fig.add_artist(Line2D([0.08, 0.92], [0.838, 0.838], color=C["border"], lw=1.4))

def _pill(fig, x, y, text, fc, tc="#0d1117", fs=13):
    fig.text(x, y, text, fontsize=fs, color=tc, ha="center", va="center", fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.34", fc=fc, ec="none"))

def _legend(fig, items, y=0.235):
    n = len(items)
    xs = np.linspace(0.5 - 0.16 * (n - 1), 0.5 + 0.16 * (n - 1), n)
    for x, (lab, col) in zip(xs, items):
        _pill(fig, x, y, lab, col, fs=12.5)

def _ax_clean(ax):
    ax.set_facecolor(C["bg"])
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0, colors=C["text"])


# ── 卡1 封面 ──────────────────────────────────────────────────────
def card_cover():
    fig = _fig()
    dd_pct = current["drawdown"] * 100
    pctile = current["price_pctile"] * 100
    mom12 = current["mom_12m"] * 100
    # 当前所处分位桶的历史前瞻 (一次性 5 年)
    win5 = PWIN(cur_pct_bucket, "lump", 60)
    med5 = PMED(cur_pct_bucket, "lump", 60)
    win5_low = PWIN("low", "lump", 60)
    med5_low = PMED("low", "lump", 60)

    fig.text(0.5, 0.93, "有 色 金 属 · 量 化 评 估", ha="center", fontsize=14, color=C["gold"], fontweight="bold")
    fig.text(0.5, 0.852, "有色金属·周期之王", ha="center", fontsize=33, color=C["text"], fontweight="bold")
    fig.text(0.5, 0.778, "现在能追吗?", ha="center", fontsize=36, color=C["orange"], fontweight="bold")
    fig.text(0.5, 0.706, f"申万有色 {N_YEAR:.0f} 年, {N_MONTH} 个起点, 滚一遍历史看胜率", ha="center", fontsize=13.5, color=C["muted"])

    ax = fig.add_axes([0.07, 0.28, 0.86, 0.40]); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.012",
                                fc=C["card"], ec=C["border"], lw=1.5, transform=ax.transAxes))

    # 行1: 当前位置 = 99 分位高位 (不是底部!)
    ax.text(0.06, 0.86, "当前位置", ha="left", fontsize=14.5, color=C["text"], fontweight="bold", transform=ax.transAxes)
    ax.text(0.50, 0.78, f"{pctile:.0f} 分位", ha="center", fontsize=40, color=C["red"], fontweight="bold", transform=ax.transAxes)
    ax.text(0.50, 0.655, f"近 12 月 {mom12:+.0f}% · 距高点仅 {dd_pct:.0f}% · 山顶不是山脚", ha="center", fontsize=11.5, color=C["muted"], transform=ax.transAxes)
    ax.add_line(Line2D([0.04, 0.96], [0.56, 0.56], color=C["border"], lw=1, transform=ax.transAxes))

    # 行2: 历史在这个分位入场的命运 vs 低位
    ax.text(0.06, 0.48, "历史买在 ≥90 分位 (现在) · 一次性持有 5 年", ha="left", fontsize=12.5, color=C["text"], fontweight="bold", transform=ax.transAxes)
    ax.text(0.30, 0.25, f"{win5:.0f}%", ha="center", fontsize=44, color=C["red"], fontweight="bold", transform=ax.transAxes)
    ax.text(0.30, 0.11, "赚钱概率", ha="center", fontsize=12, color=C["muted"], transform=ax.transAxes)
    ax.text(0.70, 0.25, f"{med5:.0f}%", ha="center", fontsize=44, color=C["red"], fontweight="bold", transform=ax.transAxes)
    ax.text(0.70, 0.11, "中位收益", ha="center", fontsize=12, color=C["muted"], transform=ax.transAxes)

    fig.text(0.5, 0.225, f"对比: 买在 ≤30 分位低位, 5 年胜率 {win5_low:.0f}% · 中位 {med5_low:+.0f}%", ha="center", fontsize=12.5, color=C["green"], fontweight="bold")
    fig.text(0.5, 0.178, "周期品的钱在山脚赚, 不在山顶追", ha="center", fontsize=14, color=C["gold"], fontweight="bold")
    fig.text(0.5, 0.135, f"数据截止 {AS_OF} · 申万有色金属(801050) · {N_MONTH} 个月度起点 · 可复现", ha="center", fontsize=11, color=C["text"])
    _disc(fig)
    _save(fig, "01_cover.png")


# ── 卡2 实验设计 ──────────────────────────────────────────────────
def card_design():
    fig = _fig()
    _header(fig, "实验设计", "怎么算才公平?")
    rows = [
        (C["blue"], "标的", f"申万有色金属指数 801050 (主代理)\n{N_MONTH}个月度起点 · {N_YEAR:.0f}年 · A股最长有色序列"),
        (C["green"], "比较项", "每月入场一次, 持有 1/2/3/5 年\n定投(每月固定金额) vs 一次性梭哈"),
        (C["orange"], "基准", "沪深300 同期对照\n比的是「波动的代价 vs 周期的回报」"),
        (C["purple"], "周期信号", "回撤幅度 / 200日均线 / 12月动量 / 价格分位\n+ 不同回撤深度入场的历史条件胜率"),
    ]
    y = 0.79
    for col, tag, body in rows:
        ax = fig.add_axes([0.08, y - 0.118, 0.84, 0.115]); ax.axis("off")
        ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.015",
                                    fc=C["card"], ec=C["border"], lw=1, transform=ax.transAxes))
        ax.add_patch(FancyBboxPatch((0.0, 0.0), 0.012, 1, boxstyle="square,pad=0",
                                    fc=col, ec="none", transform=ax.transAxes))
        _pill(fig, 0.20, y - 0.034, tag, col, fs=13.5)
        ax.text(0.30, 0.5, body, ha="left", va="center", fontsize=12.5, color=C["text"], transform=ax.transAxes)
        y -= 0.135

    ax = fig.add_axes([0.08, 0.135, 0.84, 0.10]); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.02",
                                fc="#2d2410", ec=C["gold"], lw=1.6, transform=ax.transAxes))
    ax.text(0.5, 0.72, f"重点: {N_YEAR:.0f} 年涵盖完整商品周期", ha="center", fontsize=13.5,
            color=C["gold"], fontweight="bold", transform=ax.transAxes)
    ax.text(0.5, 0.30, "2006-07 超级周期 · 2008 金融危机 · 2015 杠杆牛熊\n2021 新能源/铜锂大牛 · 涵盖「在周期顶点入场」的最差情形",
            ha="center", va="center", fontsize=11.0, color=C["text"], transform=ax.transAxes)
    _pageno(fig, 2)
    _save(fig, "02_design.png")


# ── 卡3 主胜率 (1/2/3/5 年) ──────────────────────────────────────
def card_winrate():
    fig = _fig()
    _header(fig, "主结论 ①", "时间能熨平周期吗?")
    ax = fig.add_axes([0.10, 0.31, 0.82, 0.46]); _ax_clean(ax)
    labs = [l for _, l in HORIZONS]; x = np.arange(len(labs)); w = 0.35
    dca_v = [W("有色", "dca", H) for H, _ in HORIZONS]
    lump_v = [W("有色", "lump", H) for H, _ in HORIZONS]
    ax.bar(x - w/2, dca_v, w, color=C["green"], label="定投")
    ax.bar(x + w/2, lump_v, w, color=C["blue"], label="一次性")
    for xi in range(len(labs)):
        ax.text(xi - w/2, dca_v[xi] + 2, f"{dca_v[xi]:.0f}", ha="center", fontsize=13, color=C["green"], fontweight="bold")
        ax.text(xi + w/2, lump_v[xi] + 2, f"{lump_v[xi]:.0f}", ha="center", fontsize=13, color=C["blue"], fontweight="bold")
    ax.axhline(50, color=C["muted"], lw=0.9, ls="--")
    ax.text(len(labs) - 0.5, 52, "50%", fontsize=10, color=C["muted"], ha="right")
    ax.set_xticks(x); ax.set_xticklabels(labs, color=C["text"], fontsize=15)
    ax.set_ylim(0, 105); ax.set_yticks([])
    _legend(fig, [("定投", C["green"]), ("一次性", C["blue"])], y=0.255)

    d5 = W("有色","dca",60); l5 = W("有色","lump",60)
    d1 = W("有色","dca",12); l1 = W("有色","lump",12)
    fig.text(0.5, 0.18, f"持有 5 年: 定投 {d5:.0f}% · 一次性 {l5:.0f}%",
             ha="center", fontsize=14, color=C["gold"], fontweight="bold")
    fig.text(0.5, 0.135, f"持有 1 年: 定投 {d1:.0f}% · 一次性 {l1:.0f}% · 定投全程压制随机择时风险",
             ha="center", fontsize=11.5, color=C["muted"])
    _disc(fig); _pageno(fig, 3)
    _save(fig, "03_winrate.png")


# ── 卡4 vs 沪深300 风险收益 ──────────────────────────────────────
def card_vs_hs300():
    fig = _fig()
    _header(fig, "主结论 ②", "高波动的代价与回报")
    # 上图: 5 年中位收益 4 组
    ax = fig.add_axes([0.10, 0.50, 0.82, 0.27]); _ax_clean(ax)
    cats = ["有色\n定投", "有色\n一次性", "沪深300\n定投", "沪深300\n一次性"]
    vals = [MED("有色","dca",60), MED("有色","lump",60), MED("沪深300","dca",60), MED("沪深300","lump",60)]
    cols = [C["orange"], C["red"], C["purple"], C["cyan"]]
    bars = ax.bar(cats, vals, color=cols)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width()/2, v + (3 if v >= 0 else -8), f"{v:+.0f}%", ha="center", fontsize=12, color=C["text"], fontweight="bold")
    ax.axhline(0, color=C["muted"], lw=0.7, ls="--")
    ax.tick_params(axis="x", labelsize=11)
    ax.set_ylabel("5 年中位收益", color=C["text"], fontsize=11.5)
    ax.set_ylim(min(vals) * 1.3 if min(vals) < 0 else -10, max(vals) * 1.3)

    # 下图: 风险三件套 (年化波动 / 最大回撤)
    ax2 = fig.add_axes([0.10, 0.20, 0.82, 0.20]); _ax_clean(ax2)
    rcats = ["年化波动", "最大回撤"]
    nf_r = [risk["有色"]["ann_vol"]*100, abs(risk["有色"]["max_dd"])*100]
    hs_r = [risk["沪深300"]["ann_vol"]*100, abs(risk["沪深300"]["max_dd"])*100]
    xr = np.arange(len(rcats)); wr = 0.34
    ax2.bar(xr - wr/2, nf_r, wr, color=C["orange"], label="有色")
    ax2.bar(xr + wr/2, hs_r, wr, color=C["purple"], label="沪深300")
    for i in range(len(rcats)):
        ax2.text(xr[i] - wr/2, nf_r[i] + 2, f"{nf_r[i]:.0f}", ha="center", fontsize=11, color=C["orange"], fontweight="bold")
        ax2.text(xr[i] + wr/2, hs_r[i] + 2, f"{hs_r[i]:.0f}", ha="center", fontsize=11, color=C["purple"], fontweight="bold")
    ax2.set_xticks(xr); ax2.set_xticklabels(rcats, color=C["text"], fontsize=12)
    ax2.set_ylim(0, max(nf_r) * 1.3); ax2.set_yticks([])
    ax2.set_title("风险 (%)", color=C["text"], fontsize=11.5, loc="left", pad=4)

    fig.text(0.5, 0.145, f"有色年化波动 {risk['有色']['ann_vol']*100:.0f}% / 最大回撤 {abs(risk['有色']['max_dd'])*100:.0f}% · 远高于宽基",
             ha="center", fontsize=12, color=C["gold"], fontweight="bold")
    fig.text(0.5, 0.105, "高弹性的另一面是巨震 · 想拿这份收益必须扛得住回撤", ha="center", fontsize=10.5, color=C["muted"])
    _disc(fig); _pageno(fig, 4)
    _save(fig, "04_vs_hs300.png")


# ── 卡5 买在高位 vs 低位 (分位条件胜率, 核心卡) ───────────────────
def card_percentile():
    fig = _fig()
    _header(fig, "主结论 ③", "买在山顶 vs 山脚")

    keys = ["low", "mid", "high", "vhigh"]
    labels = ["低位\n≤30分位", "中位\n30-70", "高位\n70-90", "极高位\n≥90"]
    med5 = [PMED(k, "lump", 60) for k in keys]
    win5 = [PWIN(k, "lump", 60) for k in keys]
    cols = [C["green"], C["cyan"], C["orange"], C["red"]]

    # 上图: 5 年一次性中位收益
    ax = fig.add_axes([0.12, 0.47, 0.80, 0.29]); _ax_clean(ax)
    x = np.arange(len(keys))
    bars = ax.bar(x, med5, color=cols)
    for b, v in zip(bars, med5):
        ax.text(b.get_x() + b.get_width()/2, v + (10 if v >= 0 else -9), f"{v:+.0f}%",
                ha="center", fontsize=12.5, color=C["text"] if v >= 0 else C["red"], fontweight="bold",
                va="bottom" if v >= 0 else "top")
    ax.axhline(0, color=C["muted"], lw=0.8, ls="--")
    ax.set_xticks(x); ax.set_xticklabels(labels, color=C["text"], fontsize=12)
    ax.set_ylim(min(med5) * 2.4 if min(med5) < 0 else -20, max(med5) * 1.18)
    ax.set_yticks([])
    ax.set_title("买入后持有 5 年·中位总收益 (一次性)", color=C["text"], fontsize=12, loc="left", pad=6)

    # 当前位置箭头标注
    cur_idx = {"low": 0, "mid": 1, "high": 2, "vhigh": 3}[cur_pct_bucket]
    ax.annotate("现在在这里", xy=(cur_idx, med5[cur_idx] * 0.5),
                xytext=(cur_idx, max(med5) * 0.62),
                ha="center", fontsize=12, color=C["red"], fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C["red"], lw=1.8))

    # 下图: 5 年胜率
    ax2 = fig.add_axes([0.12, 0.20, 0.80, 0.16]); _ax_clean(ax2)
    bars2 = ax2.bar(x, win5, color=cols)
    for b, v in zip(bars2, win5):
        ax2.text(b.get_x() + b.get_width()/2, v + 3, f"{v:.0f}%", ha="center", fontsize=11.5, color=C["text"], fontweight="bold")
    ax2.axhline(50, color=C["muted"], lw=0.7, ls="--")
    ax2.set_xticks(x); ax2.set_xticklabels(labels, color=C["text"], fontsize=10.5)
    ax2.set_ylim(0, 118); ax2.set_yticks([])
    ax2.set_title("5 年赚钱概率 (胜率)", color=C["text"], fontsize=11.5, loc="left", pad=4)

    fig.text(0.5, 0.145, f"极高位(现在)买入: 5年胜率仅 {win5[3]:.0f}% · 中位 {med5[3]:+.0f}%",
             ha="center", fontsize=12.5, color=C["red"], fontweight="bold")
    fig.text(0.5, 0.108, f"低位买入: 5年胜率 {win5[0]:.0f}% · 中位 {med5[0]:+.0f}% · 周期品贵就是贵",
             ha="center", fontsize=11, color=C["muted"])
    _disc(fig); _pageno(fig, 5)
    _save(fig, "05_percentile.png")


# ── 卡6 周期位置 ───────────────────────────────────────────────────
def card_cycle():
    fig = _fig()
    _header(fig, "周 期 位 置", "现在到底是什么位置?")

    dd = current["drawdown"] * 100
    vs_ma = current["vs_ma200"] * 100
    mom12 = current["mom_12m"] * 100
    pctile = current["price_pctile"] * 100
    win5_now = PWIN(cur_pct_bucket, "lump", 60)

    GR = ("好", C["green"]); WN = ("注意", C["orange"]); RD = ("警惕", C["red"])
    s1 = RD if pctile >= 80 else (WN if pctile >= 55 else GR)   # 估值/位置
    s2 = GR if vs_ma >= 0 else WN                                # 趋势
    s3 = RD if mom12 >= 60 else (GR if mom12 >= 0 else WN)       # 动量(过热也是风险)
    s4 = RD if win5_now < 40 else (WN if win5_now < 60 else GR)  # 条件赔率
    rows = [
        (*s1, "估值/位置", f"价格处历史 {pctile:.0f} 分位 · 回撤仅 {dd:.0f}%",
                            "极高位 · 估值已透支, 安全垫薄"),
        (*s2, "趋势/均线", f"价 {vs_ma:+.0f}% vs 200 日均线",
                            "仍在均线上方 · 右侧趋势暂未破"),
        (*s3, "近12月动量", f"近 12 月 {mom12:+.0f}%",
                            "涨幅巨大 · 过热, 易高位剧烈回撤"),
        (*s4, "历史赔率", f"≥90 分位入场 · 5y一次性胜率 {win5_now:.0f}%",
                            "同样位置历史多数 3-5 年不赚钱"),
    ]
    y = 0.78
    for emoji, col, tag, body, note in rows:
        ax = fig.add_axes([0.07, y - 0.13, 0.86, 0.125]); ax.axis("off")
        ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.015",
                                    fc=C["card"], ec=C["border"], lw=1, transform=ax.transAxes))
        ax.add_patch(FancyBboxPatch((0.0, 0.0), 0.012, 1, boxstyle="square,pad=0",
                                    fc=col, ec="none", transform=ax.transAxes))
        ax.text(0.06, 0.50, emoji, ha="left", va="center", fontsize=12, color="#0d1117", fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", fc=col, ec="none"), transform=ax.transAxes)
        ax.text(0.18, 0.72, tag, ha="left", fontsize=13, color=col, fontweight="bold", transform=ax.transAxes)
        ax.text(0.18, 0.42, body, ha="left", fontsize=12.5, color=C["text"], transform=ax.transAxes)
        ax.text(0.18, 0.16, note, ha="left", fontsize=11, color=C["muted"], style="italic", transform=ax.transAxes)
        y -= 0.145

    fig.text(0.5, 0.155, "结论: 趋势还在, 但位置极端 → 追涨不抄底",
             ha="center", fontsize=12.5, color=C["gold"], fontweight="bold")
    fig.text(0.5, 0.118, "周期品看位置不看信仰 · 越接近顶部越要轻", ha="center", fontsize=11, color=C["muted"])
    _disc(fig); _pageno(fig, 6)
    _save(fig, "06_cycle.png")


# ── 卡7 总结 + 操作建议 ───────────────────────────────────────────
def card_summary():
    fig = _fig()
    _header(fig, "怎 么 操 作", "把胜率翻译成动作")

    win5_now = PWIN(cur_pct_bucket, "lump", 60)
    med5_now = PMED(cur_pct_bucket, "lump", 60)
    takeaways = [
        (C["red"], "1", "现在不是抄底位",
         f"价格 99 分位 + 近12月 +90% = 山顶不是山脚\n历史同位置 5 年一次性胜率仅 {win5_now:.0f}% · 中位 {med5_now:+.0f}%"),
        (C["gold"], "2", "已持有: 控仓/止盈",
         "趋势虽在但位置极端 · 设跌破200日线/月线止盈线\n分批兑现利润, 别在山顶满仓等反转"),
        (C["green"], "3", "想上车: 等回到中低位",
         f"≤30 分位低位买入, 5y 中位 {PMED('low','lump',60):+.0f}%\n或等深度回撤(≤-30%)分批定投, 别追高"),
    ]
    y = 0.78
    for col, num, tag, body in takeaways:
        ax = fig.add_axes([0.08, y - 0.155, 0.84, 0.15]); ax.axis("off")
        ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.015",
                                    fc=C["card"], ec=C["border"], lw=1, transform=ax.transAxes))
        ax.add_patch(FancyBboxPatch((0.0, 0.0), 0.012, 1, boxstyle="square,pad=0",
                                    fc=col, ec="none", transform=ax.transAxes))
        ax.text(0.07, 0.50, num, ha="center", va="center", fontsize=34, color=col, fontweight="bold", transform=ax.transAxes)
        ax.text(0.18, 0.78, tag, ha="left", fontsize=14.5, color=col, fontweight="bold", transform=ax.transAxes)
        ax.text(0.18, 0.36, body, ha="left", va="center", fontsize=11.5, color=C["text"], transform=ax.transAxes)
        y -= 0.175

    ax = fig.add_axes([0.08, 0.135, 0.84, 0.10]); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.02",
                                fc="#3a1f1f", ec=C["red"], lw=1.5, transform=ax.transAxes))
    ax.text(0.5, 0.72, "风 险 提 示", ha="center", fontsize=13, color=C["red"], fontweight="bold", transform=ax.transAxes)
    ax.text(0.5, 0.30, "有色是强周期品, 与全球商品/美元/地产基建高度绑定 · 波动巨大\n趋势可能再创新高(动量), 也可能高位崩跌; 本文只讲历史赔率, 不预测点位",
            ha="center", va="center", fontsize=10.0, color=C["text"], transform=ax.transAxes)
    _disc(fig); _pageno(fig, 7)
    _save(fig, "07_summary.png")


# ── 卡8 付费研报引流 (CTA) ────────────────────────────────────────
def card_cta():
    fig = _fig()
    win5_now = PWIN(cur_pct_bucket, "lump", 60)
    med5_low = PMED("low", "lump", 60)

    # 顶部
    fig.text(0.5, 0.928, "完 整 版 · 付 费 研 报", ha="center", fontsize=15, color=C["gold"], fontweight="bold")
    fig.text(0.5, 0.862, SALE["title"], ha="center", fontsize=27, color=C["text"], fontweight="bold")
    fig.add_artist(Line2D([0.08, 0.92], [0.836, 0.836], color=C["border"], lw=1.4))

    # 钩子: 卡片只讲了结论, 完整数据/方法/操作在研报里
    fig.text(0.5, 0.795, "卡片只是结论 · 完整数据、方法与操作框架在研报里",
             ha="center", fontsize=12.5, color=C["muted"])

    # 「研报内含」清单框
    ax = fig.add_axes([0.08, 0.45, 0.84, 0.30]); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.012",
                                fc=C["card"], ec=C["border"], lw=1.5, transform=ax.transAxes))
    ax.text(0.5, 0.90, "10 页 · 8 大章节 · 全程可复现", ha="center", fontsize=13.5,
            color=C["gold"], fontweight="bold", transform=ax.transAxes)
    items = [
        ("四档分位完整胜率表", "低位→极高位 × 3/5年, 看清你买在哪一档"),
        ("风险-收益对照", "26年波动/最大回撤/P10尾部 vs 沪深300"),
        ("当前位置 4 信号解读", "估值/趋势/动量/赔率 逐条拆解"),
        ("分位×仓位操作框架", "什么位置定投/持有/止盈, 一表给齐"),
        ("方法与局限说明", "扩张分位口径·无未来函数·诚实边界"),
    ]
    y = 0.74
    for tag, desc in items:
        ax.text(0.055, y, "✓", ha="left", va="center", fontsize=13, color=C["green"], fontweight="bold", transform=ax.transAxes)
        ax.text(0.12, y, tag, ha="left", va="center", fontsize=12.5, color=C["text"], fontweight="bold", transform=ax.transAxes)
        ax.text(0.12, y - 0.072, desc, ha="left", va="center", fontsize=10.3, color=C["muted"], transform=ax.transAxes)
        y -= 0.165

    # 价格 + 购买入口 (帖子底部挂的个人售卖链接, 无二维码/无商店)
    ax2 = fig.add_axes([0.08, 0.165, 0.84, 0.255]); ax2.axis("off")
    ax2.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.012",
                                 fc="#1c1708", ec=C["gold"], lw=1.8, transform=ax2.transAxes))

    # 价格(用「元」, DroidSansFallback 无 ¥ 字形会变豆腐块)
    ax2.text(0.5, 0.80, f"限时 {SALE['price']}元", ha="center", va="center", fontsize=31,
             color=C["gold"], fontweight="bold", transform=ax2.transAxes)
    if SALE["price_orig"]:
        ax2.text(0.685, 0.80, f"原价 {SALE['price_orig']}元", ha="left", va="center", fontsize=12,
                 color=C["muted"], transform=ax2.transAxes)
        ax2.add_line(Line2D([0.685, 0.83], [0.80, 0.80], color=C["muted"], lw=1.1, transform=ax2.transAxes))
    # 主入口: 帖子底部售卖链接
    ax2.text(0.5, 0.50, SALE["channel"], ha="center", va="center", fontsize=14, color=C["text"], fontweight="bold", transform=ax2.transAxes)
    ax2.text(0.5, 0.30, "（就在这条笔记最下方 ↓ 蓝色链接）", ha="center", va="center", fontsize=11, color=C["gold"], transform=ax2.transAxes)
    # 备用入口: 关注+私信, 手动发送
    ax2.text(0.5, 0.11, f"或 关注后私信「{SALE['keyword']}」· 看到后手动发你", ha="center", va="center", fontsize=10.8, color=C["muted"], transform=ax2.transAxes)

    # 一句价值钩子
    fig.text(0.5, 0.118, f"现在 99 分位高位, 历史同位置 5 年胜率仅 {win5_now:.0f}% — 别让一张图替你做决定",
             ha="center", fontsize=11, color=C["gold"], fontweight="bold")
    fig.text(0.5, 0.085, "数据源开源 · 方法可复现 · 作者：靳秋野 · 量化研究笔记", ha="center", fontsize=10, color=C["muted"])
    fig.text(0.5, 0.045, "* 知识付费内容 · 历史回测不代表未来 · 不构成投资建议", ha="center", fontsize=10, color=C["muted"])
    _pageno(fig, 8)
    _save(fig, "08_cta.png")


# ════════════════════════════════════════════════════════════════
# 9. 渲染所有卡片
# ════════════════════════════════════════════════════════════════
print("\n[7] 渲染小红书卡片 ...")
card_cover(); print("    01_cover.png")
card_design(); print("    02_design.png")
card_winrate(); print("    03_winrate.png")
card_vs_hs300(); print("    04_vs_hs300.png")
card_percentile(); print("    05_percentile.png")
card_cycle(); print("    06_cycle.png")
card_summary(); print("    07_summary.png")
card_cta(); print("    08_cta.png")

print(f"\n✓ 全部完成. 输出目录: {ROOT}")
print(f"  cards/   {len(list(CARDS.glob('*.png')))} 张卡片")
print(f"  figures/ {len(list(FIGS.glob('*.png')))} 张研报图")
print(f"  data/    {len(list(DATA.glob('*.csv')))} 个 CSV")
fig_riskreturn(); print("    fig_riskreturn.png")
