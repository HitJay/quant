import numpy as np
from quant.factors.value import pe_inverse, pb_inverse, dividend_yield
from quant.factors.quality import roe
from quant.factors.volatility import historical_volatility
from quant.factors.cb import dual_low, conversion_premium
from quant.factors.macro import erp, fed_signal, fed_weight


def test_pe_inverse():
    assert abs(pe_inverse(10) - 0.1) < 0.001
    assert pe_inverse(-5) is None
    assert pe_inverse(0) is None


def test_dividend_yield():
    assert abs(dividend_yield(2.0, 40.0) - 0.05) < 0.001


def test_roe():
    assert abs(roe(100, 1000) - 0.1) < 0.001


def test_volatility():
    import pandas as pd
    prices = pd.Series([100.0] * 70 + [101.0])  # 几乎无波动
    vol = historical_volatility(prices, window=63)
    assert vol < 0.05  # 年化波动应该很低


def test_dual_low():
    # 价格120 + 溢价率5% → 双低=125
    assert abs(dual_low(120, 5) - 125) < 0.01


def test_conversion_premium():
    assert abs(conversion_premium(110, 100) - 0.1) < 0.01  # 溢价10%
    assert conversion_premium(100, 0) == 999


def test_erp():
    assert abs(erp(6.0, 3.0) - 3.0) < 0.01  # E/P 6% - 国债3% = 3%


def test_fed_signal():
    assert fed_signal(3.0) == "aggressive"
    assert fed_signal(1.0) == "neutral"
    assert fed_signal(-1.0) == "defensive"


def test_fed_weight():
    assert fed_weight(3.0) == 0.9
    assert fed_weight(-1.0) == 0.2
    w = fed_weight(1.0)
    assert 0.2 < w < 0.9
