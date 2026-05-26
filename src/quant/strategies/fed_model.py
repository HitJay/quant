"""FED模型 — 股债性价比驱动的动态仓位管理"""

from quant.strategies.base import Strategy, Signal
from quant.factors.macro import erp, fed_weight


class FEDModel(Strategy):
    """
    FED模型：根据股权风险溢价(ERP)动态调整权益仓位

    ERP = 沪深300 PE倒数(E/P) - 10年国债收益率
    ERP > 2% → 权益激进(90%)
    ERP < 0% → 权益防御(20%)
    中间 → 线性插值
    """

    def __init__(
        self,
        equity_etf: str = "510300",
        bond_etf: str = "511260",
        cash_etf: str = "511990",
        aggressive_threshold: float = 2.0,
        defensive_threshold: float = 0.0,
    ):
        self.equity_etf = equity_etf
        self.bond_etf = bond_etf
        self.cash_etf = cash_etf
        self.aggressive = aggressive_threshold
        self.defensive = defensive_threshold

    def rebalance(self, date, symbols, prices, pe: float, bond_yield: float) -> Signal:
        """
        pe: 沪深300 PE
        bond_yield: 10年国债收益率 (%)
        """
        if pe is None or pe <= 0 or bond_yield is None:
            return Signal(date=str(date), weights={self.cash_etf: 1.0})

        ey = (1.0 / pe) * 100  # E/P (%)
        erp_val = erp(ey, bond_yield)
        equity_pct = fed_weight(erp_val, self.aggressive, self.defensive)

        weights = {
            self.equity_etf: equity_pct,
            self.bond_etf: 1.0 - equity_pct,
        }
        return Signal(
            date=str(date),
            weights=weights,
            metadata={"erp": round(erp_val, 2), "equity_pct": round(equity_pct, 2)},
        )
