"""现金流反共识 — 浅色 figures (PDF 研报用) — 2026-06-26."""

from __future__ import annotations

import json
import os
from pathlib import Path

for _k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
    os.environ.pop(_k, None)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd

plt.rcParams["font.sans-serif"] = ["Droid Sans Fallback", "WenQuanYi Micro Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

OUT = Path("/das/user/QYJI/quant/output/2026-06-26/fcf-contrarian")
FIG_DIR = OUT / "figures"
DATA_DIR = OUT / "data"
CACHE = Path("/das/user/QYJI/quant/data/cache/fcf")

with open(DATA_DIR / "summary.json", "r", encoding="utf-8") as f:
    S = json.load(f)


# ============ FIG 1: 5 现金流 ETF 60d 表现条形 ============
def fig_5etfs():
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=120)
    fig.patch.set_facecolor("white")

    syms = [("562340", "中证自由现金流ETF\n华泰柏瑞", "sh562340"),
            ("563690", "国新央企现金流ETF\n国新",       "sh563690"),
            ("159218", "嘉实自由现金流ETF\n嘉实",       "sz159218"),
            ("159201", "国证自由现金流ETF\n易方达",     "sz159201"),
            ("159222", "华夏自由现金流ETF\n华夏",       "sz159222")]
    data = [(name, S["fcf_etfs"][k]["ret_60d"]) for c, name, k in syms]
    data.sort(key=lambda x: x[1])
    names = [d[0] for d in data]
    vals = [d[1] * 100 for d in data]
    colors = ["#16a34a" if v < 0 else "#dc2626" for v in vals]

    y = np.arange(len(names))
    ax.barh(y, vals, color=colors, edgecolor="none", height=0.6)
    ax.axvline(0, color="#10243e", lw=1)
    for i, v in enumerate(vals):
        ax.text(v + (0.6 if v >= 0 else -0.6), i, f"{v:+.1f}%",
                va="center", ha="left" if v >= 0 else "right",
                fontsize=11, fontweight="bold",
                color=colors[i])
    ax.set_yticks(y, names, fontsize=10)
    ax.set_xlabel("近 60 日涨跌幅 (%)", fontsize=11)
    ax.set_title("5 只\"自由现金流 ETF\" 近 60 日表现 — 最强 vs 最弱差距 33 个百分点",
                 fontsize=12, fontweight="bold", pad=12)
    ax.set_xlim(min(vals) * 1.3, max(vals) * 1.3)
    ax.grid(axis="x", alpha=0.3, ls=":")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    p = FIG_DIR / "fig_5etfs.png"
    fig.savefig(p, dpi=120, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] {p}")


# ============ FIG 2: 持仓行业堆叠条 ============
def fig_holdings():
    fig, ax = plt.subplots(figsize=(11, 5), dpi=120)
    fig.patch.set_facecolor("white")

    SECTOR_COLORS = {
        "汽车": "#2563eb", "石油石化": "#ea580c", "家电": "#9333ea",
        "航运": "#0891b2", "钢铁": "#64748b", "有色": "#ca8a04",
        "机械": "#a16207", "军工": "#dc2626", "电气设备": "#16a34a",
        "建筑": "#475569", "通信": "#3b82f6",
        "银行": "#1d4ed8", "医药": "#c026d3", "半导体": "#0d9488",
        "贸易": "#6b7280", "游戏": "#e11d48", "互联网": "#0ea5e9",
    }
    etfs = [("159201", "国证自由现金流"),
            ("159222", "华夏自由现金流"),
            ("159218", "嘉实自由现金流"),
            ("562340", "华泰柏瑞中证现金流"),
            ("563690", "国新央企现金流")]

    y_positions = []
    for i, (code, name) in enumerate(etfs):
        sym_key = f"sh{code}" if code in ("562340", "563690") else f"sz{code}"
        sectors = S["holdings"][sym_key]["sectors"]
        sectors_sorted = sorted([s for s in sectors.items() if s[0] != "其他"], key=lambda x: -x[1])
        x = 0
        for sec, w in sectors_sorted:
            ax.barh(i, w, left=x, color=SECTOR_COLORS.get(sec, "#94a3b8"),
                    edgecolor="white", lw=0.5, height=0.65)
            if w >= 8:
                ax.text(x + w/2, i, f"{sec}\n{w:.0f}%",
                        ha="center", va="center", fontsize=8,
                        fontweight="bold", color="white")
            x += w
        # 剩余 (未披露)
        if x < 100:
            ax.barh(i, 100 - x, left=x, color="#e5e7eb", edgecolor="white", lw=0.5, height=0.65)
        y_positions.append(i)
    ax.set_yticks(y_positions, [name for _, name in etfs], fontsize=10)
    ax.set_xlim(0, 100)
    ax.set_xlabel("持仓占净值比 (%) · 灰色为未披露/前 10 之外", fontsize=10)
    ax.set_title("5 只 ETF 持仓行业归因 — 同名实异最直观证据",
                 fontsize=12, fontweight="bold", pad=12)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.invert_yaxis()
    fig.tight_layout()
    p = FIG_DIR / "fig_holdings.png"
    fig.savefig(p, dpi=120, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] {p}")


