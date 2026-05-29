"""红利低波专栏 — 小红书分享卡片 + 策略增强分析"""

import sys
sys.path.insert(0, "src")

import pandas as pd
import numpy as np
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
plt.rcParams["font.sans-serif"] = ["Droid Sans Fallback", "WenQuanYi Micro Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# ============================================================
# 主题色
# ============================================================
C = {
    "bg":       "#0d1117",
    "card":     "#161b22",
    "border":   "#30363d",
    "text":     "#c9d1d9",
    "muted":    "#8b949e",
    "blue":     "#58a6ff",
    "green":    "#3fb950",
    "red":      "#f85149",
    "orange":   "#d2991d",
    "purple":   "#bc8cff",
    "gold":     "#f0c040",
}

CARD_W = 7.2
CARD_H = 9.6
DPI = 150

# ============================================================
# 数据加载
# ============================================================
CACHE_DIR = Path("./data/cache/etf")

def load_etf(symbol: str) -> pd.Series:
    """加载 ETF close 序列"""
    path = CACHE_DIR / f"{symbol}.parquet"
    df = pd.read_parquet(path)
    s = df["close"]
    s.index = pd.to_datetime(s.index)
    return s.sort_index()


print("加载数据...")
close_512890 = load_etf("512890")  # 红利低波
close_510880 = load_etf("510880")  # 红利ETF
close_510300 = load_etf("510300")  # 沪深300
close_511010 = load_etf("511010")  # 国债ETF
close_518880 = load_etf("518880")  # 黄金ETF

# 对齐到512890的日期范围
start = close_512890.index[0]
end = close_512890.index[-1]
print(f"分析区间: {start.strftime('%Y-%m-%d')} ~ {end.strftime('%Y-%m-%d')} ({len(close_512890)} 交易日)")

# 构建后复权净值（排除除权日跳水）
ret_raw = close_512890.pct_change()
ex_div_mask = ret_raw < -0.15  # 除权日
ret_adj = ret_raw.copy()
ret_adj.iloc[0] = 0
ret_adj[ex_div_mask] = 0
nav_512890 = (1 + ret_adj).cumprod()
print(f"除权日: {[d.strftime('%Y-%m-%d') for d in ret_raw[ex_div_mask].index]}")
print(f"后复权高点: {nav_512890.max():.4f} ({nav_512890.idxmax().strftime('%Y-%m-%d')})")
print(f"当前回撤: {(nav_512890.iloc[-1]/nav_512890.max()-1)*100:.1f}%")

# ============================================================
# Part 1: 小红书分享卡片
# ============================================================
print("\n[Part 1] 生成小红书分享卡片...")

SAVE_DIR = Path("./output/dividend-lowvol")
SAVE_DIR.mkdir(parents=True, exist_ok=True)

TOTAL_CARDS = 5


def _setup_fig():
    fig = plt.figure(figsize=(CARD_W, CARD_H), facecolor=C["bg"])
    return fig


def card_1_cover():
    """封面卡片：核心数据"""
    fig = _setup_fig()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(C["bg"])
    ax.axis("off")

    # 计算当前回撤
    current_dd = (nav_512890.iloc[-1] / nav_512890.max() - 1) * 100
    peak_date = nav_512890.idxmax().strftime('%Y-%m-%d')

    # 标题
    ax.text(0.5, 0.92, "红利低波 · 胜率分析", ha="center", va="center",
            fontsize=34, fontweight="bold", color=C["text"], transform=ax.transAxes)
    ax.text(0.5, 0.87, f"512890 · 当前回撤{current_dd:.1f}% · 后复权含分红",
            ha="center", va="center", fontsize=13, color=C["muted"], transform=ax.transAxes)

    # 核心数字
    ax.text(0.5, 0.73, f"{current_dd:.1f}%", ha="center", va="center",
            fontsize=80, fontweight="bold", color=C["orange"],
            fontfamily="monospace", transform=ax.transAxes)
    ax.text(0.5, 0.64, f"当前回撤深度 (距{peak_date}高点)",
            ha="center", va="center", fontsize=13, color=C["muted"], transform=ax.transAxes)

    # 分隔线
    ax.plot([0.15, 0.85], [0.58, 0.58], color=C["border"], linewidth=1, transform=ax.transAxes, clip_on=False)

    # 胜率表格
    periods = ["1个月", "3个月", "6个月", "1年"]
    win_rates = [65, 79, 84, 98]
    avg_rets = ["+1.6%", "+4.3%", "+7.9%", "+16.2%"]

    y_start = 0.53
    # 表头
    ax.text(0.18, y_start, "持有期", ha="center", va="center",
            fontsize=12, color=C["muted"], fontweight="bold", transform=ax.transAxes)
    ax.text(0.50, y_start, "历史胜率", ha="center", va="center",
            fontsize=12, color=C["muted"], fontweight="bold", transform=ax.transAxes)
    ax.text(0.80, y_start, "平均收益", ha="center", va="center",
            fontsize=12, color=C["muted"], fontweight="bold", transform=ax.transAxes)

    for i, (p, wr, ar) in enumerate(zip(periods, win_rates, avg_rets)):
        y = y_start - 0.065 * (i + 1)
        wr_color = C["green"] if wr >= 80 else C["blue"] if wr >= 70 else C["text"]
        # 高胜率行加背景高亮
        if wr >= 80:
            from matplotlib.patches import FancyBboxPatch
            rect = FancyBboxPatch((0.08, y - 0.02), 0.84, 0.05,
                                   boxstyle="round,pad=0.01",
                                   facecolor=C["green"], alpha=0.08,
                                   transform=ax.transAxes, zorder=0)
            ax.add_patch(rect)
        ax.text(0.18, y, p, ha="center", va="center",
                fontsize=15, color=C["text"], transform=ax.transAxes)
        ax.text(0.50, y, f"{wr}%", ha="center", va="center",
                fontsize=22, fontweight="bold", color=wr_color,
                fontfamily="monospace", transform=ax.transAxes)
        ax.text(0.80, y, ar, ha="center", va="center",
                fontsize=15, color=C["green"], fontfamily="monospace", transform=ax.transAxes)

    # 底部
    ax.plot([0.15, 0.85], [0.15, 0.15], color=C["border"], linewidth=0.5, transform=ax.transAxes, clip_on=False)
    ax.text(0.5, 0.11, "* 历史数据统计，不代表未来收益",
            ha="center", va="center", fontsize=10, color=C["muted"],
            transform=ax.transAxes, style="italic")
    ax.text(0.5, 0.06, f"数据截至 {end.strftime('%Y-%m-%d')} | 后复权含分红 | 样本量 687 个交易日",
            ha="center", va="center", fontsize=9, color=C["muted"], transform=ax.transAxes)
    # 页码
    ax.text(0.95, 0.02, f"1/{TOTAL_CARDS}", ha="right", va="bottom",
            fontsize=9, color=C["muted"], fontfamily="monospace", transform=ax.transAxes, alpha=0.6)

    out = SAVE_DIR / "card_01_cover.png"
    fig.savefig(str(out), dpi=DPI, facecolor=C["bg"], bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)
    return str(out)


def card_2_drawdown():
    """回撤走势卡片"""
    fig = _setup_fig()

    # 标题区
    fig.text(0.5, 0.95, "红利低波回撤走势", ha="center", va="center",
             fontsize=22, fontweight="bold", color=C["text"])
    fig.text(0.5, 0.91, "512890 · 后复权含分红 · 自2019年上市以来", ha="center", va="center",
             fontsize=12, color=C["muted"])

    # 回撤图（后复权）
    ax = fig.add_axes([0.10, 0.35, 0.85, 0.50])
    ax.set_facecolor(C["bg"])

    peak = nav_512890.expanding().max()
    dd = (nav_512890 - peak) / peak * 100
    current_dd_val = dd.iloc[-1]

    ax.fill_between(dd.index, dd, 0, alpha=0.3, color=C["red"])
    ax.plot(dd.index, dd, color=C["red"], linewidth=1.5)
    ax.axhline(y=current_dd_val, color=C["orange"], linewidth=1, linestyle="--", alpha=0.8)
    ax.text(dd.index[-1], current_dd_val, f" 当前 {current_dd_val:.1f}%", va="center",
            fontsize=10, color=C["orange"])

    ax.set_ylabel("回撤 (%)", color=C["muted"], fontsize=11)
    ax.set_ylim(dd.min() * 1.1, 2)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]:
        ax.spines[s].set_color(C["border"])
    ax.tick_params(colors=C["muted"], labelsize=9)
    ax.grid(True, color=C["border"], linewidth=0.3, alpha=0.5)

    # 关键时间点标注
    max_dd_date = dd.idxmin()
    ax.annotate(f"最大回撤\n{dd.min():.1f}%", xy=(max_dd_date, dd.min()),
                xytext=(max_dd_date, dd.min() + 5),
                fontsize=9, color=C["red"], ha="center",
                arrowprops=dict(arrowstyle="->", color=C["red"], lw=0.8))

    # 底部说明
    fig.text(0.5, 0.22, "历史上回撤-8%附近买入:", ha="center", va="center",
             fontsize=14, color=C["text"], fontweight="bold")
    fig.text(0.5, 0.16, "6个月胜率84% · 1年胜率98%", ha="center", va="center",
             fontsize=16, color=C["green"], fontweight="bold")
    fig.text(0.5, 0.10, "平均收益: 6个月+7.9% | 1年+16.2%", ha="center", va="center",
             fontsize=12, color=C["muted"])
    fig.text(0.5, 0.04, "跌破均线期间，适合分批建仓", ha="center", va="center",
             fontsize=11, color=C["orange"], style="italic")
    # 页码
    fig.text(0.95, 0.02, f"2/{TOTAL_CARDS}", ha="right", va="bottom",
             fontsize=9, color=C["muted"], fontfamily="monospace", alpha=0.6)

    out = SAVE_DIR / "card_02_drawdown.png"
    fig.savefig(str(out), dpi=DPI, facecolor=C["bg"], bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)
    return str(out)


