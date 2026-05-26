"""商品ETF轮动策略"""

from quant.strategies.base import Strategy, Signal
from quant.factors.momentum import momentum_scores
from quant.universe.config import UniverseConfig


class CommodityRotation(Strategy):
    """每月持有动量最强的N个商品ETF + 止损"""

    def __init__(
        self,
        momentum_window: int = 63,
        hold_n: int = 1,
        stop_loss_pct: float = -0.08,  # 月跌幅>8%止损
        defense_etf: str = "511260",    # 防御时转国债ETF
        universe: UniverseConfig | None = None,
    ):
        self.momentum_window = momentum_window
        self.hold_n = hold_n
        self.stop_loss_pct = stop_loss_pct
        self.defense_etf = defense_etf
        self.universe = universe or UniverseConfig(etf_categories=["COMMODITY"])

    def get_symbols(self) -> list[str]:
        return self.universe.get_symbols()

    def rebalance(self, date, symbols: list[str], prices) -> Signal:
        scores = momentum_scores(prices, symbols, date, self.momentum_window)

        # 全部动量为负 → 防御模式
        if scores and all(v < 0 for v in scores.values()):
            return Signal(
                date=str(date),
                weights={self.defense_etf: 1.0},
                metadata={"mode": "defense", "reason": "all negative momentum"},
            )

        if not scores:
            return Signal(date=str(date), weights={self.defense_etf: 1.0})

        ranked = sorted(scores, key=scores.get, reverse=True)
        top = ranked[: self.hold_n]
        weight = 1.0 / len(top)
        return Signal(
            date=str(date),
            weights={s: weight for s in top},
        )
