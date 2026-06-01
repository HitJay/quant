"""指数日线数据获取器 — 用于择时研究的标的"""

import akshare as ak
import pandas as pd
import logging
from quant.data.cache import Cache

logger = logging.getLogger(__name__)

# 指数代码映射: 代码 → 新浪格式
INDEX_SYMBOLS = {
    "000001": "sh000001",  # 上证综指
    "000300": "sh000300",  # 沪深300
    "000905": "sh000905",  # 中证500
    "000852": "sh000852",  # 中证1000
    "399006": "sz399006",  # 创业板指
    "399303": "sz399303",  # 国证2000
}


class IndexFetcher:
    """A股指数日线数据获取器"""

    def __init__(self, cache_dir: str = "./data/cache"):
        self._cache = Cache(cache_dir)

    def fetch(self, symbol: str = "000300", start: str = "2005-01-01") -> pd.DataFrame:
        """
        获取指数日线数据

        Args:
            symbol: 指数代码 (如 '000300' 沪深300)
            start: 起始日期

        Returns:
            DataFrame: index=date, columns=[open, high, low, close, volume]
        """
        cache_key = f"index_{symbol}"
        cached = self._cache.load("index", cache_key)
        if cached is not None and len(cached) > 0:
            # 检查缓存是否足够新(3天内)
            last_date = cached.index[-1]
            if (pd.Timestamp.now() - last_date).days <= 3:
                return cached[cached.index >= start]

        sina_symbol = INDEX_SYMBOLS.get(symbol, f"sh{symbol}")
        logger.info("获取指数数据: %s (%s)", symbol, sina_symbol)

        df = ak.stock_zh_index_daily(symbol=sina_symbol)
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")
        df = df[["open", "high", "low", "close", "volume"]]
        df = df.sort_index()

        self._cache.save(df, "index", cache_key)
        logger.info("指数 %s: %d rows, %s ~ %s", symbol, len(df), df.index[0], df.index[-1])

        return df[df.index >= start]

    def fetch_multiple(self, symbols: list[str], start: str = "2005-01-01") -> dict[str, pd.DataFrame]:
        """获取多个指数的日线数据"""
        result = {}
        for sym in symbols:
            try:
                result[sym] = self.fetch(sym, start)
            except Exception as e:
                logger.error("获取指数 %s 失败: %s", sym, e)
        return result

    def get_close_df(self, symbols: list[str], start: str = "2005-01-01") -> pd.DataFrame:
        """获取多个指数的收盘价合并为一个DataFrame"""
        data = self.fetch_multiple(symbols, start)
        close_dict = {sym: df["close"] for sym, df in data.items()}
        return pd.DataFrame(close_dict).sort_index().ffill()
