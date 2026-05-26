"""标的范围配置 — 统一控制可投资标的池"""

from dataclasses import dataclass, field
from quant.universe.etf_map import get_etf_list


@dataclass
class UniverseConfig:
    """可投资标的范围配置
    
    优先级：etf_codes > etf_categories > 默认全部WIDE
    """
    etf_categories: list[str] | None = None   # 如 ["WIDE", "COMMODITY"]
    etf_codes: list[str] | None = None         # 如 ["510300", "510500"]
    max_symbols: int = 0                       # 0=不限制

    def get_symbols(self) -> list[str]:
        """获取当前配置下的ETF代码列表"""
        if self.etf_codes:
            symbols = list(self.etf_codes)
        elif self.etf_categories:
            symbols = []
            for cat in self.etf_categories:
                symbols.extend(get_etf_list(cat))
        else:
            symbols = get_etf_list("WIDE")

        if self.max_symbols > 0:
            symbols = symbols[: self.max_symbols]
        return symbols
