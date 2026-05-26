"""绩效指标计算"""

import numpy as np
import pandas as pd


def annual_return(nav: pd.Series) -> float:
    """年化收益率"""
    years = (nav.index[-1] - nav.index[0]).days / 365.25
    if years < 0.01:
        return 0.0
    total = nav.iloc[-1] / nav.iloc[0] - 1
    return float((1 + total) ** (1 / years) - 1)


def max_drawdown(nav: pd.Series) -> float:
    """最大回撤"""
    peak = nav.expanding().max()
    dd = (nav - peak) / peak
    return float(abs(dd.min()))


def sharpe(nav: pd.Series, risk_free: float = 0.02) -> float:
    """夏普比率"""
    daily_ret = nav.pct_change().dropna()
    if len(daily_ret) < 2 or daily_ret.std() == 0:
        return 0.0
    excess = daily_ret.mean() * 252 - risk_free
    vol = daily_ret.std() * np.sqrt(252)
    return float(excess / vol)


def calmar(nav: pd.Series) -> float:
    """卡玛比率 = 年化收益 / 最大回撤"""
    ann = annual_return(nav)
    mdd = max_drawdown(nav)
    return float(ann / mdd) if mdd > 0 else 0.0


def win_rate(nav: pd.Series) -> float:
    """月度胜率"""
    monthly = nav.resample("ME").last().pct_change().dropna()
    if len(monthly) == 0:
        return 0.0
    return float((monthly > 0).sum() / len(monthly))
