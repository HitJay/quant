import numpy as np
import pandas as pd
from quant.factors.momentum import momentum, momentum_scores


def test_momentum_upward():
    """上涨趋势：动量应为正"""
    prices = pd.Series([10.0, 11.0, 12.0, 13.0, 14.0, 15.0])
    result = momentum(prices, window=5)
    assert result > 0.3
    assert abs(result - 0.5) < 0.02  # (15-10)/10 = 0.5


def test_momentum_downward():
    """下跌趋势：动量应为负"""
    prices = pd.Series([15.0, 14.0, 13.0, 12.0, 11.0, 10.0])
    result = momentum(prices, window=5)
    assert result < -0.2
    assert abs(result - (-1 / 3)) < 0.02  # (10-15)/15 ≈ -0.333


def test_momentum_insufficient_data():
    """数据不足时返回NaN"""
    prices = pd.Series([10.0, 11.0])  # 只有2个点，窗口需要6个
    result = momentum(prices, window=5)
    assert np.isnan(result)


def test_momentum_scores_ranking():
    """批量动量排序：涨得多的排前面"""
    prices = pd.DataFrame(
        {
            "A": np.linspace(10, 20, 100),  # +100%
            "B": np.linspace(10, 15, 100),  # +50%
            "C": np.linspace(10, 8, 100),  # -20%
        },
        index=pd.date_range("2024-01-01", periods=100),
    )

    scores = momentum_scores(prices, ["A", "B", "C"], prices.index[-1], window=63)
    ordered = sorted(scores, key=scores.get, reverse=True)
    assert ordered[0] == "A"
    assert ordered[1] == "B"
    assert ordered[2] == "C"
    assert scores["A"] > scores["B"] > scores["C"]
