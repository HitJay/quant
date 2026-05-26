"""组合管理 — 再平衡 + 风险平价"""

import numpy as np
import pandas as pd


def equal_weight(assets: list[str]) -> dict[str, float]:
    """等权分配"""
    w = 1.0 / len(assets)
    return {a: w for a in assets}


def risk_parity(returns: pd.DataFrame, assets: list[str] | None = None) -> dict[str, float]:
    """
    风险平价权重：每个资产对组合的风险贡献相等
    
    简化版：权重 = (1/波动率) / sum(1/波动率)
    """
    if assets is None:
        assets = list(returns.columns)

    vols = {}
    for a in assets:
        if a not in returns.columns:
            vols[a] = np.inf
        else:
            vol = returns[a].dropna().std() * np.sqrt(252)
            vols[a] = vol if vol > 0 else np.inf

    inv_vols = {a: 1.0 / v for a, v in vols.items() if v < np.inf}
    if not inv_vols:
        return equal_weight(list(vols.keys()))

    total = sum(inv_vols.values())
    return {a: v / total for a, v in inv_vols.items()}


class Rebalancer:
    """再平衡管理"""

    @staticmethod
    def calendar_rebalance(
        current_weights: dict[str, float],
        target_weights: dict[str, float],
        date,
    ) -> bool:
        """定时再平衡：每季度"""
        return date.month in (1, 4, 7, 10) and date.day <= 5

    @staticmethod
    def threshold_rebalance(
        current_weights: dict[str, float],
        target_weights: dict[str, float],
        threshold: float = 0.05,
    ) -> bool:
        """阈值触发再平衡：任一资产偏离>5%"""
        for asset, target in target_weights.items():
            current = current_weights.get(asset, 0)
            if abs(current - target) > threshold:
                return True
        return False
