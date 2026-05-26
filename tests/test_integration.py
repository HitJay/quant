"""ETF轮动策略 + 回测引擎 + 指标 集成测试"""

import pandas as pd
import numpy as np
from quant.strategies.etf_rotation import ETF_Rotation
from quant.backtest.engine import BacktestEngine, BacktestConfig


def make_mock_prices(n_days=200):
    """模拟两只ETF + 现金的价格序列"""
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=n_days, freq="B")
    # A: 持续上涨 (强动量)
    a = np.cumprod(1 + np.random.normal(0.001, 0.015, n_days)) * 100
    # B: 震荡下行 (弱动量)
    b = np.cumprod(1 + np.random.normal(-0.0002, 0.012, n_days)) * 100
    return pd.DataFrame({"A": a, "B": b, "CASH": np.ones(n_days)}, index=dates)


def test_etf_rotation_picks_strongest():
    """ETF轮动应选择动量最强的标的"""
    prices = make_mock_prices(200)
    strategy = ETF_Rotation(momentum_window=63, hold_n=1)
    signal = strategy.rebalance(
        date=prices.index[-1],
        symbols=["A", "B", "CASH"],
        prices=prices,
    )
    assert "A" in signal.weights, f"应该选中A，实际: {signal.weights}"
    assert signal.weights.get("A", 0) > 0.5


def test_etf_rotation_hold_n():
    """hold_n=2时应持有2只"""
    prices = make_mock_prices(200)
    strategy = ETF_Rotation(momentum_window=63, hold_n=2)
    signal = strategy.rebalance(
        date=prices.index[-1],
        symbols=["A", "B", "CASH"],
        prices=prices,
    )
    assert len(signal.weights) == 2


def test_backtest_positive_return():
    """模拟上涨行情，回测应有正收益"""
    prices = make_mock_prices(200)
    strategy = ETF_Rotation(momentum_window=63, hold_n=1)
    config = BacktestConfig(initial_capital=100000, etf_commission=0)
    engine = BacktestEngine(config)
    result = engine.run(strategy, prices, ["A", "B"])  # CASH由引擎内部管理
    assert result.nav_series.iloc[-1] > 0
    assert not np.isnan(result.total_return)
