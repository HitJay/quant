"""策略层 — 返回Signal(weights)"""

from quant.strategies.base import Signal, Strategy
from quant.strategies.etf_rotation import ETF_Rotation
from quant.strategies.industry_rotation import IndustryRotation
from quant.strategies.cb_dual_low import CB_DualLow
from quant.strategies.fed_model import FEDModel
from quant.strategies.commodity_rotation import CommodityRotation
from quant.strategies.momentum_experiment import MomentumExperiment

__all__ = [
    "Signal",
    "Strategy",
    "ETF_Rotation",
    "IndustryRotation",
    "CB_DualLow",
    "FEDModel",
    "CommodityRotation",
    "MomentumExperiment",
]
