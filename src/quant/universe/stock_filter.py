"""股票池筛选器"""


class StockFilter:
    """A股股票池筛选"""

    def __init__(
        self,
        exclude_st: bool = True,
        min_price: float = 0,
        min_market_cap: float = 0,
        exclude_new_listed: bool = True,
        new_listed_days: int = 365,
    ):
        self.exclude_st = exclude_st
        self.min_price = min_price
        self.min_market_cap = min_market_cap
        self.exclude_new_listed = exclude_new_listed
        self.new_listed_days = new_listed_days

    def filter(self, stocks: dict[str, dict]) -> list[str]:
        """筛选可投资的股票列表"""
        result = []
        for code, info in stocks.items():
            if self.exclude_st and info.get("is_st", False):
                continue
            if self.min_price > 0 and info.get("close", 0) < self.min_price:
                continue
            result.append(code)
        return result
