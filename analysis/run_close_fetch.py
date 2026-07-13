"""收盘数据刷新: 给 akshare 调用加 socket 超时, 避免 em_global_news 挂死; 跳过被墙的板块接口."""
from __future__ import annotations

import json
import logging
import socket
import sys
from pathlib import Path

socket.setdefaulttimeout(25)  # 单源最多 25s, 挂死就超时失败而不是卡住

ROOT = Path("/das/user/QYJI/quant")
sys.path.insert(0, str(ROOT / "src"))

from quant.data.hotspot_fetcher import HotspotFetcher, _last_trading_day_str  # noqa: E402
from quant.monitor.hotspot_digest import summarize, generate_topics  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

DATE = "20260713"
OUT = ROOT / "output/hotspot" / DATE
OUT.mkdir(parents=True, exist_ok=True)
raw = OUT / "raw"
raw.mkdir(exist_ok=True)

f = HotspotFetcher()
data = f.fetch_all(date=DATE)

for src, df in data.items():
    if len(df) == 0:
        logging.warning("%s: 空", src)
        continue
    try:
        df.to_parquet(raw / f"{src}.parquet")
        logging.info("%s: %d 条", src, len(df))
    except Exception as e:  # noqa
        logging.warning("%s 写失败: %s", src, e)

summary = summarize(data, date=DATE)
topics = generate_topics(summary)
(OUT / "summary.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
(OUT / "topics.json").write_text(
    json.dumps(topics, ensure_ascii=False, indent=2), encoding="utf-8")
logging.info("✅ 收盘数据已更新 -> %s (summary.json, %d 源非空)",
             OUT, sum(1 for v in data.values() if len(v) > 0))
