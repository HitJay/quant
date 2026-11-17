#!/usr/bin/env python
"""Fast collector - fetch all hotspot sources with proper timeouts."""
import sys, time, json, pandas as pd, akshare as ak
from pathlib import Path
sys.path.insert(0, "/das/user/QYJI/quant/src")
from quant.data.hotspot_fetcher import HotspotFetcher, _last_trading_day_str

date = "20260723"
raw_dir = Path(f"/das/user/QYJI/quant/output/hotspot/{date}/raw")
raw_dir.mkdir(parents=True, exist_ok=True)

fetcher = HotspotFetcher()

# 1. zt_pool ✓ (cached)
t0 = time.time()
data = {"zt_pool": fetcher.zt_pool(date)}
print(f"zt_pool: {len(data['zt_pool'])} ({time.time()-t0:.1f}s)")

# 2. zt_zbgc ✓ (cached)
t0 = time.time()
data["zt_zbgc"] = fetcher.zt_zbgc(date)
print(f"zt_zbgc: {len(data['zt_zbgc'])} ({time.time()-t0:.1f}s)")

# 3. zt_strong ✓ (cached)
t0 = time.time()
data["zt_strong"] = fetcher.zt_strong(date)
print(f"zt_strong: {len(data['zt_strong'])} ({time.time()-t0:.1f}s)")

# 4. xueqiu_follow
t0 = time.time()
data["xueqiu_follow"] = fetcher.xueqiu_hot(by="follow")
print(f"xueqiu_follow: {len(data['xueqiu_follow'])} ({time.time()-t0:.1f}s)")

# 5. xueqiu_tweet
t0 = time.time()
data["xueqiu_tweet"] = fetcher.xueqiu_hot(by="tweet")
print(f"xueqiu_tweet: {len(data['xueqiu_tweet'])} ({time.time()-t0:.1f}s)")

# 6. em_hot_rank
t0 = time.time()
data["em_hot_rank"] = fetcher.em_hot_rank()
print(f"em_hot_rank: {len(data['em_hot_rank'])} ({time.time()-t0:.1f}s)")

# 7. lhb (盘后应有)
t0 = time.time()
data["lhb"] = fetcher.lhb_today(date)
print(f"lhb: {len(data['lhb'])} ({time.time()-t0:.1f}s)")

# 8. concept_board (try with 40s timeout via patched method)
print("\n--- Fetching concept board (long timeout)...")
t0 = time.time()
import requests
_EM_PUSH2 = "https://push2.eastmoney.com/api/qt/clist/get"
_EM_HEADERS = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36","Referer":"https://quote.eastmoney.com/"}
_FIELDS = "f12,f14,f3,f62,f184,f128,f140,f104,f105"
for attempt in range(3):
    try:
        r = requests.get(_EM_PUSH2, params={"pn":"1","pz":"500","po":"1","np":"1","fs":"m:90 t:3 f:!50","fields":_FIELDS},
                         headers=_EM_HEADERS, timeout=40)
        rows = r.json().get("data",{}).get("diff",[]) or []
        if rows:
            break
    except Exception as e:
        print(f"  attempt {attempt+1}: {e}")
    time.sleep(10)
if rows:
    df = pd.DataFrame(rows)
    df = df.rename(columns={"f12":"code","f14":"name","f3":"pct_chg_x100","f62":"main_net_in",
                            "f184":"main_net_in_pct_x100","f128":"leader_name","f140":"leader_code",
                            "f104":"up_count","f105":"down_count"})
    df["pct_chg"] = pd.to_numeric(df["pct_chg_x100"], errors="coerce") / 100.0
    df = df.sort_values("pct_chg", ascending=False).reset_index(drop=True)
    data["concept_board"] = df
else:
    data["concept_board"] = pd.DataFrame()
print(f"concept_board: {len(data['concept_board'])} ({time.time()-t0:.1f}s)")

# 9. industry_board (same approach)
print("--- Fetching industry board (long timeout)...")
t0 = time.time()
for attempt in range(3):
    try:
        r = requests.get(_EM_PUSH2, params={"pn":"1","pz":"500","po":"1","np":"1","fs":"m:90 t:2 f:!50","fields":_FIELDS},
                         headers=_EM_HEADERS, timeout=40)
        rows = r.json().get("data",{}).get("diff",[]) or []
        if rows:
            break
    except Exception as e:
        print(f"  attempt {attempt+1}: {e}")
    time.sleep(10)
if rows:
    df = pd.DataFrame(rows)
    df = df.rename(columns={"f12":"code","f14":"name","f3":"pct_chg_x100","f62":"main_net_in",
                            "f184":"main_net_in_pct_x100","f128":"leader_name","f140":"leader_code",
                            "f104":"up_count","f105":"down_count"})
    df["pct_chg"] = pd.to_numeric(df["pct_chg_x100"], errors="coerce") / 100.0
    df = df.sort_values("pct_chg", ascending=False).reset_index(drop=True)
    data["industry_board"] = df
else:
    data["industry_board"] = pd.DataFrame()
print(f"industry_board: {len(data['industry_board'])} ({time.time()-t0:.1f}s)")

# 10. em_global_news - skip (timeout)
data["em_global_news"] = pd.DataFrame()
print("em_global_news: skipped (timeout)")

# Save raw data
for src, df in data.items():
    if len(df) > 0:
        df.to_parquet(raw_dir / f"{src}.parquet")
        print(f"  saved raw/{src}.parquet ({len(df)} rows)")

print(f"\n=== Total sources with data: {sum(1 for v in data.values() if len(v)>0)}/10 ===")

# Quick summary
print(f"\n涨停: {len(data['zt_pool'])}")
print(f"炸板: {len(data['zt_zbgc'])}") 
print(f"强势: {len(data['zt_strong'])}")
if not data['industry_board'].empty:
    top3 = data['industry_board'].head(3)
    print(f"行业涨幅TOP3: {[(r['name'], r['pct_chg']) for _,r in top3.iterrows()]}")
    bot3 = data['industry_board'].tail(3)
    print(f"行业跌幅TOP3: {[(r['name'], r['pct_chg']) for _,r in bot3.iterrows()]}")
if not data['xueqiu_follow'].empty:
    print(f"雪球关注TOP: {data['xueqiu_follow']['股票简称'].head(5).tolist()}")
if not data['xueqiu_tweet'].empty:
    print(f"雪球讨论TOP: {data['xueqiu_tweet']['股票简称'].head(5).tolist()}")
