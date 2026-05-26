"""策略基类与信号"""

from dataclasses import dataclass, field


@dataclass
class Signal:
    """调仓信号"""
    date: str
    weights: dict[str, float] = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)


class Strategy:
    """策略基类"""
    def rebalance(self, date, symbols: list[str], prices) -> Signal:
        raise NotImplementedError
