"""宏观/情绪数据获取器 — 国债收益率、融资融券、指数估值等"""

import akshare as ak
import pandas as pd
import logging
from quant.data.cache import Cache

logger = logging.getLogger(__name__)


class MacroFetcher:
    """宏观与市场情绪数据获取，基于AKShare"""

    def __init__(self, cache_dir: str = "./data/cache"):
        self._cache = Cache(cache_dir)

    # ───────── 国债收益率 ─────────

    def get_bond_yield(self, start_date: str = "20100101") -> pd.DataFrame:
        """
        获取中国国债收益率(10年期为主)

        Returns:
            DataFrame: index=date, columns=[2Y, 5Y, 10Y, 30Y]
        """
        cached = self._cache.load("macro", "bond_yield_cn")
        if cached is not None and len(cached) > 0:
            return cached

        df = ak.bond_zh_us_rate(start_date=start_date)
        df = df.rename(columns={
            "日期": "date",
            "中国国债收益率2年": "cn_2y",
            "中国国债收益率5年": "cn_5y",
            "中国国债收益率10年": "cn_10y",
            "中国国债收益率30年": "cn_30y",
        })
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")[["cn_2y", "cn_5y", "cn_10y", "cn_30y"]]
        df = df.dropna(subset=["cn_10y"])
        df = df.sort_index()

        self._cache.save(df, "macro", "bond_yield_cn")
        logger.info("国债收益率: %d rows, %s ~ %s", len(df), df.index[0], df.index[-1])
        return df

    # ───────── 融资融券 ─────────

    def get_margin_balance(self, start_date: str = "20100101", end_date: str = "20261231") -> pd.DataFrame:
        """
        获取上交所融资融券余额(日频)

        Returns:
            DataFrame: index=date, columns=[margin_balance, margin_buy]
        """
        cached = self._cache.load("macro", "margin_sse")
        if cached is not None and len(cached) > 0:
            return cached

        df = ak.stock_margin_sse(start_date=start_date, end_date=end_date)
        df = df.rename(columns={
            "信用交易日期": "date",
            "融资余额": "margin_balance",
            "融资买入额": "margin_buy",
            "融资融券余额": "total_balance",
        })
        df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
        df = df.set_index("date")[["margin_balance", "margin_buy", "total_balance"]]
        df = df.sort_index()

        self._cache.save(df, "macro", "margin_sse")
        logger.info("融资融券: %d rows, %s ~ %s", len(df), df.index[0], df.index[-1])
        return df

    # ───────── 指数估值 (中证指数官方) ─────────

    def get_index_pe_csindex(self, symbol: str = "000300") -> pd.DataFrame:
        """
        获取中证指数官方PE/股息率数据(近20个交易日)
        注: 此接口仅返回近期数据,长期PE需用其他方式计算

        Returns:
            DataFrame: index=date, columns=[pe_ttm, pe_static, div_yield1, div_yield2]
        """
        df = ak.stock_zh_index_value_csindex(symbol=symbol)
        df = df.rename(columns={
            "日期": "date",
            "市盈率1": "pe_ttm",
            "市盈率2": "pe_static",
            "股息率1": "div_yield1",
            "股息率2": "div_yield2",
        })
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")[["pe_ttm", "pe_static", "div_yield1", "div_yield2"]]
        df = df.sort_index()
        return df

    # ───────── 成交量/换手率代理 ─────────

    def get_market_volume(self, symbol: str = "sh000001") -> pd.DataFrame:
        """
        获取指数成交量(用作全市场换手率代理)
        用上证综指成交额代理全A成交活跃度

        Returns:
            DataFrame: index=date, columns=[close, volume]
        """
        cached = self._cache.load("macro", f"volume_{symbol}")
        if cached is not None and len(cached) > 0:
            return cached

        df = ak.stock_zh_index_daily(symbol=symbol)
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")[["close", "volume"]]
        df = df.sort_index()

        self._cache.save(df, "macro", f"volume_{symbol}")
        logger.info("市场成交量(%s): %d rows", symbol, len(df))
        return df

    # ───────── 辅助: 从价格+PE反推 earnings yield ─────────

    @staticmethod
    def earnings_yield_from_pe(pe: float) -> float:
        """PE → E/P (earnings yield %)"""
        if pe <= 0:
            return 0.0
        return 100.0 / pe
