"""
定投胜率研究 — 数据抓取与缓存
================================
抓取:
  1. 场外热门主动基金 累计净值走势(含分红再投) -> data/cache/fund/{code}.parquet
  2. 当前沪深300成分股 后复权收盘 -> data/cache/stock/{code}.parquet

特性: 幂等(已缓存跳过)、双源回退(sina<->东财)、失败容忍(记录覆盖率)。

Usage:
    conda activate research
    python analysis/fund_dca_fetch.py
"""
import sys, time, json
sys.path.insert(0, "src")
from pathlib import Path

import akshare as ak
import pandas as pd

FUND_DIR = Path("./data/cache/fund")
STOCK_DIR = Path("./data/cache/stock")
FUND_DIR.mkdir(parents=True, exist_ok=True)
STOCK_DIR.mkdir(parents=True, exist_ok=True)

# ── 场外热门主动基金宇宙 (散户真正会追的明星/顶流) ───────────────────────
FUNDS = {
    "005827": "易方达蓝筹精选(张坤)",
    "110011": "易方达优质精选(张坤)",
    "003095": "中欧医疗健康(葛兰)",
    "161725": "招商中证白酒(LOF)",
    "001102": "前海开源国家比较优势",
    "320007": "诺安成长(芯片/蔡嵩松)",
    "163406": "兴全合润(谢治宇)",
    "260108": "景顺长城新兴成长(刘彦春)",
    "161005": "富国天惠成长(朱少醒)",
    "000083": "汇添富消费行业",
    "040035": "华安逆向策略",
    "519066": "汇添富蓝筹稳健",
    "162605": "景顺长城鼎益(刘彦春)",
    "001717": "工银前沿医疗",
    "002001": "华夏回报",
    "000961": "天弘沪深300(宽基基准)",
}


def fetch_fund(code: str, name: str) -> bool:
    path = FUND_DIR / f"{code}.parquet"
    if path.exists():
        print(f"  [skip] {code} {name}")
        return True
    for attempt in range(3):
        try:
            df = ak.fund_open_fund_info_em(symbol=code, indicator="累计净值走势")
            df = df.rename(columns={"净值日期": "date", "累计净值": "nav"})
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date").sort_index()[["nav"]].dropna()
            if len(df) < 200:
                print(f"  [thin] {code} {name} rows={len(df)}")
                return False
            df.to_parquet(path)
            print(f"  [ok]   {code} {name} rows={len(df)} 起={df.index[0].date()}")
            return True
        except Exception as e:
            time.sleep(2)
            err = repr(e)[:90]
    print(f"  [FAIL] {code} {name} {err}")
    return False


def sina_symbol(code: str) -> str:
    if code.startswith("6"):
        return "sh" + code
    if code.startswith(("0", "3")):
        return "sz" + code
    return "sh" + code


def fetch_stock(code: str, name: str) -> bool:
    path = STOCK_DIR / f"{code}.parquet"
    if path.exists():
        return True
    # 源1: sina
    try:
        s = ak.stock_zh_a_daily(symbol=sina_symbol(code), adjust="hfq", start_date="20050101")
        s["date"] = pd.to_datetime(s["date"])
        s = s.set_index("date").sort_index()[["close"]].dropna()
        if len(s) > 200:
            s.to_parquet(path)
            return True
    except Exception:
        pass
    # 源2: 东财
    for attempt in range(2):
        try:
            s = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="hfq", start_date="20050101")
            s = s.rename(columns={"日期": "date", "收盘": "close"})
            s["date"] = pd.to_datetime(s["date"])
            s = s.set_index("date").sort_index()[["close"]].dropna()
            if len(s) > 200:
                s.to_parquet(path)
                return True
        except Exception:
            time.sleep(2)
    return False


def main():
    print("=" * 60)
    print("定投胜率研究 — 数据抓取")
    print("=" * 60)

    print("\n[1] 场外热门基金 累计净值 ...")
    fund_ok = []
    for code, name in FUNDS.items():
        if fetch_fund(code, name):
            fund_ok.append(code)
    print(f"  基金覆盖: {len(fund_ok)}/{len(FUNDS)}")

    print("\n[2] 沪深300成分股 后复权 ...")
    cons = ak.index_stock_cons_csindex(symbol="000300")
    cons = cons[["成分券代码", "成分券名称"]].rename(
        columns={"成分券代码": "code", "成分券名称": "name"})
    cons["code"] = cons["code"].astype(str).str.zfill(6)
    (STOCK_DIR / "_constituents.json").write_text(
        cons.to_json(orient="records", force_ascii=False), encoding="utf-8")

    stock_ok = []
    for i, row in enumerate(cons.itertuples(), 1):
        ok = fetch_stock(row.code, row.name)
        if ok:
            stock_ok.append(row.code)
        if i % 25 == 0:
            print(f"  {i}/{len(cons)} 已成功 {len(stock_ok)}")
        time.sleep(0.15)
    print(f"  个股覆盖: {len(stock_ok)}/{len(cons)}")

    meta = {
        "funds_ok": fund_ok,
        "fund_names": {c: FUNDS[c] for c in fund_ok},
        "stocks_ok": stock_ok,
        "n_constituents": int(len(cons)),
    }
    (STOCK_DIR / "_fetch_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n完成。meta -> data/cache/stock/_fetch_meta.json")


if __name__ == "__main__":
    main()
