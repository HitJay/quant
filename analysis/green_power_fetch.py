"""
绿色电力 ETF 前景与长线胜率 — 数据抓取
========================================
抓取主标的(绿电 ETF)、代理指数(覆盖更长历史)与基准。

主标的 — 当前可投绿电 ETF (历史 ≤ 5 年):
  561560  绿电ETF华夏        (2022-05 至今)
  159865  绿色电力ETF汇添富   (2021-03 至今)
  159625  绿电ETF招商        (2022-04 至今)
  515790  光伏ETF           (2020-12 至今)
  561330  风电ETF           (2022-11 至今)

代理指数 — 用于长线胜率回测 (≥ 10 年):
  sh000932  中证电力公用事业指数    (2009-07 至今, 17 年)  ★主代理
  sh000063  上证电力指数           (2010-02 至今, 16 年)
  sz399808  中证新能源            (2015-07 至今, 11 年)
  sh000827  中证环保             (2012-09 至今, 14 年)

基准:
  sh000300  沪深 300
  sh000016  上证 50
  sh000928  CSI 能源 (传统化石电力对照)
  sh000986  CSI 全指能源

数据走 sina (东财在 HPC 被防火墙阻断, sina 稳定可达)。
"""
import sys, time, json
sys.path.insert(0, "src")
from pathlib import Path

import akshare as ak
import pandas as pd

ROOT = Path("./data/cache")
ETF_DIR = ROOT / "etf"
IDX_DIR = ROOT / "index"
ETF_DIR.mkdir(parents=True, exist_ok=True)
IDX_DIR.mkdir(parents=True, exist_ok=True)

GREEN_ETFS = {
    "561560": "绿电ETF华夏",
    "159865": "绿色电力ETF汇添富",
    "159625": "绿电ETF招商",
    "515790": "光伏ETF",
    "561330": "风电ETF",
    "516580": "绿色能源ETF",
    "516220": "碳中和ETF",
    "159885": "绿色50ETF",
}

INDICES = {
    "sh000932": "中证电力公用事业指数",
    "sh000063": "上证电力指数",
    "sz399808": "中证新能源",
    "sh000827": "中证环保",
    "sh000300": "沪深300",
    "sh000016": "上证50",
    "sh000928": "CSI能源",
    "sh000986": "CSI全指能源",
    "sh000852": "中证1000",
}


def sina_etf_symbol(code: str) -> str:
    return ("sh" if code.startswith(("5", "6")) else "sz") + code


def fetch_etf(code: str, name: str) -> bool:
    path = ETF_DIR / f"{code}.parquet"
    if path.exists():
        print(f"  [skip] {code} {name}")
        return True
    sym = sina_etf_symbol(code)
    for k in range(3):
        try:
            df = ak.fund_etf_hist_sina(symbol=sym)
            if df is None or len(df) < 50:
                print(f"  [thin] {code} {name} rows={0 if df is None else len(df)}")
                return False
            df = df.copy()
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date").sort_index()
            df.to_parquet(path)
            print(f"  [ok]   {code} {name} rows={len(df)} 起={df.index[0].date()} 至={df.index[-1].date()}")
            return True
        except Exception as e:
            time.sleep(2 + k)
            err = repr(e)[:80]
    print(f"  [FAIL] {code} {name} {err}")
    return False


def fetch_index(sym: str, name: str) -> bool:
    code = sym  # 含 sh/sz 前缀
    path = IDX_DIR / f"{code}.parquet"
    if path.exists():
        print(f"  [skip] {sym} {name}")
        return True
    for k in range(3):
        try:
            df = ak.stock_zh_index_daily(symbol=sym)
            df = df.reset_index() if "date" not in df.columns else df
            if df is None or len(df) < 200:
                print(f"  [thin] {sym} {name} rows={0 if df is None else len(df)}")
                return False
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date").sort_index()
            df.to_parquet(path)
            print(f"  [ok]   {sym} {name} rows={len(df)} 起={df.index[0].date()} 至={df.index[-1].date()}")
            return True
        except Exception as e:
            time.sleep(2 + k)
            err = repr(e)[:80]
    print(f"  [FAIL] {sym} {name} {err}")
    return False


def main():
    print("=" * 60)
    print("绿色电力 ETF 研究 — 数据抓取")
    print("=" * 60)

    print("\n[1] 绿电主标的 ETF ...")
    etf_ok = []
    for code, name in GREEN_ETFS.items():
        if fetch_etf(code, name):
            etf_ok.append(code)
        time.sleep(0.4)

    print("\n[2] 代理指数与基准 ...")
    idx_ok = []
    for sym, name in INDICES.items():
        if fetch_index(sym, name):
            idx_ok.append(sym)
        time.sleep(0.4)

    meta = {
        "etfs_ok": etf_ok,
        "etf_names": {c: GREEN_ETFS[c] for c in etf_ok},
        "indices_ok": idx_ok,
        "index_names": {s: INDICES[s] for s in idx_ok},
    }
    (ROOT / "_green_power_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n完成。ETF: {len(etf_ok)}/{len(GREEN_ETFS)}, 指数: {len(idx_ok)}/{len(INDICES)}")
    print("meta -> data/cache/_green_power_meta.json")


if __name__ == "__main__":
    main()
