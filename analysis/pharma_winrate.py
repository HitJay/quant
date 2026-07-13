"""医药/中药 单日大涨后胜率量化计算 (复用 hotspot_winrate_calc 的方法论)

产出: output/hotspot/20260713/pharma_winrate.json
供 hotspot_cards_20260713_pharma_html.py 的量化页使用。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/das/user/QYJI/quant")
sys.path.insert(0, str(ROOT / "analysis"))

import hotspot_winrate_calc as wc  # noqa: E402

OUT_JSON = ROOT / f"output/hotspot/{wc.__dict__.get('DATE', '20260713')}"
INDEX_CONFIG = {
    "sw801151": {"name": "申万中药", "sw": True, "sw_code": "801151"},
    "sw801150": {"name": "申万医药生物", "sw": True, "sw_code": "801150"},
    "sz399006": {"name": "创业板指", "sw": False, "ak_type": "stock_zh_index_daily"},
    "sh000300": {"name": "沪深300", "sw": False, "ak_type": "stock_zh_index_daily"},
}
SCENARIOS = [
    {"id": "zhongyao_surge_self", "label": "中药大涨>2%→中药自身", "cond_idx": "sw801151",
     "cond_fn": lambda r: r > 0.02, "target_idx": "sw801151", "holds": [20, 60]},
    {"id": "zhongyao_surge_hs300", "label": "中药大涨>2%→沪深300", "cond_idx": "sw801151",
     "cond_fn": lambda r: r > 0.02, "target_idx": "sh000300", "holds": [20, 60]},
    {"id": "yiyao_surge_self", "label": "医药生物大涨>2%→医药自身", "cond_idx": "sw801150",
     "cond_fn": lambda r: r > 0.02, "target_idx": "sw801150", "holds": [20, 60]},
    {"id": "weak_defense", "label": "弱市+中药涨(创业板跌1.5% & 中药涨1%)→沪深300",
     "cond_type": "composite", "cond_indices": ["sz399006", "sw801151"],
     "cond_fn_composite": lambda r1, r2: (r1 < -0.015) & (r2 > 0.01),
     "target_idx": "sh000300", "holds": [20]},
    {"id": "zhongyao_surge_gem", "label": "中药大涨>2%→创业板", "cond_idx": "sw801151",
     "cond_fn": lambda r: r > 0.02, "target_idx": "sz399006", "holds": [20]},
    {"id": "zy_bucket_1_2", "label": "中药涨[1%,2%)→中药自身", "cond_idx": "sw801151",
     "cond_fn": lambda r: (r >= 0.01) & (r < 0.02), "target_idx": "sw801151", "holds": [20, 60]},
    {"id": "zy_bucket_2_3", "label": "中药涨[2%,3%)→中药自身", "cond_idx": "sw801151",
     "cond_fn": lambda r: (r >= 0.02) & (r < 0.03), "target_idx": "sw801151", "holds": [20, 60]},
    {"id": "zy_bucket_3p", "label": "中药涨[3%+]→中药自身", "cond_idx": "sw801151",
     "cond_fn": lambda r: r >= 0.03, "target_idx": "sw801151", "holds": [20, 60]},
]


def load_all(fresh: bool) -> dict:
    data = {}
    for sym, cfg in INDEX_CONFIG.items():
        p = wc.CACHE / f"{sym}.parquet"
        if fresh or not p.exists():
            print(f"  拉取 {cfg['name']} ({sym})...")
            data[sym] = wc.fetch_index(sym, cfg)
        else:
            data[sym] = wc.load_index(sym)
    return data


def percentile(series: pd.Series) -> dict:
    s = series.dropna()
    cur = float(s.iloc[-1])
    lo, hi = float(s.min()), float(s.max())
    pos = (cur - lo) / (hi - lo) * 100 if hi > lo else 0.0
    return {"cur": round(cur, 2), "min": round(lo, 2), "max": round(hi, 2),
            "pct_3y": round(pos, 1), "dist_high": round((cur / hi - 1) * 100, 1),
            "dist_low": round((cur / lo - 1) * 100, 1)}


def main():
    fresh = "--fresh" in sys.argv
    data = load_all(fresh)
    returns = {sym: s.pct_change().dropna() for sym, s in data.items()}

    results = {}
    for sc in SCENARIOS:
        if sc.get("cond_type") == "composite":
            r1 = returns[sc["cond_indices"][0]]
            r2 = returns[sc["cond_indices"][1]]
            cond = sc["cond_fn_composite"](r1, r2)
            valid = cond[cond].index
            valid = valid.intersection(r1.index).intersection(r2.index)
            valid = r1.reindex(valid).notna() & r2.reindex(valid).notna()
            print(f"  [{sc['id']}] {sc['label']}: 触发 {valid.sum()} 次")
            results[sc["id"]] = {"label": sc["label"], "trigger_count": int(valid.sum()),
                                  "results": wc.calc_win_rate(valid, data[sc["target_idx"]], sc["holds"])}
        else:
            cond = sc["cond_fn"](returns[sc["cond_idx"]])
            print(f"  [{sc['id']}] {sc['label']}: 触发 {cond.sum()} 次")
            results[sc["id"]] = {"label": sc["label"], "trigger_count": int(cond.sum()),
                                  "results": wc.calc_win_rate(cond, data[sc["target_idx"]], sc["holds"])}

    pos = {sym: percentile(data[sym]) for sym in ("sw801151", "sw801150")}

    # 最近几次 中药大涨>2% 后 20 日真实表现 (历史样本)
    zy = data["sw801151"]
    zy_ret = zy.pct_change().dropna()
    trig = zy_ret[zy_ret > 0.02]
    samples = []
    for d in reversed(list(trig.index)):
        idx = zy.index.get_loc(d)
        if idx + 20 < len(zy):
            r20 = zy.iloc[idx + 20] / zy.iloc[idx] - 1
            samples.append({"date": str(d.date()), "day_ret": round(float(zy_ret[d]) * 100, 2),
                            "ret20": round(r20 * 100, 2)})
        if len(samples) >= 5:
            break

    out = {"scenarios": results, "position": pos, "samples": samples,
           "generated_at": pd.Timestamp.now().isoformat(timespec="seconds")}
    out_path = ROOT / "output/hotspot/20260713/pharma_winrate.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✅ 已保存 {out_path}")
    for sid, sc in results.items():
        print(f"  [{sid}] 触发 {sc['trigger_count']} 次")
        for hk, hr in sc["results"].items():
            if hr.get("n", 0) > 0:
                print(f"      {hk}: 胜率 {hr['win_pct']}%  均值 {hr['mean_pct']:+.2f}%  中位 {hr['med_pct']:+.2f}%")
    print("  位置:", json.dumps(pos, ensure_ascii=False))


if __name__ == "__main__":
    main()
