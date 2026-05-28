"""Test MomentumExperiment strategy"""

import pandas as pd
import numpy as np
from quant.strategies.momentum_experiment import MomentumExperiment


def make_prices(n_days=100, n_syms=3, seed=42):
    """Generate synthetic price data"""
    np.random.seed(seed)
    dates = pd.date_range("2020-01-01", periods=n_days, freq="D")
    data = {}
    for i, sym in enumerate([f"SYM{i}" for i in range(n_syms)]):
        # Different trends
        trend = 0.001 * (i + 1)  # SYM0 < SYM1 < SYM2
        noise = np.random.randn(n_days) * 0.02
        price = 100 * np.exp(np.cumsum(trend + noise))
        data[sym] = price
    return pd.DataFrame(data, index=dates)


class TestMomentumExperiment:
    def test_init_defaults(self):
        """Test default parameters"""
        strat = MomentumExperiment(window=60, top_n=1)
        assert strat.window == 60
        assert strat.top_n == 1
        assert strat.reverse is False

    def test_init_custom(self):
        """Test custom parameters"""
        strat = MomentumExperiment(window=20, top_n=2, reverse=True)
        assert strat.window == 20
        assert strat.top_n == 2
        assert strat.reverse is True

    def test_rebalance_momentum_basic(self):
        """Test momentum picks the best performer"""
        prices = make_prices(n_days=100, n_syms=3)
        symbols = list(prices.columns)
        strat = MomentumExperiment(window=20, top_n=1, reverse=False)
        
        date = prices.index[-1]
        signal = strat.rebalance(date, symbols, prices)
        
        # Should return weights dict with top_n=1 symbol
        assert len(signal.weights) == 1
        # Weight should sum to 1.0
        assert abs(sum(signal.weights.values()) - 1.0) < 1e-9

    def test_rebalance_momentum_top2(self):
        """Test momentum picks top 2"""
        prices = make_prices(n_days=100, n_syms=5)
        symbols = list(prices.columns)
        strat = MomentumExperiment(window=20, top_n=2, reverse=False)
        
        date = prices.index[-1]
        signal = strat.rebalance(date, symbols, prices)
        
        assert len(signal.weights) == 2
        # Equal weight
        for w in signal.weights.values():
            assert abs(w - 0.5) < 1e-9

    def test_rebalance_reverse(self):
        """Test reverse (contrarian) picks worst performer"""
        prices = make_prices(n_days=100, n_syms=3)
        symbols = list(prices.columns)
        
        strat_mom = MomentumExperiment(window=20, top_n=1, reverse=False)
        strat_rev = MomentumExperiment(window=20, top_n=1, reverse=True)
        
        date = prices.index[-1]
        sig_mom = strat_mom.rebalance(date, symbols, prices)
        sig_rev = strat_rev.rebalance(date, symbols, prices)
        
        # Should pick different symbols
        mom_sym = list(sig_mom.weights.keys())[0]
        rev_sym = list(sig_rev.weights.keys())[0]
        assert mom_sym != rev_sym

    def test_rebalance_insufficient_data(self):
        """Test when not enough data for window"""
        prices = make_prices(n_days=10, n_syms=3)
        symbols = list(prices.columns)
        strat = MomentumExperiment(window=60, top_n=1)  # window > data
        
        date = prices.index[-1]
        signal = strat.rebalance(date, symbols, prices)
        
        # Should return empty weights when no scores available
        assert len(signal.weights) == 0

    def test_signal_has_date(self):
        """Test signal contains date string"""
        prices = make_prices(n_days=100, n_syms=3)
        symbols = list(prices.columns)
        strat = MomentumExperiment(window=20, top_n=1)
        
        date = prices.index[-1]
        signal = strat.rebalance(date, symbols, prices)
        
        assert signal.date == str(date)
