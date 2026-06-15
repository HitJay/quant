"""
定投场外热门基金 vs 场内买股票 — 胜率量化研究 (计算 + 图 + 小红书卡片)
======================================================================
回答: 无脑定投场外热门主动基金, 胜率到底有多高? 真比自己场内买个股强吗?

方法(滚动起点回测, 月末序列, 含分红总收益口径):
  - 一次性:  S[t0+H]/S[t0] - 1
  - 定投:    t0..t0+H-1 每月投1份, t0+H 估值 -> S[t0+H]*mean(1/S[buy]) - 1
  对每个标的、每个起点 t0、持有期 H∈{1,2,3,5}年 计算, 按组(基金/个股)合并统计:
  胜率 / 中位数 / P10 / P90 / 亏损30%+ / 亏损50%+ / 最差。

四组对照: 基金定投 / 基金一次性 / 个股定投 / 个股一次性 ; 外加 沪深300定投 基准。
子实验: "追热门" — 基金近一年涨幅前1/3时入场, 一次性 vs 定投 的3年胜率。

产出: summary.json + data/*.csv + figures/(浅色,PDF用) + cards/(深色,小红书8张)

Usage:
    conda activate research
    python analysis/fund_dca_fetch.py        # 先抓数(幂等)
    python analysis/fund_dca_winrate.py
"""
import sys, json
sys.path.insert(0, "src")
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

FUND_DIR = Path("./data/cache/fund")
STOCK_DIR = Path("./data/cache/stock")
ROOT = Path("./output/2026-06-10/fund-dca-winrate")
CARDS, FIGS, DATA = ROOT / "cards", ROOT / "figures", ROOT / "data"
for d in (CARDS, FIGS, DATA):
    d.mkdir(parents=True, exist_ok=True)

# 小红书深色卡片配色
C = {
    "bg": "#0d1117", "card": "#161b22", "border": "#30363d",
    "text": "#c9d1d9", "muted": "#8b949e", "blue": "#58a6ff",
    "green": "#3fb950", "red": "#f85149", "orange": "#d2991d",
    "purple": "#bc8cff", "gold": "#f0c040", "cyan": "#56d4dd",
}
CARD_W, CARD_H, DPI = 7.2, 9.6, 200
TOTAL_CARDS = 8

HORIZONS = [(12, "1年"), (24, "2年"), (36, "3年"), (60, "5年")]
FUND_BASELINE = "000961"  # 天弘沪深300 -> "沪深300定投"基准, 从基金组里剔除

# ════════════════════════════════════════════════════════════════
# 1. 载入数据
# ════════════════════════════════════════════════════════════════
print("=" * 60)
print("定投胜率研究 — 计算")
print("=" * 60)

meta_path = STOCK_DIR / "_fetch_meta.json"
meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
# 基金名映射(镜像 fetch, 不依赖 meta)
FUND_NAMES = {
    "005827": "易方达蓝筹精选(张坤)", "110011": "易方达优质精选(张坤)",
    "003095": "中欧医疗健康(葛兰)", "161725": "招商中证白酒(LOF)",
    "001102": "前海开源国家比较优势", "320007": "诺安成长(芯片/蔡嵩松)",
    "163406": "兴全合润(谢治宇)", "260108": "景顺长城新兴成长(刘彦春)",
    "161005": "富国天惠成长(朱少醒)", "000083": "汇添富消费行业",
    "040035": "华安逆向策略", "519066": "汇添富蓝筹稳健",
    "162605": "景顺长城鼎益(刘彦春)", "001717": "工银前沿医疗",
    "002001": "华夏回报", "000961": "天弘沪深300(宽基基准)",
}
FUND_NAMES.update(meta.get("fund_names", {}))


def load_month_end(path: Path, col: str) -> pd.Series:
    df = pd.read_parquet(path)
    s = df[col].dropna()
    s.index = pd.to_datetime(s.index)
    return s.resample("ME").last().dropna()


# 直接扫描缓存目录(不依赖 fetch 是否写完 meta)
funds = {}
for p in sorted(FUND_DIR.glob("*.parquet")):
    code = p.stem
    if code == FUND_BASELINE or code not in FUND_NAMES:
        continue
    funds[code] = load_month_end(p, "nav")

baseline = load_month_end(FUND_DIR / f"{FUND_BASELINE}.parquet", "nav")  # 沪深300定投

stocks = {}
for p in sorted(STOCK_DIR.glob("*.parquet")):
    if p.stem.startswith("_"):
        continue
    try:
        stocks[p.stem] = load_month_end(p, "close")
    except Exception:
        continue  # 可能正在写入, 跳过

print(f"  场外热门基金: {len(funds)} 只")
print(f"  场内个股(沪深300成分): {len(stocks)} 只")
print(f"  数据截止: {max(s.index[-1] for s in {**funds, **stocks}.values()).date()}")
AS_OF = max(s.index[-1] for s in {**funds, **stocks}.values()).strftime("%Y.%m.%d")

# ════════════════════════════════════════════════════════════════
# 2. 核心计算: 滚动起点 一次性 / 定投 收益
# ════════════════════════════════════════════════════════════════


