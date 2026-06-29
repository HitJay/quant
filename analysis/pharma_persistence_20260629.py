"""医药行情持久度事件研究 — 2026-06-29.

口径: 使用医药长序列 ETF(159929) 和创新药 ETF(159992) 的后复权日线，
筛选单日大涨事件，统计未来 5/10/20 个交易日胜率、中位收益和回吐概率。
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/2026-06-29/today-hotspots"
OUT.mkdir(parents=True, exist_ok=True)

ASSETS = {
    "159929": "医药长序列ETF",
    "159992": "创新药ETF",
}
THRESHOLDS = [0.03, 0.04, 0.05]
HORIZONS = [5, 10, 20]
DECLUSTER_GAP = 5


def pct(value: float) -> str:
    return f"{value:.0%}"


def signed_pct(value: float) -> str:
    return f"{value:+.1%}"


def load_close(code: str) -> pd.Series:
    df = pd.read_parquet(ROOT / "data/cache/etf" / f"{code}.parquet")
    close = df["close"].dropna().astype(float).sort_index()
    return close


def decluster(index: pd.Index, all_dates: pd.Index, gap: int = DECLUSTER_GAP) -> list[pd.Timestamp]:
    pos = {date: i for i, date in enumerate(all_dates)}
    keep: list[pd.Timestamp] = []
    last_pos = -10_000
    for date in index:
        current_pos = pos[date]
        if current_pos - last_pos >= gap:
            keep.append(date)
            last_pos = current_pos
    return keep


def event_stats(code: str, name: str) -> tuple[dict, list[dict]]:
    close = load_close(code)
    ret = close.pct_change()
    latest = {
        "code": code,
        "name": name,
        "latest_date": str(close.index[-1].date()),
        "latest_close": float(close.iloc[-1]),
        "latest_ret": float(ret.iloc[-1]),
    }
    rows: list[dict] = []
    for threshold in THRESHOLDS:
        event = ret >= threshold
        for horizon in HORIZONS:
            future = close.shift(-horizon) / close - 1
            values = future[event & future.notna()]
            kept_dates = decluster(values.index, close.index)
            values = values.loc[kept_dates]
            row = {
                "code": code,
                "name": name,
                "threshold": threshold,
                "horizon": horizon,
                "n": int(len(values)),
            }
            if len(values):
                row.update({
                    "win_rate": float((values > 0).mean()),
                    "median_ret": float(values.median()),
                    "mean_ret": float(values.mean()),
                    "p25_ret": float(values.quantile(0.25)),
                    "p75_ret": float(values.quantile(0.75)),
                    "giveback_rate": float((values < -0.02).mean()),
                })
            rows.append(row)
    return latest, rows


def main() -> None:
    latest: dict[str, dict] = {}
    rows: list[dict] = []
    for code, name in ASSETS.items():
        item_latest, item_rows = event_stats(code, name)
        latest[code] = item_latest
        rows.extend(item_rows)

    result = pd.DataFrame(rows)
    result.to_csv(OUT / "pharma_persistence_event_study.csv", index=False)

    summary = {"latest": latest, "rows": rows}
    (OUT / "pharma_persistence_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    focus = result[(result["code"] == "159929") & (result["threshold"] == 0.04)].copy()
    focus10 = focus[focus["horizon"] == 10].iloc[0]
    inno = result[(result["code"] == "159992") & (result["threshold"] == 0.04)].copy()
    inno10 = inno[inno["horizon"] == 10].iloc[0]

    lines = [
        "# 医药行情持久度事件研究",
        "",
        f"数据: 159929 医药长序列ETF截至 {latest['159929']['latest_date']}, "
        f"当日涨幅 {signed_pct(latest['159929']['latest_ret'])}; "
        f"159992 创新药ETF截至 {latest['159992']['latest_date']}, "
        f"当日涨幅 {signed_pct(latest['159992']['latest_ret'])}。",
        "",
        "## 核心结论",
        f"- 医药长序列ETF历史上单日涨幅 >=4% 后, 10日胜率 {pct(focus10['win_rate'])}, "
        f"10日中位收益 {signed_pct(focus10['median_ret'])}, 样本 n={int(focus10['n'])}。",
        f"- 创新药ETF历史上单日涨幅 >=4% 后, 10日胜率 {pct(inno10['win_rate'])}, "
        f"10日中位收益 {signed_pct(inno10['median_ret'])}, 样本 n={int(inno10['n'])}。",
        f"- 医药长序列ETF >=4% 大涨日后, 5/10/20日胜率分别为 "
        + " / ".join(pct(x) for x in focus.sort_values("horizon")["win_rate"]),
        f"- 医药长序列ETF >=4% 大涨日后, 5/10/20日中位收益分别为 "
        + " / ".join(signed_pct(x) for x in focus.sort_values("horizon")["median_ret"]),
        "",
        "## 明细表: 159929 >=4% 大涨日",
        focus[["horizon", "n", "win_rate", "median_ret", "p25_ret", "p75_ret", "giveback_rate"]]
        .to_markdown(index=False),
        "",
    ]
    (OUT / "pharma_persistence_notes.md").write_text("\n".join(lines), encoding="utf-8")

    print("latest", json.dumps(latest, ensure_ascii=False))
    print("159929 >=4%")
    print(focus[["horizon", "n", "win_rate", "median_ret", "p25_ret", "p75_ret", "giveback_rate"]].to_string(index=False))
    print("159992 >=4%")
    print(inno[["horizon", "n", "win_rate", "median_ret", "p25_ret", "p75_ret", "giveback_rate"]].to_string(index=False))


if __name__ == "__main__":
    main()