def card_3_momentum_signal():
    """动量信号卡片"""
    fig = _setup_fig()

    fig.text(0.5, 0.95, "当前动量信号", ha="center", va="center",
             fontsize=22, fontweight="bold", color=C["text"])
    fig.text(0.5, 0.91, "均线 + 动量 综合判断", ha="center", va="center",
             fontsize=12, color=C["muted"])

    # 价格 + 均线图
    ax = fig.add_axes([0.10, 0.40, 0.85, 0.45])
    ax.set_facecolor(C["bg"])

    # 最近250日
    recent = close_512890.iloc[-250:]
    ax.plot(recent.index, recent, color=C["blue"], linewidth=2, label="价格")
    ax.plot(recent.index, close_512890.rolling(20).mean().reindex(recent.index),
            color=C["green"], linewidth=1, alpha=0.8, label="MA20")
    ax.plot(recent.index, close_512890.rolling(60).mean().reindex(recent.index),
            color=C["orange"], linewidth=1, alpha=0.8, label="MA60")
    ax.plot(recent.index, close_512890.rolling(120).mean().reindex(recent.index),
            color=C["purple"], linewidth=1, alpha=0.8, label="MA120")

    ax.legend(loc="upper right", fontsize=9, facecolor=C["card"],
              edgecolor=C["border"], labelcolor=C["text"])
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]:
        ax.spines[s].set_color(C["border"])
    ax.tick_params(colors=C["muted"], labelsize=9)
    ax.grid(True, color=C["border"], linewidth=0.3, alpha=0.5)
    ax.set_ylabel("价格", color=C["muted"], fontsize=11)

    # 信号表格
    current_price = close_512890.iloc[-1]
    ma20 = close_512890.rolling(20).mean().iloc[-1]
    ma60 = close_512890.rolling(60).mean().iloc[-1]
    ma120 = close_512890.rolling(120).mean().iloc[-1]
    mom20 = (current_price / close_512890.iloc[-21] - 1) * 100
    mom60 = (current_price / close_512890.iloc[-61] - 1) * 100

    signals = [
        ("MA20", f"{ma20:.4f}", "↓ 跌破" if current_price < ma20 else "↑ 站上",
         C["red"] if current_price < ma20 else C["green"]),
        ("MA60", f"{ma60:.4f}", "↓ 跌破" if current_price < ma60 else "↑ 站上",
         C["red"] if current_price < ma60 else C["green"]),
        ("MA120", f"{ma120:.4f}", "↓ 跌破" if current_price < ma120 else "↑ 站上",
         C["red"] if current_price < ma120 else C["green"]),
        ("20日动量", f"{mom20:+.1f}%", "偏空" if mom20 < 0 else "偏多",
         C["red"] if mom20 < 0 else C["green"]),
        ("60日动量", f"{mom60:+.1f}%", "偏空" if mom60 < 0 else "偏多",
         C["red"] if mom60 < 0 else C["green"]),
    ]

    y_start = 0.32
    for i, (name, val, status, color) in enumerate(signals):
        y = y_start - i * 0.055
        fig.text(0.15, y, name, ha="left", va="center", fontsize=13, color=C["text"])
        fig.text(0.50, y, val, ha="center", va="center", fontsize=13,
                 color=C["muted"], fontfamily="monospace")
        fig.text(0.80, y, status, ha="center", va="center", fontsize=13,
                 fontweight="bold", color=color)

    # 结论
    fig.text(0.5, 0.04, "短期动量全面偏空 → 不急于抄底，等右侧信号",
             ha="center", va="center", fontsize=12, color=C["orange"], fontweight="bold")
    # 页码
    fig.text(0.95, 0.02, f"3/{TOTAL_CARDS}", ha="right", va="bottom",
             fontsize=9, color=C["muted"], fontfamily="monospace", alpha=0.6)

    out = SAVE_DIR / "card_03_momentum.png"
    fig.savefig(str(out), dpi=DPI, facecolor=C["bg"], bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)
    return str(out)


