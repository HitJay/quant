"""现金流反共识分析 + 8 页小红书深色卡片 — 2026-06-26.

核心叙事:
    1. 追踪 563390/159201/159222/159221/159223 五只现金流 ETF
    2. 代表产品持仓高度趋同, 风格暴露主要集中在汽车/石油石化/家电/航运/钢铁
    3. 国证自由现金流指数 2024-12 才发布, 现金流 ETF 集中 2025 上市 → 样本很短, 不宜夸大胜率
    4. 同期红利低波与沪深300表现差异说明: 现金流不是红利低波替代品, 更像周期/价值混合暴露
    5. 操作策略: 先看持仓和行业暴露, 再讨论抄底
"""

from __future__ import annotations

import os
import json
from pathlib import Path

for _k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
    os.environ.pop(_k, None)

import numpy as np
import pandas as pd

CACHE = Path("/das/user/QYJI/quant/data/cache/fcf")
OUT = Path("/das/user/QYJI/quant/output/2026-06-26/fcf-contrarian")
DATA_DIR = OUT / "data"
FIG_DIR = OUT / "figures"
CARD_DIR = OUT / "cards"
for d in (DATA_DIR, FIG_DIR, CARD_DIR):
    d.mkdir(parents=True, exist_ok=True)

# 5 只现金流 ETF
FCF_ETFS = [
    ("sh563390", "563390", "全指现金流ETF华泰柏瑞", "华泰柏瑞", "现金流策略产品", "2025-04-30"),
    ("sz159201", "159201", "自由现金流ETF华夏", "华夏",       "自由现金流策略产品", "2025-02-27"),
    ("sz159222", "159222", "自由现金流ETF易方达", "易方达",   "自由现金流策略产品", "2025-04-17"),
    ("sz159221", "159221", "现金流ETF嘉实", "嘉实",           "现金流策略产品", "2025-05-13"),
    ("sz159223", "159223", "现金流ETF永赢", "永赢",           "现金流策略产品", "2025-07-03"),
]
BENCH = [
    ("sh510300", "沪深300ETF", "#58a6ff"),
    ("sh510880", "红利ETF",    "#d2991d"),
    ("sh515100", "红利低波100ETF", "#3fb950"),
    ("sh515220", "煤炭ETF",    "#bc8cff"),
]


def load_etf(sym: str) -> pd.DataFrame:
    df = pd.read_parquet(CACHE / f"etf_{sym}.parquet")
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)


def load_idx(sym: str) -> pd.DataFrame:
    df = pd.read_parquet(CACHE / f"idx_{sym}.parquet")
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)


def perf_window(df: pd.DataFrame, end_date: pd.Timestamp | None = None) -> dict:
    """各窗口涨幅 + 距 ATH + YTD."""
    if end_date is None:
        end_date = df["date"].iloc[-1]
    sub = df[df["date"] <= end_date].reset_index(drop=True)
    cur = float(sub["close"].iloc[-1])
    out = {"cur": cur, "date_last": sub["date"].iloc[-1].strftime("%Y-%m-%d"), "n": len(sub)}
    for label, n in [("ret_1d", 1), ("ret_5d", 5), ("ret_10d", 10), ("ret_20d", 20), ("ret_60d", 60), ("ret_120d", 120)]:
        out[label] = float(cur / sub["close"].iloc[-n - 1] - 1) if len(sub) > n else None
    # YTD (2026 起)
    y = sub[sub["date"] >= "2026-01-01"]
    out["ret_ytd"] = float(cur / y["close"].iloc[0] - 1) if len(y) > 0 else None
    # ATH 与回撤
    peak = float(sub["close"].max())
    peak_d = sub.loc[sub["close"].idxmax(), "date"].strftime("%Y-%m-%d")
    out["ath"] = peak
    out["ath_date"] = peak_d
    out["cur_dd"] = float(cur / peak - 1)
    # 当前 cummax 回撤 (即时距 ATH, 与 cur_dd 等价当 ATH 在历史)
    cummax = sub["close"].expanding().max()
    dd_series = sub["close"] / cummax - 1
    out["max_dd"] = float(dd_series.min())
    out["max_dd_date"] = sub.loc[dd_series.idxmin(), "date"].strftime("%Y-%m-%d")
    return out


