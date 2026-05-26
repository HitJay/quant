"""行业ETF轮动策略 — 选择动量最强的行业"""

from quant.strategies.base import Strategy, Signal
from quant.factors.momentum import momentum_scores
from quant.universe.config import UniverseConfig


class IndustryRotation(Strategy):
    """每月持有动量最强的N个行业ETF"""

    def __init__(
        self,
        momentum_window: int = 63,
        hold_n: int = 3,
        universe: UniverseConfig | None = None,
    ):
        self.momentum_window = momentum_window
        self.hold_n = hold_n
        self.universe = universe or UniverseConfig(etf_categories=["INDUSTRY"])

    def get_symbols(self) -> list[str]:
        return self.universe.get_symbols()

    def rebalance(self, date, symbols: list[str], prices) -> Signal:
        scores = momentum_scores(prices, symbols, date, self.momentum_window)
        if not scores:
            return Signal(date=str(date), weights={})
        ranked = sorted(scores, key=scores.get, reverse=True)
        top = ranked[: self.hold_n]
        weight = 1.0 / len(top)
        return Signal(
            date=str(date),
            weights={s: weight for s in top},
            metadata={"scores": {s: round(v, 4) for s, v in scores.items()}},
        )