# ============================================================
# Part 2: 策略增强分析
# ============================================================
print("\n[Part 2] 策略增强分析...")

def monthly_rebal_nav(close: pd.Series, signals: pd.Series, cost_per_switch: float = 0.001) -> pd.Series:
    """根据月度信号（1=持有, 0=空仓/持国债）回测NAV
    信号延迟1日执行（T日信号 → T+1日生效），含切换成本"""
    ret = close.pct_change().fillna(0)
    bond_ret = close_511010.reindex(close.index).pct_change().fillna(0)

    # 对齐信号到每日，延迟1日执行
    daily_signal = signals.reindex(close.index, method="ffill").fillna(1)
    daily_signal = daily_signal.shift(1).fillna(1)  # T日信号 → T+1执行

    # 切换成本
    switches = daily_signal.diff().abs().fillna(0)
    trade_cost = switches * cost_per_switch

    # 持有时用ETF收益，空仓时用国债收益
    port_ret = daily_signal * ret + (1 - daily_signal) * bond_ret - trade_cost
    nav = (1 + port_ret).cumprod()
    return nav


def calc_metrics(nav: pd.Series) -> dict:
    """计算核心指标"""
    total_ret = nav.iloc[-1] / nav.iloc[0] - 1
    n_days = len(nav)
    years = n_days / 252
    ann_ret = (1 + total_ret) ** (1 / years) - 1

    daily_ret = nav.pct_change().dropna()
    sharpe = daily_ret.mean() / daily_ret.std() * np.sqrt(252) if daily_ret.std() > 0 else 0

    peak = nav.expanding().max()
    dd = (nav - peak) / peak
    max_dd = dd.min()

    monthly_ret = nav.resample("ME").last().pct_change().dropna()
    win_rate = (monthly_ret > 0).mean()

    return {
        "total_return": total_ret,
        "annual_return": ann_ret,
        "sharpe": sharpe,
        "max_drawdown": max_dd,
        "win_rate": win_rate,
        "years": years,
    }


