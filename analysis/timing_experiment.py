"""
择时信号大规模回测实验

系统性测试所有择时信号在沪深300上的表现,
对比买入持有和固定比例基准,
输出结果DataFrame供后续分析与可视化。
"""

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from quant.backtest.engine import BacktestConfig, BacktestEngine
from quant.backtest.metrics import annual_return, calmar, max_drawdown, sharpe, win_rate
from quant.data.index_fetcher import IndexFetcher
from quant.data.macro_fetcher import MacroFetcher
from quant.factors import timing
from quant.strategies.timing_strategy import (
    BuyAndHoldStrategy,
    FixedMixStrategy,
    TimingStrategy,
)

# ═══════════════════════════════════════════════════════════════════
# 实验配置
# ═══════════════════════════════════════════════════════════════════

START_DATE = "2010-01-01"
SPLIT_DATE = "2022-01-01"  # 样本内/外分割线
EQUITY_SYMBOL = "000300"   # 用指数收盘价做择时回测
BOND_SYMBOL = "BOND"       # 简化: 用固定收益率模拟债券

# 实验矩阵: {名称: (择时函数, 参数字典, 调仓频率)}
EXPERIMENTS = {
    # --- 均线择时 ---
    "MA_20": (timing.ma_timing, {"window": 20}, "daily"),
    "MA_60": (timing.ma_timing, {"window": 60}, "daily"),
    "MA_120": (timing.ma_timing, {"window": 120}, "daily"),
    "MA_250": (timing.ma_timing, {"window": 250}, "daily"),
    # --- 双均线 ---
    "DualMA_5_20": (timing.dual_ma_timing, {"fast": 5, "slow": 20}, "daily"),
    "DualMA_10_60": (timing.dual_ma_timing, {"fast": 10, "slow": 60}, "daily"),
    "DualMA_20_120": (timing.dual_ma_timing, {"fast": 20, "slow": 120}, "daily"),
    "DualMA_60_250": (timing.dual_ma_timing, {"fast": 60, "slow": 250}, "daily"),
    # --- 动量择时 ---
    "Mom_20": (timing.momentum_timing, {"window": 20, "threshold": 0.0}, "daily"),
    "Mom_60": (timing.momentum_timing, {"window": 60, "threshold": 0.0}, "daily"),
    "Mom_120": (timing.momentum_timing, {"window": 120, "threshold": 0.0}, "daily"),
    # --- 波动率择时 ---
    "Vol_20": (timing.volatility_timing, {"window": 20, "high_vol": 0.30, "low_vol": 0.15}, "daily"),
    "Vol_60": (timing.volatility_timing, {"window": 60, "high_vol": 0.25, "low_vol": 0.12}, "daily"),
    # --- 布林带 ---
    "Boll_20": (timing.bollinger_timing, {"window": 20, "num_std": 2.0}, "daily"),
    "Boll_60": (timing.bollinger_timing, {"window": 60, "num_std": 1.5}, "daily"),
    # --- 成交量择时 ---
    "Turnover_250": (timing.turnover_timing, {"window": 250, "high_pct": 0.9, "low_pct": 0.1}, "daily"),
}


@dataclass
class ExperimentResult:
    name: str
    period: str  # 'full', 'in_sample', 'out_sample'
    annual_ret: float
    max_dd: float
    sharpe_ratio: float
    calmar_ratio: float
    monthly_win_rate: float
    avg_position: float  # 平均仓位
    trade_count: int  # 仓位切换次数
    nav_series: pd.Series


def create_bond_series(index: pd.DatetimeIndex, annual_yield: float = 0.03) -> pd.Series:
    """模拟债券ETF的价格序列(固定年化收益)"""
    daily_ret = (1 + annual_yield) ** (1 / 252) - 1
    prices = 100 * (1 + daily_ret) ** np.arange(len(index))
    return pd.Series(prices, index=index, name=BOND_SYMBOL)


