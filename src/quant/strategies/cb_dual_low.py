"""可转债双低轮动策略"""

from quant.strategies.base import Strategy, Signal
from quant.factors.cb import dual_low


class CB_DualLow(Strategy):
    """
    可转债双低轮动策略
    
    双低值 = 价格 + 转股溢价率 × 100
    持有双低值最低的N只转债，月度轮动
    """

    def __init__(self, max_price: float = 130, hold_n: int = 15, min_rating: str = "A+"):
        self.max_price = max_price
        self.hold_n = hold_n
        self.min_rating = min_rating

    def rebalance(self, date, cb_data: list[dict], prices) -> Signal:
        """
        cb_data: [{"code": "110xxx", "close": 108, "conversion_premium_pct": 5}, ...]
        """
        # 过滤
        valid = [
            cb
            for cb in cb_data
            if cb.get("close", 999) <= self.max_price
        ]

        if not valid:
            return Signal(date=str(date), weights={})

        # 计算双低值并排序
        for cb in valid:
            cb["dual_low"] = dual_low(
                cb.get("close", 0),
                cb.get("conversion_premium_pct", 50),
            )

        valid.sort(key=lambda x: x["dual_low"])
        top = valid[: self.hold_n]

        weight = 1.0 / len(top)
        return Signal(
            date=str(date),
            weights={cb["code"]: weight for cb in top},
        )
