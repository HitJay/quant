"""动量因子 — 计算N日价格动量"""

import numpy as np
import pandas as pd


def momentum(prices: pd.Series, window: int = 63) -> float:
    """
    计算动量：过去window天的收益率
    
    Args:
        prices: 价格序列
        window: 回溯窗口（默认63=约3个月交易日）
    
    Returns:
        动量值，如0.15表示涨了15%，NaN表示数据不足
    """
    if len(prices) < window + 1:
        return np.nan
    return float(prices.iloc[-1] / prices.iloc[-(window + 1)] - 1.0)


def momentum_scores(
    price_df: pd.DataFrame,
    symbols: list[str],
    date,
    window: int = 63,
) -> dict[str, float]:
    """
    批量计算多个标的的动量得分
    
    Args:
        price_df: 价格矩阵，列=标的
        symbols: 要计算的标的列表
        date: 计算截止日期
        window: 回溯窗口
    
    Returns:
        {symbol: momentum_score}，缺失的标的不会出现在结果中
    """
    cutoff = price_df.index.get_loc(date) if isinstance(date, (str, pd.Timestamp)) else date
    if isinstance(cutoff, slice):
        return {}

    window_data = price_df.iloc[max(0, cutoff - window) : cutoff + 1]

    scores: dict[str, float] = {}
    for sym in symbols:
        if sym not in window_data.columns:
            continue
        close = window_data[sym].dropna()
        if len(close) >= window + 1:
            scores[sym] = momentum(close, window)

    return scores
