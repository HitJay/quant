"""ETF数据获取器 — 基于AKShare，多数据源自动切换"""

import akshare as ak
import pandas as pd
import logging
from quant.data.cache import Cache

logger = logging.getLogger(__name__)

# Sina 代码前缀映射
_MARKET_PREFIX = {
    "51": "sh",   # 上海ETF
    "58": "sh",
    "56": "sh",
    "15": "sz",   # 深圳ETF
    "16": "sz",
    "18": "sz",
}


def _to_sina_code(symbol: str) -> str:
    """将 510300 转换为 sz159949 格式"""
    prefix = _MARKET_PREFIX.get(symbol[:2], "sh")
    return f"{prefix}{symbol}"


class ETFDataFetcher:
    """ETF数据获取器，从AKShare获取A股ETF历史日线数据（多源自动切换）"""

    def fetch(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        """
        获取单只ETF历史日线数据（后复权）

        Args:
            symbol: ETF代码，如 '510300'
            start: 起始日期 '2024-01-01'
            end: 截止日期 '2024-06-30'

        Returns:
            DataFrame，index为date，包含 open/high/low/close/volume 列
        """
        # 主源：东方财富（后复权）
        try:
            return self._fetch_em(symbol, start, end)
        except Exception as e:
            logger.warning("东方财富源失败(%s)，切换到新浪源: %s", symbol, e)

        # 备用源：新浪
        return self._fetch_sina(symbol, start, end)

    def _fetch_em(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        """从东方财富获取（后复权）"""
        df = ak.fund_etf_hist_em(
            symbol=symbol,
            period="daily",
            start_date=start.replace("-", ""),
            end_date=end.replace("-", ""),
            adjust="hfq",
        )
        return self._normalize(df)

    def _fetch_sina(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        """从新浪获取（前复权，数据完整性略低）"""
        code = _to_sina_code(symbol)
        df = ak.fund_etf_hist_sina(symbol=code)
        df = df.reset_index()
        return self._normalize(df)

    @staticmethod
    def _normalize(df: pd.DataFrame) -> pd.DataFrame:
        """统一列名和格式"""
        col_map = {
            "日期": "date",
            "date": "date",
            "开盘": "open",
            "open": "open",
            "收盘": "close",
            "close": "close",
            "最高": "high",
            "high": "high",
            "最低": "low",
            "low": "low",
            "成交量": "volume",
            "volume": "volume",
            "成交额": "amount",
        }
        df.rename(columns={k: v for k, v in col_map.items() if k in df.columns}, inplace=True)

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            df.set_index("date", inplace=True)

        df.sort_index(inplace=True)
        return df

    def fetch_or_cache(
        self, symbol: str, start: str, end: str, cache: "Cache | None" = None, force: bool = False
    ) -> pd.DataFrame:
        """获取数据，优先命中缓存"""
        if cache is not None and not force:
            cached = cache.load("etf", symbol)
            if cached is not None:
                return cached
        df = self.fetch(symbol, start, end)
        if cache is not None:
            cache.save(df, "etf", symbol)
        return df