def lumpsum_returns(m: np.ndarray, H: int) -> np.ndarray:
    n = len(m)
    if n <= H:
        return np.array([])
    i = np.arange(0, n - H)
    return m[i + H] / m[i] - 1.0


def dca_returns(m: np.ndarray, H: int) -> np.ndarray:
    n = len(m)
    if n <= H:
        return np.array([])
    out = []
    inv_cum = np.cumsum(1.0 / m)  # 前缀和加速 mean(1/buys)
    for i in range(0, n - H):
        # buys = m[i : i+H]; sum(1/buys) = inv_cum[i+H-1] - inv_cum[i-1]
        s = inv_cum[i + H - 1] - (inv_cum[i - 1] if i > 0 else 0.0)
        out.append(m[i + H] * (s / H) - 1.0)
    return np.array(out)


def pool(series_dict: dict, H: int, method: str) -> np.ndarray:
    fn = dca_returns if method == "dca" else lumpsum_returns
    chunks = [fn(s.values.astype(float), H) for s in series_dict.values()]
    chunks = [c for c in chunks if len(c)]
    return np.concatenate(chunks) if chunks else np.array([])


def stats(r: np.ndarray) -> dict:
    if len(r) == 0:
        return {k: np.nan for k in ["n", "win", "med", "mean", "p10", "p90", "loss30", "loss50", "worst"]}
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
    }


print("\n[2] 滚动起点回测 ...")
results = {}  # results[group][method][H] = stats
groups = {"基金": funds, "个股": stocks}
for gname, gdict in groups.items():
    results[gname] = {}
    for method in ("dca", "lump"):
        results[gname][method] = {}
        for H, hlab in HORIZONS:
            r = pool(gdict, H, method)
            results[gname][method][H] = stats(r)
            print(f"  {gname} {method} {hlab}: n={len(r):>6} 胜率={stats(r)['win']*100:5.1f}% "
                  f"中位={stats(r)['med']*100:+6.1f}% 亏50%+={stats(r)['loss50']*100:4.1f}%")

# 沪深300定投基准
base_dca = {H: stats(dca_returns(baseline.values.astype(float), H)) for H, _ in HORIZONS}
base_lump = {H: stats(lumpsum_returns(baseline.values.astype(float), H)) for H, _ in HORIZONS}

# ════════════════════════════════════════════════════════════════
# 3. 子实验: 追热门 (近一年涨幅前1/3时入场)
# ════════════════════════════════════════════════════════════════
print("\n[3] 追热门子实验 (近一年涨幅前1/3入场, 持有3年) ...")
H_CHASE = 36
chase_lump, chase_dca = [], []
all_lump, all_dca = [], []
for s in funds.values():
    m = s.values.astype(float)
    n = len(m)
    if n <= 12 + H_CHASE:
        continue
    trail = np.full(n, np.nan)
    trail[12:] = m[12:] / m[:-12] - 1.0
    valid = np.arange(12, n - H_CHASE)
    if len(valid) < 6:
        continue
    thr = np.nanpercentile(trail[valid], 66.7)  # 该基金自身近一年涨幅前1/3
    inv_cum = np.cumsum(1.0 / m)
    for i in valid:
        lump = m[i + H_CHASE] / m[i] - 1.0
        sbuy = inv_cum[i + H_CHASE - 1] - (inv_cum[i - 1] if i > 0 else 0.0)
        dca = m[i + H_CHASE] * (sbuy / H_CHASE) - 1.0
        all_lump.append(lump); all_dca.append(dca)
        if trail[i] >= thr:
            chase_lump.append(lump); chase_dca.append(dca)

chase = {
    "hot_lump": stats(np.array(chase_lump)),
    "hot_dca": stats(np.array(chase_dca)),
    "all_lump": stats(np.array(all_lump)),
    "all_dca": stats(np.array(all_dca)),
}
print(f"  追高一次性 胜率={chase['hot_lump']['win']*100:.1f}%  追高定投 胜率={chase['hot_dca']['win']*100:.1f}%")
print(f"  任意时点一次性 胜率={chase['all_lump']['win']*100:.1f}%  任意时点定投 胜率={chase['all_dca']['win']*100:.1f}%")

