"""可转债专属因子"""


def dual_low(price: float, conversion_premium_pct: float) -> float:
    """
    双低值 = 价格 + 转股溢价率 × 100
    
    越低越好（价格低+溢价低=性价比高）
    经典阈值：<120 值得关注，<110 极具吸引力
    """
    return price + conversion_premium_pct


def pure_debt_premium(price: float, debt_value: float) -> float:
    """纯债溢价率 = (价格 - 债底) / 债底"""
    if debt_value <= 0:
        return 999
    return (price - debt_value) / debt_value


def ytm_to_maturity(price: float, coupon_cashflows: list, maturity_years: float) -> float | None:
    """到期收益率（简化版：仅考虑票息+本金）"""
    if price <= 0 or maturity_years <= 0:
        return None
    total_coupon = sum(coupon_cashflows) if coupon_cashflows else 0
    return ((100 + total_coupon) / price - 1) / maturity_years


def conversion_premium(price: float, conversion_value: float) -> float:
    """转股溢价率 = (转债价格 - 转股价值) / 转股价值"""
    if conversion_value <= 0:
        return 999
    return (price - conversion_value) / conversion_value
