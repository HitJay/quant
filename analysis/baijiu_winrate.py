"""中证酒 (白酒板块) 长线定投胜率量化研究 + 7 页小红书深色卡片
================================================================
主标的:  sz399987  中证酒 (2015-05-19 起, 11 年, 134 月)
ETF 交叉: sh512690  鹏华酒ETF (2019-05 起, 7 年)
基准:    sh000300  沪深 300

方法:
  1. 滚动起点回测: 月末入场, 持有 1/2/3/5 年, 一次性 vs 定投
  2. 当前位置评估: 回撤 / 200日均线 / 12月动量 / 价格历史分位
  3. 条件胜率: 不同回撤深度入场, 后续 1/3/5 年的胜率与中位收益

Usage:
    cd /das/user/QYJI/quant && unset http_proxy https_proxy
    conda run -n research python analysis/baijiu_fetch.py
    conda run -n research python analysis/baijiu_winrate.py
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
ROOT = Path("./output/2026-06-16/baijiu-winrate")
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
TOTAL_CARDS = 7

HORIZONS = [(12, "1年"), (24, "2年"), (36, "3年"), (60, "5年")]

# ════════════════════════════════════════════════════════════════
# 1. 载入数据
# ════════════════════════════════════════════════════════════════
print("=" * 60)
print("中证酒 长线胜率研究 — 计算")
print("=" * 60)

baijiu_d = pd.read_parquet(INDEX_DIR / "sz399987.parquet")["close"].astype(float)
baijiu_d.index = pd.to_datetime(baijiu_d.index)
hs300_d = pd.read_parquet(INDEX_DIR / "sh000300.parquet")["close"].astype(float)
hs300_d.index = pd.to_datetime(hs300_d.index)
etf_d = pd.read_parquet(ETF_DIR / "512690.parquet")["close"].astype(float)
etf_d.index = pd.to_datetime(etf_d.index)

# 基准对齐到中证酒起始
hs300_d = hs300_d[hs300_d.index >= baijiu_d.index[0]]

# 月末序列
baijiu_m = baijiu_d.resample("ME").last().dropna()
hs300_m = hs300_d.resample("ME").last().dropna()

AS_OF = baijiu_d.index[-1].strftime("%Y.%m.%d")
N_MONTH = len(baijiu_m)

print(f"  中证酒 (sz399987): {baijiu_d.index[0].date()} → {baijiu_d.index[-1].date()}, {N_MONTH} 月")
print(f"  沪深300 同期对照: {len(hs300_m)} 月")
print(f"  鹏华酒ETF (512690): {etf_d.index[0].date()} → {etf_d.index[-1].date()}, {len(etf_d)} 日")
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

# ════════════════════════════════════════════════════════════════
# 3. 滚动起点 — 中证酒 vs 沪深300
# ════════════════════════════════════════════════════════════════
print("\n[2] 滚动起点回测 ...")
results = {"白酒": {}, "沪深300": {}}
for name, mser in [("白酒", baijiu_m), ("沪深300", hs300_m)]:
    mv = mser.values.astype(float)
    for method in ("dca", "lump"):
        results[name][method] = {}
        for H, hlab in HORIZONS:
            r = (dca_returns if method == "dca" else lumpsum_returns)(mv, H)
            results[name][method][H] = stats(r)
            print(f"  {name} {method} {hlab}: n={len(r):>4} "
                  f"胜率={stats(r)['win']*100:5.1f}% 中位={stats(r)['med']*100:+6.1f}% "
                  f"亏50%+={stats(r)['loss50']*100:4.1f}%")

# ════════════════════════════════════════════════════════════════
# 4. 当前位置评估
# ════════════════════════════════════════════════════════════════
print("\n[3] 当前位置评估 ...")
peak_d = baijiu_d.expanding().max()
dd_d = baijiu_d / peak_d - 1
ma200 = baijiu_d.rolling(200).mean()
current = {
    "as_of": AS_OF,
    "price": float(baijiu_d.iloc[-1]),
    "peak_price": float(baijiu_d.max()),
    "peak_date": baijiu_d.idxmax().strftime("%Y-%m-%d"),
    "drawdown": float(dd_d.iloc[-1]),
    "days_since_peak": int((baijiu_d.index[-1] - baijiu_d.idxmax()).days),
    "ma200": float(ma200.iloc[-1]),
    "vs_ma200": float(baijiu_d.iloc[-1] / ma200.iloc[-1] - 1),
    "mom_6m": float(baijiu_d.iloc[-1] / baijiu_d.iloc[-126] - 1),
    "mom_12m": float(baijiu_d.iloc[-1] / baijiu_d.iloc[-252] - 1),
    "price_pctile": float((baijiu_d <= baijiu_d.iloc[-1]).mean()),
}
for k, v in current.items():
    print(f"  {k}: {v}")

# ════════════════════════════════════════════════════════════════
# 5. 条件胜率: 不同回撤深度入场后的前瞻收益
# ════════════════════════════════════════════════════════════════
print("\n[4] 条件胜率 (历史不同回撤深度入场) ...")
mv_b = baijiu_m.values.astype(float)
mpeak = pd.Series(mv_b, index=baijiu_m.index).expanding().max().values
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
for thr_label, thr in [("dd30", -0.30), ("dd40", -0.40), ("dd50", -0.50)]:
    cond[thr_label] = {"threshold": thr, "n_obs": int((mdd <= thr).sum())}
    for H, hlab in HORIZONS:
        for method, fn in [("lump", fwd_lump), ("dca", fwd_dca)]:
            f = fn(mv_b, H)
            mask = (mdd <= thr) & ~np.isnan(f)
            sub = f[mask]
            cond[thr_label][f"{method}_{H}m"] = stats(sub)

print(f"  回撤≤-30% 入场: n={cond['dd30']['n_obs']}")
print(f"    5y定投: 胜率={cond['dd30']['dca_60m']['win']*100:.0f}% 中位={cond['dd30']['dca_60m']['med']*100:+.0f}%")
print(f"  回撤≤-50% 入场: n={cond['dd50']['n_obs']}")
print(f"    1y一次性: 胜率={cond['dd50']['lump_12m']['win']*100:.0f}% 中位={cond['dd50']['lump_12m']['med']*100:+.0f}%")

# ════════════════════════════════════════════════════════════════
# 6. 导出 summary.json + CSV
# ════════════════════════════════════════════════════════════════
summary = {
    "as_of": AS_OF,
    "n_months": int(N_MONTH),
    "horizons": [{"months": H, "label": lab} for H, lab in HORIZONS],
    "results": results,
    "current": current,
    "conditional_winrate": cond,
}
(ROOT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n[5] 写出 {ROOT}/summary.json")

rows = []
for name in ("白酒", "沪深300"):
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
for thr_label, thr in [("dd30", -0.30), ("dd40", -0.40), ("dd50", -0.50)]:
    for method, mlab in (("lump", "一次性"), ("dca", "定投")):
        for H, hlab in HORIZONS:
            st = cond[thr_label][f"{method}_{H}m"]
            cond_rows.append({"回撤阈值": f"≤{int(thr*100)}%", "方法": mlab, "持有期": hlab,
                              "n": st["n"], "胜率": st["win"], "中位": st["med"], "p10": st["p10"], "p90": st["p90"]})
pd.DataFrame(cond_rows).to_csv(DATA / "conditional_winrate.csv", index=False, encoding="utf-8-sig")
print(f"     winrate_table.csv + conditional_winrate.csv")


# 便捷取值
def W(name, method, H):  return results[name][method][H]["win"] * 100
def MED(name, method, H): return results[name][method][H]["med"] * 100
def P10(name, method, H): return results[name][method][H]["p10"] * 100
def P90(name, method, H): return results[name][method][H]["p90"] * 100
def L50(name, method, H): return results[name][method][H]["loss50"] * 100


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
    """图1: 1/2/3/5 年胜率, 一次性 vs 定投"""
    labs = [l for _, l in HORIZONS]
    x = np.arange(len(labs)); w = 0.35
    fig, ax = plt.subplots(figsize=(8.4, 4.2))
    dca_v = [W("白酒", "dca", H) for H, _ in HORIZONS]
    lump_v = [W("白酒", "lump", H) for H, _ in HORIZONS]
    ax.bar(x - w/2, dca_v, w, label="定投", color=LC["green"])
    ax.bar(x + w/2, lump_v, w, label="一次性", color=LC["blue"])
    for xi in range(len(labs)):
        ax.text(xi - w/2, dca_v[xi] + 1.5, f"{dca_v[xi]:.0f}", ha="center", fontsize=9.5, color="#333")
        ax.text(xi + w/2, lump_v[xi] + 1.5, f"{lump_v[xi]:.0f}", ha="center", fontsize=9.5, color="#333")
    ax.axhline(50, color=LC["gray"], lw=0.8, ls="--", alpha=0.6)
    ax.set_xticks(x); ax.set_xticklabels(labs, fontsize=11)
    ax.set_ylabel("胜率 (%)", fontsize=11); ax.set_ylim(0, 105)
    ax.set_title("中证酒: 持有不同年限的赚钱概率(胜率)", fontsize=13, color=LC["navy"], fontweight="bold")
    ax.legend(fontsize=10, ncol=2, loc="lower right", frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    save_lightfig(fig, "fig_winrate.png")


def fig_distribution():
    """图2: 5 年收益分布 P10/中位/P90"""
    cats = ["白酒\n定投5年", "白酒\n一次性5年", "沪深300\n定投5年", "沪深300\n一次性5年"]
    keys = [("白酒","dca"), ("白酒","lump"), ("沪深300","dca"), ("沪深300","lump")]
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
    """图3: 历史净值 + 回撤曲线 (双面板)"""
    s = baijiu_d / baijiu_d.iloc[0]  # 归一化净值, 起点=1
    pk = s.expanding().max()
    dd = s / pk - 1
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.6, 5.6), sharex=True,
                                   gridspec_kw={"height_ratios": [2, 1]})
    ax1.plot(s.index, s.values, color=LC["navy"], lw=1.4)
    ax1.fill_between(s.index, s.values, color=LC["navy"], alpha=0.10)
    ax1.set_ylabel("归一化净值 (起点=1)", fontsize=11)
    ax1.set_title("中证酒指数 (sz399987) — 11年净值 + 回撤", fontsize=13, color=LC["navy"], fontweight="bold")
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.grid(alpha=0.25)

    ax2.fill_between(dd.index, dd.values * 100, 0, color=LC["red"], alpha=0.55)
    ax2.plot(dd.index, dd.values * 100, color=LC["red"], lw=0.8)
    ax2.axhline(current["drawdown"] * 100, color=LC["orange"], lw=1.0, ls="--", alpha=0.7)
    ax2.text(s.index[20], current["drawdown"] * 100 - 3,
             f"当前 {current['drawdown']*100:.0f}%", color=LC["orange"], fontsize=9.5, fontweight="bold")
    ax2.set_ylabel("回撤 (%)", fontsize=11)
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.grid(alpha=0.25)
    fig.tight_layout()
    save_lightfig(fig, "fig_drawdown.png")


def fig_conditional():
    """图4: 不同回撤深度入场 → 5 年定投胜率"""
    labels = ["≤-30%", "≤-40%", "≤-50%"]
    keys = ["dd30", "dd40", "dd50"]
    win5 = [cond[k]["dca_60m"]["win"] * 100 if not np.isnan(cond[k]["dca_60m"]["win"]) else 0 for k in keys]
    med5 = [cond[k]["dca_60m"]["med"] * 100 if not np.isnan(cond[k]["dca_60m"]["med"]) else 0 for k in keys]
    n_obs = [cond[k]["n_obs"] for k in keys]
    x = np.arange(len(labels))
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 4.0))
    b1 = axes[0].bar(x, win5, color=[LC["green"], LC["teal"], LC["orange"]])
    for i, (b, v, n) in enumerate(zip(b1, win5, n_obs)):
        axes[0].text(b.get_x() + b.get_width()/2, v + 1.5, f"{v:.0f}%\nn={n}", ha="center", fontsize=10, color="#333")
    axes[0].set_xticks(x); axes[0].set_xticklabels(labels, fontsize=10)
    axes[0].set_ylim(0, 115); axes[0].set_ylabel("5年定投胜率 %")
    axes[0].set_title("不同回撤深度入场 → 5年定投胜率", fontsize=11.5, color=LC["navy"], fontweight="bold")
    axes[0].spines[["top","right"]].set_visible(False)

    b2 = axes[1].bar(x, med5, color=[LC["green"], LC["teal"], LC["orange"]])
    for b, v in zip(b2, med5):
        axes[1].text(b.get_x() + b.get_width()/2, v + 4, f"+{v:.0f}%", ha="center", fontsize=10, color="#333")
    axes[1].set_xticks(x); axes[1].set_xticklabels(labels, fontsize=10)
    axes[1].set_ylabel("5年定投中位收益 %")
    axes[1].set_title("不同回撤深度入场 → 5年中位收益", fontsize=11.5, color=LC["navy"], fontweight="bold")
    axes[1].spines[["top","right"]].set_visible(False)
    fig.tight_layout()
    save_lightfig(fig, "fig_conditional.png")


print("\n[5b] 渲染浅色研报图 ...")
fig_winrate(); print("    fig_winrate.png")
fig_distribution(); print("    fig_distribution.png")
fig_drawdown(); print("    fig_drawdown.png")
fig_conditional(); print("    fig_conditional.png")


# ════════════════════════════════════════════════════════════════
# 7. 小红书深色卡片 (7 张)
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
    days = current["days_since_peak"]
    pctile = current["price_pctile"] * 100

    fig.text(0.5, 0.93, "白 酒 · 量 化 评 估", ha="center", fontsize=14, color=C["gold"], fontweight="bold")
    fig.text(0.5, 0.852, "白酒板块", ha="center", fontsize=36, color=C["text"], fontweight="bold")
    fig.text(0.5, 0.778, "现在能定投吗?", ha="center", fontsize=36, color=C["blue"], fontweight="bold")
    fig.text(0.5, 0.706, "中证酒 11 年, 134 个起点, 滚一遍历史看胜率", ha="center", fontsize=13.5, color=C["muted"])

    # 中央对比面板
    ax = fig.add_axes([0.07, 0.28, 0.86, 0.40]); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.012",
                                fc=C["card"], ec=C["border"], lw=1.5, transform=ax.transAxes))

    # 行 1: 当前位置
    ax.text(0.06, 0.86, "当前位置", ha="left", fontsize=14.5, color=C["text"], fontweight="bold", transform=ax.transAxes)
    ax.text(0.50, 0.78, f"{dd_pct:.0f}%", ha="center", fontsize=42, color=C["red"], fontweight="bold", transform=ax.transAxes)
    ax.text(0.50, 0.66, f"距 2021 高点回撤 · 已 {days//365} 年 {(days%365)//30} 个月", ha="center", fontsize=12, color=C["muted"], transform=ax.transAxes)
    ax.add_line(Line2D([0.04, 0.96], [0.58, 0.58], color=C["border"], lw=1, transform=ax.transAxes))

    # 行 2: 历史在此深度入场后的命运
    w5 = cond["dd30"]["dca_60m"]["win"] * 100
    m5 = cond["dd30"]["dca_60m"]["med"] * 100
    ax.text(0.06, 0.50, "历史回撤 ≥ 30% 时入场 · 定投 5 年", ha="left", fontsize=13, color=C["text"], fontweight="bold", transform=ax.transAxes)
    # 双数字
    ax.text(0.30, 0.27, f"{w5:.0f}%", ha="center", fontsize=44, color=C["green"], fontweight="bold", transform=ax.transAxes)
    ax.text(0.30, 0.13, "赚钱概率", ha="center", fontsize=12, color=C["muted"], transform=ax.transAxes)
    ax.text(0.70, 0.27, f"+{m5:.0f}%", ha="center", fontsize=44, color=C["gold"], fontweight="bold", transform=ax.transAxes)
    ax.text(0.70, 0.13, "中位收益", ha="center", fontsize=12, color=C["muted"], transform=ax.transAxes)

    fig.text(0.5, 0.225, "深熊里入场 · 是历史给最右尾红利的姿势", ha="center", fontsize=14, color=C["gold"], fontweight="bold")
    fig.text(0.5, 0.175, f"数据截止 {AS_OF} · 中证酒(sz399987) · 共 134 个月度起点", ha="center", fontsize=11.5, color=C["text"])
    fig.text(0.5, 0.135, f"价格分位 {pctile:.0f}% · 历史回测 · 全部可复现", ha="center", fontsize=11, color=C["muted"])
    _disc(fig)
    _save(fig, "01_cover.png")

# ── 卡2 实验设计 ──────────────────────────────────────────────────
def card_design():
    fig = _fig()
    _header(fig, "实验设计", "怎么算才公平?")
    rows = [
        (C["blue"], "标的", "中证酒指数 sz399987 (主代理)\n134个月度起点 · 11年历史 · 涵盖2018/2021两轮深熊"),
        (C["green"], "比较项", "每月入场一次, 持有 1/2/3/5 年\n定投(每月固定金额) vs 一次性梭哈"),
        (C["orange"], "基准", "沪深300 同期对照\n看「白酒比宽基好/差多少」"),
        (C["purple"], "前景信号", "回撤幅度 / 200日均线 / 12月动量\n+ 当前回撤深度的历史条件胜率"),
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
    ax.text(0.5, 0.72, "重点: 11 年含两轮历史级深熊", ha="center", fontsize=13.5,
            color=C["gold"], fontweight="bold", transform=ax.transAxes)
    ax.text(0.5, 0.30, "2018年贸易战 -39% · 2021至今 -66% (历史最深)\n回测口径已包含「在历史最高点入场」的最差情形",
            ha="center", va="center", fontsize=11.5, color=C["text"], transform=ax.transAxes)
    _pageno(fig, 2)
    _save(fig, "02_design.png")

# ── 卡3 主胜率 (1/2/3/5 年) ──────────────────────────────────────
def card_winrate():
    fig = _fig()
    _header(fig, "主结论 ①", "持有越久, 胜率越高")
    ax = fig.add_axes([0.10, 0.31, 0.82, 0.46]); _ax_clean(ax)
    labs = [l for _, l in HORIZONS]; x = np.arange(len(labs)); w = 0.35
    dca_v = [W("白酒", "dca", H) for H, _ in HORIZONS]
    lump_v = [W("白酒", "lump", H) for H, _ in HORIZONS]
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

    d3 = W("白酒","dca",36); l3 = W("白酒","lump",36)
    d5 = W("白酒","dca",60); l5 = W("白酒","lump",60)
    fig.text(0.5, 0.18, f"持有 5 年: 一次性 {l5:.0f}% · 定投 {d5:.0f}%",
             ha="center", fontsize=14, color=C["gold"], fontweight="bold")
    fig.text(0.5, 0.135, f"持有 3 年: 一次性 {l3:.0f}% · 定投 {d3:.0f}% · 时间是白酒最稳的朋友",
             ha="center", fontsize=11.5, color=C["muted"])
    _disc(fig); _pageno(fig, 3)
    _save(fig, "03_winrate.png")

# ── 卡4 vs 沪深300 ────────────────────────────────────────────────
def card_vs_hs300():
    fig = _fig()
    _header(fig, "主结论 ②", "白酒 vs 沪深300: 谁更值")
    # 上图: 5 年中位收益 4 组 (白酒定投/一次性, 沪深定投/一次性)
    ax = fig.add_axes([0.10, 0.45, 0.82, 0.32]); _ax_clean(ax)
    cats = ["白酒\n定投", "白酒\n一次性", "沪深300\n定投", "沪深300\n一次性"]
    vals = [MED("白酒","dca",60), MED("白酒","lump",60), MED("沪深300","dca",60), MED("沪深300","lump",60)]
    cols = [C["green"], C["blue"], C["purple"], C["cyan"]]
    bars = ax.bar(cats, vals, color=cols)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width()/2, v + 4, f"+{v:.0f}%", ha="center", fontsize=12.5, color=C["text"], fontweight="bold")
    ax.axhline(0, color=C["muted"], lw=0.7, ls="--")
    ax.tick_params(axis="x", labelsize=11.5)
    ax.set_ylabel("5 年中位收益", color=C["text"], fontsize=12)
    ax.set_ylim(-20, max(vals) * 1.25)
    fig.text(0.5, 0.40, "5 年中位收益: 白酒一次性 +139% 远超 沪深 +3%",
             ha="center", fontsize=12.5, color=C["gold"], fontweight="bold")

    # 下图: 5 年胜率
    ax2 = fig.add_axes([0.10, 0.18, 0.82, 0.16]); _ax_clean(ax2)
    vals2 = [W("白酒","dca",60), W("白酒","lump",60), W("沪深300","dca",60), W("沪深300","lump",60)]
    bars2 = ax2.bar(cats, vals2, color=cols)
    for b, v in zip(bars2, vals2):
        ax2.text(b.get_x() + b.get_width()/2, v + 2, f"{v:.0f}%", ha="center", fontsize=11, color=C["text"])
    ax2.axhline(50, color=C["muted"], lw=0.7, ls="--")
    ax2.tick_params(axis="x", labelsize=10)
    ax2.set_ylim(0, 105); ax2.set_yticks([])
    ax2.set_title("5 年胜率", color=C["text"], fontsize=11.5, loc="left", pad=4)

    fig.text(0.5, 0.13, "白酒高 β 高弹性 · 沪深 300 低波 · 长期白酒占优但要熬",
             ha="center", fontsize=11, color=C["muted"])
    _disc(fig); _pageno(fig, 4)
    _save(fig, "04_vs_hs300.png")

# ── 卡5 收益分布 ──────────────────────────────────────────────────
def card_distribution():
    fig = _fig()
    _header(fig, "主结论 ③", "5 年的「天花板/地板」长啥样")

    ax = fig.add_axes([0.13, 0.40, 0.74, 0.40]); _ax_clean(ax)
    cats = ["定投 5 年", "一次性 5 年"]
    keys = [("白酒","dca"), ("白酒","lump")]
    p10 = [results[g][m][60]["p10"] * 100 for g, m in keys]
    med = [results[g][m][60]["med"] * 100 for g, m in keys]
    p90 = [results[g][m][60]["p90"] * 100 for g, m in keys]
    x = np.arange(len(cats))
    for i in range(len(cats)):
        ax.plot([x[i], x[i]], [p10[i], p90[i]], color=C["muted"], lw=2.2, zorder=1)
        ax.scatter([x[i]], [p10[i]], color=C["red"], s=110, zorder=2)
        ax.scatter([x[i]], [med[i]], color=C["gold"], s=160, zorder=3, marker="D")
        ax.scatter([x[i]], [p90[i]], color=C["green"], s=110, zorder=2)
        ax.text(x[i] + 0.10, p10[i], f"{p10[i]:+.0f}%", fontsize=12, va="center", color=C["red"], fontweight="bold")
        ax.text(x[i] + 0.10, med[i], f"{med[i]:+.0f}%", fontsize=13, va="center", color=C["gold"], fontweight="bold")
        ax.text(x[i] + 0.10, p90[i], f"{p90[i]:+.0f}%", fontsize=12, va="center", color=C["green"], fontweight="bold")
    ax.axhline(0, color=C["muted"], lw=0.7, ls="--")
    ax.set_xticks(x); ax.set_xticklabels(cats, color=C["text"], fontsize=14)
    ax.set_xlim(-0.4, len(cats) - 0.4)
    ax.set_ylabel("5 年总收益 %", color=C["text"], fontsize=12)
    ax.tick_params(axis="y", colors=C["text"], labelsize=10)

    _legend(fig, [("差(P10)", C["red"]), ("中位", C["gold"]), ("好(P90)", C["green"])], y=0.345)

    # 底部 callout: 亏一半概率
    ax2 = fig.add_axes([0.10, 0.14, 0.80, 0.12]); ax2.axis("off")
    ax2.add_patch(FancyBboxPatch((0,0), 1, 1, boxstyle="round,pad=0.02",
                                 fc=C["card"], ec=C["border"], lw=1.3, transform=ax2.transAxes))
    l50_dca = L50("白酒","dca",60); l50_lump = L50("白酒","lump",60)
    ax2.text(0.27, 0.65, "定投 5 年亏一半", ha="center", fontsize=12, color=C["muted"], transform=ax2.transAxes)
    ax2.text(0.27, 0.30, f"{l50_dca:.0f}%", ha="center", fontsize=24, color=C["green"], fontweight="bold", transform=ax2.transAxes)
    ax2.text(0.73, 0.65, "一次性 5 年亏一半", ha="center", fontsize=12, color=C["muted"], transform=ax2.transAxes)
    ax2.text(0.73, 0.30, f"{l50_lump:.0f}%", ha="center", fontsize=24, color=C["red"] if l50_lump>0 else C["green"], fontweight="bold", transform=ax2.transAxes)
    _disc(fig); _pageno(fig, 5)
    _save(fig, "05_distribution.png")

# ── 卡6 前景信号 ──────────────────────────────────────────────────
def card_outlook():
    fig = _fig()
    _header(fig, "前 景 信 号", "现在到底是什么位置?")

    dd = current["drawdown"] * 100
    vs_ma = current["vs_ma200"] * 100
    mom12 = current["mom_12m"] * 100
    pctile = current["price_pctile"] * 100

    # 信号灯逻辑: 
    #   回撤越深越友好(估值低), 但跌破均线/动量为负(趋势仍向下) ⇒ 左侧+底部区域
    rows = [
        ("OK", C["green"], "估值/位置", f"回撤 {dd:.0f}% · 历史价位 {pctile:.0f} 分位",
                            "深度回撤 · 估值已大幅出清"),
        ("注意", C["orange"], "趋势/均线", f"价 {vs_ma:+.0f}% vs 200 日均线",
                            "仍在均线下方 · 没确认右侧反转"),
        ("注意", C["orange"], "近12月动量", f"近 12 月 {mom12:+.0f}%",
                            "动量为负 · 抄底易被套 1-2 年"),
        ("OK", C["green"], "条件胜率", f"史上 ≤-30% 入场 · 5y定投胜率 {cond['dd30']['dca_60m']['win']*100:.0f}%",
                            "深熊入场是历史最有利姿势"),
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
        ax.text(0.13, 0.72, tag, ha="left", fontsize=13, color=col, fontweight="bold", transform=ax.transAxes)
        ax.text(0.13, 0.42, body, ha="left", fontsize=12.5, color=C["text"], transform=ax.transAxes)
        ax.text(0.13, 0.16, note, ha="left", fontsize=11, color=C["muted"], style="italic", transform=ax.transAxes)
        y -= 0.145

    fig.text(0.5, 0.155, "结论: 估值友好 / 趋势未转 → 典型「左侧定投」窗口",
             ha="center", fontsize=12.5, color=C["gold"], fontweight="bold")
    fig.text(0.5, 0.118, "适合分批拉长入场, 不适合一把梭", ha="center", fontsize=11, color=C["muted"])
    _disc(fig); _pageno(fig, 6)
    _save(fig, "06_outlook.png")

# ── 卡7 总结 + 操作建议 ───────────────────────────────────────────
def card_summary():
    fig = _fig()
    _header(fig, "怎 么 操 作", "把胜率翻译成动作")

    # 三个 takeaway 卡
    takeaways = [
        (C["green"], "1", "拉长持有期",
         f"持有 5 年定投胜率 {W('白酒','dca',60):.0f}% / 一次性 {W('白酒','lump',60):.0f}%\n中位 +{MED('白酒','lump',60):.0f}% · 时间是白酒最大的朋友"),
        (C["gold"], "2", "底部区域选定投",
         f"≤-30% 回撤入场, 5y 定投胜率 {cond['dd30']['dca_60m']['win']*100:.0f}%\n但左侧 1-2 年仍可能被套, 别期望立即反弹"),
        (C["blue"], "3", "现在该怎么做",
         "估值友好 + 趋势未转 → 适合「分 24-36 期定投」\n等月线站上 200 日均线再加大金额 (右侧加仓)"),
    ]
    y = 0.78
    for col, num, tag, body in takeaways:
        ax = fig.add_axes([0.08, y - 0.155, 0.84, 0.15]); ax.axis("off")
        ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.015",
                                    fc=C["card"], ec=C["border"], lw=1, transform=ax.transAxes))
        ax.add_patch(FancyBboxPatch((0.0, 0.0), 0.012, 1, boxstyle="square,pad=0",
                                    fc=col, ec="none", transform=ax.transAxes))
        # 数字徽章
        ax.text(0.07, 0.50, num, ha="center", va="center", fontsize=34, color=col, fontweight="bold", transform=ax.transAxes)
        ax.text(0.18, 0.78, tag, ha="left", fontsize=14.5, color=col, fontweight="bold", transform=ax.transAxes)
        ax.text(0.18, 0.36, body, ha="left", va="center", fontsize=12, color=C["text"], transform=ax.transAxes)
        y -= 0.175

    # 风险提示框
    ax = fig.add_axes([0.08, 0.135, 0.84, 0.10]); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.02",
                                fc="#3a1f1f", ec=C["red"], lw=1.5, transform=ax.transAxes))
    ax.text(0.5, 0.72, "风 险 提 示", ha="center", fontsize=13, color=C["red"], fontweight="bold", transform=ax.transAxes)
    ax.text(0.5, 0.30, "11 年样本含 2 轮深熊但样本量有限; 当前 -66% 已是历史最深\n基本面消费场景未确认拐点 · 任何模型都看不见黑天鹅",
            ha="center", va="center", fontsize=10.5, color=C["text"], transform=ax.transAxes)
    _disc(fig); _pageno(fig, 7)
    _save(fig, "07_summary.png")


# ════════════════════════════════════════════════════════════════
# 8. 渲染所有卡片
# ════════════════════════════════════════════════════════════════
print("\n[6] 渲染小红书卡片 ...")
card_cover(); print("    01_cover.png")
card_design(); print("    02_design.png")
card_winrate(); print("    03_winrate.png")
card_vs_hs300(); print("    04_vs_hs300.png")
card_distribution(); print("    05_distribution.png")
card_outlook(); print("    06_outlook.png")
card_summary(); print("    07_summary.png")

print(f"\n✓ 全部完成. 输出目录: {ROOT}")
print(f"  cards/   {len(list(CARDS.glob('*.png')))} 张卡片")
print(f"  data/    {len(list(DATA.glob('*.csv')))} 个 CSV")