def run_single_experiment(
    name: str,
    signal_func,
    signal_params: dict,
    rebalance_freq: str,
    prices_df: pd.DataFrame,
    period_label: str = "full",
) -> ExperimentResult:
    """运行单个择时实验"""
    strategy = TimingStrategy(
        signal_func=signal_func,
        signal_params=signal_params,
        equity_symbol=EQUITY_SYMBOL,
        bond_symbol=BOND_SYMBOL,
        rebalance_freq=rebalance_freq,
        signal_delay=1,
        min_change=0.05,
    )

    config = BacktestConfig(rebalance_freq=rebalance_freq)
    engine = BacktestEngine(config)
    result = engine.run(strategy, prices_df, [EQUITY_SYMBOL, BOND_SYMBOL])
    nav = result.nav_series.dropna()

    # 计算平均仓位和换手
    equity_pos = result.positions[EQUITY_SYMBOL] if EQUITY_SYMBOL in result.positions.columns else pd.Series(0)
    total_val = result.nav_series
    position_ratio = (equity_pos * prices_df[EQUITY_SYMBOL]) / total_val
    position_ratio = position_ratio.fillna(0)
    avg_pos = position_ratio.mean()

    # 换仓次数: 仓位变化>10%的次数
    pos_changes = position_ratio.diff().abs()
    trade_count = int((pos_changes > 0.1).sum())

    return ExperimentResult(
        name=name,
        period=period_label,
        annual_ret=annual_return(nav),
        max_dd=max_drawdown(nav),
        sharpe_ratio=sharpe(nav),
        calmar_ratio=calmar(nav),
        monthly_win_rate=win_rate(nav),
        avg_position=avg_pos,
        trade_count=trade_count,
        nav_series=nav,
    )


def run_baseline(prices_df: pd.DataFrame, period_label: str = "full") -> list[ExperimentResult]:
    """运行基准策略"""
    results = []

    # Buy & Hold
    bh_strategy = BuyAndHoldStrategy(symbol=EQUITY_SYMBOL)
    config = BacktestConfig(rebalance_freq="monthly")
    engine = BacktestEngine(config)
    bh_result = engine.run(bh_strategy, prices_df, [EQUITY_SYMBOL, BOND_SYMBOL])
    nav = bh_result.nav_series.dropna()
    results.append(ExperimentResult(
        name="BuyHold", period=period_label,
        annual_ret=annual_return(nav), max_dd=max_drawdown(nav),
        sharpe_ratio=sharpe(nav), calmar_ratio=calmar(nav),
        monthly_win_rate=win_rate(nav), avg_position=1.0,
        trade_count=0, nav_series=nav,
    ))

    # 60/40 Fixed Mix
    mix_strategy = FixedMixStrategy(
        equity_symbol=EQUITY_SYMBOL, bond_symbol=BOND_SYMBOL, equity_ratio=0.6
    )
    mix_result = engine.run(mix_strategy, prices_df, [EQUITY_SYMBOL, BOND_SYMBOL])
    nav = mix_result.nav_series.dropna()
    results.append(ExperimentResult(
        name="Mix_60_40", period=period_label,
        annual_ret=annual_return(nav), max_dd=max_drawdown(nav),
        sharpe_ratio=sharpe(nav), calmar_ratio=calmar(nav),
        monthly_win_rate=win_rate(nav), avg_position=0.6,
        trade_count=0, nav_series=nav,
    ))

    return results


