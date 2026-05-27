"""商品轮动策略深度分析 — 长时间回测 + 2026年1月回撤 (v2)"""

import os
for k in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']:
    os.environ.pop(k, None)

import sys
sys.path.insert(0, 'src')

import pandas as pd
import numpy as np
from quant.data.fetcher import ETFDataFetcher
from quant.data.cache import Cache
from quant.strategies.commodity_rotation import CommodityRotation
from quant.backtest.engine import BacktestEngine, BacktestConfig
from quant.backtest.metrics import annual_return, max_drawdown, sharpe, calmar
from quant.universe.config import UniverseConfig

EXPANDED_COMMODITY = {
    "518880": "黄金ETF",
    "159985": "豆粕ETF",
    "159866": "有色金属ETF",
    "161226": "白银LOF",
    "501018": "南方原油",
    "159981": "能源化工ETF",
}
DEFENSE_ETF = "511260"

fetcher = ETFDataFetcher()
cache = Cache()

print("=" * 60)
print("商品轮动策略深度分析")
print("=" * 60)

# ── 1. 获取数据 ──
print("\n[1/5] 获取数据...")
all_symbols = list(EXPANDED_COMMODITY.keys()) + [DEFENSE_ETF]
frames = {}
for sym in all_symbols:
    df = fetcher.fetch_or_cache(sym, "2013-01-01", "2026-05-27", cache=cache, force=True)
    frames[sym] = df[["close"]].copy()
    print(f"  {sym} {EXPANDED_COMMODITY.get(sym, '国债ETF')}: "
          f"{df.index[0].strftime('%Y-%m-%d')} ~ {df.index[-1].strftime('%Y-%m-%d')}")

# ── 2. 构建价格矩阵 (只保留所有标的都有数据的区间) ──
print("\n[2/5] 构建价格矩阵...")
prices_full = pd.DataFrame({sym: df["close"] for sym, df in frames.items()})
prices_full = prices_full.sort_index()

# 找到所有商品ETF都有数据的最早日期 (国债从2017开始，所以需要替代方案)
# 2015-2017期间用黄金ETF做防御替代(因为国债ETF还没上市)
# 或者从2017-09开始(所有数据齐全)

# 方案: 从2017-09开始完整回测 (国债+白银+原油+黄金+豆粕)
# 另外做一个纯原始3只的回测 2021-2026

# ── 完整池可用起始日 ──
available_dates = {}
for sym in all_symbols:
    first_valid = prices_full[sym].first_valid_index()
    if first_valid is not None:
        available_dates[sym] = first_valid
        print(f"  {sym} 可用起始: {first_valid.strftime('%Y-%m-%d')}")

# 找所有商品ETF+国债都有数据的日期
all_commodity_syms = list(EXPANDED_COMMODITY.keys())
earliest_all = max(available_dates[s] for s in all_commodity_syms + [DEFENSE_ETF])
print(f"\n  全部6只商品+国债可用起始: {earliest_all.strftime('%Y-%m-%d')}")

# 3只原始 + 国债
orig_syms = ["518880", "159985", "159866"]
earliest_orig = max(available_dates[s] for s in orig_syms + [DEFENSE_ETF])
print(f"  原始3只商品+国债可用起始: {earliest_orig.strftime('%Y-%m-%d')}")

# ── 3. 分析A: 原始3只, 2021-05 ~ 2026-05 (验证与原报告一致) ──
print(f"\n[3/5] 分析A: 原始3只回测 (验证基线)")
print("-" * 60)

prices_orig = prices_full.loc["2021-08-01":, orig_syms + [DEFENSE_ETF]].ffill().dropna()
print(f"  数据: {prices_orig.index[0].strftime('%Y-%m-%d')} ~ {prices_orig.index[-1].strftime('%Y-%m-%d')}, {len(prices_orig)} days")

