"""股票质量因子"""


def roe(net_income: float, equity: float) -> float | None:
    """净资产收益率"""
    if not equity or equity == 0:
        return None
    return net_income / equity