# ============ 1. 5 只 现金流 ETF 表现表 ============
print("=" * 60)
print("STAGE 1: 5 只 现金流 ETF 表现 + 基准对比")
print("=" * 60)
fcf_perf = {}
for sym, code, name, brand, track, ipo in FCF_ETFS:
    df = load_etf(sym)
    p = perf_window(df)
    p.update({"name": name, "brand": brand, "track": track, "ipo": ipo, "code": code, "sym": sym})
    fcf_perf[sym] = p
    print(f"\n{name} ({code}) {brand}")
    print(f"  上市 {ipo}  收盘 {p['cur']:.3f}")
    print(f"  20d={p['ret_20d']:+.2%}" if p['ret_20d'] is not None else "  20d=N/A", end="  ")
    print(f"60d={p['ret_60d']:+.2%}" if p['ret_60d'] is not None else "60d=N/A", end="  ")
    print(f"YTD={p['ret_ytd']:+.2%}" if p['ret_ytd'] is not None else "YTD=N/A")
    print(f"  ATH={p['ath']:.3f} ({p['ath_date']}) 距ATH={p['cur_dd']:+.2%}")

bench_perf = {}
for sym, name, color in BENCH:
    df = load_etf(sym)
    p = perf_window(df)
    p.update({"name": name, "color": color, "sym": sym})
    bench_perf[sym] = p

print("\n=== 基准 ===")
for sym, p in bench_perf.items():
    print(f"{p['name']:24s} 20d={p['ret_20d']:+.2%}  60d={p['ret_60d']:+.2%}  YTD={p['ret_ytd']:+.2%}")

# 国证自由现金流指数 sz980092 (现金流龙头)
idx_fcf = load_idx("sz980092")
idx_fcf_perf = perf_window(idx_fcf)
idx_fcf_perf["name"] = "国证自由现金流指数 (980092)"
print(f"\n国证自由现金流指数 980092: 60d={idx_fcf_perf['ret_60d']:+.2%}  YTD={idx_fcf_perf['ret_ytd']:+.2%}  距ATH={idx_fcf_perf['cur_dd']:+.2%}")

# 沪深300 / 中证红利 / 中证电力公用 长指数
idx_hs300 = load_idx("sh000300")
idx_perf_hs300 = perf_window(idx_hs300)
print(f"沪深300: 60d={idx_perf_hs300['ret_60d']:+.2%}  YTD={idx_perf_hs300['ret_ytd']:+.2%}")

# ============ 2. 持仓行业归类 ============
print("\n" + "=" * 60)
print("STAGE 2: 持仓行业归类 (核心反共识)")
print("=" * 60)

# 手工行业映射 (覆盖关键大权重)
SECTOR_MAP = {
    # 现金流 ETF 代表持仓 (159201/159222/159221/159223/563390)
    "600104": "汽车", "600938": "石油石化", "000651": "家电",
    "601919": "航运", "601633": "汽车", "600019": "钢铁",
    "601600": "有色", "600050": "通信", "000338": "机械",
    "601877": "电气设备", "600170": "建筑", "000708": "钢铁",
    "601727": "电气设备", "600057": "贸易", "000039": "机械",
    "601728": "通信", "002714": "农牧", "000100": "电子",
    "002352": "物流",
}

holdings_by_etf = {}
for sym, code, name, brand, track, ipo in FCF_ETFS:
    hp = CACHE / f"hold_{code}.parquet"
    if not hp.exists():
        print(f"  [skip] {code} 无持仓数据")
        continue
    hd = pd.read_parquet(hp)
    # 过滤 占净值比例 > 0
    hd = hd[hd["占净值比例"] > 0.001].copy()
    hd["sector"] = hd["股票代码"].map(SECTOR_MAP).fillna("其他")
    # 按行业聚合
    sec = hd.groupby("sector")["占净值比例"].sum().sort_values(ascending=False)
    holdings_by_etf[sym] = {
        "name": name, "brand": brand, "code": code,
        "top10": hd[["股票代码", "股票名称", "占净值比例", "sector"]].head(10).to_dict(orient="records"),
        "sectors": sec.to_dict(),
        "total_pct": float(hd["占净值比例"].sum()),
        "n_stocks": int(len(hd)),
    }
    print(f"\n{name} ({code}) top sectors:")
    for s, w in sec.head(6).items():
        print(f"  {s:8s} {w:.2f}%")

