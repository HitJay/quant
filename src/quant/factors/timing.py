"""
择时因子库 — 将各类信号统一为 position_signal ∈ [0.0, 1.0]

0.0 = 空仓/纯债
1.0 = 满仓权益

所有函数签名统一:
    func(prices: pd.Series, **params) -> pd.Series
    返回与 prices 同 index 的信号序列
"""

import numpy as np
import pandas as pd


# ═══════════════════════════════════════════════════════════════════
# 第一类: 技术面择时 (Price-based)
# ═══════════════════════════════════════════════════════════════════


def ma_timing(prices: pd.Series, window: int = 200) -> pd.Series:
    """
    均线择时: 价格 > MA(N) → 1.0, 否则 → 0.0

    经典策略: 200日均线是最常见的牛熊分界线
    """
    ma = prices.rolling(window=window, min_periods=window).mean()
    signal = (prices > ma).astype(float)
    return signal


def dual_ma_timing(prices: pd.Series, fast: int = 20, slow: int = 60) -> pd.Series:
    """
    双均线交叉: MA(fast) > MA(slow) → 1.0

    金叉做多, 死叉做空
    """
    ma_fast = prices.rolling(window=fast, min_periods=fast).mean()
    ma_slow = prices.rolling(window=slow, min_periods=slow).mean()
    signal = (ma_fast > ma_slow).astype(float)
    return signal


def momentum_timing(prices: pd.Series, window: int = 60, threshold: float = 0.0) -> pd.Series:
    """
    动量择时: N日收益率 > threshold → 1.0

    threshold=0 即 "只要过去N天是涨的就满仓"
    """
    returns = prices.pct_change(periods=window)
    signal = (returns > threshold).astype(float)
    return signal


def volatility_timing(prices: pd.Series, window: int = 20, high_vol: float = 0.30, low_vol: float = 0.15) -> pd.Series:
    """
    波动率择时: 低波满仓, 高波空仓, 中间线性

    逻辑: 高波动环境风险大, 降低仓位
    high_vol/low_vol 为年化波动率阈值
    """
    daily_ret = prices.pct_change()
    rolling_vol = daily_ret.rolling(window=window, min_periods=window).std() * np.sqrt(252)

    signal = pd.Series(index=prices.index, dtype=float)
    signal[rolling_vol <= low_vol] = 1.0
    signal[rolling_vol >= high_vol] = 0.0
    # 线性插值
    mid_mask = (rolling_vol > low_vol) & (rolling_vol < high_vol)
    signal[mid_mask] = 1.0 - (rolling_vol[mid_mask] - low_vol) / (high_vol - low_vol)
    return signal


def bollinger_timing(prices: pd.Series, window: int = 20, num_std: float = 2.0) -> pd.Series:
    """
    布林带择时:
    - 价格在中轨以上 → 1.0
    - 跌破下轨 → 0.0
    - 中轨到下轨之间线性衰减
    """
    ma = prices.rolling(window=window, min_periods=window).mean()
    std = prices.rolling(window=window, min_periods=window).std()
    lower = ma - num_std * std

    signal = pd.Series(index=prices.index, dtype=float)
    signal[prices >= ma] = 1.0
    signal[prices <= lower] = 0.0
    mid_mask = (prices < ma) & (prices > lower)
    signal[mid_mask] = (prices[mid_mask] - lower[mid_mask]) / (ma[mid_mask] - lower[mid_mask])
    return signal