# ════════════════════════════════════════════════════════════════
# 4. 导出 summary.json + CSV
# ════════════════════════════════════════════════════════════════
summary = {
    "as_of": AS_OF,
    "n_funds": len(funds),
    "n_stocks": len(stocks),
    "fund_names": {c: FUND_NAMES.get(c, c) for c in funds},
    "horizons": [{"months": H, "label": lab} for H, lab in HORIZONS],
    "results": results,
    "baseline_dca": base_dca,
    "baseline_lump": base_lump,
    "chase": chase,
}
(ROOT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print("\n[4] 写出 summary.json")

# CSV: 胜率/中位/尾部 按组×方法×持有期
rows = []
for gname in groups:
    for method, mlab in (("dca", "定投"), ("lump", "一次性")):
        for H, hlab in HORIZONS:
            st = results[gname][method][H]
            rows.append({"组": gname, "方法": mlab, "持有期": hlab, "样本数": st["n"],
                         "胜率": st["win"], "中位收益": st["med"], "均值收益": st["mean"],
                         "P10": st["p10"], "P90": st["p90"],
                         "亏30%+概率": st["loss30"], "亏50%+概率": st["loss50"], "最差": st["worst"]})
for method, mlab in (("dca", "定投"), ("lump", "一次性")):
    base = base_dca if method == "dca" else base_lump
    for H, hlab in HORIZONS:
        st = base[H]
        rows.append({"组": "沪深300基准", "方法": mlab, "持有期": hlab, "样本数": st["n"],
                     "胜率": st["win"], "中位收益": st["med"], "均值收益": st["mean"],
                     "P10": st["p10"], "P90": st["p90"],
                     "亏30%+概率": st["loss30"], "亏50%+概率": st["loss50"], "最差": st["worst"]})
pd.DataFrame(rows).to_csv(DATA / "winrate_table.csv", index=False, encoding="utf-8-sig")
pd.DataFrame([
    {"情形": "追高一次性", **chase["hot_lump"]},
    {"情形": "追高定投", **chase["hot_dca"]},
    {"情形": "任意时点一次性", **chase["all_lump"]},
    {"情形": "任意时点定投", **chase["all_dca"]},
]).to_csv(DATA / "chasing.csv", index=False, encoding="utf-8-sig")
print("[4] 写出 data/winrate_table.csv, data/chasing.csv")

# 便捷取值
def W(g, m, H):  # 胜率%
    return results[g][m][H]["win"] * 100
def MED(g, m, H):
    return results[g][m][H]["med"] * 100

# ════════════════════════════════════════════════════════════════
# 5. 浅色图 (PDF 研报用)
# ════════════════════════════════════════════════════════════════
LC = {"navy": "#10243e", "green": "#16a34a", "red": "#dc2626", "orange": "#ea580c",
      "blue": "#2563eb", "gray": "#666", "teal": "#0e7490", "gold": "#b8860b",
      "light": "#eef2f7", "purple": "#7c3aed"}


def save_fig(fig, name):
    fig.savefig(FIGS / name, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def fig_winrate():
    labs = [lab for _, lab in HORIZONS]
    series = [
        ("基金定投", [W("基金", "dca", H) for H, _ in HORIZONS], LC["green"]),
        ("沪深300定投", [base_dca[H]["win"] * 100 for H, _ in HORIZONS], LC["teal"]),
        ("个股定投", [W("个股", "dca", H) for H, _ in HORIZONS], LC["orange"]),
        ("个股一次性", [W("个股", "lump", H) for H, _ in HORIZONS], LC["red"]),
    ]
    x = np.arange(len(labs)); w = 0.2
    fig, ax = plt.subplots(figsize=(8, 4.3))
    for k, (name, vals, col) in enumerate(series):
        off = (k - 1.5) * w
        bars = ax.bar(x + off, vals, w, label=name, color=col)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.8, f"{v:.0f}", ha="center",
                    fontsize=8.5, color="#333")
    ax.axhline(50, color=LC["gray"], lw=0.8, ls="--", alpha=0.6)
    ax.set_xticks(x); ax.set_xticklabels(labs, fontsize=11)
    ax.set_ylabel("胜率 (%)", fontsize=11); ax.set_ylim(0, 105)
    ax.set_title("持有不同年限的赚钱概率(胜率)", fontsize=13, color=LC["navy"], fontweight="bold")
    ax.legend(fontsize=9, ncol=4, loc="lower center", bbox_to_anchor=(0.5, -0.22), frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    save_fig(fig, "fig_winrate.png")


def fig_tailrisk():
    cats = ["基金定投", "基金一次性", "个股定投", "个股一次性"]
    keys = [("基金", "dca"), ("基金", "lump"), ("个股", "dca"), ("个股", "lump")]
    loss50 = [results[g][m][36]["loss50"] * 100 for g, m in keys]
    worst = [results[g][m][36]["worst"] * 100 for g, m in keys]
    cols = [LC["green"], LC["teal"], LC["orange"], LC["red"]]
    fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.9))
    b1 = axes[0].bar(cats, loss50, color=cols)
    for b, v in zip(b1, loss50):
        axes[0].text(b.get_x() + b.get_width() / 2, v + 0.3, f"{v:.1f}%", ha="center", fontsize=9)
    axes[0].set_title("持有3年「亏损过半」概率", fontsize=12, color=LC["navy"], fontweight="bold")
    axes[0].set_ylabel("P(收益<-50%)  %", fontsize=10)
    b2 = axes[1].bar(cats, worst, color=cols)
    for b, v in zip(b2, worst):
        axes[1].text(b.get_x() + b.get_width() / 2, v - 3, f"{v:.0f}%", ha="center", fontsize=9, color="white")
    axes[1].set_title("持有3年「最差情形」", fontsize=12, color=LC["navy"], fontweight="bold")
    axes[1].set_ylabel("最差收益 %", fontsize=10)
    for ax in axes:
        ax.tick_params(axis="x", labelsize=8.5, rotation=12)
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    save_fig(fig, "fig_tailrisk.png")


