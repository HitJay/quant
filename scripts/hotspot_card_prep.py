"""A 股热点 → 自主选题 → 8 页深色 cards 端到端 wrapper.

被 cron 在 11:30 (早盘) / 15:00 (收盘) 调用。

流程:
1. 拉当日 hotspot (scripts/daily_hotspot.py)
2. 读 topics.json, 选 1 个最适合做小红书反共识的 angle
3. 写 selection 报告 (供 agent 后续手工或 cron 二次跑)

不在这里直接渲染 cards — 因为选题 + 数据 fetch + 卡片设计需要 LLM 推理,
cron 调用的 LLM agent 会接管后续步骤. 本脚本只准备\"事实材料\".
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def main():
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
        os.environ.pop(k, None)

    label = sys.argv[1] if len(sys.argv) > 1 else "snapshot"
    date_str = datetime.now().strftime("%Y%m%d")
    out_root = Path("/das/user/QYJI/quant/output/hotspot") / date_str
    print(f"=== Hotspot pull ({label}) @ {datetime.now().strftime('%H:%M:%S')} ===")

    # 1. 拉 hotspot (走仓里已有的 daily_hotspot.py)
    r = subprocess.run(
        ["conda", "run", "-n", "research", "python",
         "/das/user/QYJI/quant/scripts/daily_hotspot.py",
         "--quiet", "--no-cache"],
        capture_output=True, text=True, timeout=600,
        cwd="/das/user/QYJI/quant",
    )
    print(f"daily_hotspot RC: {r.returncode}")
    if r.returncode != 0:
        print("STDERR:", r.stderr[-2000:])
        sys.exit(1)
    print(r.stdout[-1500:])

    # 2. 读 topics.json + summary.json 给后续 agent
    topics_path = out_root / "topics.json"
    summary_path = out_root / "summary.json"
    digest_path = out_root / "digest.md"

    if not topics_path.exists():
        print(f"FAIL: {topics_path} not generated")
        sys.exit(2)

    topics = json.loads(topics_path.read_text(encoding="utf-8"))
    print()
    print(f"=== {len(topics)} 个选题候选 ===")
    for i, t in enumerate(topics, 1):
        print(f"  [{i}] [{t.get('angle','?')}] {t.get('hook','')[:80]}")
        ev = t.get('evidence', '')
        if ev:
            print(f"      证据: {str(ev)[:120]}")

    # 3. 标记 label (供 agent 区分早盘/收盘)
    marker = out_root / f"_pulled_{label}.txt"
    marker.write_text(
        f"{datetime.now().isoformat()}\n"
        f"label: {label}\n"
        f"topics: {len(topics)}\n",
        encoding="utf-8",
    )
    print(f"\n[OK] marker -> {marker}")
    print(f"[NEXT] agent 选题 + 渲染 cards: {out_root}")


if __name__ == "__main__":
    main()
