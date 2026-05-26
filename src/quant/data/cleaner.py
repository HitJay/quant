"""数据清洗工具"""

import pandas as pd
import numpy as np


def mark_suspended(df: pd.DataFrame, volume_col: str = "volume") -> pd.Series:
    """标记停牌日（成交量为0或NaN）"""
    if volume_col not in df.columns:
        return pd.Series(False, index=df.index)
    return (df[volume_col].isna()) | (df[volume_col] == 0)


def fill_forward(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """前向填充缺失值"""
    df = df.copy()
    for col in cols:
        if col in df.columns:
            df[col] = df[col].ffill()
    return df


def align_to_trading_days(df: pd.DataFrame, calendar: pd.DatetimeIndex) -> pd.DataFrame:
    """对齐到交易日历"""
    return df.reindex(calendar)