def fig_dca_vs_lump():
    labs = [lab for _, lab in HORIZONS]
    x = np.arange(len(labs)); w = 0.35
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.8))
    # 左: 胜率
    axes[0].bar(x - w / 2, [W("基金", "dca", H) for H, _ in HORIZONS], w, label="定投", color=LC["green"])
    axes[0].bar(x + w / 2, [W("基金", "lump", H) for H, _ in HORIZONS], w, label="一次性", color=LC["blue"])
    axes[0].set_title("基金: 胜率", fontsize=12, color=LC["navy"], fontweight="bold")
    axes[0].set_ylabel("胜率 %", fontsize=10); axes[0].set_ylim(0, 105)
    # 右: 均值收益
    axes[1].bar(x - w / 2, [results["基金"]["dca"][H]["mean"] * 100 for H, _ in HORIZONS], w, label="定投", color=LC["green"])
    axes[1].bar(x + w / 2, [results["基金"]["lump"][H]["mean"] * 100 for H, _ in HORIZONS], w, label="一次性", color=LC["blue"])
    axes[1].set_title("基金: 平均收益", fontsize=12, color=LC["navy"], fontweight="bold")
    axes[1].set_ylabel("平均收益 %", fontsize=10)
    for ax in axes:
        ax.set_xticks(x); ax.set_xticklabels(labs, fontsize=10)
        ax.legend(fontsize=9, frameon=False)
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    save_fig(fig, "fig_dca_vs_lump.png")


def fig_chasing():
    cats = ["任意时点\n一次性", "追热门高点\n一次性", "任意时点\n定投", "追热门高点\n定投"]
    vals = [chase["all_lump"]["win"] * 100, chase["hot_lump"]["win"] * 100,
            chase["all_dca"]["win"] * 100, chase["hot_dca"]["win"] * 100]
    cols = [LC["blue"], LC["red"], "#86c98e", LC["green"]]
    fig, ax = plt.subplots(figsize=(7.6, 4.0))
    bars = ax.bar(cats, vals, color=cols)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.8, f"{v:.0f}%", ha="center", fontsize=10, fontweight="bold")
    ax.axhline(50, color=LC["gray"], lw=0.8, ls="--", alpha=0.6)
    ax.set_ylabel("3年胜率 %", fontsize=11); ax.set_ylim(0, 105)
    ax.set_title("「追在热门高点」时, 定投能救你多少", fontsize=13, color=LC["navy"], fontweight="bold")
    ax.tick_params(axis="x", labelsize=9.5)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    save_fig(fig, "fig_chasing.png")