def adx_timing(prices: pd.Series, high: pd.Series, low: pd.Series, window: int = 14, threshold: float = 25.0) -> pd.Series:
    """
    ADX趋势强度择时:
    - ADX > threshold 且趋势向上 → 1.0
    - ADX < 20 → 0.5 (震荡市减半仓)

    需要 high/low 数据
    """
    # True Range
    prev_close = prices.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)

    # +DM, -DM
    up_move = high - high.shift(1)
    down_move = low.shift(1) - low
    plus_dm = pd.Series(np.where((up_move > down_move) & (up_move > 0), up_move, 0), index=prices.index)
    minus_dm = pd.Series(np.where((down_move > up_move) & (down_move > 0), down_move, 0), index=prices.index)

    # Smoothed
    atr = tr.rolling(window=window, min_periods=window).mean()
    plus_di = 100 * plus_dm.rolling(window=window, min_periods=window).mean() / atr
    minus_di = 100 * minus_dm.rolling(window=window, min_periods=window).mean() / atr

    # ADX
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    adx = dx.rolling(window=window, min_periods=window).mean()

    # Signal: ADX strong + uptrend
    signal = pd.Series(0.5, index=prices.index)  # default: half position
    signal[(adx > threshold) & (plus_di > minus_di)] = 1.0  # strong uptrend
    signal[(adx > threshold) & (plus_di < minus_di)] = 0.0  # strong downtrend
    return signal


# ═══════════════════════════════════════════════════════════════════
# 第二类: 估值面择时 (Valuation-based)
# ═══════════════════════════════════════════════════════════════════


def pe_percentile_timing(pe_series: pd.Series, window: int = 2520, low_pct: float = 0.3, high_pct: float = 0.7) -> pd.Series:
    """
    PE百分位择时:
    - PE处于历史低位(< low_pct分位) → 满仓
    - PE处于历史高位(> high_pct分位) → 空仓
    - 中间线性

    window: 回溯窗口(默认10年≈2520交易日)
    """
    pct_rank = pe_series.rolling(window=window, min_periods=252).apply(
        lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=False
    )

    signal = pd.Series(index=pe_series.index, dtype=float)
    signal[pct_rank <= low_pct] = 1.0
    signal[pct_rank >= high_pct] = 0.0
    mid_mask = (pct_rank > low_pct) & (pct_rank < high_pct)
    signal[mid_mask] = 1.0 - (pct_rank[mid_mask] - low_pct) / (high_pct - low_pct)
    return signal


def erp_timing(pe_series: pd.Series, bond_yield_series: pd.Series, aggressive: float = 3.0, defensive: float = 0.0) -> pd.Series:
    """
    股债性价比(ERP)择时:
    ERP = E/P - 10Y国债收益率
    - ERP > aggressive → 满仓(股票极便宜)
    - ERP < defensive → 空仓(债券更有吸引力)
    - 中间线性

    pe_series: 指数PE(TTM)
    bond_yield_series: 10年国债收益率(%)
    """
    earnings_yield = 100.0 / pe_series  # E/P in %
    erp = earnings_yield - bond_yield_series

    # 对齐index
    erp = erp.dropna()

    signal = pd.Series(index=erp.index, dtype=float)
    signal[erp >= aggressive] = 1.0
    signal[erp <= defensive] = 0.0
    mid_mask = (erp > defensive) & (erp < aggressive)
    signal[mid_mask] = (erp[mid_mask] - defensive) / (aggressive - defensive)
    return signal


# ═══════════════════════════════════════════════════════════════════
# 第三类: 情绪/资金面择时 (Sentiment/Flow)
# ═══════════════════════════════════════════════════════════════════


def turnover_timing(volume: pd.Series, window: int = 250, high_pct: float = 0.9, low_pct: float = 0.1) -> pd.Series:
    """
    成交量/换手率择时:
    - 极低成交(< low_pct分位) → 满仓(市场冷清=底部信号)
    - 极高成交(> high_pct分位) → 空仓(过热=顶部信号)
    - 中间线性

    volume: 市场日成交量/额序列
    """
    # 用对数成交量, 消除趋势
    log_vol = np.log(volume.replace(0, np.nan)).dropna()
    pct_rank = log_vol.rolling(window=window, min_periods=60).apply(
        lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=False
    )

    signal = pd.Series(index=pct_rank.index, dtype=float)
    signal[pct_rank <= low_pct] = 1.0
    signal[pct_rank >= high_pct] = 0.0
    mid_mask = (pct_rank > low_pct) & (pct_rank < high_pct)
    # 反向: 成交越大越看空
    signal[mid_mask] = 1.0 - (pct_rank[mid_mask] - low_pct) / (high_pct - low_pct)
    return signal


