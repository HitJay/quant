"""A股股票数据获取器"""

import akshare as ak
import pandas as pd

from quant.data.fetcher import ETFDataFetcher


class StockDataFetcher:
    """A股个股数据获取器"""

    def fetch(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        """获取个股日线（后复权）"""
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start.replace("-", ""),
            end_date=end.replace("-", ""),
            adjust="hfq",
        )
        return ETFDataFetcher._normalize(df)