def fig_distribution():
    cats = ["基金定投", "个股一次性"]
    keys = [("基金", "dca"), ("个股", "lump")]
    p10 = [results[g][m][36]["p10"] * 100 for g, m in keys]
    med = [results[g][m][36]["med"] * 100 for g, m in keys]
    p90 = [results[g][m][36]["p90"] * 100 for g, m in keys]
    x = np.arange(len(cats))
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    for i in range(len(cats)):
        ax.plot([x[i], x[i]], [p10[i], p90[i]], color=LC["gray"], lw=2, zorder=1)
        ax.scatter([x[i]], [p10[i]], color=LC["red"], s=60, zorder=2, label="P10(差)" if i == 0 else "")
        ax.scatter([x[i]], [med[i]], color=LC["navy"], s=90, zorder=3, marker="D", label="中位数" if i == 0 else "")
        ax.scatter([x[i]], [p90[i]], color=LC["green"], s=60, zorder=2, label="P90(好)" if i == 0 else "")
        ax.text(x[i] + 0.07, p10[i], f"{p10[i]:+.0f}%", fontsize=9, va="center", color=LC["red"])
        ax.text(x[i] + 0.07, med[i], f"{med[i]:+.0f}%", fontsize=9, va="center", color=LC["navy"])
        ax.text(x[i] + 0.07, p90[i], f"{p90[i]:+.0f}%", fontsize=9, va="center", color=LC["green"])
    ax.axhline(0, color=LC["gray"], lw=0.8, ls="--", alpha=0.6)
    ax.set_xticks(x); ax.set_xticklabels(cats, fontsize=11)
    ax.set_ylabel("3年收益分布 %", fontsize=11)
    ax.set_title("持有3年的收益分布(P10 / 中位 / P90)", fontsize=13, color=LC["navy"], fontweight="bold")
    ax.legend(fontsize=9, frameon=False, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    save_fig(fig, "fig_distribution.png")


print("\n[5] 生成研报图 ...")
fig_winrate(); fig_tailrisk(); fig_dca_vs_lump(); fig_chasing(); fig_distribution()
print("    figures/ 完成")

# ════════════════════════════════════════════════════════════════
# 6. 小红书深色卡片 (8 张)
# ════════════════════════════════════════════════════════════════
from matplotlib.lines import Line2D


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
    # items: [(label,color)] 居中药丸图例
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
    f3, s3 = W("基金", "dca", 36), W("个股", "lump", 36)
    sl = results["个股"]["lump"][36]["loss50"] * 100
    fig.text(0.5, 0.93, "量 化 复 盘", ha="center", fontsize=15, color=C["gold"], fontweight="bold")
    fig.text(0.5, 0.852, "定投热门基金", ha="center", fontsize=35, color=C["text"], fontweight="bold")
    fig.text(0.5, 0.778, "真比自己买股票稳?", ha="center", fontsize=35, color=C["blue"], fontweight="bold")
    fig.text(0.5, 0.706, "把「定投明星基金」和「自己买个股」放一起, 滚一遍历史", ha="center", fontsize=14, color=C["muted"])

    # 对比面板: 两行(胜率 / 亏一半概率)
    ax = fig.add_axes([0.07, 0.30, 0.86, 0.36]); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.012",
                                fc=C["card"], ec=C["border"], lw=1.5, transform=ax.transAxes))
    ax.text(0.60, 0.88, "定投基金", ha="center", fontsize=15.5, color=C["green"], fontweight="bold", transform=ax.transAxes)
    ax.text(0.85, 0.88, "自己买个股", ha="center", fontsize=15.5, color=C["orange"], fontweight="bold", transform=ax.transAxes)
    ax.add_line(Line2D([0.04, 0.96], [0.77, 0.77], color=C["border"], lw=1, transform=ax.transAxes))
    # 行1: 赚钱概率
    ax.text(0.07, 0.60, "赚钱概率", ha="left", fontsize=15.5, color=C["text"], fontweight="bold", transform=ax.transAxes)
    ax.text(0.07, 0.50, "持有3年", ha="left", fontsize=11.5, color=C["muted"], transform=ax.transAxes)
    ax.text(0.60, 0.54, f"{f3:.0f}%", ha="center", fontsize=33, color=C["text"], fontweight="bold", transform=ax.transAxes)
    ax.text(0.85, 0.54, f"{s3:.0f}%", ha="center", fontsize=33, color=C["text"], fontweight="bold", transform=ax.transAxes)
    ax.text(0.07, 0.40, "→ 几乎一样", ha="left", fontsize=12.5, color=C["muted"], transform=ax.transAxes)
    ax.add_line(Line2D([0.04, 0.96], [0.35, 0.35], color=C["border"], lw=1, transform=ax.transAxes))
    # 行2: 亏一半概率 (高亮)
    ax.text(0.07, 0.205, "亏一半概率", ha="left", fontsize=15.5, color=C["red"], fontweight="bold", transform=ax.transAxes)
    ax.text(0.07, 0.105, "持有3年", ha="left", fontsize=11.5, color=C["muted"], transform=ax.transAxes)
    ax.text(0.60, 0.15, "≈ 0%", ha="center", fontsize=33, color=C["green"], fontweight="bold", transform=ax.transAxes)
    ax.text(0.85, 0.15, f"{sl:.0f}%", ha="center", fontsize=33, color=C["red"], fontweight="bold", transform=ax.transAxes)

    fig.text(0.5, 0.247, "真正的差距, 不在胜率 —— 而在「翻车率」",
             ha="center", fontsize=15.5, color=C["gold"], fontweight="bold")
    fig.text(0.5, 0.185, f"{summary['n_funds']}只顶流明星基金  ×  沪深300全部 {summary['n_stocks']} 只成分股",
             ha="center", fontsize=13, color=C["text"])
    fig.text(0.5, 0.14, f"数据截止 {AS_OF} · 数据源 AKShare(开源) · 全程可复现", ha="center", fontsize=11.5, color=C["muted"])
    _disc(fig)
    _save(fig, "01_cover.png")


# ── 卡2 实验设计 ──────────────────────────────────────────────────
def card_design():
    fig = _fig()
    _header(fig, "实验设计", "怎么算才公平?")
    rows = [
        (C["blue"], "比什么", "定投(每月固定金额) vs 一次性梭哈;\n场外热门基金 vs 场内个股"),
        (C["green"], "基金池", f"{summary['n_funds']}只散户最爱的明星基金\n张坤/葛兰/刘彦春/谢治宇/朱少醒…用累计净值(含分红)"),
        (C["orange"], "个股池", f"当前沪深300全部 {summary['n_stocks']} 只成分股\n用后复权价(客观池, 不手挑)"),
        (C["purple"], "怎么测", "每个月末都入场一次, 分别持有\n1 / 2 / 3 / 5 年, 统计赚钱概率与亏损分布"),
    ]
    y = 0.79
    for col, tag, body in rows:
        ax = fig.add_axes([0.08, y - 0.118, 0.84, 0.115]); ax.axis("off")
        ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.015",
                                    fc=C["card"], ec=C["border"], lw=1, transform=ax.transAxes))
        ax.add_patch(FancyBboxPatch((0.0, 0.0), 0.012, 1, boxstyle="square,pad=0",
                                    fc=col, ec="none", transform=ax.transAxes))
        _pill(fig, 0.20, y - 0.034, tag, col, fs=13.5)
        ax.text(0.30, 0.5, body, ha="left", va="center", fontsize=13, color=C["text"], transform=ax.transAxes)
        y -= 0.135

    # caveat 强化结论
    ax = fig.add_axes([0.08, 0.135, 0.84, 0.10]); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.02",
                                fc="#2d2410", ec=C["gold"], lw=1.6, transform=ax.transAxes))
    ax.text(0.5, 0.72, "关键: 我们甚至给个股开了「幸存者光环」", ha="center", fontsize=13.5,
            color=C["gold"], fontweight="bold", transform=ax.transAxes)
    ax.text(0.5, 0.30, "用的是今天还活在沪深300里的大白马(都是熬出来的赢家)\n即便如此, 结论依然如下 →",
            ha="center", va="center", fontsize=11.8, color=C["text"], transform=ax.transAxes)
    _pageno(fig, 2)
    _save(fig, "02_design.png")


