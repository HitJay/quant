"""择时因子单元测试"""

import numpy as np
import pandas as pd
import pytest

from quant.factors.timing import (
    ma_timing,
    dual_ma_timing,
    momentum_timing,
    volatility_timing,
    bollinger_timing,
    pe_percentile_timing,
    erp_timing,
    turnover_timing,
    margin_timing,
    composite_vote,
    composite_mean,
    composite_weighted,
    apply_hysteresis,
    signal_delay,
    min_holding_filter,
)


@pytest.fixture
def prices():
    """合成价格序列: 先涨后跌再涨"""
    dates = pd.date_range("2020-01-01", periods=500, freq="B")
    np.random.seed(42)
    # 构造明确趋势: 涨200天, 跌150天, 涨150天
    trend = np.concatenate([
        np.linspace(0, 0.5, 200),
        np.linspace(0.5, -0.2, 150),
        np.linspace(-0.2, 0.3, 150),
    ])
    noise = np.random.randn(500) * 0.01
    log_prices = trend + noise.cumsum() * 0.1
    return pd.Series(100 * np.exp(log_prices), index=dates)


@pytest.fixture
def flat_prices():
    """平稳无趋势价格"""
    dates = pd.date_range("2020-01-01", periods=300, freq="B")
    return pd.Series(100.0, index=dates)


class TestMATiming:
    def test_output_range(self, prices):
        sig = ma_timing(prices, window=20)
        valid = sig.dropna()
        assert valid.min() >= 0.0
        assert valid.max() <= 1.0

    def test_binary_output(self, prices):
        sig = ma_timing(prices, window=20)
        valid = sig.dropna()
        assert set(valid.unique()).issubset({0.0, 1.0})

    def test_warmup_period(self, prices):
        sig = ma_timing(prices, window=60)
        # MA rolling产生NaN时, 比较结果为False=0.0
        # 验证启动期后信号正常
        assert len(sig.dropna()) == len(prices)

    def test_uptrend_signal(self):
        """持续上涨应该全部是1"""
        dates = pd.date_range("2020-01-01", periods=100, freq="B")
        prices = pd.Series(np.linspace(100, 200, 100), index=dates)
        sig = ma_timing(prices, window=20)
        # 启动期后应该全是1
        assert sig.iloc[20:].mean() == 1.0

    def test_downtrend_signal(self):
        """持续下跌应该全部是0"""
        dates = pd.date_range("2020-01-01", periods=100, freq="B")
        prices = pd.Series(np.linspace(200, 100, 100), index=dates)
        sig = ma_timing(prices, window=20)
        assert sig.iloc[20:].mean() == 0.0


class TestDualMATiming:
    def test_output_range(self, prices):
        sig = dual_ma_timing(prices, fast=10, slow=60)
        valid = sig.dropna()
        assert valid.min() >= 0.0
        assert valid.max() <= 1.0

    def test_fast_gt_slow_in_uptrend(self):
        dates = pd.date_range("2020-01-01", periods=200, freq="B")
        prices = pd.Series(np.linspace(100, 300, 200), index=dates)
        sig = dual_ma_timing(prices, fast=10, slow=60)
        # 稳定上涨后快均线>慢均线
        assert sig.iloc[70:].mean() == 1.0


class TestMomentumTiming:
    def test_output_range(self, prices):
        sig = momentum_timing(prices, window=20)
        valid = sig.dropna()
        assert set(valid.unique()).issubset({0.0, 1.0})

    def test_positive_return_signal(self):
        dates = pd.date_range("2020-01-01", periods=100, freq="B")
        prices = pd.Series(np.linspace(100, 150, 100), index=dates)
        sig = momentum_timing(prices, window=20)
        assert sig.iloc[20:].mean() == 1.0


class TestVolatilityTiming:
    def test_output_range(self, prices):
        sig = volatility_timing(prices, window=20)
        valid = sig.dropna()
        assert valid.min() >= 0.0
        assert valid.max() <= 1.0

    def test_flat_is_low_vol(self, flat_prices):
        """平稳价格=低波动=满仓"""
        # 完全平稳价格 pct_change=0, vol=0 < low_vol → 1.0
        sig = volatility_timing(flat_prices, window=20)
        valid = sig.dropna()
        assert valid.mean() == 1.0


class TestBollingerTiming:
    def test_output_range(self, prices):
        sig = bollinger_timing(prices, window=20)
        valid = sig.dropna()
        assert valid.min() >= 0.0
        assert valid.max() <= 1.0


class TestPEPercentileTiming:
    def test_low_pe_bullish(self):
        """低PE百分位→看多"""
        dates = pd.date_range("2010-01-01", periods=3000, freq="B")
        # PE先高后低
        pe = pd.Series(np.concatenate([
            np.linspace(20, 30, 2500),  # 先逐渐升高
            np.full(500, 10),            # 最后突然很低
        ]), index=dates)
        sig = pe_percentile_timing(pe, window=2520)
        # 最后500天PE极低, 信号应该接近1
        assert sig.iloc[-100:].mean() > 0.8

    def test_output_range(self):
        dates = pd.date_range("2010-01-01", periods=3000, freq="B")
        pe = pd.Series(15 + 5 * np.sin(np.linspace(0, 10, 3000)), index=dates)
        sig = pe_percentile_timing(pe, window=2520)
        valid = sig.dropna()
        assert valid.min() >= 0.0
        assert valid.max() <= 1.0