# ============ FIG 3: 现金流指数 vs 沪深300 vs 红利低波 净值曲线 (rebase 100) ============
def fig_nav_compare():
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=120)
    fig.patch.set_facecolor("white")

    # 取 现金流指数 sz980092 自发布以来
    idx_fcf = pd.read_parquet(CACHE / "idx_sz980092.parquet")
    idx_fcf["date"] = pd.to_datetime(idx_fcf["date"])
    idx_fcf = idx_fcf.set_index("date")["close"]
    start = idx_fcf.index[0]
    # 取相同窗口的沪深300, 红利低波 ETF
    hs300 = pd.read_parquet(CACHE / "idx_sh000300.parquet")
    hs300["date"] = pd.to_datetime(hs300["date"])
    hs300 = hs300.set_index("date")["close"].loc[start:]
    dvd_lv = pd.read_parquet(CACHE / "etf_sz159211.parquet")
    dvd_lv["date"] = pd.to_datetime(dvd_lv["date"])
    dvd_lv = dvd_lv.set_index("date")["close"].loc[start:]

    fcf_n = idx_fcf / idx_fcf.iloc[0] * 100
    hs300_n = hs300 / hs300.iloc[0] * 100
    dvd_n = dvd_lv / dvd_lv.iloc[0] * 100

    ax.plot(fcf_n.index, fcf_n.values, color="#16a34a", lw=2.2, label=f"国证自由现金流指数 ({fcf_n.iloc[-1]-100:+.1f}%)")
    ax.plot(hs300_n.index, hs300_n.values, color="#2563eb", lw=2.0, label=f"沪深 300 ({hs300_n.iloc[-1]-100:+.1f}%)")
    ax.plot(dvd_n.index, dvd_n.values, color="#dc2626", lw=2.0, label=f"红利低波 100 ({dvd_n.iloc[-1]-100:+.1f}%)")

    # 标记顶点
    peak_idx = fcf_n.idxmax()
    peak_val = fcf_n.max()
    ax.scatter([peak_idx], [peak_val], s=100, c="#16a34a", zorder=5, ec="white", lw=1.5)
    ax.annotate(f"现金流指数顶点\n{peak_idx.strftime('%Y-%m-%d')} ({peak_val:.1f})",
                xy=(peak_idx, peak_val), xytext=(0.55, 0.92),
                textcoords="axes fraction",
                fontsize=9.5, color="#16a34a", fontweight="bold",
                arrowprops=dict(arrowstyle="->", color="#16a34a", lw=1.0))

    ax.axhline(100, color="#64748b", lw=0.8, ls=":")
    ax.set_ylabel("净值 (起点 = 100)", fontsize=11)
    ax.set_title("发布即顶点 — 现金流指数 vs 沪深300 vs 红利低波 (起点对齐)",
                 fontsize=12, fontweight="bold", pad=12)
    ax.legend(loc="lower left", fontsize=10, frameon=False)
    ax.grid(alpha=0.3, ls=":")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    p = FIG_DIR / "fig_nav.png"
    fig.savefig(p, dpi=120, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] {p}")


# ============ FIG 4: 现金流指数回撤曲线 ============
def fig_drawdown():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), dpi=120,
                                    gridspec_kw={"height_ratios": [2, 1]}, sharex=True)
    fig.patch.set_facecolor("white")

    idx_fcf = pd.read_parquet(CACHE / "idx_sz980092.parquet")
    idx_fcf["date"] = pd.to_datetime(idx_fcf["date"])
    idx_fcf = idx_fcf.set_index("date")["close"]
    cummax = idx_fcf.expanding().max()
    dd = (idx_fcf / cummax - 1) * 100

    # 上: 价格
    ax1.plot(idx_fcf.index, idx_fcf.values, color="#10243e", lw=1.8)
    ax1.fill_between(idx_fcf.index, idx_fcf.values, cummax.values, color="#16a34a", alpha=0.15)
    ax1.plot(cummax.index, cummax.values, color="#16a34a", lw=0.8, ls="--", alpha=0.6, label="历史峰值 (ATH)")
    peak_d = idx_fcf.idxmax()
    ax1.scatter([peak_d], [idx_fcf.max()], s=80, c="#16a34a", zorder=5, ec="white", lw=1.5)
    ax1.set_ylabel("国证自由现金流指数", fontsize=10)
    ax1.set_title("国证自由现金流指数 (sz980092) 价格 + 回撤双面板",
                  fontsize=12, fontweight="bold", pad=10)
    ax1.legend(loc="upper left", fontsize=9, frameon=False)
    ax1.grid(alpha=0.3, ls=":")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    # 下: 回撤
    ax2.fill_between(dd.index, dd.values, 0, color="#16a34a", alpha=0.30)
    ax2.plot(dd.index, dd.values, color="#16a34a", lw=1.5)
    ax2.axhline(0, color="#10243e", lw=0.6)
    cur_dd = dd.iloc[-1]
    ax2.axhline(cur_dd, color="#16a34a", ls="--", lw=0.8, alpha=0.6)
    ax2.annotate(f"当前回撤 {cur_dd:+.1f}%",
                 xy=(dd.index[-1], cur_dd), xytext=(-160, -10),
                 textcoords="offset points",
                 fontsize=10, color="#16a34a", fontweight="bold")
    ax2.set_ylabel("回撤 (%)", fontsize=10)
    ax2.set_xlabel("日期", fontsize=10)
    ax2.grid(alpha=0.3, ls=":")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    fig.tight_layout()
    p = FIG_DIR / "fig_drawdown.png"
    fig.savefig(p, dpi=120, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] {p}")


if __name__ == "__main__":
    fig_5etfs()
    fig_holdings()
    fig_nav_compare()
    fig_drawdown()
    print("\n[DONE] 4 figures @", FIG_DIR)