# ── 卡3 胜率主图 ──────────────────────────────────────────────────
def card_winrate():
    fig = _fig()
    _header(fig, "主结论 ①", "比「胜率」, 基金并没赢个股")
    ax = fig.add_axes([0.10, 0.31, 0.82, 0.45]); _ax_clean(ax)
    labs = [l for _, l in HORIZONS]; x = np.arange(len(labs)); w = 0.26
    fd = [W("基金", "dca", H) for H, _ in HORIZONS]
    sd = [W("个股", "dca", H) for H, _ in HORIZONS]
    sl = [W("个股", "lump", H) for H, _ in HORIZONS]
    ax.bar(x - w, fd, w, color=C["green"])
    ax.bar(x, sd, w, color=C["orange"])
    ax.bar(x + w, sl, w, color=C["red"])
    for xi in range(len(labs)):
        for off, v, col in [(-w, fd[xi], C["green"]), (0, sd[xi], C["orange"]), (w, sl[xi], C["red"])]:
            ax.text(xi + off, v + 2, f"{v:.0f}", ha="center", fontsize=12, color=col, fontweight="bold")
    ax.axhline(50, color=C["muted"], lw=0.9, ls="--")
    ax.text(len(labs) - 0.5, 52, "50%", fontsize=10, color=C["muted"], ha="right")
    ax.set_xticks(x); ax.set_xticklabels(labs, color=C["text"], fontsize=15)
    ax.set_ylim(0, 112); ax.set_yticks([])
    _legend(fig, [("基金定投", C["green"]), ("个股定投", C["orange"]), ("个股一把梭", C["red"])], y=0.245)

    f3, s3 = W("基金", "dca", 36), W("个股", "lump", 36)
    fig.text(0.5, 0.17, f"持有3年: 基金定投 {f3:.0f}%  ≈  个股一把梭 {s3:.0f}%",
             ha="center", fontsize=14.5, color=C["text"], fontweight="bold")
    fig.text(0.5, 0.125, "胜率主要看「拿多久」, 而不是「买基金还是买股」", ha="center", fontsize=12.5, color=C["muted"])
    _disc(fig); _pageno(fig, 3)
    _save(fig, "03_winrate.png")


# ── 卡4 尾部风险 ──────────────────────────────────────────────────
def card_tailrisk():
    fig = _fig()
    _header(fig, "主结论 ②", "真正的差距在「翻车率」", tcolor=C["red"])
    fl = results["基金"]["dca"][36]["loss50"] * 100
    sl = results["个股"]["lump"][36]["loss50"] * 100
    fw = results["基金"]["dca"][36]["worst"] * 100
    sw = results["个股"]["lump"][36]["worst"] * 100

    # 上: 亏损过半概率 对比条
    fig.text(0.08, 0.77, "持有3年「亏损过半(-50%)」的概率", fontsize=14.5, color=C["text"], fontweight="bold")
    ax = fig.add_axes([0.24, 0.55, 0.66, 0.16]); _ax_clean(ax)
    ax.barh([1], [sl], color=C["red"], height=0.5)
    ax.barh([0], [max(fl, 0.4)], color=C["green"], height=0.5)
    ax.text(sl + 0.4, 1, f"{sl:.1f}%", va="center", fontsize=15, color=C["red"], fontweight="bold")
    ax.text(max(fl, 0.4) + 0.4, 0, f"{fl:.1f}%", va="center", fontsize=15, color=C["green"], fontweight="bold")
    ax.set_yticks([0, 1]); ax.set_yticklabels(["基金定投", "个股一把梭"], fontsize=13.5, color=C["text"])
    ax.set_xlim(0, max(sl * 1.35, 5)); ax.set_xticks([])

    # 下: 最差情形
    fig.text(0.08, 0.45, "历史上最惨的一次, 亏成什么样", fontsize=14.5, color=C["text"], fontweight="bold")
    ax2 = fig.add_axes([0.24, 0.255, 0.66, 0.15]); _ax_clean(ax2)
    ax2.barh([1], [sw], color=C["red"], height=0.5)
    ax2.barh([0], [fw], color=C["green"], height=0.5)
    ax2.text(sw * 0.5, 1, f"{sw:.0f}%", va="center", ha="center", fontsize=15, color="white", fontweight="bold")
    ax2.text(fw * 0.5, 0, f"{fw:.0f}%", va="center", ha="center", fontsize=15, color="white", fontweight="bold")
    ax2.set_yticks([0, 1]); ax2.set_yticklabels(["基金定投", "个股一把梭"], fontsize=13.5, color=C["text"])
    ax2.set_xlim(min(sw * 1.12, -5), 0); ax2.set_xticks([])

    fig.text(0.5, 0.16, "分散持仓 ≈ 不会归零;  押注单一个股 = 可能腰斩甚至膝盖斩",
             ha="center", fontsize=12.8, color=C["gold"], fontweight="bold")
    _disc(fig); _pageno(fig, 4)
    _save(fig, "04_tailrisk.png")