def run_all_experiments() -> tuple[pd.DataFrame, dict[str, pd.Series]]:
    """
    运行全部实验

    Returns:
        results_df: 所有实验指标汇总表
        nav_dict: {name: nav_series} 净值曲线字典
    """
    print("=" * 60)
    print("A股择时策略大规模回测实验")
    print("=" * 60)

    # 1. 获取数据
    print("\n[1/4] 获取数据...")
    idx_fetcher = IndexFetcher()
    hs300 = idx_fetcher.fetch(EQUITY_SYMBOL, start=START_DATE)
    macro_fetcher = MacroFetcher()
    market_vol = macro_fetcher.get_market_volume("sh000001")

    # 构建价格DataFrame
    equity_prices = hs300["close"]
    bond_prices = create_bond_series(equity_prices.index)
    prices_df = pd.DataFrame({
        EQUITY_SYMBOL: equity_prices,
        BOND_SYMBOL: bond_prices,
    }).dropna()

    print(f"  数据区间: {prices_df.index[0].date()} ~ {prices_df.index[-1].date()}")
    print(f"  总交易日: {len(prices_df)}")

    # 分割样本内/外
    in_sample = prices_df[prices_df.index < SPLIT_DATE]
    out_sample = prices_df[prices_df.index >= SPLIT_DATE]
    print(f"  样本内: {in_sample.index[0].date()} ~ {in_sample.index[-1].date()} ({len(in_sample)} days)")
    print(f"  样本外: {out_sample.index[0].date()} ~ {out_sample.index[-1].date()} ({len(out_sample)} days)")

    # 2. 运行基准
    print("\n[2/4] 运行基准策略...")
    all_results = []
    nav_dict = {}

    for period_label, period_data in [("full", prices_df), ("in_sample", in_sample), ("out_sample", out_sample)]:
        baselines = run_baseline(period_data, period_label)
        all_results.extend(baselines)
        if period_label == "full":
            for b in baselines:
                nav_dict[b.name] = b.nav_series

    # 3. 运行择时实验
    print("\n[3/4] 运行择时实验...")
    total = len(EXPERIMENTS)
    for i, (name, (func, params, freq)) in enumerate(EXPERIMENTS.items(), 1):
        print(f"  [{i}/{total}] {name}...", end=" ")

        # 成交量择时需要特殊处理: 用市场成交量作为输入
        if func == timing.turnover_timing:
            # 将成交量数据注入到prices_df中作为信号源
            # TimingStrategy默认用equity_symbol的价格，这里需要hack一下
            # 简化方案: 直接计算信号并用包装函数
            vol_data = market_vol["volume"].reindex(prices_df.index).ffill()
            _params = params.copy()
            _params["_volume_override"] = vol_data
            # 用一个wrapper函数
            def _turnover_wrapper(prices, window=250, high_pct=0.9, low_pct=0.1, _volume_override=None, **kw):
                if _volume_override is not None:
                    return timing.turnover_timing(_volume_override, window=window, high_pct=high_pct, low_pct=low_pct)
                return timing.turnover_timing(prices, window=window, high_pct=high_pct, low_pct=low_pct)

            for period_label, period_data in [("full", prices_df), ("in_sample", in_sample), ("out_sample", out_sample)]:
                vol_period = vol_data.reindex(period_data.index).ffill()
                p = {k: v for k, v in params.items()}
                p["_volume_override"] = vol_period
                r = run_single_experiment(name, _turnover_wrapper, p, freq, period_data, period_label)
                all_results.append(r)
                if period_label == "full":
                    nav_dict[name] = r.nav_series
        else:
            for period_label, period_data in [("full", prices_df), ("in_sample", in_sample), ("out_sample", out_sample)]:
                r = run_single_experiment(name, func, params, freq, period_data, period_label)
                all_results.append(r)
                if period_label == "full":
                    nav_dict[name] = r.nav_series

        print(f"done")

    # 4. 汇总结果
    print("\n[4/4] 汇总结果...")
    results_df = pd.DataFrame([
        {
            "name": r.name,
            "period": r.period,
            "annual_return": r.annual_ret,
            "max_drawdown": r.max_dd,
            "sharpe": r.sharpe_ratio,
            "calmar": r.calmar_ratio,
            "win_rate": r.monthly_win_rate,
            "avg_position": r.avg_position,
            "trade_count": r.trade_count,
        }
        for r in all_results
    ])

    return results_df, nav_dict


