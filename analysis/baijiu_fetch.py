"""白酒板块数据抓取 (幂等, sina 源)
=====================================
主标的:  sz399987  中证酒 (2015-05-19 起, ~11 年, 长历史 proxy)
ETF 交叉: sh512690  鹏华酒ETF (2016-09 起, 现金交易)
基准:    sh000300  沪深 300

环境必须 unset http_proxy/https_proxy. sina 速率限制 → sleep 0.4s.
"""
import time
from pathlib import Path
import akshare as ak
import pandas as pd

INDEX_DIR = Path("./data/cache/index")
ETF_DIR = Path("./data/cache/etf")
INDEX_DIR.mkdir(parents=True, exist_ok=True)
ETF_DIR.mkdir(parents=True, exist_ok=True)

INDEXES = [
    ("sz399987", "中证酒", INDEX_DIR / "sz399987.parquet"),
    ("sh000300", "沪深300", INDEX_DIR / "sh000300.parquet"),
]
ETFS = [
    ("sh512690", "鹏华酒ETF", ETF_DIR / "512690.parquet"),
]


def fetch_index(sym: str, name: str, dst: Path, retries: int = 3):
    if dst.exists():
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
            print(f"         saved {len(df)} rows, range {df.index[0].date()} → {df.index[-1].date()}")
            return df
        except Exception as e:
            print(f"         fail: {e}")
            time.sleep(1.5)
    raise RuntimeError(f"无法拉取 {sym}")


def fetch_etf(sym: str, name: str, dst: Path, retries: int = 3):
    if dst.exists():
        df = pd.read_parquet(dst)
        if len(df) > 100:
            print(f"  [skip] {sym} {name} cached, {len(df)} rows, last={df.index[-1].date()}")
            return df
    for i in range(retries):
        try:
            print(f"  [pull] {sym} {name} (try {i+1})")
            df = ak.fund_etf_hist_sina(symbol=sym)
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date").sort_index()
            df.to_parquet(dst)
            print(f"         saved {len(df)} rows, range {df.index[0].date()} → {df.index[-1].date()}")
            return df
        except Exception as e:
            print(f"         fail: {e}")
            time.sleep(1.5)
    raise RuntimeError(f"无法拉取 {sym}")


if __name__ == "__main__":
    print("=" * 60)
    print("白酒数据抓取 (sina)")
    print("=" * 60)
    for sym, name, dst in INDEXES:
        fetch_index(sym, name, dst)
        time.sleep(0.4)
    for sym, name, dst in ETFS:
        fetch_etf(sym, name, dst)
        time.sleep(0.4)
    print("\nDone.")