class TestERPTiming:
    def test_high_erp_bullish(self):
        """高ERP (股票便宜) → 满仓"""
        dates = pd.date_range("2020-01-01", periods=100, freq="B")
        pe = pd.Series(10.0, index=dates)    # E/P = 10%
        bond = pd.Series(2.0, index=dates)   # 国债2%
        # ERP = 10% - 2% = 8% >> 3% → 满仓
        sig = erp_timing(pe, bond, aggressive=3.0, defensive=0.0)
        assert sig.mean() == 1.0

    def test_low_erp_bearish(self):
        """低ERP (股票贵) → 空仓"""
        dates = pd.date_range("2020-01-01", periods=100, freq="B")
        pe = pd.Series(50.0, index=dates)    # E/P = 2%
        bond = pd.Series(4.0, index=dates)   # 国债4%
        # ERP = 2% - 4% = -2% << 0% → 空仓
        sig = erp_timing(pe, bond, aggressive=3.0, defensive=0.0)
        assert sig.mean() == 0.0


class TestTurnoverTiming:
    def test_output_range(self, prices):
        # Use volume-like data
        dates = prices.index
        volume = pd.Series(np.random.lognormal(20, 1, len(dates)), index=dates)
        sig = turnover_timing(volume, window=250)
        valid = sig.dropna()
        assert valid.min() >= 0.0
        assert valid.max() <= 1.0


class TestMarginTiming:
    def test_growing_margin_bullish(self):
        """融资余额增长→看多"""
        dates = pd.date_range("2020-01-01", periods=200, freq="B")
        margin = pd.Series(np.linspace(1e12, 1.5e12, 200), index=dates)
        sig = margin_timing(margin, window=60)
        # 持续增长, 60日增速 > 5%, 后期应为1
        assert sig.iloc[-50:].mean() > 0.8


class TestComposite:
    def test_vote(self, prices):
        s1 = ma_timing(prices, 20)
        s2 = dual_ma_timing(prices, 10, 60)
        s3 = momentum_timing(prices, 20)
        result = composite_vote([s1, s2, s3])
        valid = result.dropna()
        assert set(valid.unique()).issubset({0.0, 1.0})

    def test_mean_range(self, prices):
        s1 = ma_timing(prices, 20)
        s2 = volatility_timing(prices, 20)
        result = composite_mean([s1, s2])
        valid = result.dropna()
        assert valid.min() >= 0.0
        assert valid.max() <= 1.0

    def test_weighted_sum_to_one(self, prices):
        s1 = pd.Series(1.0, index=prices.index)
        s2 = pd.Series(0.0, index=prices.index)
        result = composite_weighted([s1, s2], weights=[0.7, 0.3])
        assert abs(result.iloc[0] - 0.7) < 1e-10


class TestFilters:
    def test_hysteresis(self):
        """滞后过滤减少切换次数"""
        dates = pd.date_range("2020-01-01", periods=20, freq="B")
        # 在阈值附近波动的信号
        raw = pd.Series([0.3, 0.4, 0.6, 0.7, 0.5, 0.4, 0.3, 0.2,
                         0.6, 0.7, 0.8, 0.5, 0.4, 0.3, 0.6, 0.7,
                         0.8, 0.9, 0.4, 0.3], index=dates)
        filtered = apply_hysteresis(raw, on_threshold=0.6, off_threshold=0.4)
        # 过滤后切换次数应该少于原始信号
        raw_switches = (raw > 0.5).astype(int).diff().abs().sum()
        filt_switches = filtered.diff().abs().sum()
        assert filt_switches <= raw_switches

    def test_signal_delay(self, prices):
        sig = ma_timing(prices, 20)
        delayed = signal_delay(sig, delay=2)
        # 延迟后前2个额外NaN
        assert delayed.iloc[0:2].isna().all()
        # 延迟后的值=原来前移2位的值(按位置比较)
        assert (delayed.values[22:] == sig.values[20:-2]).all()

    def test_min_holding(self):
        dates = pd.date_range("2020-01-01", periods=20, freq="B")
        # 快速切换信号
        raw = pd.Series([1, 1, 0, 1, 1, 0, 0, 1, 1, 1,
                         0, 0, 0, 1, 0, 1, 1, 1, 0, 0], index=dates, dtype=float)
        filtered = min_holding_filter(raw, min_days=3)
        # 过滤后切换应更少
        raw_switches = raw.diff().abs().sum()
        filt_switches = filtered.diff().abs().sum()
        assert filt_switches <= raw_switches
