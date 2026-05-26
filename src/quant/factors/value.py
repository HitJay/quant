"""股票价值因子 — PE/PB/PS/股息率"""


def pe_inverse(pe: float) -> float | None:
    """PE倒数（E/P），值越大越便宜"""
    if pe is None or pe <= 0:
        return None
    return 1.0 / pe


def pb_inverse(pb: float) -> float | None:
    """PB倒数（B/P），值越大越便宜"""
    if pb is None or pb <= 0:
        return None
    return 1.0 / pb


def dividend_yield(dividend: float, price: float) -> float | None:
    """股息率"""
    if not price or price <= 0:
        return None
    return dividend / price if dividend else 0.0