def print_summary(results_df: pd.DataFrame):
    """打印结果摘要"""
    print("\n" + "=" * 80)
    print("实验结果汇总 (全样本)")
    print("=" * 80)

    full = results_df[results_df["period"] == "full"].copy()
    full = full.sort_values("sharpe", ascending=False)

    print(f"\n{'策略':<18} {'年化收益':>8} {'最大回撤':>8} {'Sharpe':>8} {'Calmar':>8} {'月胜率':>8} {'换手次数':>8}")
    print("-" * 80)
    for _, row in full.iterrows():
        print(f"{row['name']:<18} {row['annual_return']:>7.1%} {row['max_drawdown']:>7.1%} "
              f"{row['sharpe']:>8.2f} {row['calmar']:>8.2f} {row['win_rate']:>7.0%} {row['trade_count']:>8.0f}")

    # 样本内外对比
    print("\n\n" + "=" * 80)
    print("样本内 vs 样本外 Sharpe 对比")
    print("=" * 80)

    in_s = results_df[results_df["period"] == "in_sample"].set_index("name")["sharpe"]
    out_s = results_df[results_df["period"] == "out_sample"].set_index("name")["sharpe"]
    compare = pd.DataFrame({"in_sample": in_s, "out_sample": out_s}).dropna()
    compare["diff"] = compare["out_sample"] - compare["in_sample"]
    compare = compare.sort_values("out_sample", ascending=False)

    print(f"\n{'策略':<18} {'样本内Sharpe':>12} {'样本外Sharpe':>12} {'差值':>8}")
    print("-" * 60)
    for name, row in compare.iterrows():
        print(f"{name:<18} {row['in_sample']:>12.2f} {row['out_sample']:>12.2f} {row['diff']:>8.2f}")


def bootstrap_sharpe_ci(nav: pd.Series, n_boot: int = 1000, ci: float = 0.95) -> tuple[float, float, float]:
    """
    Bootstrap Sharpe比率置信区间

    Returns: (sharpe, lower_bound, upper_bound)
    """
    daily_ret = nav.pct_change().dropna().values
    n = len(daily_ret)
    sharpes = []
    for _ in range(n_boot):
        sample = np.random.choice(daily_ret, size=n, replace=True)
        sr = (sample.mean() * 252 - 0.02) / (sample.std() * np.sqrt(252))
        sharpes.append(sr)
    sharpes = np.array(sharpes)
    alpha = (1 - ci) / 2
    return float(np.mean(sharpes)), float(np.percentile(sharpes, alpha * 100)), float(np.percentile(sharpes, (1 - alpha) * 100))


if __name__ == "__main__":
    # 运行全部实验
    results_df, nav_dict = run_all_experiments()

    # 打印摘要
    print_summary(results_df)

    # Bootstrap检验 top策略
    print("\n\n" + "=" * 80)
    print("Bootstrap Sharpe 置信区间 (95%)")
    print("=" * 80)
    full = results_df[results_df["period"] == "full"].sort_values("sharpe", ascending=False)
    top_names = full["name"].head(8).tolist()
    print(f"\n{'策略':<18} {'Sharpe':>8} {'95% CI Lower':>12} {'95% CI Upper':>12} {'显著>0?':>8}")
    print("-" * 65)
    for name in top_names:
        if name in nav_dict:
            sr, lo, hi = bootstrap_sharpe_ci(nav_dict[name])
            sig = "✓" if lo > 0 else "✗"
            print(f"{name:<18} {sr:>8.2f} {lo:>12.2f} {hi:>12.2f} {sig:>8}")

    # 保存结果
    output_dir = Path("output/timing-research")
    output_dir.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(output_dir / "experiment_results.csv", index=False)

    # 保存净值
    nav_df = pd.DataFrame(nav_dict)
    nav_df.to_csv(output_dir / "nav_curves.csv")

    print(f"\n\n结果已保存到 {output_dir}/")
    print("  - experiment_results.csv")
    print("  - nav_curves.csv")