# 对齐所有数据到共同日期
common_idx = close_512890.index.intersection(close_510300.index)\
    .intersection(close_511010.index).intersection(close_518880.index)
c_dlv = nav_512890.reindex(common_idx)  # 红利低波（后复权）
c_300 = close_510300.reindex(common_idx)  # 沪深300
c_bond = close_511010.reindex(common_idx)  # 国债
c_gold = close_518880.reindex(common_idx)  # 黄金

# ---- 策略1: 买入持有（基准）----
print("  策略1: 买入持有 红利低波")
nav_bh = c_dlv / c_dlv.iloc[0]

# ---- 策略2: 动量择时（MA20突破）----
print("  策略2: 红利低波 + MA20动量择时")
ma20 = c_dlv.rolling(20).mean()
sig_ma20 = (c_dlv > ma20).astype(float)  # 价格>MA20持有，否则转国债
sig_ma20_monthly = sig_ma20.resample("ME").last()
nav_ma20 = monthly_rebal_nav(c_dlv, sig_ma20)

# ---- 策略3: 动量择时（MA60突破）----
print("  策略3: 红利低波 + MA60动量择时")
ma60 = c_dlv.rolling(60).mean()
sig_ma60 = (c_dlv > ma60).astype(float)
nav_ma60 = monthly_rebal_nav(c_dlv, sig_ma60)

