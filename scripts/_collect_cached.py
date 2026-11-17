#!/usr/bin/env python
"""Generate digest from existing cache + raw data (no push2 needed)."""
import sys, json, pandas as pd
from pathlib import Path

sys.path.insert(0, "/das/user/QYJI/quant/src")
from quant.data.hotspot_fetcher import HotspotFetcher, _last_trading_day_str
from quant.monitor.hotspot_digest import summarize, generate_topics, to_markdown

date = "20260723"
raw_dir = Path(f"/das/user/QYJI/quant/output/hotspot/{date}/raw")
out_dir = Path(f"/das/user/QYJI/quant/output/hotspot/{date}")
out_dir.mkdir(parents=True, exist_ok=True)
raw_dir.mkdir(parents=True, exist_ok=True)

fetcher = HotspotFetcher()

# Fetch from cache (this is fast since parquet exists)
data = {}
sources = [
    ("zt_pool", lambda: fetcher.zt_pool(date)),
    ("zt_zbgc", lambda: fetcher.zt_zbgc(date)),
    ("zt_strong", lambda: fetcher.zt_strong(date)),
    ("xueqiu_follow", lambda: fetcher.xueqiu_hot(by="follow")),
    ("xueqiu_tweet", lambda: fetcher.xueqiu_hot(by="tweet")),
    ("em_hot_rank", lambda: fetcher.em_hot_rank()),
    ("lhb", lambda: fetcher.lhb_today(date)),
]

for name, fn in sources:
    try:
        df = fn()
        data[name] = df
        print(f"{name}: {len(df)} rows")
    except Exception as e:
        data[name] = pd.DataFrame()
        print(f"{name}: ERROR {e}")

# Try loading cached concept_board
try:
    cached = fetcher._load_cache("concept_board", date)
    if cached is not None and len(cached) > 0:
        data["concept_board"] = cached
        print(f"concept_board (cached): {len(cached)} rows")
    else:
        data["concept_board"] = pd.DataFrame()
        print("concept_board: no cache")
except:
    data["concept_board"] = pd.DataFrame()
    print("concept_board: load error")

# Industry board - no cache available
data["industry_board"] = pd.DataFrame()
print("industry_board: unavailable (push2 timeout)")

data["em_global_news"] = pd.DataFrame()
print("em_global_news: unavailable (timeout)")

# Save raw parquet files
for src, df in data.items():
    if len(df) > 0:
        df.to_parquet(raw_dir / f"{src}.parquet")
        print(f"  saved raw/{src}.parquet")

# Generate digest
summary = summarize(data, date=date)
topics = generate_topics(summary)

(out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
(out_dir / "topics.json").write_text(json.dumps(topics, ensure_ascii=False, indent=2), encoding="utf-8")
md = to_markdown(summary, topics)
(out_dir / "digest.md").write_text(md, encoding="utf-8")

print(f"\n=== DONE ===")
print(f"Topics: {len(topics)} candidates")
print(f"Digest lines: {len(md.strip().splitlines())}")

# Quick summary
print(f"\n涨停: {len(data.get('zt_pool',pd.DataFrame()))}")
print(f"炸板: {len(data.get('zt_zbgc',pd.DataFrame()))}")
if not data.get('xueqiu_follow',pd.DataFrame()).empty:
    print(f"雪球关注TOP5: {data['xueqiu_follow']['股票简称'].head(5).tolist()}")
if not data.get('xueqiu_tweet',pd.DataFrame()).empty:
    print(f"雪球讨论TOP5: {data['xueqiu_tweet']['股票简称'].head(5).tolist()}")
if not data.get('em_hot_rank',pd.DataFrame()).empty:
    print(f"东财人气TOP5: {data['em_hot_rank']['股票名称'].head(5).tolist()}")
