"""回测引擎"""

from dataclasses import dataclass
import pandas as pd
import numpy as np


@dataclass
class BacktestConfig:
    initial_capital: float = 1_000_000
    etf_commission: float = 0.0001
    stamp_duty: float = 0.0005
    stock_commission: float = 0.0003
    min_commission: float = 5.0
    slippage: float = 0.001
    cash_symbol: str = "CASH"
    rebalance_freq: str = "monthly"  # 'daily', 'weekly', 'monthly'


@dataclass
class BacktestResult:
    nav_series: pd.Series
    positions: pd.DataFrame
    trades: list
    initial_capital: float

    @property
    def final_value(self) -> float:
        return float(self.nav_series.iloc[-1])

    @property
    def total_return(self) -> float:
        return self.final_value / self.initial_capital - 1


class BacktestEngine:
    def __init__(self, config: BacktestConfig | None = None):
        self.config = config or BacktestConfig()

    def _should_rebalance(self, i: int, date, dates) -> bool:
        """判断是否需要调仓"""
        if i == 0:
            return True
        freq = self.config.rebalance_freq
        if freq == "daily":
            return True
        elif freq == "weekly":
            return date.weekday() < dates[i - 1].weekday() or (date - dates[i - 1]).days > 5
        else:  # monthly
            return date.month != dates[i - 1].month

    def run(self, strategy, prices: pd.DataFrame, symbols: list[str]) -> BacktestResult:
        dates = prices.index
        nav = pd.Series(index=dates, dtype=float)
        all_symbols = symbols + [self.config.cash_symbol]
        positions = pd.DataFrame(0.0, index=dates, columns=all_symbols)
        trades: list[dict] = []

        cash = self.config.initial_capital
        holdings = {s: 0.0 for s in all_symbols}
        holdings[self.config.cash_symbol] = self.config.initial_capital

        current_weights: dict[str, float] = {}

        for i, date in enumerate(dates):
            # 根据调仓频率决定是否重新生成信号
            if self._should_rebalance(i, date, dates):
                signal = strategy.rebalance(date, symbols, prices.loc[:date])
                current_weights = signal.weights
                # 将信号中出现的新标的加入 all_symbols 和 positions
                for s in current_weights:
                    if s not in all_symbols and s != self.config.cash_symbol:
                        all_symbols.append(s)
                        positions[s] = 0.0

            # 获取当前价格（包括策略信号中引用的所有标的）
            current_prices = {s: prices.loc[date, s] for s in prices.columns}
            current_prices[self.config.cash_symbol] = 1.0

            # 计算总市值
            total_value = sum(
                holdings.get(s, 0) * current_prices.get(s, 0)
                for s in all_symbols
                if not np.isnan(current_prices.get(s, 0))
            )

            # 调仓：现金清空，按目标权重分配给交易标的
            if current_weights:
                for s in all_symbols:
                    holdings[s] = 0.0
                for s, w in current_weights.items():
                    if s in current_prices and w > 0:
                        holdings[s] = (total_value * w) / current_prices[s]
                # 剩余归现金
                allocated = sum(current_weights.values())
                holdings[self.config.cash_symbol] = total_value * max(0, 1 - allocated)

            # 重新计算总价值
            total_value = sum(
                holdings.get(s, 0) * current_prices.get(s, 0)
                for s in all_symbols
                if not np.isnan(current_prices.get(s, 0))
            )
            nav[date] = total_value

            for s in all_symbols:
                positions.loc[date, s] = holdings.get(s, 0)

        return BacktestResult(
            nav_series=nav,
            positions=positions,
            trades=trades,
            initial_capital=self.config.initial_capital,
        )
