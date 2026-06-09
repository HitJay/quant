"""
科技股大跌，能抄底吗？— 量化抄底胜率研究 + 小红书卡片(7张)
================================================================
2026年6月，美股(纳指)与A股科技(科创50/芯片/创业板)集体大跌。
本脚本用历史日线数据量化"回调后抄底"的胜率、接飞刀风险与策略表现。

主角:
    美股科技 → 纳指ETF(513100, QDII, A股可买)
    A股科技 → 科创50ETF(588000) / 芯片ETF(159995) / 创业板50(159949)

产出:
    cards/      7张小红书卡片(暗色)
    figures/    研报用图表(浅色)
    data/       条件胜率/接飞刀/策略指标/净值 CSV
    summary.json 关键数字(供研报PDF复用)

Usage:
    conda activate research
    python analysis/tech_dip_analysis.py
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

# ════════════════════════════════════════════════════════════════
# 配置
# ════════════════════════════════════════════════════════════════
C = {
    "bg": "#0d1117", "card": "#161b22", "border": "#30363d",
    "text": "#c9d1d9", "muted": "#8b949e", "blue": "#58a6ff",
    "green": "#3fb950", "red": "#f85149", "orange": "#d2991d",
    "purple": "#bc8cff", "gold": "#f0c040", "cyan": "#56d4dd",
}
CARD_W, CARD_H, DPI = 7.2, 9.6, 200  # 1440x1920 高清(小红书手机端)
TOTAL_CARDS = 7
DATE_DIR = "2026-06-08"
ROOT = Path(f"./output/{DATE_DIR}/tech-dip-buy")
CARDS = ROOT / "cards"
FIGS = ROOT / "figures"
DATA = ROOT / "data"
for d in (CARDS, FIGS, DATA):
    d.mkdir(parents=True, exist_ok=True)

ASSETS = {
    "513100": "纳指ETF",
    "588000": "科创50ETF",
    "159995": "芯片ETF",
    "159949": "创业板50",
}
# 双主角
US_TECH = "513100"   # 美股科技代表
A_TECH = "588000"    # A股科技代表

# 抄底回撤档位(距近一年高点)
DD_BINS = [(-1.00, -0.30), (-0.30, -0.20), (-0.20, -0.15),
           (-0.15, -0.10), (-0.10, -0.05), (-0.05, 0.0)]
DD_LABELS = ["≤-30%", "-30~-20%", "-20~-15%", "-15~-10%", "-10~-5%", "-5~0%"]
HORIZONS = [20, 60, 120]  # 交易日: ~1/3/6月


def _fig():
    return plt.figure(figsize=(CARD_W, CARD_H), facecolor=C["bg"])


def _page_number(fig, n):
    fig.text(0.94, 0.052, f"{n}/{TOTAL_CARDS}", ha="right", fontsize=12,
             color=C["muted"], fontfamily="monospace")


def _disclaimer(fig):
    fig.text(0.5, 0.052, "* 历史回测不代表未来 · 不构成投资建议",
             ha="center", fontsize=11, color=C["muted"])


# ════════════════════════════════════════════════════════════════
# 1. 数据与特征
# ════════════════════════════════════════════════════════════════
print("=" * 64)
print("科技抄底量化研究")
print("=" * 64)

cache = Cache("./data/cache")
data = {}
for code, name in ASSETS.items():
    df = cache.load("etf", code)
    if df is None:
        print(f"  !! {code} {name} 无缓存, 跳过")
        continue
    close = df["close"].dropna()
    data[code] = close
    print(f"  {code} {name}: {close.index[0].date()}~{close.index[-1].date()} n={len(close)}")

END_DATE = max(s.index[-1] for s in data.values())
END_STR = END_DATE.strftime("%Y.%m.%d")


def build_features(close: pd.Series) -> pd.DataFrame:
    f = pd.DataFrame({"close": close})
    for w in [5, 10, 20, 60, 120, 250]:
        f[f"ret{w}"] = close.pct_change(w)
        f[f"ma{w}"] = close.rolling(w).mean()
    f["dist_ma20"] = close / f["ma20"] - 1
    f["dist_ma60"] = close / f["ma60"] - 1
    f["dist_ma250"] = close / f["ma250"] - 1
    f["roll_high"] = close.rolling(252, min_periods=20).max()
    f["dd"] = close / f["roll_high"] - 1            # 距一年高点
    # RSI(14)
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    f["rsi"] = 100 - 100 / (1 + rs)
    # 未来收益
    for h in HORIZONS:
        f[f"fwd{h}"] = close.shift(-h) / close - 1
        # 未来H日内最大浮亏(接飞刀风险, MAE)
        fwd_min = close.shift(-1).rolling(h, min_periods=1).min().shift(-(h - 1))
        f[f"mae{h}"] = fwd_min / close - 1
    return f


feat = {code: build_features(s) for code, s in data.items()}
state = {}
for code, f in feat.items():
    last = f.iloc[-1]
    state[code] = {
        "name": ASSETS[code], "close": float(last["close"]),
        "ret5": float(last["ret5"]), "ret10": float(last["ret10"]),
        "ret20": float(last["ret20"]), "ret60": float(last["ret60"]),
        "ret250": float(last["ret250"]),
        "dist_ma20": float(last["dist_ma20"]), "dist_ma60": float(last["dist_ma60"]),
        "dist_ma250": float(last["dist_ma250"]),
        "dd": float(last["dd"]), "rsi": float(last["rsi"]),
    }
    print(f"\n[{code} {ASSETS[code]}] 收{last['close']:.3f} "
          f"5日{last['ret5']:+.1%} 10日{last['ret10']:+.1%} 20日{last['ret20']:+.1%} "
          f"距一年高{last['dd']:+.1%} RSI{last['rsi']:.0f}")


def dd_bin_label(dd: float) -> str:
    for (lo, hi), lab in zip(DD_BINS, DD_LABELS):
        if lo < dd <= hi:
            return lab
    return DD_LABELS[0] if dd <= -0.30 else DD_LABELS[-1]


# ════════════════════════════════════════════════════════════════
# 2. 条件胜率: 不同回撤档位买入, 持有H日
# ════════════════════════════════════════════════════════════════
def winrate_by_dd(f: pd.DataFrame, horizon: int) -> pd.DataFrame:
    rows = []
    for (lo, hi), lab in zip(DD_BINS, DD_LABELS):
        mask = (f["dd"] > lo) & (f["dd"] <= hi)
        vals = f.loc[mask, f"fwd{horizon}"].dropna()
        if len(vals) < 5:
            rows.append({"档位": lab, "样本": len(vals), "胜率": np.nan,
                         "均值": np.nan, "中位数": np.nan, "盈亏比": np.nan})
            continue
        wins, losses = vals[vals > 0], vals[vals <= 0]
        aw = wins.mean() if len(wins) else 0
        al = losses.mean() if len(losses) else 0
        rr = aw / abs(al) if (len(losses) and al != 0) else np.nan
        rows.append({
            "档位": lab, "样本": int(len(vals)),
            "胜率": float((vals > 0).mean()), "均值": float(vals.mean()),
            "中位数": float(vals.median()), "盈亏比": float(rr) if rr == rr else np.nan,
        })
    return pd.DataFrame(rows)


winrate_tables = {}  # code -> {horizon -> df}
for code in [US_TECH, A_TECH]:
    winrate_tables[code] = {h: winrate_by_dd(feat[code], h) for h in HORIZONS}

print("\n--- 抄底条件胜率(持有60交易日) ---")
for code in [US_TECH, A_TECH]:
    print(f"\n{ASSETS[code]}:")
    print(winrate_tables[code][60].to_string(index=False))

# 当前档位 + 对应胜率(60日)
cur_dip = {}
for code in [US_TECH, A_TECH]:
    dd = state[code]["dd"]
    lab = dd_bin_label(dd)
    row = winrate_tables[code][60]
    r = row[row["档位"] == lab]
    cur_dip[code] = {
        "label": lab,
        "win60": float(r["胜率"].iloc[0]) if len(r) and r["胜率"].iloc[0] == r["胜率"].iloc[0] else np.nan,
        "avg60": float(r["均值"].iloc[0]) if len(r) and r["均值"].iloc[0] == r["均值"].iloc[0] else np.nan,
        "n60": int(r["样本"].iloc[0]) if len(r) else 0,
    }
    print(f"\n{ASSETS[code]} 当前档位 {lab}: 60日胜率 {cur_dip[code]['win60']:.0%} "
          f"均值 {cur_dip[code]['avg60']:+.1%} (n={cur_dip[code]['n60']})")


# ════════════════════════════════════════════════════════════════
# 3. 接飞刀风险: 当前档位历史上的后续最大浮亏(MAE)
# ════════════════════════════════════════════════════════════════
def falling_knife(f: pd.DataFrame, dd_lab: str, horizon: int = 60) -> dict:
    idx = DD_LABELS.index(dd_lab)
    lo, hi = DD_BINS[idx]
    mask = (f["dd"] > lo) & (f["dd"] <= hi)
    mae = f.loc[mask, f"mae{horizon}"].dropna()
    fwd = f.loc[mask, f"fwd{horizon}"].dropna()
    if len(mae) < 5:
        return {"n": len(mae)}
    return {
        "n": int(len(mae)),
        "mae_median": float(mae.median()),
        "mae_p25": float(mae.quantile(0.25)),
        "mae_worst": float(mae.min()),
        "prob_drop10": float((mae <= -0.10).mean()),  # 后续还跌>10%概率
        "fwd_median": float(fwd.median()),
    }


knife = {}
for code in [US_TECH, A_TECH]:
    knife[code] = falling_knife(feat[code], cur_dip[code]["label"], 60)
    k = knife[code]
    if "mae_median" in k:
        print(f"\n[{ASSETS[code]}] 接飞刀(当前档{cur_dip[code]['label']}, n={k['n']}): "
              f"后续浮亏中位{k['mae_median']:+.1%} 最坏{k['mae_worst']:+.1%} "
              f"再跌>10%概率{k['prob_drop10']:.0%}")


# ════════════════════════════════════════════════════════════════
# 4. 抄底策略回测(仓位法, 单位资金, 现金零利率)
#    主回测标的: 科创50(数据含多轮回调)
# ════════════════════════════════════════════════════════════════
def nav_from_position(position: pd.Series, close: pd.Series) -> pd.Series:
    ret = close.pct_change().fillna(0)
    pos = position.shift(1).fillna(0).clip(0, 1)  # T+1执行
    return (1 + pos * ret).cumprod()


def backtest_dip(code: str) -> dict:
    f = feat[code]
    close = f["close"]
    # 策略1: 一把梭(买入持有)
    pos_bh = pd.Series(1.0, index=close.index)
    # 策略2: 智能抄底(越跌越买): 目标仓位=clip(-dd/0.30,0,1)
    pos_dip = (-f["dd"] / 0.30).clip(0, 1).fillna(0)
    # 策略3: 定投(20交易日加一档, 5个月建满仓)
    n = len(close)
    ramp = np.minimum(np.arange(n) // 20 / 6.0, 1.0)
    pos_dca = pd.Series(ramp, index=close.index)
    navs = {
        "一把梭(持有)": nav_from_position(pos_bh, close),
        "智能抄底(越跌越买)": nav_from_position(pos_dip, close),
        "无脑定投(分批)": nav_from_position(pos_dca, close),
    }
    metrics = {}
    for name, nav in navs.items():
        metrics[name] = {
            "ann": annual_return(nav), "mdd": max_drawdown(nav),
            "sharpe": sharpe(nav), "calmar": calmar(nav),
            "total": float(nav.iloc[-1] - 1),
        }
    return {"navs": navs, "metrics": metrics, "close": close}


bt = backtest_dip(A_TECH)
bt_us = backtest_dip(US_TECH)
for tag, b in [("A股科技", bt), ("美股科技", bt_us)]:
    print(f"\n--- 抄底策略回测 [{tag}] ({b['close'].index[0].date()}~{b['close'].index[-1].date()}) ---")
    for name, m in b["metrics"].items():
        print(f"  {name}: 总{m['total']:+.0%} 年化{m['ann']:+.1%} MDD{m['mdd']:.0%} "
              f"Sharpe{m['sharpe']:.2f} Calmar{m['calmar']:.2f}")


# ════════════════════════════════════════════════════════════════
# 5. 导出 CSV + summary.json
# ════════════════════════════════════════════════════════════════
# 当前状态
pd.DataFrame(state).T.to_csv(DATA / "current_state.csv", encoding="utf-8-sig")
# 条件胜率(两标的, 三周期)
for code in [US_TECH, A_TECH]:
    for h in HORIZONS:
        winrate_tables[code][h].to_csv(
            DATA / f"winrate_{code}_fwd{h}.csv", index=False, encoding="utf-8-sig")
# 策略净值 + 指标
nav_df = pd.DataFrame({k: v for k, v in bt["navs"].items()})
nav_df.to_csv(DATA / "strategy_nav.csv", encoding="utf-8-sig")
pd.DataFrame(bt["metrics"]).T.to_csv(DATA / "strategy_metrics.csv", encoding="utf-8-sig")
# 接飞刀
pd.DataFrame(knife).T.to_csv(DATA / "falling_knife.csv", encoding="utf-8-sig")

summary = {
    "as_of": END_STR, "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "assets": ASSETS, "us_tech": US_TECH, "a_tech": A_TECH,
    "state": state, "cur_dip": cur_dip, "knife": knife,
    "strategy_metrics": bt["metrics"],
    "strategy_metrics_us": bt_us["metrics"],
    "winrate_us": winrate_tables[US_TECH][60].to_dict("records"),
    "winrate_a": winrate_tables[A_TECH][60].to_dict("records"),
}
(ROOT / "summary.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n已导出 CSV + summary.json → {DATA}")


# ════════════════════════════════════════════════════════════════
# 6. 研报用图表(浅色文档风格)
# ════════════════════════════════════════════════════════════════
LC = {"text": "#1a1a2e", "sub": "#555", "grid": "#e6e6e6", "blue": "#2563eb",
      "green": "#16a34a", "red": "#dc2626", "orange": "#ea580c",
      "gold": "#b8860b", "muted": "#999", "band": "#fde7d6"}


def fig_dd_history():
    f = feat[A_TECH]
    fig, ax = plt.subplots(figsize=(9, 3.6), facecolor="white")
    ax.fill_between(f.index, f["dd"] * 100, 0, color=LC["red"], alpha=0.18, lw=0)
    ax.plot(f.index, f["dd"] * 100, color=LC["red"], lw=1.0)
    ax.axhline(state[A_TECH]["dd"] * 100, color=LC["blue"], ls="--", lw=1.2,
               label=f"当前 {state[A_TECH]['dd']:+.0%}")
    ax.axhspan(-20, -10, color=LC["gold"], alpha=0.10)
    ax.set_title(f"{ASSETS[A_TECH]} 距一年高点回撤(%) — 当前处于历史抄底区间",
                 fontsize=12, color=LC["text"], fontweight="bold")
    ax.set_ylabel("回撤 %", color=LC["sub"])
    ax.legend(loc="lower left", fontsize=9)
    ax.grid(True, color=LC["grid"], lw=0.6)
    for s in ax.spines.values():
        s.set_color(LC["grid"])
    ax.tick_params(colors=LC["sub"])
    fig.tight_layout()
    fig.savefig(FIGS / "fig_dd_history.png", dpi=150, facecolor="white")
    plt.close()


def fig_winrate_compare():
    fig, ax = plt.subplots(figsize=(9, 4.0), facecolor="white")
    x = np.arange(len(DD_LABELS))
    w = 0.38
    us = winrate_tables[US_TECH][60].set_index("档位")["胜率"].reindex(DD_LABELS) * 100
    a = winrate_tables[A_TECH][60].set_index("档位")["胜率"].reindex(DD_LABELS) * 100
    ax.bar(x - w / 2, us.values, w, color=LC["blue"], label="美股科技(纳指)")
    ax.bar(x + w / 2, a.values, w, color=LC["orange"], label="A股科技(科创50)")
    ax.axhline(50, color=LC["muted"], ls=":", lw=1)
    for i, (u, av) in enumerate(zip(us.values, a.values)):
        if u == u:
            ax.text(i - w / 2, u + 1.5, f"{u:.0f}", ha="center", fontsize=8, color=LC["blue"])
        if av == av:
            ax.text(i + w / 2, av + 1.5, f"{av:.0f}", ha="center", fontsize=8, color=LC["orange"])
    ax.set_xticks(x)
    ax.set_xticklabels(DD_LABELS, fontsize=9, color=LC["sub"])
    ax.set_ylabel("60交易日后上涨概率 %", color=LC["sub"])
    ax.set_title("不同回撤档位买入 · 持有3个月胜率对比", fontsize=12,
                 color=LC["text"], fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(True, axis="y", color=LC["grid"], lw=0.6)
    for s in ax.spines.values():
        s.set_color(LC["grid"])
    ax.tick_params(colors=LC["sub"])
    fig.tight_layout()
    fig.savefig(FIGS / "fig_winrate_compare.png", dpi=150, facecolor="white")
    plt.close()


def fig_strategy_nav():
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), facecolor="white")
    for ax, b, tag in [(axes[0], bt, f"A股科技 · {ASSETS[A_TECH]}"),
                       (axes[1], bt_us, f"美股科技 · {ASSETS[US_TECH]}")]:
        cmap = {"一把梭(持有)": LC["red"], "智能抄底(越跌越买)": LC["green"],
                "无脑定投(分批)": LC["blue"]}
        for name, nav in b["navs"].items():
            ax.plot(nav.index, nav.values, color=cmap[name], lw=1.3, label=name)
        ax.set_title(tag, fontsize=11, color=LC["text"], fontweight="bold")
        ax.legend(fontsize=8, loc="upper left")
        ax.grid(True, color=LC["grid"], lw=0.6)
        for s in ax.spines.values():
            s.set_color(LC["grid"])
        ax.tick_params(colors=LC["sub"], labelsize=8)
        ax.axhline(1, color=LC["muted"], ls=":", lw=0.8)
    fig.suptitle("三种抄底方式净值对比(仓位法,单位资金)", fontsize=12,
                 color=LC["text"], fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIGS / "fig_strategy_nav.png", dpi=150, facecolor="white")
    plt.close()


def fig_mae_dist():
    fig, ax = plt.subplots(figsize=(9, 3.6), facecolor="white")
    for code, col, tag in [(US_TECH, LC["blue"], "纳指"), (A_TECH, LC["orange"], "科创50")]:
        lab = cur_dip[code]["label"]
        idx = DD_LABELS.index(lab)
        lo, hi = DD_BINS[idx]
        m = (feat[code]["dd"] > lo) & (feat[code]["dd"] <= hi)
        mae = feat[code].loc[m, "mae60"].dropna() * 100
        ax.hist(mae, bins=30, color=col, alpha=0.45, label=f"{tag}(当前档{lab})")
    ax.axvline(-10, color=LC["red"], ls="--", lw=1, label="再跌10%线")
    ax.set_title("买入后3个月内最大浮亏(接飞刀风险)分布", fontsize=12,
                 color=LC["text"], fontweight="bold")
    ax.set_xlabel("买入后最大浮亏 %", color=LC["sub"])
    ax.set_ylabel("历史天数", color=LC["sub"])
    ax.legend(fontsize=9)
    ax.grid(True, color=LC["grid"], lw=0.6)
    for s in ax.spines.values():
        s.set_color(LC["grid"])
    ax.tick_params(colors=LC["sub"])
    fig.tight_layout()
    fig.savefig(FIGS / "fig_mae_dist.png", dpi=150, facecolor="white")
    plt.close()


print("\n生成研报图表...")
fig_dd_history()
fig_winrate_compare()
fig_strategy_nav()
fig_mae_dist()
print(f"  研报图表 → {FIGS}")


# ════════════════════════════════════════════════════════════════
# 7. 小红书卡片(暗色, 7张)
# ════════════════════════════════════════════════════════════════
def card_1_cover():
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(C["bg"]); ax.axis("off")
    ax.text(0.5, 0.89, "美股A股科技集体跳水", ha="center", fontsize=35,
            fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.805, "现在能抄底吗？", ha="center", fontsize=45,
            fontweight="bold", color=C["gold"], transform=ax.transAxes)
    ax.text(0.5, 0.728, f"数据截止 {END_STR} · 用十年历史数据算胜率",
            ha="center", fontsize=14.5, color=C["muted"], transform=ax.transAxes)
    ax.plot([0.13, 0.87], [0.688, 0.688], color=C["border"], lw=1.2, transform=ax.transAxes)
    # 核心暴跌数字
    ax.text(0.5, 0.585, f"{state[US_TECH]['ret5']:+.1%}", ha="center", fontsize=74,
            fontweight="bold", color=C["red"], fontfamily="monospace", transform=ax.transAxes)
    ax.text(0.5, 0.497, "纳指ETF 近5日", ha="center", fontsize=16,
            color=C["muted"], transform=ax.transAxes)
    kpis = [
        ("纳指距一年高", f"{state[US_TECH]['dd']:+.1%}", C["orange"]),
        ("科创50距高", f"{state[A_TECH]['dd']:+.1%}", C["red"]),
        ("芯片10日跌", f"{state['159995']['ret10']:+.1%}", C["red"]),
    ]
    for i, (label, val, color) in enumerate(kpis):
        x = 0.2 + i * 0.3
        rect = FancyBboxPatch((x - 0.135, 0.325), 0.27, 0.125, boxstyle="round,pad=0.01",
                              facecolor=C["card"], edgecolor=C["border"], lw=0.8,
                              transform=ax.transAxes, zorder=0)
        ax.add_patch(rect)
        ax.text(x, 0.405, val, ha="center", fontsize=24, fontweight="bold",
                color=color, fontfamily="monospace", transform=ax.transAxes)
        ax.text(x, 0.347, label, ha="center", fontsize=12.5, color=C["muted"], transform=ax.transAxes)
    ax.text(0.5, 0.24, "抄底=猜底？不，用胜率说话", ha="center", fontsize=19,
            color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.172, "美股科技 vs A股科技，谁更值得抄", ha="center", fontsize=15,
            color=C["cyan"], transform=ax.transAxes)
    ax.text(0.5, 0.105, "#抄底  #科技股  #纳指  #科创50  #量化投资", ha="center",
            fontsize=13, color=C["blue"], transform=ax.transAxes)
    _page_number(fig, 1)
    fig.savefig(CARDS / "01_cover.png", dpi=DPI, facecolor=C["bg"]); plt.close()
    print("  [1/7] cover")


def card_2_thermometer():
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(C["bg"]); ax.axis("off")
    ax.text(0.5, 0.93, "这次跌得有多深？", ha="center", fontsize=29,
            fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.875, f"截止 {END_STR} · 四大科技标的回调扫描",
            ha="center", fontsize=13.5, color=C["muted"], transform=ax.transAxes)
    headers = ["标的", "5日", "10日", "距一年高", "RSI"]
    xs = [0.07, 0.40, 0.55, 0.74, 0.92]
    y = 0.795
    for x, h in zip(xs, headers):
        ax.text(x, y, h, fontsize=13, fontweight="bold", color=C["muted"],
                ha="left" if x < 0.1 else "center", transform=ax.transAxes)
    y -= 0.02
    ax.plot([0.05, 0.95], [y, y], color=C["border"], transform=ax.transAxes)
    order = ["513100", "588000", "159995", "159949"]
    for code in order:
        s = state[code]; y -= 0.112
        rect = FancyBboxPatch((0.04, y - 0.042), 0.92, 0.092, boxstyle="round,pad=0.006",
                              facecolor=C["card"], edgecolor=C["border"], lw=0.6,
                              transform=ax.transAxes, zorder=0)
        ax.add_patch(rect)
        ax.text(xs[0], y, s["name"], fontsize=15, fontweight="bold", color=C["text"],
                va="center", transform=ax.transAxes)
        ax.text(xs[0], y - 0.03, code, fontsize=10.5, color=C["muted"],
                va="center", fontfamily="monospace", transform=ax.transAxes)
        for x, key in [(xs[1], "ret5"), (xs[2], "ret10"), (xs[3], "dd")]:
            v = s[key]
            ax.text(x, y, f"{v:+.1%}", fontsize=15, fontweight="bold", ha="center",
                    color=C["red"] if v < 0 else C["green"], va="center",
                    fontfamily="monospace", transform=ax.transAxes)
        rsi = s["rsi"]
        rsi_c = C["green"] if rsi < 35 else (C["gold"] if rsi < 50 else C["muted"])
        ax.text(xs[4], y, f"{rsi:.0f}", fontsize=15, fontweight="bold", ha="center",
                color=rsi_c, va="center", fontfamily="monospace", transform=ax.transAxes)
    y -= 0.11
    ax.plot([0.08, 0.92], [y + 0.035, y + 0.035], color=C["border"], transform=ax.transAxes)
    ax.text(0.5, y - 0.005, "纳指5日急跌10%，A股芯片/科创10日跌16%", ha="center",
            fontsize=15, fontweight="bold", color=C["gold"], transform=ax.transAxes)
    ax.text(0.5, y - 0.06, "RSI<35=超卖(科创50已到)，回调进入历史抄底区间",
            ha="center", fontsize=12.5, color=C["muted"], transform=ax.transAxes)
    _page_number(fig, 2); _disclaimer(fig)
    fig.savefig(CARDS / "02_thermometer.png", dpi=DPI, facecolor=C["bg"]); plt.close()
    print("  [2/7] thermometer")


def card_3_winrate():
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(C["bg"]); ax.axis("off")
    ax.text(0.5, 0.95, "抄底胜率：跌多少才该买", ha="center", fontsize=27,
            fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.905, "按回撤档位买入，持有3个月后上涨概率",
            ha="center", fontsize=13, color=C["muted"], transform=ax.transAxes)

    def block(code, y0, title, accent):
        ax.text(0.06, y0, title, fontsize=16, fontweight="bold", color=accent,
                transform=ax.transAxes)
        cur_lab = cur_dip[code]["label"]
        tbl = winrate_tables[code][60].set_index("档位")
        yy = y0 - 0.05
        for lab in DD_LABELS:
            r = tbl.loc[lab]
            wr = r["胜率"]; n = int(r["样本"])
            is_cur = (lab == cur_lab)
            if n < 5 or wr != wr:
                yy -= 0.052; continue
            if is_cur:
                hl = FancyBboxPatch((0.04, yy - 0.023), 0.92, 0.046, boxstyle="round,pad=0.004",
                                    facecolor=accent, alpha=0.13, transform=ax.transAxes, zorder=0)
                ax.add_patch(hl)
            bar_c = C["green"] if wr >= 0.6 else (C["red"] if wr < 0.45 else C["gold"])
            ax.text(0.06, yy, lab, fontsize=12.5, color=C["text"] if not is_cur else accent,
                    va="center", fontweight="bold" if is_cur else "normal", transform=ax.transAxes)
            ax.add_patch(FancyBboxPatch((0.29, yy - 0.012), 0.40 * wr, 0.024,
                        boxstyle="round,pad=0.002", facecolor=bar_c, alpha=0.55,
                        transform=ax.transAxes, zorder=1))
            ax.text(0.715, yy, f"{wr:.0%}", fontsize=15, fontweight="bold", color=bar_c,
                    va="center", ha="left", fontfamily="monospace", transform=ax.transAxes)
            ax.text(0.815, yy, f"n={n}", fontsize=10.5, color=C["muted"], va="center",
                    fontfamily="monospace", transform=ax.transAxes)
            if is_cur:
                pill = FancyBboxPatch((0.895, yy - 0.019), 0.08, 0.038,
                                      boxstyle="round,pad=0.004", facecolor=accent,
                                      edgecolor="none", transform=ax.transAxes, zorder=2)
                ax.add_patch(pill)
                ax.text(0.935, yy, "现在", fontsize=10.5, color=C["bg"], fontweight="bold",
                        va="center", ha="center", transform=ax.transAxes, zorder=3)
            yy -= 0.052
        return yy

    yend = block(US_TECH, 0.85, "美股科技 · 纳指ETF(513100)", C["blue"])
    block(A_TECH, yend - 0.012, "A股科技 · 科创50ETF(588000)", C["orange"])
    ax.text(0.5, 0.092, "纳指跌10-15%抄→胜率74%；科创50同档仅53%",
            ha="center", fontsize=14, fontweight="bold", color=C["gold"], transform=ax.transAxes)
    _page_number(fig, 3); _disclaimer(fig)
    fig.savefig(CARDS / "03_winrate.png", dpi=DPI, facecolor=C["bg"]); plt.close()
    print("  [3/7] winrate")


def card_4_knife():
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(C["bg"]); ax.axis("off")
    ax.text(0.5, 0.935, "小心接飞刀", ha="center", fontsize=30, fontweight="bold",
            color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.882, "在当前回撤档位买入后，历史上还会跌多少",
            ha="center", fontsize=13, color=C["muted"], transform=ax.transAxes)
    y0 = 0.80
    for code, accent in [(US_TECH, C["blue"]), (A_TECH, C["orange"])]:
        k = knife[code]; s = state[code]
        rect = FancyBboxPatch((0.05, y0 - 0.265), 0.90, 0.285, boxstyle="round,pad=0.01",
                              facecolor=C["card"], edgecolor=C["border"], lw=0.8,
                              transform=ax.transAxes, zorder=0)
        ax.add_patch(rect)
        ax.text(0.09, y0 - 0.015, f"{s['name']}", fontsize=17, fontweight="bold",
                color=accent, transform=ax.transAxes)
        ax.text(0.91, y0 - 0.015, f"当前档 {cur_dip[code]['label']}", fontsize=12.5,
                color=C["muted"], ha="right", transform=ax.transAxes)
        items = [
            ("买入后浮亏中位", f"{k['mae_median']:+.1%}", C["gold"]),
            ("最坏情况浮亏", f"{k['mae_worst']:+.1%}", C["red"]),
            ("再跌超10%概率", f"{k['prob_drop10']:.0%}", C["red"]),
        ]
        for i, (lab, val, col) in enumerate(items):
            x = 0.20 + i * 0.30
            ax.text(x, y0 - 0.095, val, ha="center", fontsize=23, fontweight="bold",
                    color=col, fontfamily="monospace", transform=ax.transAxes)
            ax.text(x, y0 - 0.15, lab, ha="center", fontsize=12, color=C["muted"],
                    transform=ax.transAxes)
        ax.text(0.5, y0 - 0.222, f"历史样本 n={k['n']} · 3个月内最大浮亏统计",
                ha="center", fontsize=11, color=C["muted"], transform=ax.transAxes)
        y0 -= 0.36
    ax.text(0.5, 0.105, "抄底≠抄到最低点，要给浮亏留空间",
            ha="center", fontsize=15, fontweight="bold", color=C["gold"], transform=ax.transAxes)
    _page_number(fig, 4); _disclaimer(fig)
    fig.savefig(CARDS / "04_knife.png", dpi=DPI, facecolor=C["bg"]); plt.close()
    print("  [4/7] knife")


def card_5_strategy():
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(C["bg"]); ax.axis("off")
    ax.text(0.5, 0.94, "一把梭 vs 越跌越买 vs 定投", ha="center", fontsize=23,
            fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.895, f"{ASSETS[A_TECH]} 上市以来 · 三种抄底方式回测",
            ha="center", fontsize=13, color=C["muted"], transform=ax.transAxes)
    # 净值曲线
    axp = fig.add_axes([0.12, 0.50, 0.78, 0.32]); axp.set_facecolor(C["card"])
    cmap = {"一把梭(持有)": C["red"], "智能抄底(越跌越买)": C["green"], "无脑定投(分批)": C["blue"]}
    for name, nav in bt["navs"].items():
        axp.plot(nav.index, nav.values, color=cmap[name], lw=1.6, label=name)
    axp.axhline(1, color=C["muted"], ls=":", lw=0.8)
    axp.legend(fontsize=10.5, loc="upper left", facecolor=C["card"], edgecolor=C["border"],
               labelcolor=C["text"])
    axp.grid(True, color=C["border"], lw=0.5, alpha=0.5)
    for sp in axp.spines.values():
        sp.set_color(C["border"])
    axp.tick_params(colors=C["muted"], labelsize=9.5)
    # 指标表
    y = 0.40
    cols = ["策略", "总收益", "年化", "最大回撤", "夏普"]
    xs = [0.08, 0.40, 0.56, 0.74, 0.90]
    for x, c in zip(xs, cols):
        ax.text(x, y, c, fontsize=12.5, fontweight="bold", color=C["muted"],
                ha="left" if x < 0.1 else "center", transform=ax.transAxes)
    y -= 0.018
    ax.plot([0.06, 0.94], [y, y], color=C["border"], transform=ax.transAxes)
    for name, m in bt["metrics"].items():
        y -= 0.072
        ax.text(xs[0], y, name, fontsize=12.5, color=cmap[name], va="center",
                fontweight="bold", transform=ax.transAxes)
        for x, v, col in [
            (xs[1], f"{m['total']:+.0%}", C["green"] if m['total'] > 0 else C["red"]),
            (xs[2], f"{m['ann']:+.1%}", C["green"] if m['ann'] > 0 else C["red"]),
            (xs[3], f"{m['mdd']:.0%}", C["red"]),
            (xs[4], f"{m['sharpe']:.2f}", C["text"]),
        ]:
            ax.text(x, y, v, fontsize=14, fontweight="bold", color=col, ha="center",
                    va="center", fontfamily="monospace", transform=ax.transAxes)
    ax.text(0.5, 0.105, "高波动品种里，无脑定投/分批反而比一把梭稳",
            ha="center", fontsize=14, fontweight="bold", color=C["gold"], transform=ax.transAxes)
    _page_number(fig, 5); _disclaimer(fig)
    fig.savefig(CARDS / "05_strategy.png", dpi=DPI, facecolor=C["bg"]); plt.close()
    print("  [5/7] strategy")


def card_6_playbook():
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(C["bg"]); ax.axis("off")
    ax.text(0.5, 0.935, "抄底实操手册", ha="center", fontsize=30, fontweight="bold",
            color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.882, "美股科技 与 A股科技，打法不一样",
            ha="center", fontsize=13, color=C["muted"], transform=ax.transAxes)
    blocks = [
        ("美股科技(纳指)", C["blue"], [
            "长期向上，回调即机会",
            "跌10-15%分2-3批进场",
            "胜率高，可适当重仓",
            "靠汇率+QDII溢价要留意",
        ]),
        ("A股科技(科创50/芯片)", C["orange"], [
            "波动大，别一把梭",
            "等RSI<35+跌破年线再分批",
            "胜率平庸，仓位要克制",
            "设-15%硬止损，破位认错",
        ]),
    ]
    y0 = 0.80
    for title, accent, items in blocks:
        rect = FancyBboxPatch((0.05, y0 - 0.275), 0.90, 0.295, boxstyle="round,pad=0.01",
                              facecolor=C["card"], edgecolor=accent, lw=1.2,
                              transform=ax.transAxes, zorder=0)
        ax.add_patch(rect)
        ax.text(0.08, y0 - 0.025, title, fontsize=17, fontweight="bold",
                color=accent, transform=ax.transAxes)
        yy = y0 - 0.09
        for it in items:
            ax.text(0.11, yy, "▪", fontsize=13, color=accent, va="center", transform=ax.transAxes)
            ax.text(0.16, yy, it, fontsize=14, color=C["text"], va="center",
                    transform=ax.transAxes)
            yy -= 0.055
        y0 -= 0.37
    ax.text(0.5, 0.105, "通用铁律：分批 · 留子弹 · 不借钱 · 设止损",
            ha="center", fontsize=15, fontweight="bold", color=C["gold"], transform=ax.transAxes)
    _page_number(fig, 6); _disclaimer(fig)
    fig.savefig(CARDS / "06_playbook.png", dpi=DPI, facecolor=C["bg"]); plt.close()
    print("  [6/7] playbook")


def card_7_conclusion():
    fig = _fig()
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(C["bg"]); ax.axis("off")
    ax.text(0.5, 0.92, "结论：能不能抄底？", ha="center", fontsize=29,
            fontweight="bold", color=C["gold"], transform=ax.transAxes)
    win_us = cur_dip[US_TECH]["win60"]; win_a = cur_dip[A_TECH]["win60"]
    prob_us = knife[US_TECH]["prob_drop10"]; prob_a = knife[A_TECH]["prob_drop10"]
    lines = [
        ("美股科技(纳指)", f"当前档抄底3月胜率 {win_us:.0%}", "宜抄 · 历史上回调即买，胜率高", C["green"]),
        ("A股科技(科创50)", f"当前档抄底3月胜率 {win_a:.0%}", "谨慎 · 胜率平庸，需分批+止损", C["gold"]),
        ("接飞刀风险", f"两者再跌>10%概率 {prob_us:.0%} / {prob_a:.0%}", "高危 · 抄底后仍可能深跌，留余地", C["red"]),
    ]
    y = 0.80
    for title, stat, verdict, col in lines:
        rect = FancyBboxPatch((0.06, y - 0.145), 0.88, 0.16, boxstyle="round,pad=0.01",
                              facecolor=C["card"], edgecolor=C["border"], lw=0.8,
                              transform=ax.transAxes, zorder=0)
        ax.add_patch(rect)
        ax.text(0.10, y - 0.008, title, fontsize=16.5, fontweight="bold", color=col,
                transform=ax.transAxes)
        ax.text(0.10, y - 0.062, stat, fontsize=14, color=C["text"], transform=ax.transAxes)
        ax.text(0.10, y - 0.11, verdict, fontsize=13, color=C["muted"], transform=ax.transAxes)
        y -= 0.195
    ax.text(0.5, y + 0.012, "一句话：可以抄，但要分品种、分批、带止损", ha="center",
            fontsize=16.5, fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, y - 0.048, "完整研报+数据+源码 见主页", ha="center", fontsize=14,
            color=C["cyan"], transform=ax.transAxes)
    ax.text(0.5, y - 0.104, "#抄底  #科技股  #纳指  #科创50  #量化投资  #ETF",
            ha="center", fontsize=13, color=C["blue"], transform=ax.transAxes)
    _page_number(fig, 7); _disclaimer(fig)
    fig.savefig(CARDS / "07_conclusion.png", dpi=DPI, facecolor=C["bg"]); plt.close()
    print("  [7/7] conclusion")


print("\n生成小红书卡片...")
card_1_cover()
card_2_thermometer()
card_3_winrate()
card_4_knife()
card_5_strategy()
card_6_playbook()
card_7_conclusion()
print(f"\n全部完成 → {ROOT}")