# ============ 3. 跌的真相 — 5 只 ETF 的相关性矩阵 + 与煤炭/资源/红利的相关性 ============
print("\n" + "=" * 60)
print("STAGE 3: 现金流跑势归因 (相关性 + 跟踪指数辨析)")
print("=" * 60)

# 取最近 120 个交易日, 各 ETF 收益率序列
SERIES = {}
for sym, code, name, *_ in FCF_ETFS:
    df = load_etf(sym).set_index("date")
    SERIES[sym] = df["close"].pct_change().dropna().iloc[-120:]
for sym, name, _ in BENCH:
    df = load_etf(sym).set_index("date")
    SERIES[sym] = df["close"].pct_change().dropna().iloc[-120:]

# 对齐
ret_df = pd.DataFrame(SERIES).dropna()
print(f"\n相关性窗口 N={len(ret_df)}, range={ret_df.index[0].date()} ~ {ret_df.index[-1].date()}")
corr = ret_df.corr()
# 焦点: 国证现金流 (159201) 与各基准的相关
key_sym = "sz159201"
print(f"\n{key_sym} 国证自由现金流ETF 与基准相关性:")
for s in ["sh510300", "sh510880", "sh515100", "sh515220"]:
    if s in corr.columns:
        print(f"  vs {bench_perf[s]['name']:24s} corr={corr.loc[key_sym, s]:.3f}")

# ============ 4. 条件胜率 (用代理) ============
# 现金流指数 980092 只有 363 天, 不够长. 取煤炭 ETF 515220 (4 年) + 沪深300 长期数据做 fallback.
# 用国证自由现金流指数 sz980092 月线做 fwd 回测, 接受样本小
print("\n" + "=" * 60)
print("STAGE 4: 现金流指数(短样本)前瞻收益分布 — 当前位置诊断")
print("=" * 60)

fcf_m = idx_fcf.set_index("date").resample("ME").last()
fcf_m_close = fcf_m["close"].dropna()
print(f"国证自由现金流指数月线 N={len(fcf_m_close)} {fcf_m_close.index[0].date()}~{fcf_m_close.index[-1].date()}")
# 太短 (18 个月), 无法做长期回测. 把这条放到卡片注解里诚实说明.

# 改用日线: 自上线以来不同回撤深度入场, 后续 3M/6M 表现 (尽量榨样本)
fcf_d = idx_fcf.set_index("date")["close"]
cummax_fcf = fcf_d.expanding().max()
dd_fcf = fcf_d / cummax_fcf - 1
print("\n国证 现金流指数 自发布以来回撤分布:")
print(f"  当前回撤  {dd_fcf.iloc[-1]:+.2%}")
print(f"  历史最深  {dd_fcf.min():+.2%} ({dd_fcf.idxmin().date()})")
print(f"  历史中位  {dd_fcf.median():+.2%}")
print(f"  10/90 分位 {dd_fcf.quantile(0.10):+.2%} / {dd_fcf.quantile(0.90):+.2%}")

# 把当前回撤的分位数算出来 — 当前 -22.81% 是历史多深?
cur_dd = float(dd_fcf.iloc[-1])
worse_pct = float((dd_fcf <= cur_dd).mean())
print(f"  当前回撤 {cur_dd:+.2%} 是历史样本中第 {(1 - worse_pct)*100:.0f}% 分位 (越低越深)")

