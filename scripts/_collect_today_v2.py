#!/usr/bin/env python
"""Retry boards with 5 attempts + generate digest."""
import sys, json, requests, time, pandas as pd
from pathlib import Path

sys.path.insert(0, "/das/user/QYJI/quant/src")
from quant.data.hotspot_fetcher import HotspotFetcher
from quant.monitor.hotspot_digest import summarize, generate_topics, to_markdown

date = "20260723"
raw_dir = Path(f"/das/user/QYJI/quant/output/hotspot/{date}/raw")

_EM_PUSH2 = "https://push2.eastmoney.com/api/qt/clist/get"
_EM_HEADERS = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36","Referer":"https://quote.eastmoney.com/"}
_FIELDS = "f12,f14,f3,f62,f184,f128,f140,f104,f105"

def df_from_rows(rows):
    df = pd.DataFrame(rows)
    df = df.rename(columns={"f12":"code","f14":"name","f3":"pct_chg_x100","f62":"main_net_in",
                            "f184":"main_net_in_pct_x100","f128":"leader_name","f140":"leader_code",
                            "f104":"up_count","f105":"down_count"})
    df["pct_chg"] = pd.to_numeric(df["pct_chg_x100"], errors="coerce") / 100.0
    df = df.sort_values("pct_chg", ascending=False).reset_index(drop=True)
    cols = ["code","name","pct_chg","up_count","down_count","main_net_in","main_net_in_pct","leader_name","leader_code"]
    return df[[c for c in cols if c in df.columns]]

# ---- concept board ----
print("--- concept_board (5 attempts, sleep 15) ---")
concept_rows = None
for i in range(5):
    try:
        r = requests.get(_EM_PUSH2, params={"pn":"1","pz":"500","po":"1","np":"1","fs":"m:90 t:3 f:!50","fields":_FIELDS},
                         headers=_EM_HEADERS, timeout=40)
        j = r.json()
        concept_rows = j.get("data",{}).get("diff",[]) or []
        print(f"  attempt {i+1}: {r.status_code} rows={len(concept_rows)}")
        if concept_rows:
            break
    except Exception as e:
        print(f"  attempt {i+1}: {type(e).__name__}: {str(e)[:80]}")
    if i < 4:
        time.sleep(15)

if concept_rows:
    concept_df = df_from_rows(concept_rows)
    concept_df.to_parquet(raw_dir / "concept_board.parquet")
    print(f"concept_board saved: {len(concept_df)} rows")
else:
    concept_df = pd.DataFrame()
    print("concept_board: FAILED")

# ---- industry board ----
print("--- industry_board (5 attempts, sleep 15) ---")
industry_rows = None
for i in range(5):
    try:
        r = requests.get(_EM_PUSH2, params={"pn":"1","pz":"500","po":"1","np":"1","fs":"m:90 t:2 f:!50","fields":_FIELDS},
                         headers=_EM_HEADERS, timeout=40)
        j = r.json()
        industry_rows = j.get("data",{}).get("diff",[]) or []
        print(f"  attempt {i+1}: {r.status_code} rows={len(industry_rows)}")
        if industry_rows:
            break
    except Exception as e:
        print(f"  attempt {i+1}: {type(e).__name__}: {str(e)[:80]}")
    if i < 4:
        time.sleep(15)

if industry_rows:
    industry_df = df_from_rows(industry_rows)
    industry_df.to_parquet(raw_dir / "industry_board.parquet")
    print(f"industry_board saved: {len(industry_df)} rows")
else:
    industry_df = pd.DataFrame()
    print("industry_board: FAILED")

# ---- Load all raw data ----
data = {}
for src in ["zt_pool","zt_zbgc","zt_strong","xueqiu_follow","xueqiu_tweet","em_hot_rank","lhb"]:
    p = raw_dir / f"{src}.parquet"
    if p.exists():
        data[src] = pd.read_parquet(p)
        print(f"Loaded {src}: {len(data[src])} rows")
    else:
        data[src] = pd.DataFrame()

data["concept_board"] = concept_df
data["industry_board"] = industry_df
data["em_global_news"] = pd.DataFrame()

# ---- Generate digest ----
out_dir = Path(f"/das/user/QYJI/quant/output/hotspot/{date}")
summary = summarize(data, date=date)
topics = generate_topics(summary)

(out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
(out_dir / "topics.json").write_text(json.dumps(topics, ensure_ascii=False, indent=2), encoding="utf-8")
md = to_markdown(summary, topics)
(out_dir / "digest.md").write_text(md, encoding="utf-8")

print(f"\n=== DONE ===")
print(f"Digest: {out_dir}/digest.md")
print(f"Topics: {len(topics)} candidates")

# Quick stats
print(f"\n涨停: {len(data['zt_pool'])}")
print(f"炸板: {len(data['zt_zbgc'])}")
print(f"强势股: {len(data['zt_strong'])}")
if not industry_df.empty:
    top3 = industry_df.head(3)
    print(f"\n行业涨幅TOP3:")
    for _,r in top3.iterrows():
        print(f"  {r['name']}: {r['pct_chg']:+.2f}%")
    bot3 = industry_df.tail(3)
    print(f"\n行业跌幅TOP3:")
    for _,r in bot3.iterrows():
        print(f"  {r['name']}: {r['pct_chg']:+.2f}%")

xq_follow = data['xueqiu_follow']
xq_tweet = data['xueqiu_tweet']
if not xq_follow.empty:
    print(f"\n雪球关注TOP5: {xq_follow['股票简称'].head(5).tolist()}")
if not xq_tweet.empty:
    print(f"雪球讨论TOP5: {xq_tweet['股票简称'].head(5).tolist()}")
