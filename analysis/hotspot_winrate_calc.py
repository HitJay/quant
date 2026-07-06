#!/usr/bin/env python
"""热点题材胜率量化计算器.

基于申万行业指数/中证指数历史日线, 计算关键市场信号后的胜率.
产出: JSON 供卡片脚本使用.

用法:
    python analysis/hotspot_winrate_calc.py                     # 标准回测
    python analysis/hotspot_winrate_calc.py --fresh             # 强制重拉数据
    python analysis/hotspot_winrate_calc.py --json              # 只输出 JSON

回测场景:
    A: 创业板单日大跌 >1.5% → 后续 20/60 日表现
    B: 煤炭单日大涨 >3%    → 后续 20/60 日行业及大盘表现
    C: 极端分化 (创业板跌>1.5% + 煤炭涨>2%) → 后续创业板
    D: 银行单日大涨 >2%    → 后续 20 日市场表现
    E: 中证红利大涨 >2%    → 后续 20/60 日市场表现
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

CACHE = ROOT / "data/cache/index"

# ─── 指数配置 ──────────────────────────
INDEX_CONFIG = {
    "sz399006": {"name": "创业板指", "sw": False, "ak_type": "stock_zh_index_daily"},
    "sw801950": {"name": "申万煤炭", "sw": True, "sw_code": "801950"},
    "sw801780": {"name": "申万银行", "sw": True, "sw_code": "801780"},
    "sh000300": {"name": "沪深300",  "sw": False, "ak_type": "stock_zh_index_daily"},
    "sh000922": {"name": "中证红利", "sw": False, "ak_type": "stock_zh_index_daily"},
}

# ─── 回测场景定义 ──────────────────────
SCENARIOS = [
    {
        "id": "A_gem_crash",
        "label": "创业板大跌>1.5%→创业板自身",
        "cond_idx": "sz399006", "cond_fn": lambda r: r < -0.015,
        "target_idx": "sz399006",
        "holds": [20, 60],
    },
    {
        "id": "B_coal_surge_self",
        "label": "煤炭大涨>3%→煤炭自身",
        "cond_idx": "sw801950", "cond_fn": lambda r: r > 0.03,
        "target_idx": "sw801950",
        "holds": [20, 60],
    },
    {
        "id": "B_coal_surge_gem",
        "label": "煤炭大涨>3%→创业板",
        "cond_idx": "sw801950", "cond_fn": lambda r: r > 0.03,
        "target_idx": "sz399006",
        "holds": [20, 60],
    },
    {
        "id": "B_coal_surge_hs300",
        "label": "煤炭大涨>3%→沪深300",
        "cond_idx": "sw801950", "cond_fn": lambda r: r > 0.03,
        "target_idx": "sh000300",
        "holds": [20, 60],
    },
    {
        "id": "C_extreme_divergence",
        "label": "极端分化(创业板跌1.5%+煤炭涨2%)→创业板",
        "cond_type": "composite",
        "cond_indices": ["sz399006", "sw801950"],
        "cond_fn_composite": lambda r1, r2: (r1 < -0.015) & (r2 > 0.02),
        "target_idx": "sz399006",
        "holds": [20, 60],
    },
    {
        "id": "D_bank_surge_hs300",
        "label": "银行大涨>2%→沪深300",
        "cond_idx": "sw801780", "cond_fn": lambda r: r > 0.02,
        "target_idx": "sh000300",
        "holds": [20],
    },
    {
        "id": "D_bank_surge_gem",
        "label": "银行大涨>2%→创业板",
        "cond_idx": "sw801780", "cond_fn": lambda r: r > 0.02,
        "target_idx": "sz399006",
        "holds": [20],
    },
    {
        "id": "E_div_surge_self",
        "label": "红利大涨>2%→红利自身",
        "cond_idx": "sh000922", "cond_fn": lambda r: r > 0.02,
        "target_idx": "sh000922",
        "holds": [20, 60],
    },
    {
        "id": "E_div_surge_hs300",
        "label": "红利大涨>2%→沪深300",
        "cond_idx": "sh000922", "cond_fn": lambda r: r > 0.02,
        "target_idx": "sh000300",
        "holds": [20, 60],
    },
    {
        "id": "E_div_surge_gem",
        "label": "红利大涨>2%→创业板",
        "cond_idx": "sh000922", "cond_fn": lambda r: r > 0.02,
        "target_idx": "sz399006",
        "holds": [20, 60],
    },
]


# ─── 数据加载 ──────────────────────────
def load_index(sym: str) -> pd.Series:
    """加载指数收盘价序列"""
    p = CACHE / f"{sym}.parquet"
    if not p.exists():
        raise FileNotFoundError(f"缓存不存在: {p}，请先运行 --fresh")
    df = pd.read_parquet(p)

    # 列名归一化
    rename_map = {}
    for c in df.columns:
        cl = str(c).lower()
        if cl in ("date", "日期", "datetime"):
            rename_map[c] = "date"
        elif cl in ("close", "收盘", "收盘价", "closevalue"):
            rename_map[c] = "close"
    df = df.rename(columns=rename_map)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date").sort_index()

    if "close" not in df.columns:
        # 申万指数: 取第一列数值
        num_cols = df.select_dtypes(include=[np.number]).columns
        if len(num_cols) > 0:
            df = df.rename(columns={num_cols[0]: "close"})

    return pd.to_numeric(df["close"], errors="coerce").dropna()


def fetch_index(sym: str, cfg: dict) -> pd.Series:
    """拉取指数数据并缓存"""
    import akshare as ak

    p = CACHE / f"{sym}.parquet"
    p.parent.mkdir(parents=True, exist_ok=True)

    if cfg.get("sw"):
        df = ak.index_hist_sw(symbol=cfg["sw_code"], period="day")
    else:
        df = ak.stock_zh_index_daily(symbol=sym)

    df.to_parquet(p)
    return load_index(sym)


# ─── 胜率计算 ──────────────────────────
def calc_win_rate(condition: pd.Series, target: pd.Series, hold_days: list[int]) -> dict:
    """条件触发后持有N日的胜率统计"""
    trigger_dates = condition[condition].index
    trigger_dates = trigger_dates.intersection(target.index)

    if len(trigger_dates) == 0:
        return {f"hold{h}d": {"n": 0} for h in hold_days}

    results = {}
    for h in hold_days:
        wins, returns = 0, []
        for d in trigger_dates:
            try:
                idx = target.index.get_loc(d)
                if idx + h < len(target):
                    ret = target.iloc[idx + h] / target.iloc[idx] - 1
                    returns.append(ret)
                    if ret > 0:
                        wins += 1
            except (KeyError, IndexError):
                continue

        n = len(returns)
        if n == 0:
            results[f"hold{h}d"] = {"n": 0}
        else:
            arr = np.array(returns)
            results[f"hold{h}d"] = {
                "n": n,
                "win_pct": round(wins / n * 100, 1),
                "mean_pct": round(arr.mean() * 100, 2),
                "med_pct": round(np.median(arr) * 100, 2),
                "p25_pct": round(np.percentile(arr, 25) * 100, 2),
                "p75_pct": round(np.percentile(arr, 75) * 100, 2),
                "worst_pct": round(arr.min() * 100, 2),
                "best_pct": round(arr.max() * 100, 2),
            }

    return results


def run_all_scenarios(data: dict[str, pd.Series]) -> dict:
    """运行所有回测场景"""
    # 预计算日收益率
    returns = {sym: s.pct_change().dropna() for sym, s in data.items()}

    results = {}
    for sc in SCENARIOS:
        sid = sc["id"]
        holds = sc["holds"]

        if sc.get("cond_type") == "composite":
            # 复合条件（多指数同时满足）
            r1 = returns[sc["cond_indices"][0]]
            r2 = returns[sc["cond_indices"][1]]
            cond = sc["cond_fn_composite"](r1, r2)
            common = cond[cond].index
            r1_aligned = r1.reindex(common)
            r2_aligned = r2.reindex(common)
            valid = r1_aligned.notna() & r2_aligned.notna()
            print(f"  [{sid}] {sc['label']}: 触发 {valid.sum()} 次")
            target_s = data[sc["target_idx"]]
            results[sid] = {
                "label": sc["label"],
                "trigger_count": int(valid.sum()),
                "results": calc_win_rate(valid, target_s, holds),
            }
        else:
            cond = sc["cond_fn"](returns[sc["cond_idx"]])
            print(f"  [{sid}] {sc['label']}: 触发 {cond.sum()} 次")
            target_s = data[sc["target_idx"]]
            results[sid] = {
                "label": sc["label"],
                "trigger_count": int(cond.sum()),
                "results": calc_win_rate(cond, target_s, holds),
            }

    return results


# ─── 命令行 ────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="热点题材胜率量化计算器")
    ap.add_argument("--fresh", action="store_true", help="强制重拉数据")
    ap.add_argument("--json", action="store_true", help="只输出 JSON")
    args = ap.parse_args()

    # 1. 加载/拉取数据
    data = {}
    for sym, cfg in INDEX_CONFIG.items():
        if args.fresh or not (CACHE / f"{sym}.parquet").exists():
            if not args.json:
                print(f"  拉取 {cfg['name']} ({sym})...")
            data[sym] = fetch_index(sym, cfg)
        else:
            data[sym] = load_index(sym)

    if not args.json:
        print(f"\n{'='*60}")
        print("📊 热点胜率量化回测")
        print(f"{'='*60}\n")

    # 2. 运行回测
    results = run_all_scenarios(data)

    # 3. 输出
    out_path = ROOT / "output/hotspot/winrate_benchmark.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(f"\n{'='*60}")
        print("📈 结果摘要")
        print(f"{'='*60}")
        for sid, sc in results.items():
            label = sc["label"]
            print(f"\n  [{sid}] {label}")
            print(f"      触发: {sc['trigger_count']} 次")
            for hk, hr in sc["results"].items():
                if hr.get("n", 0) > 0:
                    print(f"      {hk}: 胜率 {hr['win_pct']}%  (n={hr['n']})  "
                          f"均值 {hr['mean_pct']:+.2f}%  中位 {hr['med_pct']:+.2f}%  "
                          f"[P25={hr['p25_pct']:+.2f}%, P75={hr['p75_pct']:+.2f}%]")

        print(f"\n✅ 已保存到 {out_path}")
        print(f"   共 {len(results)} 个场景, {sum(sc['trigger_count'] for sc in results.values())} 次触发")


if __name__ == "__main__":
    main()