# ============ 5. 红利 vs 现金流 长期对比 (用代理) ============
# 红利低波 sh510880 (4721 天 2007 起) vs 沪深300 vs (FCF 没法长 proxy)
# 取一段共同窗口, 滚动 12M 回报对比
print("\n" + "=" * 60)
print("STAGE 5: 红利 vs 沪深300 长期对比 (说明红利不是 FCF)")
print("=" * 60)
dvd = load_etf("sh510880").set_index("date")["close"]
hs300 = load_etf("sh510300").set_index("date")["close"]
common = pd.concat([dvd, hs300], axis=1, keys=["红利", "沪深300"]).dropna()
print(f"共同窗口 {common.index[0].date()} ~ {common.index[-1].date()} N={len(common)}")
ret_dvd_total = float(common["红利"].iloc[-1] / common["红利"].iloc[0] - 1)
ret_300_total = float(common["沪深300"].iloc[-1] / common["沪深300"].iloc[0] - 1)
years = (common.index[-1] - common.index[0]).days / 365.25
ann_dvd = (1 + ret_dvd_total) ** (1 / years) - 1
ann_300 = (1 + ret_300_total) ** (1 / years) - 1
print(f"红利 ETF: 累计 {ret_dvd_total:+.2%} 年化 {ann_dvd:+.2%}")
print(f"沪深300:  累计 {ret_300_total:+.2%} 年化 {ann_300:+.2%}")

# ============ 6. 导出 summary.json ============
summary = {
    "topic": "现金流反共识帖",
    "date": "2026-06-26",
    "headline": {
        "fcf_index_60d": idx_fcf_perf["ret_60d"],
        "fcf_index_ytd": idx_fcf_perf["ret_ytd"],
        "fcf_index_dd": idx_fcf_perf["cur_dd"],
        "hs300_60d": idx_perf_hs300["ret_60d"],
        "hs300_ytd": idx_perf_hs300["ret_ytd"],
        "dvd_lowvol_60d": bench_perf["sh515100"]["ret_60d"],
        "dvd_lowvol_ytd": bench_perf["sh515100"]["ret_ytd"],
        "underperf_pp_60d": idx_fcf_perf["ret_60d"] - idx_perf_hs300["ret_60d"],
        "underperf_pp_vs_dvd": idx_fcf_perf["ret_60d"] - bench_perf["sh515100"]["ret_60d"],
        "current_dd_percentile": 1 - worse_pct,
    },
    "fcf_etfs": fcf_perf,
    "benchmarks": bench_perf,
    "fcf_index_sz980092": idx_fcf_perf,
    "holdings": holdings_by_etf,
    "correlation_fcf_vs_bench": {
        "vs_hs300": float(corr.loc["sz159201", "sh510300"]),
        "vs_dividend": float(corr.loc["sz159201", "sh510880"]),
        "vs_dividend_lowvol": float(corr.loc["sz159201", "sh515100"]),
        "vs_coal": float(corr.loc["sz159201", "sh515220"]),
    },
    "long_term_dvd_vs_300": {
        "window_start": str(common.index[0].date()),
        "window_end": str(common.index[-1].date()),
        "years": round(years, 2),
        "dvd_total": ret_dvd_total,
        "hs300_total": ret_300_total,
        "dvd_annualized": ann_dvd,
        "hs300_annualized": ann_300,
    },
    "fcf_index_drawdown_stats": {
        "current_dd": cur_dd,
        "worst_dd": float(dd_fcf.min()),
        "median_dd": float(dd_fcf.median()),
        "sample_days": int(len(fcf_d)),
        "current_dd_percentile_deeper": 1 - worse_pct,
    },
}

with open(DATA_DIR / "summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
print(f"\n[OK] summary.json -> {DATA_DIR/'summary.json'}")

# 导出几个关键 CSV
pd.DataFrame([fcf_perf[s] for s in fcf_perf]).to_csv(DATA_DIR / "fcf_etf_perf.csv", index=False)
pd.DataFrame([bench_perf[s] for s in bench_perf]).to_csv(DATA_DIR / "bench_perf.csv", index=False)

# 持仓矩阵
rows = []
for sym, h in holdings_by_etf.items():
    for s, w in h["sectors"].items():
        rows.append({"etf": h["name"], "code": h["code"], "sector": s, "weight_pct": w})
pd.DataFrame(rows).to_csv(DATA_DIR / "holdings_sectors.csv", index=False)

print(f"[OK] CSV exports @ {DATA_DIR}")
print("\n[STAGE 1-6 DONE] 数据 + summary 完成. 下一步: 卡片渲染.")