universe_orig = UniverseConfig(etf_codes=orig_syms)
strat_orig = CommodityRotation(
    momentum_window=63, hold_n=1, defense_etf=DEFENSE_ETF, universe=universe_orig,
)
engine = BacktestEngine(BacktestConfig())
result_orig = engine.run(strat_orig, prices_orig, orig_syms)
nav_orig = result_orig.nav_series.dropna()

if len(nav_orig) > 10:
    print(f"  年化: {annual_return(nav_orig)*100:+.1f}%  回撤: {max_drawdown(nav_orig)*100:.1f}%  夏普: {sharpe(nav_orig):.2f}")
    print(f"  总收益: {result_orig.total_return*100:+.1f}%")
else:
    print("  NAV数据不足!")
    print(f"  NAV前10: {nav_orig.head(10).to_dict()}")

# ── 4. 分析B: 扩展6只, 2021-05 ~ 2026-05 (同期对比) ──
print(f"\n[4/5] 分析B: 扩展6只 vs 原始3只 (同期对比)")
print("-" * 60)

prices_exp = prices_full.loc["2021-08-01":, all_commodity_syms + [DEFENSE_ETF]].ffill().dropna()
print(f"  数据: {prices_exp.index[0].strftime('%Y-%m-%d')} ~ {prices_exp.index[-1].strftime('%Y-%m-%d')}")

universe_exp = UniverseConfig(etf_codes=all_commodity_syms)
strat_exp = CommodityRotation(
    momentum_window=63, hold_n=1, defense_etf=DEFENSE_ETF, universe=universe_exp,
)
result_exp = engine.run(strat_exp, prices_exp, all_commodity_syms)
nav_exp = result_exp.nav_series.dropna()

if len(nav_exp) > 10 and len(nav_orig) > 10:
    print(f"\n  {'指标':<10} {'原始3只':>10} {'扩展6只':>10}")
    print(f"  {'─'*32}")
    ar_orig, ar_exp = annual_return(nav_orig), annual_return(nav_exp)
    mdd_orig, mdd_exp = max_drawdown(nav_orig), max_drawdown(nav_exp)
    sp_orig, sp_exp = sharpe(nav_orig), sharpe(nav_exp)
    cm_orig, cm_exp = calmar(nav_orig), calmar(nav_exp)
    print(f"  {'年化收益':<8} {ar_orig*100:>+9.1f}% {ar_exp*100:>+9.1f}%")
    print(f"  {'最大回撤':<8} {mdd_orig*100:>9.1f}% {mdd_exp*100:>9.1f}%")
    print(f"  {'夏普比率':<8} {sp_orig:>10.2f} {sp_exp:>10.2f}")
    print(f"  {'卡玛比率':<8} {cm_orig:>10.2f} {cm_exp:>10.2f}")
    print(f"  {'总收益':<8} {(nav_orig.iloc[-1]/nav_orig.iloc[0]-1)*100:>+9.1f}% {(nav_exp.iloc[-1]/nav_exp.iloc[0]-1)*100:>+9.1f}%")
    
    # 分年度
    print(f"\n  分年度对比:")
    for yr in range(2022, 2027):
        n_o = nav_orig.loc[f"{yr}"]
        n_e = nav_exp.loc[f"{yr}"]
        if len(n_o) > 1 and len(n_e) > 1:
            r_o = (n_o.iloc[-1]/n_o.iloc[0]-1)*100
            r_e = (n_e.iloc[-1]/n_e.iloc[0]-1)*100
            print(f"    {yr}: 原始 {r_o:+6.1f}%  扩展 {r_e:+6.1f}%")

# ── 5. 分析C: 黄金弱势期 + 2026年1月回撤 ──
print(f"\n[5/5] 分析C: 黄金弱势期 & 2026年1月回撤")
print("=" * 60)

# 用原始3只的NAV（因为涵盖2021-2026完整数据）
nav = nav_orig if len(nav_orig) > len(nav_exp) else nav_exp