# ── 卡5 定投 vs 一次性 (诚实) ─────────────────────────────────────
def card_method():
    fig = _fig()
    _header(fig, "主结论 ③", "定投 vs 梭哈, 各买什么?")
    # 表格: 基金 定投 vs 一次性 (胜率 / 中位 / 均值 / 最差)
    cols = ["", "定投", "一次性"]
    data = [
        ("3年胜率", f"{W('基金','dca',36):.0f}%", f"{W('基金','lump',36):.0f}%"),
        ("平均收益", f"{results['基金']['dca'][36]['mean']*100:+.0f}%", f"{results['基金']['lump'][36]['mean']*100:+.0f}%"),
        ("中位收益", f"{MED('基金','dca',36):+.0f}%", f"{MED('基金','lump',36):+.0f}%"),
        ("最差情形", f"{results['基金']['dca'][36]['worst']*100:.0f}%", f"{results['基金']['lump'][36]['worst']*100:.0f}%"),
    ]
    ax = fig.add_axes([0.10, 0.40, 0.82, 0.36]); ax.axis("off")
    ax.set_xlim(0, 3); ax.set_ylim(0, len(data) + 1)
    # 表头
    for j, c in enumerate(cols):
        col = C["text"] if j == 0 else (C["green"] if j == 1 else C["blue"])
        ax.text(j + 0.5, len(data) + 0.4, c, ha="center", fontsize=15, color=col, fontweight="bold")
    ax.add_line(Line2D([0, 3], [len(data) + 0.0, len(data) + 0.0], color=C["border"], lw=1.2))
    for i, (lab, a, b) in enumerate(data):
        yy = len(data) - i - 0.5
        ax.text(0.5, yy, lab, ha="center", fontsize=13.5, color=C["text"])
        ax.text(1.5, yy, a, ha="center", fontsize=15, color=C["green"], fontweight="bold")
        ax.text(2.5, yy, b, ha="center", fontsize=15, color=C["blue"], fontweight="bold")

    # 诚实结论盒
    ax2 = fig.add_axes([0.08, 0.135, 0.84, 0.22]); ax2.axis("off")
    ax2.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.02",
                                 fc=C["card"], ec=C["border"], lw=1.2, transform=ax2.transAxes))
    ax2.text(0.5, 0.82, "别误会: 定投不是为了「赚最多」", ha="center", fontsize=14.5,
             color=C["gold"], fontweight="bold", transform=ax2.transAxes)
    ax2.text(0.5, 0.5,
             "牛市里, 一次性梭哈的胜率和收益往往都更高(早买早涨);\n"
             "定投真正降的是: 最差情形、回撤与波动。",
             ha="center", va="center", fontsize=12.3, color=C["text"], transform=ax2.transAxes)
    ax2.text(0.5, 0.14, "定投买的是「拿得住 + 不暴雷」, 不是更高收益或胜率",
             ha="center", fontsize=12.8, color=C["green"], fontweight="bold", transform=ax2.transAxes)
    _disc(fig); _pageno(fig, 5)
    _save(fig, "05_method.png")


# ── 卡6 追热门 ────────────────────────────────────────────────────
def card_chasing():
    fig = _fig()
    _header(fig, "主结论 ④", "追在最火的时候买, 最伤胜率")
    fig.text(0.08, 0.79, "把入场时点卡在「基金近一年大涨(前1/3)」时", fontsize=13.5, color=C["muted"])
    ax = fig.add_axes([0.12, 0.37, 0.80, 0.38]); _ax_clean(ax)
    cats = ["任意时点\n一把梭", "追热门\n一把梭", "任意时点\n定投", "追热门\n定投"]
    vals = [chase["all_lump"]["win"] * 100, chase["hot_lump"]["win"] * 100,
            chase["all_dca"]["win"] * 100, chase["hot_dca"]["win"] * 100]
    cols = [C["blue"], C["red"], C["green"], C["orange"]]
    bars = ax.bar(cats, vals, color=cols, width=0.66)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 2, f"{v:.0f}%", ha="center",
                fontsize=14, color="white", fontweight="bold")
    ax.axhline(50, color=C["muted"], lw=0.9, ls="--")
    ax.set_ylim(0, 112); ax.set_yticks([])
    ax.set_xticks(range(len(cats)))
    ax.set_xticklabels(cats, color=C["text"], fontsize=11.5)
    fig.text(0.5, 0.25, f"追在高点, 胜率明显下降: 一把梭 {chase['all_lump']['win']*100:.0f}%→{chase['hot_lump']['win']*100:.0f}%, "
             f"定投 {chase['all_dca']['win']*100:.0f}%→{chase['hot_dca']['win']*100:.0f}%",
             ha="center", fontsize=11.5, color=C["red"], fontweight="bold")
    fig.text(0.5, 0.205, "连定投也救不回追高(强势基金高位后, 往往要消化很久)",
             ha="center", fontsize=12.5, color=C["text"])
    fig.text(0.5, 0.15, "别追热门, 比「用什么方法买」更重要", ha="center", fontsize=13.5, color=C["gold"], fontweight="bold")
    _disc(fig); _pageno(fig, 6)
    _save(fig, "06_chasing.png")


