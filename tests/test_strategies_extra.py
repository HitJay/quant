"""新增策略集成测试"""
import pandas as pd
import numpy as np
from quant.strategies.industry_rotation import IndustryRotation
from quant.strategies.commodity_rotation import CommodityRotation
from quant.strategies.cb_dual_low import CB_DualLow
from quant.universe.config import UniverseConfig


def make_prices(n=200):
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=n, freq="B")
    return pd.DataFrame(
        {
            "512880": np.cumprod(1 + np.random.normal(0.001, 0.02, n)) * 100,
            "512690": np.cumprod(1 + np.random.normal(0.0005, 0.015, n)) * 100,
            "159995": np.cumprod(1 + np.random.normal(-0.0002, 0.025, n)) * 100,
        },
        index=dates,
    )


def test_industry_rotation():
    prices = make_prices()
    s = IndustryRotation(momentum_window=63, hold_n=2)
    sig = s.rebalance(prices.index[-1], ["512880", "512690", "159995"], prices)
    assert len(sig.weights) == 2


def test_commodity_rotation_defense():
    """全部下跌时触发防御模式"""
    dates = pd.date_range("2024-01-01", periods=100, freq="B")
    prices = pd.DataFrame(
        {
            "518880": np.linspace(10, 8, 100),  # 持续下跌
            "159985": np.linspace(10, 7, 100),
            "511260": np.ones(100),
        },
        index=dates,
    )
    s = CommodityRotation(momentum_window=20, defense_etf="511260")
    sig = s.rebalance(prices.index[-1], ["518880", "159985", "511260"], prices)
    assert "511260" in sig.weights  # 防御模式


def test_cb_dual_low():
    """可转债双低选便宜的"""
    cb_data = [
        {"code": "110001", "close": 105, "conversion_premium_pct": 3},   # 双低=108
        {"code": "110002", "close": 120, "conversion_premium_pct": 2},   # 双低=122
        {"code": "110003", "close": 108, "conversion_premium_pct": 2},   # 双低=110
        {"code": "110004", "close": 150, "conversion_premium_pct": 5},   # 超过max_price
    ]
    s = CB_DualLow(max_price=130, hold_n=2)
    sig = s.rebalance("2024-01-01", cb_data, None)
    assert "110001" in sig.weights  # 最便宜
    assert "110004" not in sig.weights  # 超过130
    assert len(sig.weights) == 2