def margin_timing(margin_balance: pd.Series, window: int = 60, threshold: float = 0.05) -> pd.Series:
    """
    融资余额变化率择时:
    - 融资余额N日增速 > threshold → 做多(资金入场)
    - 增速 < -threshold → 减仓(资金离场)
    - 中间线性

    注意: 融资余额过快增长也可能是过热信号, 这里先用简单版本
    """
    growth = margin_balance.pct_change(periods=window)

    signal = pd.Series(index=growth.index, dtype=float)
    signal[growth >= threshold] = 1.0
    signal[growth <= -threshold] = 0.0
    mid_mask = (growth > -threshold) & (growth < threshold)
    signal[mid_mask] = (growth[mid_mask] + threshold) / (2 * threshold)
    return signal


# ═══════════════════════════════════════════════════════════════════
# 第四类: 复合择时 (Composite)
# ═══════════════════════════════════════════════════════════════════


def composite_vote(signals: list[pd.Series], threshold: float = 0.5) -> pd.Series:
    """
    多信号投票:
    将各信号二值化(>0.5=1, else=0), 统计多数派

    threshold: 多数比例阈值
    """
    df = pd.concat(signals, axis=1).dropna()
    binary = (df > 0.5).astype(float)
    vote_ratio = binary.mean(axis=1)
    signal = (vote_ratio >= threshold).astype(float)
    return signal


def composite_mean(signals: list[pd.Series]) -> pd.Series:
    """
    信号均值: 对所有信号取平均, 保留连续仓位
    """
    df = pd.concat(signals, axis=1).dropna()
    return df.mean(axis=1)


def composite_weighted(signals: list[pd.Series], weights: list[float]) -> pd.Series:
    """
    加权复合信号: sum(signal_i * weight_i) / sum(weights)
    """
    df = pd.concat(signals, axis=1).dropna()
    w = np.array(weights) / np.sum(weights)
    return (df * w).sum(axis=1)


# ═══════════════════════════════════════════════════════════════════
# 辅助工具
# ═══════════════════════════════════════════════════════════════════


def apply_hysteresis(signal: pd.Series, on_threshold: float = 0.6, off_threshold: float = 0.4) -> pd.Series:
    """
    滞后过滤: 避免信号在阈值附近频繁切换

    - 当前空仓, 信号 > on_threshold → 开仓
    - 当前持仓, 信号 < off_threshold → 平仓
    """
    result = pd.Series(index=signal.index, dtype=float)
    position = 0.0
    for i, val in enumerate(signal.values):
        if np.isnan(val):
            result.iloc[i] = np.nan
            continue
        if position == 0.0 and val >= on_threshold:
            position = 1.0
        elif position == 1.0 and val <= off_threshold:
            position = 0.0
        result.iloc[i] = position
    return result


def signal_delay(signal: pd.Series, delay: int = 1) -> pd.Series:
    """
    信号延迟: 防止look-ahead bias
    实际交易中T日产生信号, T+delay日才能执行
    """
    return signal.shift(delay)


def min_holding_filter(signal: pd.Series, min_days: int = 5) -> pd.Series:
    """
    最短持仓期过滤: 避免过于频繁的交易
    信号切换后至少持续 min_days 天才允许下次切换
    """
    result = signal.copy()
    last_switch = -min_days
    prev_val = np.nan

    for i in range(len(result)):
        val = result.iloc[i]
        if np.isnan(val):
            continue
        if not np.isnan(prev_val) and val != prev_val:
            if i - last_switch < min_days:
                result.iloc[i] = prev_val  # 不允许切换
            else:
                last_switch = i
                prev_val = val
        elif np.isnan(prev_val):
            prev_val = val
            last_switch = i

    return result
