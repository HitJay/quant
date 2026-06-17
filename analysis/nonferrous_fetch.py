"""有色金属板块数据抓取 (幂等 + 关键标的强制刷新)
================================================================
主代理:  801050  申万有色金属指数 (1999-12 起, 26 年, 319 月) ★长历史周期之王
交叉:    sh000819 中证有色金属指数 (2012-05 起, 14 年)
可投:    159866   有色金属ETF (2021-04 起, 现金交易)
基准:    sh000300 沪深 300

口径说明:
  - 申万有色 (801050) 走 ak.index_hist_sw, 列名 日期/收盘 → date/close
  - 中证有色 / 沪深300 走 ak.stock_zh_index_daily (sina)
  - 有色金属ETF 走 ak.fund_etf_hist_sina

环境必须 unset http_proxy/https_proxy. sina 速率限制 → sleep 0.4s.

Usage:
    cd /home/QYJI/das/quant && unset http_proxy https_proxy
    conda run -n research python analysis/nonferrous_fetch.py
"""
import time
from pathlib import Path
import akshare as ak
import pandas as pd

INDEX_DIR = Path("./data/cache/index")
ETF_DIR = Path("./data/cache/etf")
INDEX_DIR.mkdir(parents=True, exist_ok=True)
ETF_DIR.mkdir(parents=True, exist_ok=True)

SW_DST = INDEX_DIR / "sw801050.parquet"          # 申万有色金属 (主代理, 长历史)
CSI_NF = ("sh000819", "中证有色金属", INDEX_DIR / "sh000819.parquet")
HS300 = ("sh000300", "沪深300", INDEX_DIR / "sh000300.parquet")
ETF_NF = ("sz159866", "有色金属ETF", ETF_DIR / "159866.parquet")  # 159 开头深市 → sz


def fetch_sw(dst: Path, retries: int = 3, force: bool = False):
    """申万一级行业指数: 有色金属 801050 (1999 起)。"""
    if dst.exists() and not force:
        df = pd.read_parquet(dst)
        if len(df) > 100:
            print(f"  [skip] 801050 申万有色金属 cached, {len(df)} rows, last={df.index[-1].date()}")
            return df
    for i in range(retries):
        try:
            print(f"  [pull] 801050 申万有色金属 (try {i+1})")
            df = ak.index_hist_sw(symbol="801050", period="day")
            df = df.rename(columns={"日期": "date", "收盘": "close", "开盘": "open",
                                    "最高": "high", "最低": "low", "成交量": "volume"})
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date").sort_index()[["open", "high", "low", "close", "volume"]]
            df.to_parquet(dst)
            print(f"         saved {len(df)} rows, range {df.index[0].date()} → {df.index[-1].date()}")
            return df
        except Exception as e:
            print(f"         fail: {e}")
            time.sleep(1.5)
    raise RuntimeError("无法拉取 801050 申万有色金属")


def fetch_index(sym: str, name: str, dst: Path, retries: int = 3, force: bool = False):
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
            print(f"         saved {len(df)} rows, range {df.index[0].date()} → {df.index[-1].date()}")
            return df
        except Exception as e:
            print(f"         fail: {e}")
            time.sleep(1.5)
    raise RuntimeError(f"无法拉取 {sym}")


def fetch_etf(sym: str, name: str, dst: Path, retries: int = 3, force: bool = False):
    if dst.exists() and not force:
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
    print("有色金属数据抓取 (申万 + sina)")
    print("=" * 60)
    # 主代理长历史指数 — 当前位置评估需最新, force 刷新
    fetch_sw(SW_DST, force=True)
    time.sleep(0.4)
    # 中证有色交叉 — force 取最新
    fetch_index(*CSI_NF, force=True)
    time.sleep(0.4)
    # 基准 — force 刷到最新交易日
    fetch_index(*HS300, force=True)
    time.sleep(0.4)
    # 可投 ETF — force 刷新 (缓存偏旧)
    fetch_etf(*ETF_NF, force=True)
    print("\nDone.")
