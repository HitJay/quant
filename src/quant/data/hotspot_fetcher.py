"""散户向热点数据获取器 — 面向小红书选题素材

主打"散户在聊什么 / 谁在涨 / 谁炸板 / 哪条新闻在传"，不是择时数据。

数据源:
  - 东方财富涨停池/炸板/强势股 (akshare)
  - 雪球关注榜/讨论榜 (akshare)
  - 东财人气榜 (akshare)
  - 龙虎榜 (akshare)
  - 东财快讯 (akshare, 替代财联社电报 — cls.cn 现被WAF拦)
  - 东财 push2 概念/行业板块涨跌 (自写直连, akshare 该接口反爬)

设计:
  - 每个方法独立 try/except，失败返回空 DataFrame，不让单个源拖垮全局
  - 当日缓存（同一交易日同一接口默认只拉一次，按 date+source 落 parquet）
  - 字段统一英文化方便下游处理
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import akshare as ak
import pandas as pd
import requests

logger = logging.getLogger(__name__)

# 东财 push2 客户端常量
_EM_PUSH2 = "https://push2.eastmoney.com/api/qt/clist/get"
_EM_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Referer": "https://quote.eastmoney.com/",
}


def _today_str() -> str:
    return datetime.now().strftime("%Y%m%d")


def _last_trading_day_str(d: Optional[datetime] = None) -> str:
    """简易回退：周末/节假日时往前回推到最近的工作日（不查交易日历，盘后用够了）"""
    d = d or datetime.now()
    while d.weekday() >= 5:  # 5=Sat, 6=Sun
        d -= timedelta(days=1)
    return d.strftime("%Y%m%d")


class HotspotFetcher:
    """散户向热点数据获取器"""

    def __init__(self, cache_dir: str = "./data/cache/hotspot"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    # ───────── 缓存 ─────────

    def _cache_path(self, source: str, date: str) -> Path:
        return self.cache_dir / f"{source}_{date}.parquet"

    def _load_cache(self, source: str, date: str) -> Optional[pd.DataFrame]:
        p = self._cache_path(source, date)
        if p.exists():
            try:
                return pd.read_parquet(p)
            except Exception as e:
                logger.warning("缓存读取失败 %s: %s", p, e)
        return None

    def _save_cache(self, df: pd.DataFrame, source: str, date: str) -> None:
        if df is None or len(df) == 0:
            return
        try:
            df.to_parquet(self._cache_path(source, date))
        except Exception as e:
            logger.warning("缓存写入失败 %s: %s", source, e)

    # ───────── 涨停板情绪 ─────────

    def zt_pool(self, date: Optional[str] = None, use_cache: bool = True) -> pd.DataFrame:
        """涨停股池 (含连板数, 行业)

        小红书用法: "今日XX连板天梯", "X连板XXX妖股盘点"
        """
        date = date or _last_trading_day_str()
        if use_cache:
            cached = self._load_cache("zt_pool", date)
            if cached is not None:
                return cached
        try:
            df = ak.stock_zt_pool_em(date=date)
            self._save_cache(df, "zt_pool", date)
            return df
        except Exception as e:
            logger.warning("zt_pool失败: %s", e)
            return pd.DataFrame()

    def zt_zbgc(self, date: Optional[str] = None, use_cache: bool = True) -> pd.DataFrame:
        """炸板股池 (今天涨停又被打开的)

        小红书用法: "今天XX炸板，散户被埋"
        """
        date = date or _last_trading_day_str()
        if use_cache:
            cached = self._load_cache("zt_zbgc", date)
            if cached is not None:
                return cached
        try:
            df = ak.stock_zt_pool_zbgc_em(date=date)
            self._save_cache(df, "zt_zbgc", date)
            return df
        except Exception as e:
            logger.warning("zt_zbgc失败: %s", e)
            return pd.DataFrame()

    def zt_strong(self, date: Optional[str] = None, use_cache: bool = True) -> pd.DataFrame:
        """强势股池 (创新高/涨速快)"""
        date = date or _last_trading_day_str()
        if use_cache:
            cached = self._load_cache("zt_strong", date)
            if cached is not None:
                return cached
        try:
            df = ak.stock_zt_pool_strong_em(date=date)
            self._save_cache(df, "zt_strong", date)
            return df
        except Exception as e:
            logger.warning("zt_strong失败: %s", e)
            return pd.DataFrame()

    # ───────── 散户关注度 ─────────

    def xueqiu_hot(self, by: str = "follow", market: str = "最热门") -> pd.DataFrame:
        """雪球热度榜

        Args:
            by: 'follow'=关注榜（看长线散户在盯哪只）, 'tweet'=讨论榜（看今天在吵啥）
            market: '最热门' / 'A股' / '港股' / '美股'
        """
        try:
            if by == "tweet":
                return ak.stock_hot_tweet_xq(symbol=market)
            return ak.stock_hot_follow_xq(symbol=market)
        except Exception as e:
            logger.warning("xueqiu_hot(%s) 失败: %s", by, e)
            return pd.DataFrame()

    def em_hot_rank(self, retries: int = 2) -> pd.DataFrame:
        """东方财富人气榜（散户用户量大，最反映草根关注度）

        东财人气榜接口偶发 connection reset，自动重试一次。
        """
        import time as _t
        last_err = None
        for i in range(retries + 1):
            try:
                df = ak.stock_hot_rank_em()
                if df is not None and len(df) > 0:
                    return df
            except Exception as e:
                last_err = e
                if i < retries:
                    _t.sleep(1.5)
        logger.warning("em_hot_rank失败(重试%d次): %s", retries, last_err)
        return pd.DataFrame()

    # ───────── 资金/游资 ─────────

    def lhb_today(self, date: Optional[str] = None, use_cache: bool = True) -> pd.DataFrame:
        """龙虎榜（含上榜原因，是游资八卦素材的金矿）

        盘中数据没出来时，akshare 返回 None，做兜底。
        """
        date = date or _last_trading_day_str()
        if use_cache:
            cached = self._load_cache("lhb", date)
            if cached is not None:
                return cached
        try:
            df = ak.stock_lhb_detail_em(start_date=date, end_date=date)
            if df is None or len(df) == 0:
                return pd.DataFrame()
            self._save_cache(df, "lhb", date)
            return df
        except Exception as e:
            logger.warning("lhb失败: %s", e)
            return pd.DataFrame()

    # ───────── 板块涨跌（自写，绕akshare反爬）─────────

    def _em_board_clist(self, fs_code: str) -> pd.DataFrame:
        """直连东财 push2 拉板块行情，比akshare稳。

        Args:
            fs_code: 'm:90 t:3 f:!50' 概念 / 'm:90 t:2 f:!50' 行业
        """
        try:
            r = requests.get(
                _EM_PUSH2,
                params={
                    "pn": "1", "pz": "500", "po": "1", "np": "1",
                    "fs": fs_code,
                    "fields": "f12,f14,f3,f62,f184,f128,f140,f104,f105",
                },
                headers=_EM_HEADERS,
                timeout=15,
            )
            r.raise_for_status()
            data = r.json().get("data") or {}
            diff = data.get("diff") or []
            if not diff:
                return pd.DataFrame()
            df = pd.DataFrame(diff)
            df = df.rename(columns={
                "f12": "code",
                "f14": "name",
                "f3": "pct_chg_x100",       # 涨跌幅×100 (整数)
                "f62": "main_net_in",       # 主力净流入
                "f184": "main_net_in_pct_x100",  # 净流入占比×100
                "f128": "leader_name",      # 领涨股名
                "f140": "leader_code",      # 领涨股代码
                "f104": "up_count",         # 上涨家数
                "f105": "down_count",       # 下跌家数
            })
            df["pct_chg"] = pd.to_numeric(df["pct_chg_x100"], errors="coerce") / 100.0
            df["main_net_in_pct"] = pd.to_numeric(df.get("main_net_in_pct_x100"), errors="coerce") / 100.0
            df = df.sort_values("pct_chg", ascending=False).reset_index(drop=True)
            return df[["code", "name", "pct_chg", "up_count", "down_count",
                       "main_net_in", "main_net_in_pct", "leader_name", "leader_code"]]
        except Exception as e:
            logger.warning("em_board_clist(%s) 失败: %s", fs_code, e)
            return pd.DataFrame()

    def concept_board(self, use_cache: bool = True) -> pd.DataFrame:
        """概念板块涨跌排名 (按涨跌幅倒序)"""
        date = _last_trading_day_str()
        if use_cache:
            cached = self._load_cache("concept_board", date)
            if cached is not None:
                return cached
        df = self._em_board_clist("m:90 t:3 f:!50")
        self._save_cache(df, "concept_board", date)
        return df

    def industry_board(self, use_cache: bool = True) -> pd.DataFrame:
        """行业板块涨跌排名 (按涨跌幅倒序)"""
        date = _last_trading_day_str()
        if use_cache:
            cached = self._load_cache("industry_board", date)
            if cached is not None:
                return cached
        df = self._em_board_clist("m:90 t:2 f:!50")
        self._save_cache(df, "industry_board", date)
        return df

    # ───────── 新闻流 ─────────

    def em_global_news(self, limit: int = 200) -> pd.DataFrame:
        """东方财富全球财经快讯（替代被墙的财联社电报）

        Returns:
            DataFrame: 标题, 摘要, 发布时间, 链接
        """
        try:
            df = ak.stock_info_global_em()
            if "发布时间" in df.columns:
                df["发布时间"] = pd.to_datetime(df["发布时间"], errors="coerce")
                df = df.sort_values("发布时间", ascending=False)
            return df.head(limit).reset_index(drop=True)
        except Exception as e:
            logger.warning("em_global_news失败: %s", e)
            return pd.DataFrame()

    # ───────── 一键拉全部 ─────────

    def fetch_all(self, date: Optional[str] = None) -> dict[str, pd.DataFrame]:
        """拉所有数据源，返回字典。失败的源对应空DataFrame，不抛异常。"""
        date = date or _last_trading_day_str()
        return {
            "zt_pool": self.zt_pool(date),
            "zt_zbgc": self.zt_zbgc(date),
            "zt_strong": self.zt_strong(date),
            "xueqiu_follow": self.xueqiu_hot(by="follow"),
            "xueqiu_tweet": self.xueqiu_hot(by="tweet"),
            "em_hot_rank": self.em_hot_rank(),
            "lhb": self.lhb_today(date),
            "concept_board": self.concept_board(),
            "industry_board": self.industry_board(),
            "em_global_news": self.em_global_news(limit=100),
        }
