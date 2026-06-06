"""择时策略 — 基于仓位信号在权益与债券/现金之间切换"""

import pandas as pd
from quant.strategies.base import Strategy, Signal
from quant.factors import timing


class TimingStrategy(Strategy):
    """
    通用择时策略:
    - 计算择时信号 (0.0~1.0)
    - signal=1.0 → 100% equity_etf
    - signal=0.0 → 100% bond_etf (或 cash)

    支持任意择时因子函数
    """

    def __init__(
        self,
        signal_func,
        signal_params: dict | None = None,
        equity_symbol: str = "510300",
        bond_symbol: str = "511010",
        rebalance_freq: str = "daily",
        signal_delay: int = 1,
        min_change: float = 0.1,
    ):
        """
        Args:
            signal_func: 择时因子函数, 签名 func(prices, **params) -> pd.Series
            signal_params: 因子参数字典
            equity_symbol: 权益ETF代码
            bond_symbol: 债券ETF代码 (None则用现金)
            rebalance_freq: 调仓频率 'daily'|'weekly'|'monthly'
            signal_delay: 信号延迟天数(防look-ahead)
            min_change: 最小仓位变化阈值(避免频繁微调)
        """
        self.signal_func = signal_func
        self.signal_params = signal_params or {}
        self.equity_symbol = equity_symbol
        self.bond_symbol = bond_symbol
        self.rebalance_freq = rebalance_freq
        self.signal_delay = signal_delay
        self.min_change = min_change
        self._last_weight = None
        self._signal_cache = None

    def rebalance(self, date, symbols: list[str], prices: pd.DataFrame) -> Signal:
        """根据择时信号决定权益/债券配比"""
        # 计算信号 (用权益标的价格)
        if self.equity_symbol in prices.columns:
            equity_prices = prices[self.equity_symbol].dropna()
        else:
            # 如果prices只有一列，直接用
            equity_prices = prices.iloc[:, 0].dropna()

        # 计算全历史信号
        raw_signal = self.signal_func(equity_prices, **self.signal_params)

        # 应用延迟
        if self.signal_delay > 0:
            raw_signal = timing.signal_delay(raw_signal, self.signal_delay)

        # 取当日信号
        if date not in raw_signal.index:
            # 找最近的信号日
            valid = raw_signal.loc[:date].dropna()
            if len(valid) == 0:
                equity_weight = 0.5  # 无信号时半仓
            else:
                equity_weight = float(valid.iloc[-1])
        else:
            val = raw_signal.loc[date]
            equity_weight = float(val) if not pd.isna(val) else 0.5

        # 限制在 [0, 1]
        equity_weight = max(0.0, min(1.0, equity_weight))

        # 最小变化阈值
        if self._last_weight is not None:
            if abs(equity_weight - self._last_weight) < self.min_change:
                equity_weight = self._last_weight

        self._last_weight = equity_weight

        # 构建权重
        weights = {}
        if equity_weight > 0:
            weights[self.equity_symbol] = equity_weight
        if self.bond_symbol and equity_weight < 1.0:
            weights[self.bond_symbol] = 1.0 - equity_weight
        # 如果没有bond_symbol, 剩余部分自动变成cash(引擎处理)

        return Signal(
            date=str(date),
            weights=weights,
            metadata={
                "signal_value": equity_weight,
                "signal_func": self.signal_func.__name__,
            },
        )


class BuyAndHoldStrategy(Strategy):
    """买入持有基准策略"""

    def __init__(self, symbol: str = "510300"):
        self.symbol = symbol

    def rebalance(self, date, symbols: list[str], prices: pd.DataFrame) -> Signal:
        return Signal(date=str(date), weights={self.symbol: 1.0})


class FixedMixStrategy(Strategy):
    """固定比例股债混合基准 (如 60/40)"""

    def __init__(self, equity_symbol: str = "510300", bond_symbol: str = "511010", equity_ratio: float = 0.6):
        self.equity_symbol = equity_symbol
        self.bond_symbol = bond_symbol
        self.equity_ratio = equity_ratio

    def rebalance(self, date, symbols: list[str], prices: pd.DataFrame) -> Signal:
        return Signal(
            date=str(date),
            weights={
                self.equity_symbol: self.equity_ratio,
                self.bond_symbol: 1.0 - self.equity_ratio,
            },
        )
