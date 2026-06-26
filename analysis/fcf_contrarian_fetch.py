"""Fetch 现金流 ETF + 基准 + 持仓表 — 反共识帖 2026-06-26.

数据源:
- ETF 日线: ak.fund_etf_hist_sina (HPC 稳定)
- 指数日线: ak.stock_zh_index_daily (sina)
- ETF 持仓: ak.fund_portfolio_hold_em (东财, 偶发 SSL 失败, 重试 3 次)

落盘: /das/user/QYJI/quant/data/cache/fcf/*.parquet
"""

from __future__ import annotations

import os
import time
import sys
from pathlib import Path

# 必须在 import akshare 之前清代理 (HPC sina 防火墙)
for _k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
    os.environ.pop(_k, None)

import pandas as pd
import akshare as ak

CACHE = Path("/das/user/QYJI/quant/data/cache/fcf")
CACHE.mkdir(parents=True, exist_ok=True)

# 5 只 现金流 ETF (sina 必须带 sh/sz 前缀)
FCF_ETFS = {
    "sh562340": "中证自由现金流ETF(华泰柏瑞)",   # 2024-05-08 上市, 历史最长
    "sz159201": "国证自由现金流ETF",              # 2025-02-27
    "sz159222": "自由现金流ETF华夏",              # 2025-04-17
    "sz159218": "自由现金流ETF",                  # 2025-05-22  (实际是国货航天指数)
    "sh563690": "国新央企现金流ETF",              # 2025-10-10
}

# 基准: 沪深300 + 红利 + 红利低波 + 资源股 ETF (用于 现金流风格归因)
BENCH_ETFS = {
    "sh510300": "沪深300ETF",
    "sh510880": "红利ETF",
    "sz159211": "中证红利低波100ETF",
    "sh515220": "煤炭ETF",
    "sh510410": "资源ETF",
    "sh515790": "光伏ETF",
}

# 指数 (用 sina 走 stock_zh_index_daily)
INDEXES = {
    "sh000300": "沪深300",
    "sz980092": "国证自由现金流指数",  # 现金流 ETF 主跟踪标的, 但只有 2024-12 起
    "sh000922": "中证红利",
    "sh000932": "中证电力公用",
}


def fetch_etf(sym: str, name: str, retries: int = 3) -> pd.DataFrame | None:
    """ETF 日线 (sina, 后复权)."""
    out = CACHE / f"etf_{sym}.parquet"
    if out.exists():
        df = pd.read_parquet(out)
        print(f"  [skip] {sym} {name} N={len(df)}")
        return df
    for k in range(retries):
        try:
            df = ak.fund_etf_hist_sina(symbol=sym)
            if df is None or len(df) == 0:
                print(f"  [empty] {sym} {name}")
                return None
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date").reset_index(drop=True)
            df.to_parquet(out, index=False)
            print(f"  [ok]   {sym} {name} N={len(df)} {df['date'].iloc[0].date()}~{df['date'].iloc[-1].date()}")
            return df
        except Exception as e:
            print(f"  [retry{k+1}] {sym} {name}: {type(e).__name__}: {str(e)[:80]}")
            time.sleep(1.0)
    print(f"  [FAIL] {sym} {name}")
    return None


def fetch_index(sym: str, name: str, retries: int = 3) -> pd.DataFrame | None:
    out = CACHE / f"idx_{sym}.parquet"
    if out.exists():
        df = pd.read_parquet(out)
        print(f"  [skip] {sym} {name} N={len(df)}")
        return df
    for k in range(retries):
        try:
            df = ak.stock_zh_index_daily(symbol=sym)
            if df is None or len(df) == 0:
                print(f"  [empty] {sym} {name}")
                return None
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date").reset_index(drop=True)
            df.to_parquet(out, index=False)
            print(f"  [ok]   {sym} {name} N={len(df)} {df['date'].iloc[0].date()}~{df['date'].iloc[-1].date()}")
            return df
        except Exception as e:
            print(f"  [retry{k+1}] {sym} {name}: {type(e).__name__}: {str(e)[:80]}")
            time.sleep(1.0)
    return None


def fetch_holdings(code: str, name: str, retries: int = 3) -> pd.DataFrame | None:
    """ETF 持仓表 (东财, 用 6 位代码不带前缀)."""
    out = CACHE / f"hold_{code}.parquet"
    if out.exists():
        df = pd.read_parquet(out)
        print(f"  [skip] hold_{code} {name} N={len(df)}")
        return df
    for k in range(retries):
        try:
            df = ak.fund_portfolio_hold_em(symbol=code, date="2026")
            if df is None or len(df) == 0:
                df = ak.fund_portfolio_hold_em(symbol=code, date="2025")
            if df is None or len(df) == 0:
                print(f"  [empty] hold_{code} {name}")
                return None
            df.to_parquet(out, index=False)
            print(f"  [ok]   hold_{code} {name} N={len(df)}")
            return df
        except Exception as e:
            print(f"  [retry{k+1}] hold_{code} {name}: {type(e).__name__}: {str(e)[:80]}")
            time.sleep(2.0)
    print(f"  [FAIL] hold_{code} {name}")
    return None


def main() -> None:
    print("=== 现金流 ETFs ===")
    for sym, name in FCF_ETFS.items():
        fetch_etf(sym, name)
        time.sleep(0.5)
    print()
    print("=== Benchmark ETFs ===")
    for sym, name in BENCH_ETFS.items():
        fetch_etf(sym, name)
        time.sleep(0.5)
    print()
    print("=== Indexes ===")
    for sym, name in INDEXES.items():
        fetch_index(sym, name)
        time.sleep(0.5)
    print()
    print("=== Holdings ===")
    # 持仓接口用 6 位代码
    for sym, name in FCF_ETFS.items():
        code = sym[2:]
        fetch_holdings(code, name)
        time.sleep(1.5)
    print()
    print("[DONE] cache @", CACHE)


if __name__ == "__main__":
    main()
