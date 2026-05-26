"""宏观因子 — 股债性价比/利率/估值"""


def erp(earnings_yield_pct: float, bond_yield_pct: float) -> float:
    """
    股权风险溢价 (ERP) = E/P - 国债收益率
    
    > 2%: 股票极具吸引力
    0~2%: 中性
    < 0%: 债券更有吸引力
    """
    return earnings_yield_pct - bond_yield_pct


def fed_signal(erp_value: float, aggressive: float = 2.0, defensive: float = 0.0) -> str:
    """
    FED模型信号
    
    Returns: 'aggressive' | 'neutral' | 'defensive'
    """
    if erp_value > aggressive:
        return "aggressive"
    elif erp_value < defensive:
        return "defensive"
    return "neutral"


def fed_weight(erp_value: float, aggressive: float = 2.0, defensive: float = 0.0) -> float:
    """
    根据ERP计算权益建议仓位 (0.0~1.0)
    """
    if erp_value > aggressive:
        return 0.9
    elif erp_value < defensive:
        return 0.2
    # 线性插值: defensive~aggressive → 0.2~0.9
    ratio = (erp_value - defensive) / (aggressive - defensive)
    return 0.2 + ratio * 0.7