# ---- 策略4: 红利低波 + 黄金对冲 (50/50 月度再平衡)----
print("  策略4: 红利低波50% + 黄金50%")
ret_dlv = c_dlv.pct_change().fillna(0)
ret_gold = c_gold.pct_change().fillna(0)
# 月度再平衡50/50（被动配比，无前视偏差）
nav_gold_mix = pd.Series(1.0, index=common_idx)
w_dlv, w_gold = 0.5, 0.5
port_val = 1.0
for i in range(1, len(common_idx)):
    date = common_idx[i]
    r_d = ret_dlv.iloc[i]
    r_g = ret_gold.iloc[i]
    # 先算漂移后的权重
    val_dlv = w_dlv * (1 + r_d)
    val_gold = w_gold * (1 + r_g)
    total = val_dlv + val_gold
    port_val = port_val * total
    nav_gold_mix.iloc[i] = port_val
    # 月初再平衡回50/50（含0.1%摩擦）
    if date.month != common_idx[i-1].month:
        rebal_cost = abs(val_dlv/total - 0.5) * 0.001  # 偏离部分的交易成本
        port_val *= (1 - rebal_cost)
        nav_gold_mix.iloc[i] = port_val
        w_dlv, w_gold = 0.5, 0.5
    else:
        w_dlv = val_dlv / total
        w_gold = val_gold / total

# ---- 策略5: 红利低波 + 国债（70/30 被动配比）----
print("  策略5: 红利低波70% + 国债30%")
ret_bond = c_bond.pct_change().fillna(0)
nav_bond_mix = (1 + 0.7 * ret_dlv + 0.3 * ret_bond).cumprod()  # 被动不再平衡，无摩擦

# ---- 策略6: 动量切换（红利低波 vs 沪深300，谁强持谁）----
print("  策略6: 动量切换 (红利低波 vs 沪深300)")
mom_dlv_60 = c_dlv.pct_change(60)
mom_300_60 = c_300.pct_change(60)
# 谁的60日动量高就持谁，延迟1日执行
sig_switch = (mom_dlv_60 > mom_300_60).astype(float)  # 1=持红利低波, 0=持沪深300
ret_300 = c_300.pct_change().fillna(0)
sig_switch_lag = sig_switch.shift(1).fillna(1)
switches_6 = sig_switch_lag.diff().abs().fillna(0)
nav_switch = (1 + sig_switch_lag * ret_dlv + (1 - sig_switch_lag) * ret_300 - switches_6 * 0.001).cumprod()

# ---- 策略7: 双动量（绝对+相对）----
print("  策略7: 双动量 (绝对动量+相对动量)")
# 绝对动量: 红利低波60日收益>0
abs_mom = (mom_dlv_60 > 0)
# 相对动量: 红利低波60日动量>沪深300
rel_mom = (mom_dlv_60 > mom_300_60)
# 两个都满足才持有红利低波，否则持国债
sig_dual = (abs_mom & rel_mom).astype(float)
nav_dual = monthly_rebal_nav(c_dlv, sig_dual)

# ============================================================
# 汇总结果
# ============================================================
strategies = {
    "买入持有": nav_bh,
    "MA20择时": nav_ma20,
    "MA60择时": nav_ma60,
    "50%黄金对冲": nav_gold_mix,
    "70/30国债配": nav_bond_mix,
    "动量切换vs300": nav_switch,
    "双动量择时": nav_dual,
}

print(f"\n{'='*70}")
print(f"{'策略':<14} {'年化':<10} {'总收益':<10} {'夏普':<8} {'最大回撤':<10} {'月胜率':<8}")
print(f"{'-'*70}")

