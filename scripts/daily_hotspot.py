#!/usr/bin/env python
"""每日散户热点简报 CLI

用法:
    python scripts/daily_hotspot.py                     # 拉今日(或最近交易日)数据 → 写到 output/hotspot/
    python scripts/daily_hotspot.py --date 20260617     # 指定日期
    python scripts/daily_hotspot.py --no-cache          # 强制重抓
    python scripts/daily_hotspot.py --json-only         # 只输出 JSON, 不渲染 markdown

产出:
    output/hotspot/<date>/
      ├── summary.json       结构化数据
      ├── topics.json        选题候选
      ├── digest.md          人读简报
      └── raw/<source>.parquet  各源原始数据
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# 让 src/ 可被 import
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from quant.data.hotspot_fetcher import HotspotFetcher, _last_trading_day_str  # noqa: E402
from quant.monitor.hotspot_digest import summarize, generate_topics, to_markdown  # noqa: E402


def _df_to_records(df) -> list:
    """DataFrame → list[dict], 处理日期等不可序列化字段"""
    if df is None or len(df) == 0:
        return []
    out = df.copy()
    for c in out.columns:
        if str(out[c].dtype).startswith("datetime"):
            out[c] = out[c].astype(str)
    return out.to_dict("records")


def main():
    ap = argparse.ArgumentParser(description="每日散户热点简报")
    ap.add_argument("--date", default=None, help="日期 YYYYMMDD, 默认最近交易日")
    ap.add_argument("--no-cache", action="store_true", help="强制重抓不读缓存")
    ap.add_argument("--output-dir", default="output/hotspot", help="输出目录")
    ap.add_argument("--json-only", action="store_true", help="只输出 JSON")
    ap.add_argument("--quiet", action="store_true", help="不打印到 stdout")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    log = logging.getLogger("daily_hotspot")

    date = args.date or _last_trading_day_str()
    out_dir = Path(args.output_dir) / date
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = out_dir / "raw"
    raw_dir.mkdir(exist_ok=True)

    log.info("开始拉取 %s 散户热点数据 ...", date)
    fetcher = HotspotFetcher()
    if args.no_cache:
        # 简单粗暴: 删掉当日缓存
        for p in fetcher.cache_dir.glob(f"*_{date}.parquet"):
            p.unlink()

    data = fetcher.fetch_all(date=date)

    # 保存原始数据
    for src, df in data.items():
        if len(df) == 0:
            log.warning("%s: 空", src)
            continue
        try:
            df.to_parquet(raw_dir / f"{src}.parquet")
            log.info("%s: %d 条", src, len(df))
        except Exception as e:
            log.warning("%s 写入失败: %s", src, e)

    # 汇总
    log.info("汇总数据 ...")
    summary = summarize(data, date=date)
    topics = generate_topics(summary)

    # 写 json
    (out_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    (out_dir / "topics.json").write_text(
        json.dumps(topics, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    if not args.json_only:
        md = to_markdown(summary, topics)
        (out_dir / "digest.md").write_text(md, encoding="utf-8")

    log.info("✅ 完成. 产出 → %s", out_dir.resolve())
    log.info("  - summary.json (%d sources)", sum(1 for v in data.values() if len(v) > 0))
    log.info("  - topics.json  (%d 选题候选)", len(topics))
    if not args.json_only:
        log.info("  - digest.md")

    if not args.quiet and not args.json_only:
        print()
        print((out_dir / "digest.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