# 黄金弱势期
print(f"\n  黄金弱势期 (策略 vs 黄金买入持有):")
for label, s, e in [
    ("2021H2 黄金震荡",   "2021-08-01", "2021-12-31"),
    ("2022 加息周期",     "2022-01-01", "2022-12-31"),
    ("2023H2 黄金盘整",   "2023-06-01", "2023-12-31"),
]:
    sub = nav.loc[s:e]
    gold_sub = prices_full["518880"].loc[s:e].dropna()
    if len(sub) < 5 or len(gold_sub) < 5:
        continue
    str_ret = (sub.iloc[-1]/sub.iloc[0]-1)*100
    str_mdd = max_drawdown(sub)*100
    g_ret = (gold_sub.iloc[-1]/gold_sub.iloc[0]-1)*100
    print(f"    {label}:")
    print(f"      策略: {str_ret:+.1f}%  (回撤 {str_mdd:.1f}%)")
    print(f"      黄金: {g_ret:+.1f}%")

# 2026年1月回撤分析
print(f"\n  2026年1月黄金暴跌分析:")
print(f"  {'─'*50}")

# 看 2025-11 ~ 2026-03
window_nav = nav.loc["2025-11-01":"2026-04-30"]
window_gold = prices_full["518880"].loc["2025-11-01":"2026-04-30"].dropna()

if len(window_nav) > 5:
    # 策略回撤
    peak = window_nav.expanding().max()
    dd = (window_nav - peak) / peak
    worst_idx = dd.idxmin()
    worst_dd = dd.min()
    peak_idx = window_nav.loc[:worst_idx].idxmax()
    
    print(f"  策略:")
    print(f"    峰值: {peak_idx.strftime('%Y-%m-%d')}  NAV={window_nav[peak_idx]:,.0f}")
    print(f"    谷底: {worst_idx.strftime('%Y-%m-%d')}  NAV={window_nav[worst_idx]:,.0f}")
    print(f"    回撤: {worst_dd*100:.1f}%")
    
    # 黄金回撤
    if len(window_gold) > 5:
        g_peak = window_gold.expanding().max()
        g_dd = (window_gold - g_peak) / g_peak
        g_worst = g_dd.idxmin()
        g_peak_idx = window_gold.loc[:g_worst].idxmax()
        
        print(f"  黄金:")
        print(f"    峰值: {g_peak_idx.strftime('%Y-%m-%d')}  价格={window_gold[g_peak_idx]:.4f}")
        print(f"    谷底: {g_worst.strftime('%Y-%m-%d')}  价格={window_gold[g_worst]:.4f}")
        print(f"    回撤: {g_dd.min()*100:.1f}%")
    
    # 月度明细
    print(f"\n  月度收益:")
    monthly_nav = nav.resample("ME").last()
    monthly_ret = monthly_nav.pct_change().dropna()
    for dt in pd.date_range("2025-11-01", "2026-03-31", freq="ME"):
        if dt in monthly_ret.index:
            r = monthly_ret[dt]
            emoji = "🟩" if r > 0 else "🟥"
            print(f"    {dt.strftime('%Y-%m')}: {r*100:+6.1f}% {emoji}")

    # 持仓变化
    print(f"\n  持仓切换:")
    prices_for_strat = prices_orig if len(nav_orig) > len(nav_exp) else prices_exp
    syms_for_strat = orig_syms if len(nav_orig) > len(nav_exp) else all_commodity_syms
    strat_for_display = strat_orig if len(nav_orig) > len(nav_exp) else strat_exp
    
    prev_held = None
    for i, date in enumerate(prices_for_strat.index):
        if date < pd.Timestamp("2025-11-01") or date > pd.Timestamp("2026-04-30"):
            continue
        if i == 0 or date.month != prices_for_strat.index[i-1].month:
            sig = strat_for_display.rebalance(date, syms_for_strat, prices_for_strat.loc[:date])
            held = ", ".join(f"{EXPANDED_COMMODITY.get(s,s)}({w:.0%})" for s, w in sig.weights.items())
            if held != prev_held:
                print(f"    {date.strftime('%Y-%m-%d')}: → {held}")
                prev_held = held

print(f"\n{'='*60}")
print("分析完成!")