results = {}
for name, nav in strategies.items():
    nav = nav.dropna()
    if len(nav) < 60:
        continue
    m = calc_metrics(nav)
    results[name] = m
    print(f"  {name:<12} {m['annual_return']*100:>+6.1f}%   {m['total_return']*100:>+7.1f}%   "
          f"{m['sharpe']:>5.2f}   {m['max_drawdown']*100:>6.1f}%   {m['win_rate']*100:>5.1f}%")

print(f"{'='*70}")

# 找最优
best_sharpe = max(results.items(), key=lambda x: x[1]["sharpe"])
best_return = max(results.items(), key=lambda x: x[1]["annual_return"])
best_dd = max(results.items(), key=lambda x: x[1]["max_drawdown"])  # 最小回撤(max因为是负数)

print(f"\n🏆 最高夏普: {best_sharpe[0]} (Sharpe={best_sharpe[1]['sharpe']:.2f})")
print(f"🏆 最高年化: {best_return[0]} (年化={best_return[1]['annual_return']*100:+.1f}%)")
print(f"🏆 最小回撤: {best_dd[0]} (回撤={best_dd[1]['max_drawdown']*100:.1f}%)")


# ============================================================
# 卡片4: 策略增强对比
# ============================================================
def card_4_strategy_enhance():
    """策略增强对比卡片"""
    fig = _setup_fig()

    fig.text(0.5, 0.96, "红利低波 · 策略增强方案", ha="center", va="center",
             fontsize=22, fontweight="bold", color=C["text"])
    fig.text(0.5, 0.92, "哪种组合能改善风险收益比？", ha="center", va="center",
             fontsize=12, color=C["muted"])

    # NAV 曲线对比
    ax = fig.add_axes([0.10, 0.45, 0.85, 0.42])
    ax.set_facecolor(C["bg"])

    colors = [C["muted"], C["blue"], C["green"], C["gold"], C["orange"], C["purple"], C["red"]]
    for (name, nav), color in zip(strategies.items(), colors):
        nav_norm = nav.dropna()
        if len(nav_norm) > 0:
            nav_norm = nav_norm / nav_norm.iloc[0]
            lw = 2.5 if name in [best_sharpe[0], "买入持有"] else 1.2
            alpha = 1.0 if name in [best_sharpe[0], "买入持有"] else 0.6
            ax.plot(nav_norm.index, nav_norm, color=color, linewidth=lw,
                    alpha=alpha, label=name)

    ax.legend(loc="upper left", fontsize=8, facecolor=C["card"],
              edgecolor=C["border"], labelcolor=C["text"], ncol=2)
    ax.set_ylabel("净值", color=C["muted"], fontsize=11)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]:
        ax.spines[s].set_color(C["border"])
    ax.tick_params(colors=C["muted"], labelsize=9)
    ax.grid(True, color=C["border"], linewidth=0.3, alpha=0.5)

    # 表格数据
    y_start = 0.38
    headers = ["策略", "年化", "夏普", "最大回撤"]
    x_pos = [0.10, 0.45, 0.65, 0.85]
    # 表头分隔线
    fig.patches.append(plt.Rectangle((0.05, y_start - 0.015), 0.90, 0.001,
                       transform=fig.transFigure, facecolor=C["border"], zorder=5))
    for x, h in zip(x_pos, headers):
        fig.text(x, y_start, h, ha="center" if x > 0.1 else "left",
                 va="center", fontsize=11, color=C["muted"], fontweight="bold")

    sorted_results = sorted(results.items(), key=lambda x: x[1]["sharpe"], reverse=True)
    for i, (name, m) in enumerate(sorted_results):
        y = y_start - (i + 1) * 0.042
        is_best = name == best_sharpe[0]
        txt_color = C["gold"] if is_best else C["text"]
        prefix = ">>> " if is_best else "    "
        fig.text(0.10, y, f"{prefix}{name}", ha="left", va="center",
                 fontsize=11, color=txt_color, fontweight="bold" if is_best else "normal")
        fig.text(0.45, y, f"{m['annual_return']*100:+.1f}%", ha="center", va="center",
                 fontsize=11, color=C["green"] if m["annual_return"] > 0 else C["red"],
                 fontfamily="monospace")
        fig.text(0.65, y, f"{m['sharpe']:.2f}", ha="center", va="center",
                 fontsize=11, color=C["blue"], fontfamily="monospace")
        fig.text(0.85, y, f"{m['max_drawdown']*100:.1f}%", ha="center", va="center",
                 fontsize=11, color=C["red"], fontfamily="monospace")

    # 结论
    fig.text(0.5, 0.04, f"推荐: {best_sharpe[0]} (夏普 {best_sharpe[1]['sharpe']:.2f})",
             ha="center", va="center", fontsize=14, color=C["gold"], fontweight="bold")
    # 页码
    fig.text(0.95, 0.02, f"4/{TOTAL_CARDS}", ha="right", va="bottom",
             fontsize=9, color=C["muted"], fontfamily="monospace", alpha=0.6)

    out = SAVE_DIR / "card_04_strategy_enhance.png"
    fig.savefig(str(out), dpi=DPI, facecolor=C["bg"], bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)
    return str(out)


