"""波动率因子（低波动=高分）"""

import numpy as np
import pandas as pd


def historical_volatility(prices: pd.Series, window: int = 63) -> float:
    """历史波动率（年化），低波动=好"""
    if len(prices) < window + 1:
        return np.nan
    returns = prices.pct_change().dropna().iloc[-window:]
    if len(returns) < 2:
        return np.nan
    return float(returns.std() * np.sqrt(252))


def volatility_score(prices: pd.Series, window: int = 63) -> float:
    """低波动得分：波动率越低，得分越高"""
    vol = historical_volatility(prices, window)
    if np.isnan(vol) or vol == 0:
        return np.nan
    return 1.0 / vol  # 倒数，波动越低得分越高
