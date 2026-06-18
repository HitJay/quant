"""蓝宝石概念股池数据抓取 (7 只成分股 + 沪深300 基准)
================================================================
A 股没有"蓝宝石指数"，本研报自建"蓝宝石概念等权指数"。
成分股按"业务纯度 + 历史长度 + 流动性"筛：

  核心层 (蓝宝石主营):
    600330  天通股份    长晶炉+衬底片 (2003 上市)
    002617  露笑科技    长晶炉龙头 (2011 上市)
    600666  奥瑞德      窗口片 (2015 借壳)
    002273  水晶光电    滤光片+蓝宝石 (2008 上市)
    300316  晶盛机电    长晶设备 (2012 上市)

  外延层 (蓝宝石是多元业务之一):
    300285  国瓷材料    蓝宝石+陶瓷 (2012 上市)
    300554  三超新材    切片砂线 (2017 上市)

起始日期: 2017-06-01 (三超上市后所有 7 只都齐了，~9 年月度回测)
基准:    sh000300 沪深 300

口径:
  - 个股走 ak.stock_zh_a_hist (前复权)
  - 沪深 300 走 ak.stock_zh_index_daily (sina)

环境必须 unset http_proxy/https_proxy. sina 速率限制 → sleep 0.4s.

Usage:
    cd /das/user/QYJI/quant && unset http_proxy https_proxy
    conda run -n research python analysis/sapphire_fetch.py
"""
import time
from pathlib import Path
import akshare as ak
import pandas as pd

CACHE_DIR = Path("./data/cache/sapphire")
INDEX_DIR = Path("./data/cache/index")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
INDEX_DIR.mkdir(parents=True, exist_ok=True)

# 7 只蓝宝石概念股 (code, 简称, 业务说明)
COMPONENTS = [
    ("600330", "天通股份", "长晶炉+衬底片"),
    ("002617", "露笑科技", "长晶炉龙头"),
    ("600666", "奥瑞德",   "窗口片"),
    ("002273", "水晶光电", "滤光片+蓝宝石"),
    ("300316", "晶盛机电", "长晶设备"),
    ("300285", "国瓷材料", "蓝宝石+陶瓷"),
    ("300554", "三超新材", "切片砂线"),
]

HS300 = ("sh000300", "沪深300", INDEX_DIR / "sh000300.parquet")

START = "20170101"  # 三超 2017-04 上市, 拉宽一点
END = "20260618"


def fetch_stock(code: str, name: str, retries: int = 3, force: bool = False) -> pd.DataFrame:
    """拉个股前复权日线."""
    dst = CACHE_DIR / f"{code}.parquet"
    if dst.exists() and not force:
        df = pd.read_parquet(dst)
        if len(df) > 100:
            print(f"  [skip] {code} {name} cached, {len(df)} rows, last={df.index[-1].date()}")
            return df
    for i in range(retries):
        try:
            print(f"  [pull] {code} {name} (try {i+1})")
            df = ak.stock_zh_a_hist(symbol=code, period="daily",
                                    start_date=START, end_date=END,
                                    adjust="qfq")
            df = df.rename(columns={
                "日期": "date", "开盘": "open", "收盘": "close",
                "最高": "high", "最低": "low", "成交量": "volume",
                "成交额": "amount", "换手率": "turnover",
            })
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date").sort_index()
            keep = [c for c in ["open", "high", "low", "close", "volume", "amount", "turnover"] if c in df.columns]
            df = df[keep]
            df.to_parquet(dst)
            print(f"         saved {len(df)} rows, {df.index[0].date()} → {df.index[-1].date()}")
            return df
        except Exception as e:
            print(f"         fail: {e}")
            time.sleep(1.5)
    raise RuntimeError(f"无法拉取 {code} {name}")


def fetch_index(sym: str, name: str, dst: Path, retries: int = 3, force: bool = False) -> pd.DataFrame:
    if dst.exists() and not force:
        df = pd.read_parquet(dst)
        if len(df) > 100:
            print(f"  [skip] {sym} {name} cached, {len(df)} rows, last={df.index[-1].date()}")
            return df
    for i in range(retries):
        try:
            print(f"  [pull] {sym} {name} (try {i+1})")
            df = ak.stock_zh_index_daily(symbol=sym)
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date").sort_index()
            df.to_parquet(dst)
            print(f"         saved {len(df)} rows, {df.index[0].date()} → {df.index[-1].date()}")
            return df
        except Exception as e:
            print(f"         fail: {e}")
            time.sleep(1.5)
    raise RuntimeError(f"无法拉取 {sym}")


if __name__ == "__main__":
    print("=" * 60)
    print("蓝宝石概念股池数据抓取 (7 只 + 沪深300)")
    print("=" * 60)
    for code, name, biz in COMPONENTS:
        fetch_stock(code, name, force=True)
        time.sleep(0.4)
    fetch_index(*HS300, force=False)  # 基准用缓存即可
    print("\nDone. 7 只成分股 + 沪深300 全部到位.")