# ── 卡7 实操手册 ──────────────────────────────────────────────────
def card_playbook():
    fig = _fig()
    _header(fig, "实操手册", "定投热门基金的正确姿势")
    items = [
        (C["green"], "1", "宽基打底, 主动增强", "无脑定投沪深300, 胜率不输明星基金、回撤还更小;\n主动基金做卫星仓, 别All in单一爆款"),
        (C["blue"], "2", "定投不为多赚, 为更稳", "高位/看不懂时用定投摊低成本;\n它换的是更浅回撤和拿得住, 不是更高胜率"),
        (C["orange"], "3", "越火越要克制", "近一年涨翻天的爆款, 正是一把梭最危险的时候;\n要买就分批定投"),
        (C["purple"], "4", "拉长持有期", "1年像掷硬币, 3-5年胜率才显著抬升;\n定投最忌3个月就割肉"),
        (C["red"], "5", "止盈比止损重要", "主动基金会风格漂移, 涨多了要分批止盈;\n别让浮盈坐成过山车"),
    ]
    y = 0.785
    for col, num, head, body in items:
        ax = fig.add_axes([0.08, y - 0.115, 0.84, 0.112]); ax.axis("off")
        ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.015",
                                    fc=C["card"], ec=C["border"], lw=1, transform=ax.transAxes))
        ax.add_patch(FancyBboxPatch((0.022, 0.30), 0.055, 0.40, boxstyle="round,pad=0.01",
                                    fc=col, ec="none", transform=ax.transAxes))
        ax.text(0.05, 0.5, num, ha="center", va="center", fontsize=19, color="#0d1117",
                fontweight="bold", transform=ax.transAxes)
        ax.text(0.135, 0.72, head, ha="left", va="center", fontsize=14.5, color=col,
                fontweight="bold", transform=ax.transAxes)
        ax.text(0.135, 0.30, body, ha="left", va="center", fontsize=11.6, color=C["text"], transform=ax.transAxes)
        y -= 0.128
    _disc(fig); _pageno(fig, 7)
    _save(fig, "07_playbook.png")


# ── 卡8 结论 + 关注 ───────────────────────────────────────────────
def card_conclusion():
    fig = _fig()
    _header(fig, "一图总结", "结论")
    f3, s3 = W("基金", "dca", 36), W("个股", "lump", 36)
    sl50 = results["个股"]["lump"][36]["loss50"] * 100
    al, hl = chase["all_lump"]["win"] * 100, chase["hot_lump"]["win"] * 100
    takeaways = [
        (C["green"], f"比胜率: 定投基金 ≈ 买个股(都~{f3:.0f}%)", "「买基金胜率碾压个股」其实是误解"),
        (C["red"], f"比翻车率: 个股一把梭3年亏一半概率 {sl50:.0f}%", "基金/宽基定投 ≈ 0 — 这才是买基金的意义"),
        (C["blue"], "定投不提高胜率, 也不让你多赚", "它降的是回撤和波动, 治的是择时焦虑"),
        (C["gold"], "最该避开的动作: 追热门", f"追高把一把梭胜率从 {al:.0f}% 打到 {hl:.0f}%"),
    ]
    y = 0.78
    for col, head, body in takeaways:
        ax = fig.add_axes([0.08, y - 0.105, 0.84, 0.10]); ax.axis("off")
        ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.015",
                                    fc=C["card"], ec=col, lw=1.5, transform=ax.transAxes))
        ax.text(0.04, 0.5, "✓", ha="center", va="center", fontsize=20, color=col,
                fontweight="bold", transform=ax.transAxes)
        ax.text(0.11, 0.70, head, ha="left", va="center", fontsize=14.5, color=C["text"],
                fontweight="bold", transform=ax.transAxes)
        ax.text(0.11, 0.27, body, ha="left", va="center", fontsize=11.8, color=C["muted"], transform=ax.transAxes)
        y -= 0.122

    ax = fig.add_axes([0.08, 0.10, 0.84, 0.16]); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.02",
                                fc="#13243b", ec=C["blue"], lw=1.6, transform=ax.transAxes))
    ax.text(0.5, 0.70, "完整研报 + 全部数据 + 可复现代码", ha="center", fontsize=14.5,
            color=C["blue"], fontweight="bold", transform=ax.transAxes)
    ax.text(0.5, 0.34, "已整理好 · 点赞收藏关注, 评论区扣「定投」",
            ha="center", fontsize=12.8, color=C["text"], transform=ax.transAxes)
    _disc(fig)
    _save(fig, "08_conclusion.png")


print("\n[6] 生成小红书卡片 ...")
card_cover(); card_design(); card_winrate(); card_tailrisk()
card_method(); card_chasing(); card_playbook(); card_conclusion()
print(f"    cards/ 完成 ({TOTAL_CARDS} 张)")
print("\n全部完成 ->", ROOT)