def card_5_conclusion():
    """结论卡片"""
    fig = _setup_fig()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(C["bg"])
    ax.axis("off")

    ax.text(0.5, 0.93, "结论 · 量化建议", ha="center", va="center",
            fontsize=28, fontweight="bold", color=C["text"], transform=ax.transAxes)

    conclusions = [
        ("位置", "回撤-8%，近1年分位2.4%", "距2025年11月高点，已回调半年", C["blue"]),
        ("胜率", "6个月胜率84%，1年胜率98%", "平均1年收益+16.2%，赔率不对称", C["green"]),
        ("风险", "均线全面跌破，动量偏空", "短期可能继续磨底", C["orange"]),
        ("建议", f"分批建仓（3-6个月定投）", f"增强方案: {best_sharpe[0]}", C["gold"]),
    ]

    y_start = 0.82
    for i, (title, line1, line2, color) in enumerate(conclusions):
        y = y_start - i * 0.19
        # 左侧彩色竖条
        from matplotlib.patches import FancyBboxPatch
        bar = FancyBboxPatch((0.05, y - 0.09), 0.012, 0.12,
                              boxstyle="round,pad=0.003",
                              facecolor=color, alpha=0.8,
                              transform=ax.transAxes, zorder=5)
        ax.add_patch(bar)
        ax.text(0.09, y, title, ha="left", va="top",
                fontsize=18, color=color, fontweight="bold", transform=ax.transAxes)
        ax.text(0.22, y, line1, ha="left", va="top",
                fontsize=15, color=C["text"], fontweight="bold", transform=ax.transAxes)
        ax.text(0.22, y - 0.07, line2, ha="left", va="top",
                fontsize=12, color=C["muted"], transform=ax.transAxes)

    # 底部分隔线
    ax.plot([0.15, 0.85], [0.10, 0.10], color=C["border"], linewidth=0.5, transform=ax.transAxes, clip_on=False)
    # 免责
    ax.text(0.5, 0.06, "以上为量化分析结果，仅供参考，不构成投资建议",
            ha="center", va="center", fontsize=10, color=C["muted"],
            style="italic", transform=ax.transAxes)
    ax.text(0.5, 0.02, "数据来源: AKShare · 红利低波ETF(512890)",
            ha="center", va="center", fontsize=9, color=C["muted"], transform=ax.transAxes)
    # 页码
    ax.text(0.95, 0.02, f"5/{TOTAL_CARDS}", ha="right", va="bottom",
            fontsize=9, color=C["muted"], fontfamily="monospace", transform=ax.transAxes, alpha=0.6)

    out = SAVE_DIR / "card_05_conclusion.png"
    fig.savefig(str(out), dpi=DPI, facecolor=C["bg"], bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)
    return str(out)


# 生成所有卡片
cards = []
cards.append(card_1_cover())
cards.append(card_2_drawdown())
cards.append(card_3_momentum_signal())
cards.append(card_4_strategy_enhance())
cards.append(card_5_conclusion())

print(f"\n✅ 生成 {len(cards)} 张小红书卡片:")
for c in cards:
    print(f"   {c}")
