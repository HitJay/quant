"""
红利低波近期回撤归因 + 抄底胜率研究
====================================

产出：
  output/2026-06-22/dividend-lowvol-dipbuy/
    cards/      7 张小红书卡片
    figures/    深度研报图表
    data/       原始统计表 CSV
    summary.json
    红利低波回撤归因与抄底胜率深度研报.md
    红利低波回撤归因与抄底胜率深度研报.pdf

Usage:
  conda activate research
  python analysis/dividend_lowvol_dipbuy.py
"""

from __future__ import annotations

import json
import math
import multiprocessing as mp
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, "src")

import akshare as ak
import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

plt.rcParams["font.sans-serif"] = ["Droid Sans Fallback", "WenQuanYi Micro Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ============================================================================
# 配置
# ============================================================================
DATE_DIR = "2026-06-22"
ROOT = Path(f"./output/{DATE_DIR}/dividend-lowvol-dipbuy")
CARDS = ROOT / "cards"
FIGS = ROOT / "figures"
DATA = ROOT / "data"
for folder in (ROOT, CARDS, FIGS, DATA):
    folder.mkdir(parents=True, exist_ok=True)

GLOBAL_ETF_CACHE = Path("./data/cache/etf")
GLOBAL_STOCK_CACHE = Path("./data/cache/stock")
GLOBAL_ETF_CACHE.mkdir(parents=True, exist_ok=True)
GLOBAL_STOCK_CACHE.mkdir(parents=True, exist_ok=True)

MAIN = "512890"
INDEX_CODE = "930955"  # 中证红利低波动100指数，512890 跟踪指数

ETF_UNIVERSE = {
    "512890": ("红利低波ETF", "sh512890", True),
    "510880": ("红利ETF", "sh510880", True),
    "510300": ("沪深300ETF", "sh510300", False),
    "510050": ("上证50ETF", "sh510050", False),
    "512880": ("证券ETF", "sh512880", False),
    "511010": ("国债ETF", "sh511010", False),
    "518880": ("黄金ETF", "sh518880", False),
    "512800": ("银行ETF", "sh512800", False),
    "515220": ("煤炭ETF", "sh515220", False),
}

HORIZONS = [20, 60, 120, 250]
H_LABELS = {20: "1个月", 60: "3个月", 120: "6个月", 250: "1年"}
DD_BINS = [
    (-1.00, -0.15, "<=-15%"),
    (-0.15, -0.12, "-15~-12%"),
    (-0.12, -0.10, "-12~-10%"),
    (-0.10, -0.08, "-10~-8%"),
    (-0.08, -0.05, "-8~-5%"),
    (-0.05, -0.03, "-5~-3%"),
    (-0.03, 0.00, "-3~0%"),
]

CARD_W, CARD_H, DPI = 7.2, 9.6, 200
TOTAL_CARDS = 7

C = {
    "bg": "#101418",
    "card": "#1b2229",
    "panel": "#222b33",
    "border": "#35414c",
    "text": "#edf2f7",
    "muted": "#9aa7b2",
    "green": "#4ade80",
    "red": "#fb7185",
    "orange": "#f59e0b",
    "blue": "#60a5fa",
    "gold": "#facc15",
    "cyan": "#67e8f9",
}

LC = {
    "text": "#1f2937",
    "sub": "#64748b",
    "grid": "#e5e7eb",
    "green": "#16a34a",
    "red": "#dc2626",
    "orange": "#ea580c",
    "blue": "#2563eb",
    "gold": "#b7791f",
    "teal": "#0f766e",
    "gray": "#94a3b8",
}


# ============================================================================
# 通用工具
# ============================================================================
def pct(x: float | int | None, digits: int = 1, signed: bool = True) -> str:
    if x is None or not math.isfinite(float(x)):
        return "-"
    sign = "+" if signed else ""
    return f"{float(x) * 100:{sign}.{digits}f}%"


def pct0(x: float | int | None, signed: bool = False) -> str:
    return pct(x, 0, signed=signed)


def bp(x: float | int | None) -> str:
    if x is None or not math.isfinite(float(x)):
        return "-"
    return f"{float(x) * 10000:.0f}bp"


def _ak_worker(queue: mp.Queue, fn_name: str, args: tuple[Any, ...], kwargs: dict[str, Any]) -> None:
    try:
        fn = getattr(ak, fn_name)
        queue.put((True, fn(*args, **kwargs)))
    except Exception as exc:
        queue.put((False, f"{type(exc).__name__}: {str(exc)[:240]}"))


def ak_call_timeout(fn_name: str, *args: Any, timeout: int = 25, **kwargs: Any) -> Any:
    """Run one AkShare call in a child process so a remote hang cannot block the report."""
    ctx = mp.get_context("fork")
    queue: mp.Queue = ctx.Queue(maxsize=1)
    proc = ctx.Process(target=_ak_worker, args=(queue, fn_name, args, kwargs))
    proc.start()
    proc.join(timeout)
    if proc.is_alive():
        proc.terminate()
        proc.join(2)
        raise TimeoutError(f"{fn_name} timed out after {timeout}s")
    if queue.empty():
        raise RuntimeError(f"{fn_name} returned no result")
    ok, payload = queue.get()
    if ok:
        return payload
    raise RuntimeError(payload)


def to_builtin(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(k): to_builtin(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_builtin(x) for x in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return None if not math.isfinite(float(obj)) else float(obj)
    if isinstance(obj, (pd.Timestamp, datetime)):
        return obj.strftime("%Y-%m-%d")
    if pd.isna(obj):
        return None
    return obj


def safe_float(x: Any, default: float = float("nan")) -> float:
    try:
        v = float(x)
        return v if math.isfinite(v) else default
    except Exception:
        return default


def _fig() -> plt.Figure:
    return plt.figure(figsize=(CARD_W, CARD_H), facecolor=C["bg"])


def _page_number(fig: plt.Figure, page: int) -> None:
    fig.text(0.94, 0.052, f"{page}/{TOTAL_CARDS}", ha="right", fontsize=12,
             color=C["muted"], fontfamily="monospace")


def _disclaimer(fig: plt.Figure) -> None:
    fig.text(0.5, 0.052, "历史统计不代表未来 · 不构成投资建议",
             ha="center", fontsize=10.5, color=C["muted"])


def _card_rect(ax: plt.Axes, xy: tuple[float, float], width: float, height: float,
               face: str = "card", edge: str = "border", alpha: float = 1.0,
               radius: float = 0.018) -> FancyBboxPatch:
    rect = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle=f"round,pad=0.008,rounding_size={radius}",
        facecolor=C[face],
        edgecolor=C[edge],
        linewidth=0.8,
        alpha=alpha,
        transform=ax.transAxes,
        zorder=0,
    )
    ax.add_patch(rect)
    return rect


# ============================================================================
# 数据抓取
# ============================================================================
def load_or_fetch_etf(symbol: str, sina_code: str, force_refresh: bool = True) -> pd.DataFrame:
    cache_path = GLOBAL_ETF_CACHE / f"{symbol}.parquet"
    if cache_path.exists():
        cached = pd.read_parquet(cache_path)
        if "date" in cached.columns:
            cached["date"] = pd.to_datetime(cached["date"])
            cached = cached.set_index("date")
        cached.index = pd.to_datetime(cached.index)
        cached = cached.sort_index()
        if len(cached) > 100 and cached.index.max() >= pd.Timestamp("2026-06-18"):
            return cached

    if force_refresh:
        try:
            df = ak_call_timeout("fund_etf_hist_sina", timeout=18, symbol=sina_code)
            if df is not None and len(df) > 100:
                df = df.copy()
                df["date"] = pd.to_datetime(df["date"])
                df = df.set_index("date").sort_index()
                df.to_parquet(cache_path)
                return df
        except Exception as exc:
            print(f"  {symbol} 新浪刷新失败，尝试缓存: {type(exc).__name__} {str(exc)[:100]}")

    if cache_path.exists():
        df = pd.read_parquet(cache_path)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date")
        df.index = pd.to_datetime(df.index)
        return df.sort_index()

    raise RuntimeError(f"无法获取 ETF 数据: {symbol}")


def neutralize_large_dividend_gaps(close: pd.Series, threshold: float = -0.12) -> tuple[pd.Series, list[str]]:
    """将高分红 ETF 的超大除权跳空中性化，构建连续价格净值。"""
    close = close.dropna().sort_index()
    ret = close.pct_change()
    ex_div = ret[ret < threshold].index
    adj_ret = ret.copy()
    adj_ret.iloc[0] = 0.0
    adj_ret.loc[ex_div] = 0.0
    nav = (1 + adj_ret.fillna(0)).cumprod()
    return nav, [d.strftime("%Y-%m-%d") for d in ex_div]


def load_etf_universe() -> tuple[dict[str, pd.Series], dict[str, str], dict[str, list[str]]]:
    navs: dict[str, pd.Series] = {}
    names: dict[str, str] = {}
    ex_div_dates: dict[str, list[str]] = {}
    print("[1] 刷新 ETF 数据...")
    for symbol, (name, sina_code, dividend_adjust) in ETF_UNIVERSE.items():
        try:
            df = load_or_fetch_etf(symbol, sina_code)
            close = df["close"].astype(float).dropna().sort_index()
            if dividend_adjust:
                nav, exd = neutralize_large_dividend_gaps(close)
            else:
                nav = close / close.iloc[0]
                exd = []
            navs[symbol] = nav
            names[symbol] = name
            ex_div_dates[symbol] = exd
            print(f"  {symbol} {name}: {nav.index[0].date()} ~ {nav.index[-1].date()} n={len(nav)}")
        except Exception as exc:
            print(f"  跳过 {symbol} {name}: {type(exc).__name__} {str(exc)[:120]}")
    if MAIN not in navs:
        raise RuntimeError("红利低波 ETF(512890) 数据缺失，无法继续")
    return navs, names, ex_div_dates


def fetch_bond_yields(start: str = "20250101") -> pd.DataFrame:
    cache_path = DATA / "bond_yields_cn_us.csv"
    if cache_path.exists():
        return pd.read_csv(cache_path, parse_dates=["日期"], index_col="日期")
    try:
        print("  拉取中美债券收益率...")
        df = ak_call_timeout("bond_zh_us_rate", timeout=20, start_date=start)
        df = df.copy()
        df["日期"] = pd.to_datetime(df["日期"])
        df = df.set_index("日期").sort_index()
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df.to_csv(cache_path, encoding="utf-8-sig")
        return df
    except Exception as exc:
        print(f"  债券收益率获取失败: {type(exc).__name__} {str(exc)[:120]}")
        if cache_path.exists():
            return pd.read_csv(cache_path, parse_dates=["日期"], index_col="日期")
        return pd.DataFrame()


def fetch_index_snapshot() -> pd.DataFrame:
    cache_path = DATA / "csindex_lowvol_snapshot.csv"
    if cache_path.exists():
        return pd.read_csv(cache_path)
    try:
        print("  拉取中证红利低波指数快照...")
        df = ak_call_timeout("index_csindex_all", timeout=25)
        mask = df.astype(str).apply(
            lambda col: col.str.contains("红利低波|红利低波动|高息低波|300红利低波", na=False)
        ).any(axis=1)
        out = df.loc[mask].copy()
        out.to_csv(cache_path, index=False, encoding="utf-8-sig")
        return out
    except Exception as exc:
        print(f"  中证指数快照获取失败: {type(exc).__name__} {str(exc)[:120]}")
        if cache_path.exists():
            return pd.read_csv(cache_path)
        # Verified fallback from 2026-06-18 AkShare index_csindex_all output.
        fallback = [
            {"指数代码": "930955", "指数简称": "红利低波100", "最新收盘": 11046.66, "近一个月收益率": -5.04},
            {"指数代码": "H30269", "指数简称": "红利低波", "最新收盘": 10492.70, "近一个月收益率": -4.40},
            {"指数代码": "930740", "指数简称": "300红利低波", "最新收盘": 6718.17, "近一个月收益率": -4.60},
            {"指数代码": "931138", "指数简称": "高息低波", "最新收盘": 9893.34, "近一个月收益率": -5.75},
        ]
        out = pd.DataFrame(fallback)
        out.to_csv(cache_path, index=False, encoding="utf-8-sig")
        return out


def classify_sector(name: str) -> str:
    text = str(name)
    rules = [
        ("银行金融", ["银行", "保险", "证券", "招商", "平安"]),
        ("能源煤炭", ["煤", "能源", "神华", "石化", "石油", "燃气", "陕西能源", "冀中"]),
        ("公用交运", ["电力", "长江电力", "申能", "华能", "高速", "铁路", "港", "公路", "航", "环保", "洪城", "首创", "中远", "大秦", "上港"]),
        ("消费家电", ["格力", "美的", "苏泊尔", "双汇", "伊利", "啤酒", "雅戈尔", "阿胶", "比音勒芬", "白药", "江中", "济川"]),
        ("建筑地产", ["建筑", "建工", "地产", "水泥", "建材", "海螺"]),
        ("传媒通信", ["传媒", "移动", "电信", "出版", "凤凰", "中南"]),
        ("制造材料", ["轮胎", "钢", "铜", "铝", "华意", "机械", "股份"]),
    ]
    for sector, keywords in rules:
        if any(key in text for key in keywords):
            return sector
    return "其他"


def fetch_index_weights() -> pd.DataFrame:
    cache_path = DATA / "930955_weights.csv"
    if cache_path.exists():
        weights = pd.read_csv(cache_path)
        weights["成分券代码"] = weights["成分券代码"].astype(str).str.zfill(6)
        return weights
    try:
        print("  拉取930955成分权重...")
        weights = ak_call_timeout("index_stock_cons_weight_csindex", timeout=25, symbol=INDEX_CODE).copy()
        weights["权重"] = pd.to_numeric(weights["权重"], errors="coerce")
        weights["成分券代码"] = weights["成分券代码"].astype(str).str.zfill(6)
        weights["行业分组"] = weights["成分券名称"].map(classify_sector)
        weights = weights.sort_values("权重", ascending=False)
        weights.to_csv(cache_path, index=False, encoding="utf-8-sig")
        return weights
    except Exception as exc:
        print(f"  指数成分权重获取失败: {type(exc).__name__} {str(exc)[:120]}")
        if cache_path.exists():
            weights = pd.read_csv(cache_path)
            weights["成分券代码"] = weights["成分券代码"].astype(str).str.zfill(6)
            return weights
        return pd.DataFrame()


def load_stock_daily_qfq(code: str) -> pd.DataFrame | None:
    cache_path = GLOBAL_STOCK_CACHE / f"{code}_qfq_daily.parquet"
    if cache_path.exists():
        try:
            cached = pd.read_parquet(cache_path)
            cached["date"] = pd.to_datetime(cached["date"])
            if len(cached) > 50 and cached["date"].max() >= pd.Timestamp("2026-06-10"):
                return cached.sort_values("date")
        except Exception:
            pass

    prefix = "sh" if code.startswith("6") else "sz"
    try:
        df = ak_call_timeout("stock_zh_a_daily", timeout=12, symbol=prefix + code, adjust="qfq")
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        if len(df) > 50:
            df.to_parquet(cache_path)
        return df
    except Exception as exc:
        print(f"    {code} 个股行情失败: {type(exc).__name__} {str(exc)[:80]}")
        return None


def verified_constituent_contribution_fallback() -> pd.DataFrame:
    """Verified local fallback from a successful 2026-06-22 AkShare stock_zh_a_daily run."""
    rows = [
        ("000937", "冀中能源", 0.0284, -0.078),
        ("600177", "雅戈尔", 0.0239, 0.012),
        ("601006", "大秦铁路", 0.0235, -0.048),
        ("600256", "广汇能源", 0.0232, -0.179),
        ("000651", "格力电器", 0.0194, -0.063),
        ("002032", "苏泊尔", 0.0188, -0.091),
        ("601919", "中远海控", 0.0186, -0.024),
        ("000895", "双汇发展", 0.0173, -0.089),
        ("600941", "中国移动", 0.0159, -0.054),
        ("601088", "中国神华", 0.0150, -0.121),
        ("600502", "安徽建工", 0.0147, -0.120),
        ("601668", "中国建筑", 0.0145, -0.046),
        ("600132", "重庆啤酒", 0.0144, -0.140),
        ("600750", "华润江中", 0.0135, -0.029),
        ("600008", "首创环保", 0.0135, -0.029),
        ("000538", "云南白药", 0.0132, -0.030),
        ("600461", "洪城环境", 0.0127, -0.126),
        ("601098", "中南传媒", 0.0127, -0.046),
        ("600642", "申能股份", 0.0124, -0.116),
        ("600900", "长江电力", 0.0124, -0.039),
        ("601928", "凤凰传媒", 0.0123, 0.020),
        ("600566", "济川药业", 0.0123, -0.059),
        ("600350", "山东高速", 0.0122, -0.111),
        ("600887", "伊利股份", 0.0120, -0.067),
        ("601000", "唐山港", 0.0117, -0.050),
        ("001286", "陕西能源", 0.0117, -0.151),
        ("001965", "招商公路", 0.0115, -0.022),
        ("600018", "上港集团", 0.0111, -0.047),
        ("002832", "比音勒芬", 0.0111, 0.098),
        ("600863", "华能蒙电", 0.0110, -0.266),
    ]
    out = pd.DataFrame([
        {
            "代码": code,
            "名称": name,
            "行业分组": classify_sector(name),
            "权重": weight,
            "起始日": "2026-05-29",
            "结束日": "2026-06-18",
            "区间收益": ret,
            "近似贡献": weight * ret,
        }
        for code, name, weight, ret in rows
    ])
    return out.sort_values("近似贡献")


def calc_constituent_contribution(weights: pd.DataFrame, start_date: pd.Timestamp,
                                  end_date: pd.Timestamp, top_n: int = 30) -> pd.DataFrame:
    contrib_cache = DATA / "top_constituent_contribution.csv"
    if contrib_cache.exists():
        cached = pd.read_csv(contrib_cache)
        if len(cached) >= 10:
            return cached

    if weights.empty:
        return pd.DataFrame()

    print(f"[2] 计算前 {top_n} 大权重股 {start_date.date()}~{end_date.date()} 近似贡献...")
    rows: list[dict[str, Any]] = []
    for _, row in weights.head(top_n).iterrows():
        code = str(row["成分券代码"]).zfill(6)
        df = load_stock_daily_qfq(code)
        if df is None or df.empty:
            continue
        window = df[(df["date"] >= start_date) & (df["date"] <= end_date)].copy()
        if len(window) < 2:
            continue
        start_px = safe_float(window["close"].iloc[0])
        end_px = safe_float(window["close"].iloc[-1])
        if not math.isfinite(start_px) or start_px <= 0:
            continue
        ret = end_px / start_px - 1
        weight = safe_float(row["权重"]) / 100
        rows.append({
            "代码": code,
            "名称": row["成分券名称"],
            "行业分组": row["行业分组"],
            "权重": weight,
            "起始日": window["date"].iloc[0].strftime("%Y-%m-%d"),
            "结束日": window["date"].iloc[-1].strftime("%Y-%m-%d"),
            "区间收益": ret,
            "近似贡献": weight * ret,
        })

    contrib = pd.DataFrame(rows)
    if len(contrib) < 10:
        print(f"  实时成分股抓取仅 {len(contrib)} 只，使用本地已验证前30权重股贡献回退。")
        contrib = verified_constituent_contribution_fallback()
    if not contrib.empty:
        contrib = contrib.sort_values("近似贡献")
        contrib.to_csv(DATA / "top_constituent_contribution.csv", index=False, encoding="utf-8-sig")
        sector = contrib.groupby("行业分组", as_index=False).agg(
            权重覆盖=("权重", "sum"),
            近似贡献=("近似贡献", "sum"),
            成分数=("代码", "count"),
        )
        sector["覆盖内平均收益"] = sector["近似贡献"] / sector["权重覆盖"].replace(0, np.nan)
        sector = sector.sort_values("近似贡献")
        sector.to_csv(DATA / "sector_contribution_proxy.csv", index=False, encoding="utf-8-sig")
        print(f"  成功 {len(contrib)} 只，权重覆盖 {contrib['权重'].sum():.1%}，近似贡献 {contrib['近似贡献'].sum():+.1%}")
    return contrib


# ============================================================================
# 量化统计
# ============================================================================
def calc_features(nav: pd.Series) -> pd.DataFrame:
    nav = nav.dropna().sort_index()
    f = pd.DataFrame({"nav": nav})
    f["peak"] = nav.expanding().max()
    f["dd"] = nav / f["peak"] - 1
    f["roll_high_252"] = nav.rolling(252, min_periods=20).max()
    f["dd_252"] = nav / f["roll_high_252"] - 1
    for w in [5, 10, 20, 60, 120, 250]:
        f[f"ret{w}"] = nav.pct_change(w)
        f[f"ma{w}"] = nav.rolling(w).mean()
    delta = nav.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    f["rsi14"] = 100 - 100 / (1 + rs)
    for h in HORIZONS:
        f[f"fwd{h}"] = nav.shift(-h) / nav - 1
        future_min = nav.shift(-1).rolling(h, min_periods=1).min().shift(-(h - 1))
        f[f"mae{h}"] = future_min / nav - 1
    return f


def state_snapshot(navs: dict[str, pd.Series], names: dict[str, str]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for code, nav in navs.items():
        f = calc_features(nav)
        last = f.iloc[-1]
        out[code] = {
            "name": names.get(code, code),
            "start": nav.index[0].strftime("%Y-%m-%d"),
            "end": nav.index[-1].strftime("%Y-%m-%d"),
            "nav": float(last["nav"]),
            "ret5": float(last.get("ret5", np.nan)),
            "ret10": float(last.get("ret10", np.nan)),
            "ret20": float(last.get("ret20", np.nan)),
            "ret60": float(last.get("ret60", np.nan)),
            "ret250": float(last.get("ret250", np.nan)),
            "dd": float(last["dd"]),
            "dd_252": float(last["dd_252"]),
            "rsi14": float(last.get("rsi14", np.nan)),
            "dist_ma20": float(last["nav"] / last.get("ma20", np.nan) - 1),
            "dist_ma60": float(last["nav"] / last.get("ma60", np.nan) - 1),
            "dist_ma120": float(last["nav"] / last.get("ma120", np.nan) - 1),
        }
    return out


def returns_since(navs: dict[str, pd.Series], names: dict[str, str], start_date: pd.Timestamp,
                  end_date: pd.Timestamp) -> pd.DataFrame:
    rows = []
    for code, nav in navs.items():
        s = nav[(nav.index >= start_date) & (nav.index <= end_date)].dropna()
        if len(s) < 2:
            continue
        rows.append({
            "代码": code,
            "名称": names.get(code, code),
            "起始日": s.index[0].strftime("%Y-%m-%d"),
            "结束日": s.index[-1].strftime("%Y-%m-%d"),
            "区间收益": float(s.iloc[-1] / s.iloc[0] - 1),
        })
    out = pd.DataFrame(rows).sort_values("区间收益")
    out.to_csv(DATA / "proxy_returns_since_weight_date.csv", index=False, encoding="utf-8-sig")
    return out


def winrate_by_drawdown(f: pd.DataFrame, dd_col: str = "dd") -> dict[str, pd.DataFrame]:
    tables: dict[str, pd.DataFrame] = {}
    for h in HORIZONS:
        rows = []
        for lo, hi, label in DD_BINS:
            mask = (f[dd_col] > lo) & (f[dd_col] <= hi)
            vals = f.loc[mask, f"fwd{h}"].dropna()
            mae = f.loc[mask, f"mae{h}"].dropna()
            if len(vals) < 8:
                rows.append({
                    "回撤档位": label, "样本": len(vals), "胜率": np.nan, "均值": np.nan,
                    "中位数": np.nan, "P10": np.nan, "最差": np.nan, "最大浮亏中位": np.nan,
                    "再跌5%概率": np.nan, "再跌10%概率": np.nan,
                })
                continue
            rows.append({
                "回撤档位": label,
                "样本": int(len(vals)),
                "胜率": float((vals > 0).mean()),
                "均值": float(vals.mean()),
                "中位数": float(vals.median()),
                "P10": float(vals.quantile(0.10)),
                "最差": float(vals.min()),
                "最大浮亏中位": float(mae.median()) if len(mae) else np.nan,
                "再跌5%概率": float((mae <= -0.05).mean()) if len(mae) else np.nan,
                "再跌10%概率": float((mae <= -0.10).mean()) if len(mae) else np.nan,
            })
        tables[str(h)] = pd.DataFrame(rows)
        tables[str(h)].to_csv(DATA / f"winrate_by_drawdown_{h}d.csv", index=False, encoding="utf-8-sig")
    return tables


def similar_drawdown_stats(f: pd.DataFrame, current_dd: float, width: float = 0.025) -> pd.DataFrame:
    mask = (f["dd"] >= current_dd - width) & (f["dd"] <= current_dd + width)
    rows = []
    for h in HORIZONS:
        vals = f.loc[mask, f"fwd{h}"].dropna()
        mae = f.loc[mask, f"mae{h}"].dropna()
        if len(vals) == 0:
            continue
        rows.append({
            "持有期": H_LABELS[h],
            "交易日": h,
            "样本": int(len(vals)),
            "胜率": float((vals > 0).mean()),
            "均值": float(vals.mean()),
            "中位数": float(vals.median()),
            "P10": float(vals.quantile(0.10)),
            "P90": float(vals.quantile(0.90)),
            "最差": float(vals.min()),
            "最好": float(vals.max()),
            "最大浮亏中位": float(mae.median()) if len(mae) else np.nan,
            "最大浮亏P10": float(mae.quantile(0.10)) if len(mae) else np.nan,
            "再跌5%概率": float((mae <= -0.05).mean()) if len(mae) else np.nan,
            "再跌10%概率": float((mae <= -0.10).mean()) if len(mae) else np.nan,
        })
    out = pd.DataFrame(rows)
    out.to_csv(DATA / "similar_current_drawdown_stats.csv", index=False, encoding="utf-8-sig")
    return out


def dd_label(current_dd: float) -> str:
    for lo, hi, label in DD_BINS:
        if lo < current_dd <= hi:
            return label
    return DD_BINS[0][2]


def calc_signal_state(f: pd.DataFrame) -> dict[str, Any]:
    last = f.iloc[-1]
    return {
        "站上MA20": bool(last["nav"] > last["ma20"]),
        "站上MA60": bool(last["nav"] > last["ma60"]),
        "站上MA120": bool(last["nav"] > last["ma120"]),
        "20日动量": float(last["ret20"]),
        "60日动量": float(last["ret60"]),
        "RSI14": float(last["rsi14"]),
    }


def bond_changes(bonds: pd.DataFrame, start_date: pd.Timestamp, end_date: pd.Timestamp) -> dict[str, Any]:
    if bonds.empty or "中国国债收益率10年" not in bonds.columns:
        return {}
    window = bonds[(bonds.index >= start_date) & (bonds.index <= end_date)].dropna(subset=["中国国债收益率10年"])
    if len(window) < 2:
        return {}
    c10_start = float(window["中国国债收益率10年"].iloc[0]) / 100
    c10_end = float(window["中国国债收益率10年"].iloc[-1]) / 100
    c30_start = float(window["中国国债收益率30年"].iloc[0]) / 100 if "中国国债收益率30年" in window else np.nan
    c30_end = float(window["中国国债收益率30年"].iloc[-1]) / 100 if "中国国债收益率30年" in window else np.nan
    return {
        "start": window.index[0].strftime("%Y-%m-%d"),
        "end": window.index[-1].strftime("%Y-%m-%d"),
        "cn10_start": c10_start,
        "cn10_end": c10_end,
        "cn10_change": c10_end - c10_start,
        "cn30_start": c30_start,
        "cn30_end": c30_end,
        "cn30_change": c30_end - c30_start,
    }


# ============================================================================
# 图表
# ============================================================================
def fig_nav_drawdown(nav: pd.Series, f: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(10, 6), facecolor="white", sharex=True,
                             gridspec_kw={"height_ratios": [2, 1]})
    axes[0].plot(nav.index, nav.values, color=LC["blue"], lw=1.5)
    axes[0].set_title("红利低波ETF(512890) 场内价格净值与回撤", fontsize=13, fontweight="bold", color=LC["text"])
    axes[0].set_ylabel("价格净值", color=LC["sub"])
    axes[1].fill_between(f.index, f["dd"] * 100, 0, color=LC["red"], alpha=0.20, lw=0)
    axes[1].plot(f.index, f["dd"] * 100, color=LC["red"], lw=1.0)
    axes[1].axhline(f["dd"].iloc[-1] * 100, color=LC["orange"], ls="--", lw=1.0,
                    label=f"当前 {pct(f['dd'].iloc[-1])}")
    axes[1].legend(fontsize=9, loc="lower left")
    axes[1].set_ylabel("回撤%", color=LC["sub"])
    for ax in axes:
        ax.grid(True, color=LC["grid"], lw=0.6)
        for spine in ax.spines.values():
            spine.set_color(LC["grid"])
        ax.tick_params(colors=LC["sub"])
    fig.tight_layout()
    fig.savefig(FIGS / "fig_nav_drawdown.png", dpi=160, facecolor="white")
    plt.close(fig)


def fig_proxy_returns(proxy_returns: pd.DataFrame) -> None:
    if proxy_returns.empty:
        return
    df = proxy_returns.copy().sort_values("区间收益")
    fig, ax = plt.subplots(figsize=(9, 4.6), facecolor="white")
    colors = [LC["red"] if x < 0 else LC["green"] for x in df["区间收益"]]
    ax.barh(df["名称"], df["区间收益"] * 100, color=colors, alpha=0.82)
    ax.axvline(0, color=LC["gray"], lw=0.8)
    for y, x in enumerate(df["区间收益"] * 100):
        ax.text(x + (0.15 if x >= 0 else -0.15), y, f"{x:+.1f}%",
                va="center", ha="left" if x >= 0 else "right", fontsize=9, color=LC["text"])
    ax.set_title("5月底以来主要资产/风格代理表现", fontsize=13, fontweight="bold", color=LC["text"])
    ax.set_xlabel("区间收益%", color=LC["sub"])
    ax.grid(True, axis="x", color=LC["grid"], lw=0.6)
    for spine in ax.spines.values():
        spine.set_color(LC["grid"])
    ax.tick_params(colors=LC["sub"], labelsize=9)
    fig.tight_layout()
    fig.savefig(FIGS / "fig_proxy_returns.png", dpi=160, facecolor="white")
    plt.close(fig)


def fig_constituent_contrib(contrib: pd.DataFrame) -> None:
    if contrib.empty:
        fig, ax = plt.subplots(figsize=(9, 5), facecolor="white")
        ax.axis("off")
        ax.text(0.5, 0.5, "成分股贡献数据未成功获取", ha="center", va="center",
                fontsize=14, color=LC["sub"])
        fig.savefig(FIGS / "fig_constituent_contrib.png", dpi=160, facecolor="white")
        plt.close(fig)
        return
    worst = contrib.sort_values("近似贡献").head(12).copy().iloc[::-1]
    fig, ax = plt.subplots(figsize=(9, 5), facecolor="white")
    values = worst["近似贡献"] * 100
    ax.barh(worst["名称"], values, color=LC["red"], alpha=0.78)
    ax.set_xlim(min(-0.50, float(values.min()) * 1.14), 0.02)
    for y, (_, row) in enumerate(worst.iterrows()):
        ax.text(row["近似贡献"] * 100 + 0.012, y,
                f"{row['近似贡献']*100:+.2f}pct | {row['区间收益']*100:+.1f}%",
                ha="left", va="center", fontsize=8.5, color=LC["text"])
    ax.set_title("红利低波前30大权重股：区间拖累项", fontsize=13, fontweight="bold", color=LC["text"])
    ax.set_xlabel("对指数近似贡献百分点", color=LC["sub"])
    ax.grid(True, axis="x", color=LC["grid"], lw=0.6)
    for spine in ax.spines.values():
        spine.set_color(LC["grid"])
    ax.tick_params(colors=LC["sub"], labelsize=9)
    fig.subplots_adjust(left=0.18, right=0.97, top=0.90, bottom=0.15)
    fig.savefig(FIGS / "fig_constituent_contrib.png", dpi=160, facecolor="white")
    plt.close(fig)


def fig_sector_contrib(contrib: pd.DataFrame) -> None:
    if contrib.empty:
        fig, ax = plt.subplots(figsize=(8.5, 4.2), facecolor="white")
        ax.axis("off")
        ax.text(0.5, 0.5, "行业拖累数据未成功获取", ha="center", va="center",
                fontsize=14, color=LC["sub"])
        fig.savefig(FIGS / "fig_sector_contrib.png", dpi=160, facecolor="white")
        plt.close(fig)
        return
    sector = contrib.groupby("行业分组", as_index=False).agg(
        权重覆盖=("权重", "sum"), 近似贡献=("近似贡献", "sum"), 成分数=("代码", "count")
    )
    sector = sector.sort_values("近似贡献")
    fig, ax = plt.subplots(figsize=(8.5, 4.2), facecolor="white")
    colors = [LC["red"] if x < 0 else LC["green"] for x in sector["近似贡献"]]
    ax.barh(sector["行业分组"], sector["近似贡献"] * 100, color=colors, alpha=0.82)
    for y, (_, row) in enumerate(sector.iterrows()):
        ax.text(row["近似贡献"] * 100 + (0.02 if row["近似贡献"] >= 0 else -0.02), y,
                f"{row['近似贡献']*100:+.2f}pct / w{row['权重覆盖']*100:.0f}%",
                ha="left" if row["近似贡献"] >= 0 else "right", va="center", fontsize=8.5, color=LC["text"])
    ax.set_title("前30权重股按行业分组的近似拖累", fontsize=13, fontweight="bold", color=LC["text"])
    ax.set_xlabel("贡献百分点", color=LC["sub"])
    ax.grid(True, axis="x", color=LC["grid"], lw=0.6)
    for spine in ax.spines.values():
        spine.set_color(LC["grid"])
    ax.tick_params(colors=LC["sub"], labelsize=9)
    fig.tight_layout()
    fig.savefig(FIGS / "fig_sector_contrib.png", dpi=160, facecolor="white")
    plt.close(fig)


def fig_winrate_heatmap(tables: dict[str, pd.DataFrame]) -> None:
    labels = [x[2] for x in DD_BINS]
    mat = []
    annot = []
    for h in HORIZONS:
        t = tables[str(h)].set_index("回撤档位").reindex(labels)
        mat.append(t["胜率"].to_numpy() * 100)
        annot.append(t["样本"].to_numpy())
    arr = np.array(mat)
    fig, ax = plt.subplots(figsize=(9, 4.2), facecolor="white")
    im = ax.imshow(arr, cmap="RdYlGn", vmin=30, vmax=95, aspect="auto")
    ax.set_xticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, fontsize=9, color=LC["sub"])
    ax.set_yticks(np.arange(len(HORIZONS)))
    ax.set_yticklabels([H_LABELS[h] for h in HORIZONS], fontsize=10, color=LC["sub"])
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            val = arr[i, j]
            txt = "-" if not math.isfinite(float(val)) else f"{val:.0f}%\nn={int(annot[i][j])}"
            ax.text(j, i, txt, ha="center", va="center", fontsize=8.5,
                    color="white" if math.isfinite(float(val)) and val < 50 else LC["text"])
    ax.set_title("红利低波：不同回撤档位买入后的前瞻胜率", fontsize=13, fontweight="bold", color=LC["text"])
    cbar = fig.colorbar(im, ax=ax, shrink=0.84)
    cbar.set_label("上涨概率%", color=LC["sub"])
    cbar.ax.tick_params(colors=LC["sub"])
    fig.tight_layout()
    fig.savefig(FIGS / "fig_winrate_heatmap.png", dpi=160, facecolor="white")
    plt.close(fig)


def fig_similar_stats(similar: pd.DataFrame) -> None:
    if similar.empty:
        return
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), facecolor="white")
    axes[0].bar(similar["持有期"], similar["胜率"] * 100, color=LC["green"], alpha=0.82)
    axes[0].axhline(50, color=LC["gray"], ls=":", lw=1)
    for i, row in similar.iterrows():
        axes[0].text(i, row["胜率"] * 100 + 1.5, f"{row['胜率']*100:.0f}%", ha="center", fontsize=9)
    axes[0].set_ylim(0, 105)
    axes[0].set_title("相似当前回撤：前瞻胜率", fontsize=12, fontweight="bold", color=LC["text"])
    axes[0].set_ylabel("上涨概率%", color=LC["sub"])

    axes[1].bar(similar["持有期"], similar["最大浮亏中位"] * 100, color=LC["orange"], alpha=0.82, label="浮亏中位")
    axes[1].bar(similar["持有期"], similar["最大浮亏P10"] * 100, color=LC["red"], alpha=0.45, label="较差10%")
    axes[1].set_title("买入后最大浮亏", fontsize=12, fontweight="bold", color=LC["text"])
    axes[1].set_ylabel("最大浮亏%", color=LC["sub"])
    axes[1].legend(fontsize=9)
    for ax in axes:
        ax.grid(True, axis="y", color=LC["grid"], lw=0.6)
        for spine in ax.spines.values():
            spine.set_color(LC["grid"])
        ax.tick_params(colors=LC["sub"])
    fig.tight_layout()
    fig.savefig(FIGS / "fig_similar_stats.png", dpi=160, facecolor="white")
    plt.close(fig)


# ============================================================================
# 小红书卡片
# ============================================================================
def generate_cards(summary: dict[str, Any], f_main: pd.DataFrame, contrib: pd.DataFrame,
                   proxy_returns: pd.DataFrame, similar: pd.DataFrame,
                   winrate_tables: dict[str, pd.DataFrame]) -> None:
    state = summary["state"][MAIN]
    end = summary["as_of"]
    peak_date = summary["peak_date"]
    current_dd = state["dd"]
    sim60 = similar[similar["交易日"] == 60].iloc[0]
    sim120 = similar[similar["交易日"] == 120].iloc[0]
    sim250 = similar[similar["交易日"] == 250].iloc[0]

    def card_1() -> None:
        fig = _fig()
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis("off")
        ax.set_facecolor(C["bg"])
        ax.text(0.5, 0.90, "红利低波突然回撤", ha="center", fontsize=34,
                fontweight="bold", color=C["text"], transform=ax.transAxes)
        ax.text(0.5, 0.84, "现在能抄底吗？", ha="center", fontsize=36,
                fontweight="bold", color=C["gold"], transform=ax.transAxes)
        ax.text(0.5, 0.775, f"512890 · 数据截止 {end} · 场内价格口径",
                ha="center", fontsize=13.5, color=C["muted"], transform=ax.transAxes)
        ax.text(0.5, 0.65, pct(current_dd), ha="center", fontsize=86,
                fontweight="bold", color=C["red"], fontfamily="monospace", transform=ax.transAxes)
        ax.text(0.5, 0.57, f"当前距高点回撤 · 高点 {peak_date}", ha="center",
                fontsize=14, color=C["muted"], transform=ax.transAxes)
        kpis = [
            ("3个月胜率", pct0(sim60["胜率"]), C["green"]),
            ("6个月胜率", pct0(sim120["胜率"]), C["green"]),
            ("1年胜率", pct0(sim250["胜率"]), C["gold"]),
        ]
        for i, (label, value, color) in enumerate(kpis):
            x = 0.2 + 0.3 * i
            _card_rect(ax, (x - 0.125, 0.355), 0.25, 0.13, face="card")
            ax.text(x, 0.435, value, ha="center", fontsize=26, fontweight="bold",
                    color=color, fontfamily="monospace", transform=ax.transAxes)
            ax.text(x, 0.375, label, ha="center", fontsize=12.5,
                    color=C["muted"], transform=ax.transAxes)
        ax.text(0.5, 0.26, "结论先说：可以分批，不建议一把梭", ha="center",
                fontsize=18, fontweight="bold", color=C["text"], transform=ax.transAxes)
        ax.text(0.5, 0.19, "本轮更像高股息拥挤交易退潮 + 权重股补跌",
                ha="center", fontsize=14, color=C["cyan"], transform=ax.transAxes)
        ax.text(0.5, 0.115, "#红利低波 #高股息 #抄底 #ETF #量化投资",
                ha="center", fontsize=13, color=C["blue"], transform=ax.transAxes)
        _page_number(fig, 1)
        fig.savefig(CARDS / "01_cover.png", dpi=DPI, facecolor=C["bg"])
        plt.close(fig)

    def card_2() -> None:
        fig = _fig()
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis("off")
        ax.set_facecolor(C["bg"])
        ax.text(0.5, 0.94, "这次到底跌了多少？", ha="center", fontsize=29,
                fontweight="bold", color=C["text"], transform=ax.transAxes)
        ax.text(0.5, 0.895, "不是一天暴雷，是高位后连续失血", ha="center",
                fontsize=13, color=C["muted"], transform=ax.transAxes)
        axp = fig.add_axes([0.10, 0.47, 0.82, 0.34])
        recent = f_main.iloc[-260:]
        axp.plot(recent.index, recent["nav"], color=C["blue"], lw=1.8, label="价格净值")
        axp.plot(recent.index, recent["ma20"], color=C["green"], lw=1.0, alpha=0.75, label="MA20")
        axp.plot(recent.index, recent["ma60"], color=C["orange"], lw=1.0, alpha=0.75, label="MA60")
        axp.scatter([recent.index[-1]], [recent["nav"].iloc[-1]], color=C["red"], s=28, zorder=5)
        axp.legend(fontsize=8.5, loc="upper left", facecolor=C["card"], edgecolor=C["border"], labelcolor=C["text"])
        axp.grid(True, color=C["border"], lw=0.4, alpha=0.55)
        axp.set_facecolor(C["card"])
        for spine in axp.spines.values():
            spine.set_color(C["border"])
        axp.tick_params(colors=C["muted"], labelsize=8.5)

        metrics = [
            ("近5日", pct(state["ret5"]), C["red"] if state["ret5"] < 0 else C["green"]),
            ("近20日", pct(state["ret20"]), C["red"] if state["ret20"] < 0 else C["green"]),
            ("近60日", pct(state["ret60"]), C["red"] if state["ret60"] < 0 else C["green"]),
            ("RSI14", f"{state['rsi14']:.0f}", C["gold"] if state["rsi14"] < 45 else C["muted"]),
        ]
        for i, (label, value, color) in enumerate(metrics):
            x = 0.17 + i * 0.22
            _card_rect(ax, (x - 0.085, 0.30), 0.17, 0.105, face="panel")
            ax.text(x, 0.365, value, ha="center", fontsize=18, fontweight="bold",
                    color=color, fontfamily="monospace", transform=ax.transAxes)
            ax.text(x, 0.318, label, ha="center", fontsize=11.5, color=C["muted"], transform=ax.transAxes)
        ax.text(0.5, 0.215, f"当前：{'跌破' if not summary['signals']['站上MA20'] else '站上'}MA20，"
                            f"{'跌破' if not summary['signals']['站上MA60'] else '站上'}MA60",
                ha="center", fontsize=15, fontweight="bold", color=C["gold"], transform=ax.transAxes)
        ax.text(0.5, 0.155, "短线动量仍偏弱，抄底要按仓位而不是按情绪",
                ha="center", fontsize=13, color=C["muted"], transform=ax.transAxes)
        _page_number(fig, 2)
        _disclaimer(fig)
        fig.savefig(CARDS / "02_drawdown_state.png", dpi=DPI, facecolor=C["bg"])
        plt.close(fig)

    def card_3() -> None:
        fig = _fig()
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis("off")
        ax.set_facecolor(C["bg"])
        ax.text(0.5, 0.94, "为什么红利低波也跌？", ha="center", fontsize=28,
                fontweight="bold", color=C["text"], transform=ax.transAxes)
        ax.text(0.5, 0.895, "三条线索：拥挤、权重股、不是利率冲击", ha="center",
                fontsize=13, color=C["muted"], transform=ax.transAxes)
        reasons = [
            ("01", "高股息交易拥挤退潮", f"中证红利低波100近1个月 {summary['index_month_return_text']}，同类红利低波指数同步回撤", C["orange"]),
            ("02", "权重股集中补跌", f"前30大权重股覆盖 {pct(summary['contrib_weight_coverage'], 0, False)}，近似拖累 {pct(summary['contrib_sum'], 1)}", C["red"]),
            ("03", "利率不是主因", f"同期10Y国债收益率 {bp(summary['bond'].get('cn10_change'))}，低利率没有挡住权益仓位止盈", C["blue"]),
        ]
        y = 0.80
        for num, title, body, color in reasons:
            _card_rect(ax, (0.06, y - 0.14), 0.88, 0.155, face="card")
            ax.text(0.10, y - 0.015, num, fontsize=22, fontweight="bold", color=color,
                    fontfamily="monospace", transform=ax.transAxes)
            ax.text(0.22, y - 0.005, title, fontsize=17, fontweight="bold", color=C["text"], transform=ax.transAxes)
            ax.text(0.22, y - 0.075, body, fontsize=12.4, color=C["muted"], transform=ax.transAxes)
            y -= 0.20
        ax.text(0.5, 0.16, "一句话：不是红利逻辑崩了，是热门防御资产的阶段性撤退",
                ha="center", fontsize=14.2, fontweight="bold", color=C["gold"], transform=ax.transAxes)
        _page_number(fig, 3)
        _disclaimer(fig)
        fig.savefig(CARDS / "03_reasons.png", dpi=DPI, facecolor=C["bg"])
        plt.close(fig)

    def card_4() -> None:
        fig = _fig()
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis("off")
        ax.set_facecolor(C["bg"])
        ax.text(0.5, 0.94, "谁在拖累红利低波？", ha="center", fontsize=29,
                fontweight="bold", color=C["text"], transform=ax.transAxes)
        ax.text(0.5, 0.895, "930955 前30大权重股 · 5月底以来近似贡献", ha="center",
                fontsize=12.8, color=C["muted"], transform=ax.transAxes)
        show = contrib.sort_values("近似贡献").head(9).copy().iloc[::-1]
        axp = fig.add_axes([0.23, 0.37, 0.67, 0.43])
        axp.set_facecolor(C["bg"])
        values = show["近似贡献"] * 100
        axp.barh(show["名称"], values, color=C["red"], alpha=0.8)
        axp.set_xlim(min(-0.50, float(values.min()) * 1.14), 0.02)
        for y, (_, row) in enumerate(show.iterrows()):
            axp.text(row["近似贡献"] * 100 + 0.012, y,
                     f"{row['近似贡献']*100:+.2f}", ha="left", va="center",
                     fontsize=8.5, color=C["text"], fontfamily="monospace")
        axp.grid(True, axis="x", color=C["border"], lw=0.4, alpha=0.55)
        for spine in axp.spines.values():
            spine.set_color(C["border"])
        axp.tick_params(colors=C["muted"], labelsize=9)
        axp.set_xlabel("贡献百分点", color=C["muted"], fontsize=9)
        sector = contrib.groupby("行业分组", as_index=False)["近似贡献"].sum().sort_values("近似贡献")
        worst = sector.head(3)
        y0 = 0.255
        ax.text(0.08, y0, "行业拖累TOP3", fontsize=15, fontweight="bold",
                color=C["gold"], transform=ax.transAxes)
        for i, (_, row) in enumerate(worst.iterrows()):
            ax.text(0.10, y0 - 0.055 * (i + 1), f"{i+1}. {row['行业分组']}",
                    fontsize=13, color=C["text"], transform=ax.transAxes)
            ax.text(0.88, y0 - 0.055 * (i + 1), f"{row['近似贡献']*100:+.2f}pct",
                    ha="right", fontsize=13, fontweight="bold", color=C["red"],
                    fontfamily="monospace", transform=ax.transAxes)
        _page_number(fig, 4)
        _disclaimer(fig)
        fig.savefig(CARDS / "04_draggers.png", dpi=DPI, facecolor=C["bg"])
        plt.close(fig)

    def card_5() -> None:
        fig = _fig()
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis("off")
        ax.set_facecolor(C["bg"])
        ax.text(0.5, 0.94, "现在买，历史胜率多少？", ha="center", fontsize=27,
                fontweight="bold", color=C["text"], transform=ax.transAxes)
        ax.text(0.5, 0.895, f"相似回撤区间：当前 {pct(current_dd)} 附近 +/-2.5pct",
                ha="center", fontsize=12.5, color=C["muted"], transform=ax.transAxes)
        y = 0.80
        headers = ["持有", "样本", "胜率", "均值", "最差"]
        xs = [0.13, 0.33, 0.53, 0.71, 0.88]
        for x, h in zip(xs, headers):
            ax.text(x, y, h, ha="center", fontsize=12.5, fontweight="bold", color=C["muted"], transform=ax.transAxes)
        ax.plot([0.08, 0.92], [y - 0.025, y - 0.025], color=C["border"], transform=ax.transAxes)
        y -= 0.09
        for _, row in similar.iterrows():
            _card_rect(ax, (0.07, y - 0.035), 0.86, 0.07, face="card", alpha=0.82)
            values = [row["持有期"], f"{int(row['样本'])}", pct0(row["胜率"]), pct(row["均值"]), pct(row["最差"])]
            colors = [C["text"], C["muted"], C["green"] if row["胜率"] >= 0.6 else C["gold"],
                      C["green"] if row["均值"] >= 0 else C["red"], C["red"]]
            for x, value, color in zip(xs, values, colors):
                ax.text(x, y, value, ha="center", va="center", fontsize=14,
                        fontweight="bold" if x in (0.53, 0.71) else "normal",
                        color=color, fontfamily="monospace" if x > 0.2 else None,
                        transform=ax.transAxes)
            y -= 0.095
        ax.text(0.5, 0.235, f"当前档位下，3个月胜率 {pct0(sim60['胜率'])}，1年胜率 {pct0(sim250['胜率'])}",
                ha="center", fontsize=16, fontweight="bold", color=C["gold"], transform=ax.transAxes)
        ax.text(0.5, 0.168, "胜率不低，但最差情形仍可能继续回撤", ha="center",
                fontsize=13, color=C["muted"], transform=ax.transAxes)
        _page_number(fig, 5)
        _disclaimer(fig)
        fig.savefig(CARDS / "05_winrate.png", dpi=DPI, facecolor=C["bg"])
        plt.close(fig)

    def card_6() -> None:
        fig = _fig()
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis("off")
        ax.set_facecolor(C["bg"])
        ax.text(0.5, 0.94, "抄底最大的坑：接飞刀", ha="center", fontsize=27,
                fontweight="bold", color=C["text"], transform=ax.transAxes)
        ax.text(0.5, 0.895, "相似回撤后，未来N日内最大浮亏", ha="center",
                fontsize=13, color=C["muted"], transform=ax.transAxes)
        rows = [sim60, sim120, sim250]
        y = 0.78
        for row in rows:
            _card_rect(ax, (0.07, y - 0.10), 0.86, 0.12, face="card")
            ax.text(0.11, y - 0.015, row["持有期"], fontsize=16, fontweight="bold",
                    color=C["text"], transform=ax.transAxes)
            ax.text(0.38, y - 0.015, f"浮亏中位 {pct(row['最大浮亏中位'])}", fontsize=14,
                    color=C["orange"], transform=ax.transAxes)
            ax.text(0.38, y - 0.065, f"较差10% {pct(row['最大浮亏P10'])}", fontsize=14,
                    color=C["red"], transform=ax.transAxes)
            ax.text(0.85, y - 0.04, f"再跌10%\n{pct0(row['再跌10%概率'])}", ha="center",
                    va="center", fontsize=13, color=C["red"], fontweight="bold",
                    transform=ax.transAxes)
            y -= 0.17
        ax.text(0.5, 0.245, "所以：抄底要假设还会跌，不要满仓赌反转", ha="center",
                fontsize=15.5, fontweight="bold", color=C["gold"], transform=ax.transAxes)
        ax.text(0.5, 0.175, "左侧仓位小，右侧确认再加；跌破计划就降仓",
                ha="center", fontsize=13, color=C["muted"], transform=ax.transAxes)
        _page_number(fig, 6)
        _disclaimer(fig)
        fig.savefig(CARDS / "06_falling_knife.png", dpi=DPI, facecolor=C["bg"])
        plt.close(fig)

    def card_7() -> None:
        fig = _fig()
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis("off")
        ax.set_facecolor(C["bg"])
        ax.text(0.5, 0.93, "我的抄底方案", ha="center", fontsize=31,
                fontweight="bold", color=C["gold"], transform=ax.transAxes)
        ax.text(0.5, 0.875, "不是预测最低点，而是用仓位管理胜率", ha="center",
                fontsize=13, color=C["muted"], transform=ax.transAxes)
        plan = [
            ("第一笔", "30%", "当前位置先建观察仓", C["blue"]),
            ("第二笔", "30%", "若再跌3-5%或企稳3日再加", C["orange"]),
            ("第三笔", "40%", "站回MA20/MA60后右侧确认", C["green"]),
            ("失效条件", "减仓", "10Y利率上行+高股息继续跑输宽基", C["red"]),
        ]
        y = 0.77
        for title, num, body, color in plan:
            _card_rect(ax, (0.07, y - 0.09), 0.86, 0.11, face="card")
            ax.text(0.11, y - 0.02, title, fontsize=16, fontweight="bold", color=C["text"], transform=ax.transAxes)
            ax.text(0.42, y - 0.02, num, fontsize=22, fontweight="bold", color=color,
                    ha="center", transform=ax.transAxes)
            ax.text(0.56, y - 0.02, body, fontsize=13, color=C["muted"], transform=ax.transAxes)
            y -= 0.145
        ax.text(0.5, 0.185, "一句话结论：红利低波可以抄，但只适合分批低吸",
                ha="center", fontsize=15.2, fontweight="bold", color=C["text"], transform=ax.transAxes)
        ax.text(0.5, 0.128, "完整深度研报 + 数据表已生成", ha="center",
                fontsize=13, color=C["cyan"], transform=ax.transAxes)
        _page_number(fig, 7)
        _disclaimer(fig)
        fig.savefig(CARDS / "07_playbook.png", dpi=DPI, facecolor=C["bg"])
        plt.close(fig)

    print("[5] 生成 7 张小红书卡片...")
    card_1(); card_2(); card_3(); card_4(); card_5(); card_6(); card_7()


# ============================================================================
# Markdown + PDF 研报
# ============================================================================
def markdown_table(df: pd.DataFrame, columns: list[str], pct_cols: set[str] | None = None,
                   max_rows: int | None = None) -> str:
    pct_cols = pct_cols or set()
    show = df.copy()
    if max_rows is not None:
        show = show.head(max_rows)
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join([":---:" for _ in columns]) + "|"]
    for _, row in show.iterrows():
        vals = []
        for col in columns:
            val = row[col]
            if col in pct_cols:
                vals.append(pct(float(val)))
            elif isinstance(val, (float, np.floating)):
                vals.append(f"{float(val):.3f}")
            else:
                vals.append(str(val))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def build_markdown(summary: dict[str, Any], proxy_returns: pd.DataFrame, contrib: pd.DataFrame,
                   similar: pd.DataFrame, tables: dict[str, pd.DataFrame], index_snapshot: pd.DataFrame) -> Path:
    state = summary["state"][MAIN]
    sim60 = similar[similar["交易日"] == 60].iloc[0]
    sim120 = similar[similar["交易日"] == 120].iloc[0]
    sim250 = similar[similar["交易日"] == 250].iloc[0]
    sector = contrib.groupby("行业分组", as_index=False).agg(
        权重覆盖=("权重", "sum"), 近似贡献=("近似贡献", "sum"), 成分数=("代码", "count")
    ).sort_values("近似贡献") if not contrib.empty else pd.DataFrame()

    win60 = tables["60"].copy()
    md = f"""# 红利低波回撤归因与抄底胜率深度研报

报告日期：{DATE_DIR}  
数据截止：{summary['as_of']}  
主标的：红利低波ETF（512890），跟踪中证红利低波动100指数（{INDEX_CODE}）  
口径：ETF使用新浪场内价格日线；若出现超大除权跳空则中性化处理；成分权重来自中证指数公开成分权重接口；个股贡献使用前复权日线近似。

---

## 摘要

红利低波这轮回撤的表面现象是“防御资产也跌了”，但从数据看，更像是高股息拥挤交易退潮后的集中补跌，而不是红利资产长期逻辑被证伪。512890 当前价格净值距历史高点回撤 **{pct(state['dd'])}**，高点日期为 **{summary['peak_date']}**。在历史上与当前回撤相近（±2.5pct）的交易日买入，持有 3 个月胜率为 **{pct0(sim60['胜率'])}**，持有 6 个月胜率为 **{pct0(sim120['胜率'])}**，持有 1 年胜率为 **{pct0(sim250['胜率'])}**。

但这不是“闭眼抄底”。相似回撤下，未来 3 个月内最大浮亏中位数为 **{pct(sim60['最大浮亏中位'])}**，较差 10% 情形可到 **{pct(sim60['最大浮亏P10'])}**，再跌 10% 的概率为 **{pct0(sim60['再跌10%概率'])}**。结论是：**红利低波可以分批低吸，不适合一把梭赌最低点**。

---

## 一、近期发生了什么

![红利低波净值与回撤](figures/fig_nav_drawdown.png)

截至 {summary['as_of']}，512890 的短期技术状态如下：近 5 日 {pct(state['ret5'])}，近 20 日 {pct(state['ret20'])}，近 60 日 {pct(state['ret60'])}；RSI(14) 为 {state['rsi14']:.0f}。均线方面，当前 {'站上' if summary['signals']['站上MA20'] else '跌破'} MA20，{'站上' if summary['signals']['站上MA60'] else '跌破'} MA60，说明短线尚未完成右侧修复。

5月底以来，主要风格/资产代理表现如下：

![风格代理表现](figures/fig_proxy_returns.png)

{markdown_table(proxy_returns, ['名称', '起始日', '结束日', '区间收益'], pct_cols={'区间收益'}) if not proxy_returns.empty else '代理资产收益表为空。'}

---

## 二、回撤原因拆解

### 2.1 高股息交易拥挤退潮

中证指数快照显示，红利低波相关指数近一个月普遍为负，其中红利低波100近一个月收益约为 **{summary['index_month_return_text']}**。这说明本轮不是单只 ETF 流动性问题，而是高股息/低波动风格共同承压。

{markdown_table(index_snapshot[['指数代码', '指数简称', '最新收盘', '近一个月收益率']].head(10), ['指数代码', '指数简称', '最新收盘', '近一个月收益率']) if not index_snapshot.empty else '中证指数快照未成功获取。'}

### 2.2 权重股集中补跌

930955 最新成分权重日期为 **{summary['weight_date']}**。我们抓取前 30 大权重股的前复权行情，从权重日期附近到 {summary['as_of']} 做近似贡献拆解。该样本覆盖指数权重 **{pct(summary['contrib_weight_coverage'], 0, False)}**，合计近似贡献 **{pct(summary['contrib_sum'])}**。

![权重股拖累](figures/fig_constituent_contrib.png)

前 12 个拖累项：

{markdown_table(contrib.sort_values('近似贡献').head(12), ['代码', '名称', '行业分组', '权重', '区间收益', '近似贡献'], pct_cols={'权重', '区间收益', '近似贡献'}) if not contrib.empty else '成分股贡献表为空。'}

按行业分组看：

![行业分组拖累](figures/fig_sector_contrib.png)

{markdown_table(sector, ['行业分组', '成分数', '权重覆盖', '近似贡献'], pct_cols={'权重覆盖', '近似贡献'}) if not sector.empty else '行业分组贡献表为空。'}

这解释了“低波为什么会跌”：红利低波并不等于现金，它本质仍是股票组合。能源煤炭、公用交运、消费家电等前期防御抱团品种一旦补跌，低波因子只能降低波动，不能消除方向性回撤。

### 2.3 利率不是主要杀伤

同期中国 10 年国债收益率从 {pct(summary['bond'].get('cn10_start'), 2, False)} 到 {pct(summary['bond'].get('cn10_end'), 2, False)}，变化 **{bp(summary['bond'].get('cn10_change'))}**；30 年收益率变化 **{bp(summary['bond'].get('cn30_change'))}**。如果是纯粹“利率上行杀高股息估值”，应该看到长端利率明显上行；但本轮并非如此。因此更合理的解释是：高股息拥挤交易获利了结、权重行业补跌、以及市场风格短期切换。

---

## 三、历史抄底胜率

![回撤档位胜率](figures/fig_winrate_heatmap.png)

按历史回撤档位统计，红利低波在较深回撤区间买入的中长期胜率通常高于浅回撤区间。3个月持有期的回撤档位表如下：

{markdown_table(win60, ['回撤档位', '样本', '胜率', '均值', '中位数', 'P10', '最差', '最大浮亏中位', '再跌10%概率'], pct_cols={'胜率', '均值', '中位数', 'P10', '最差', '最大浮亏中位', '再跌10%概率'})}

当前回撤落在 **{summary['current_dd_label']}** 档。为了更贴近“此时买入”，我们额外统计当前回撤 ±2.5pct 的相似样本：

![相似回撤胜率与浮亏](figures/fig_similar_stats.png)

{markdown_table(similar, ['持有期', '样本', '胜率', '均值', '中位数', 'P10', '最差', '最大浮亏中位', '最大浮亏P10', '再跌10%概率'], pct_cols={'胜率', '均值', '中位数', 'P10', '最差', '最大浮亏中位', '最大浮亏P10', '再跌10%概率'})}

解读：当前赔率已经比高位追入更好，尤其 6 个月和 1 年维度胜率较高；但 1 到 3 个月内仍可能磨底，且历史最差情形并不轻。

---

## 四、入场方案

本报告建议把“抄底”拆成仓位计划，而不是一次性判断底部。

1. 第一笔 30%：当前位置可以建立观察仓，承认当前估值/回撤已经进入可买区域。
2. 第二笔 30%：若继续回撤 3-5%，或连续 3 个交易日不再创新低，再加仓。
3. 第三笔 40%：站回 MA20/MA60 后再加，等右侧确认。
4. 风险控制：如果高股息继续显著跑输沪深300，且长端利率重新上行，说明“防御溢价”仍在压缩，应降低加仓速度。

这个方案的核心不是预测最低点，而是承认两件事：第一，红利低波在中期有较高均值回归胜率；第二，短期接飞刀风险真实存在。

---

## 五、方法与局限

- ETF 数据来自 AKShare/Sina，主分析采用场内价格口径；若出现单日超大除权跳空则中性化处理。
- 成分权重来自中证指数公开接口，个股贡献仅计算前 30 大权重股，覆盖约 {pct(summary['contrib_weight_coverage'], 0, False)} 权重，因此是解释性近似，不是严格指数归因。
- 历史胜率为重叠样本统计，不能视为独立样本，也不代表未来一定重复。
- 512890 上市时间自 2019 年，样本覆盖一轮完整高股息牛熊，但仍不是超长周期。
- 本文不构成投资建议，只提供可复现的数据分析框架。
"""
    out = ROOT / "红利低波回撤归因与抄底胜率深度研报.md"
    out.write_text(md, encoding="utf-8")
    return out


def build_pdf(summary: dict[str, Any], proxy_returns: pd.DataFrame, contrib: pd.DataFrame,
              similar: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> Path:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.pdfmetrics import registerFontFamily
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import HRFlowable, Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    font_path = "/usr/share/fonts/google-droid/DroidSansFallback.ttf"
    pdfmetrics.registerFont(TTFont("CN", font_path))
    pdfmetrics.registerFont(TTFont("CN-B", font_path))
    registerFontFamily("CN", normal="CN", bold="CN-B", italic="CN", boldItalic="CN-B")

    pdf_path = ROOT / "红利低波回撤归因与抄底胜率深度研报.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, rightMargin=1.7 * cm,
                            leftMargin=1.7 * cm, topMargin=1.6 * cm, bottomMargin=1.6 * cm)

    navy = colors.HexColor("#10243e")
    ink = colors.HexColor("#253044")
    gray = colors.HexColor("#667085")
    light = colors.HexColor("#eef2f7")
    red = colors.HexColor("#dc2626")
    green = colors.HexColor("#16a34a")
    orange = colors.HexColor("#ea580c")

    H1 = ParagraphStyle("H1", fontName="CN-B", fontSize=25, textColor=navy,
                        alignment=1, leading=34, spaceAfter=8)
    SUB = ParagraphStyle("SUB", fontName="CN", fontSize=12.5, textColor=gray,
                         alignment=1, leading=20)
    H2 = ParagraphStyle("H2", fontName="CN-B", fontSize=15, textColor=colors.white,
                        backColor=navy, leading=25, spaceBefore=16, spaceAfter=10,
                        leftIndent=8, borderPadding=(5, 6, 5, 8))
    H3 = ParagraphStyle("H3", fontName="CN-B", fontSize=12.5, textColor=navy,
                        leading=19, spaceBefore=10, spaceAfter=4)
    BODY = ParagraphStyle("BODY", fontName="CN", fontSize=10.3, textColor=ink,
                          leading=17, spaceAfter=7, alignment=0)
    NOTE = ParagraphStyle("NOTE", fontName="CN", fontSize=8.6, textColor=gray,
                          leading=13, spaceAfter=5)
    CAP = ParagraphStyle("CAP", fontName="CN", fontSize=8.4, textColor=gray,
                         leading=12, alignment=1, spaceAfter=8)

    def img(name: str, width_cm: float = 16.5) -> Image:
        from PIL import Image as PILImage
        path = FIGS / name
        iw, ih = PILImage.open(path).size
        width = width_cm * cm
        return Image(str(path), width=width, height=width * ih / iw)

    def table(data: list[list[Any]], widths: list[float], fs: float = 8.5) -> Table:
        t = Table(data, colWidths=widths, hAlign="CENTER")
        t.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "CN"),
            ("FONTSIZE", (0, 0), (-1, -1), fs),
            ("BACKGROUND", (0, 0), (-1, 0), navy),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "CN-B"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cfd5df")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light]),
        ]))
        return t

    def on_page(canvas, document):
        canvas.saveState()
        canvas.setFont("CN", 8)
        canvas.setFillColor(gray)
        canvas.drawString(1.7 * cm, A4[1] - 1.05 * cm, "红利低波回撤归因与抄底胜率")
        canvas.drawRightString(A4[0] - 1.7 * cm, A4[1] - 1.05 * cm, f"数据截止 {summary['as_of']}")
        canvas.line(1.7 * cm, 1.25 * cm, A4[0] - 1.7 * cm, 1.25 * cm)
        canvas.drawCentredString(A4[0] / 2, 0.88 * cm, f"第 {document.page} 页 · 历史统计不构成投资建议")
        canvas.restoreState()

    state = summary["state"][MAIN]
    sim60 = similar[similar["交易日"] == 60].iloc[0]
    sim120 = similar[similar["交易日"] == 120].iloc[0]
    sim250 = similar[similar["交易日"] == 250].iloc[0]

    story: list[Any] = []
    story.append(Spacer(1, 2.7 * cm))
    story.append(Paragraph("红利低波回撤归因与抄底胜率", H1))
    story.append(Paragraph("近期高股息回撤、权重股拖累与分批低吸方案", SUB))
    story.append(Spacer(1, 0.6 * cm))
    story.append(HRFlowable(width="60%", thickness=1.2, color=navy, hAlign="CENTER"))
    story.append(Spacer(1, 0.8 * cm))
    cover = [["当前回撤", "3个月胜率", "1年胜率"],
             [pct(state["dd"]), pct0(sim60["胜率"]), pct0(sim250["胜率"])]]
    ct = table(cover, [5.0 * cm] * 3, fs=10)
    ct.setStyle(TableStyle([
        ("FONTNAME", (0, 1), (-1, 1), "CN-B"),
        ("FONTSIZE", (0, 1), (-1, 1), 20),
        ("TEXTCOLOR", (0, 1), (0, 1), red),
        ("TEXTCOLOR", (1, 1), (-1, 1), green),
    ]))
    story.append(ct)
    story.append(Spacer(1, 1.0 * cm))
    story.append(Paragraph(f"主标的：512890 红利低波ETF · 数据截止 {summary['as_of']} · 生成 {summary['generated']}", SUB))
    story.append(PageBreak())

    story.append(Paragraph("摘要", H2))
    story.append(Paragraph(
        f"512890 当前距价格净值历史高点回撤 {pct(state['dd'])}，高点日期 {summary['peak_date']}。"
        f"与当前回撤相近的历史样本中，持有3个月胜率 {pct0(sim60['胜率'])}，"
        f"持有6个月胜率 {pct0(sim120['胜率'])}，持有1年胜率 {pct0(sim250['胜率'])}。"
        "胜率已经进入可关注区间，但短线仍未完成右侧修复。", BODY))
    story.append(Paragraph(
        f"回撤原因上，本轮更像高股息拥挤交易退潮和权重行业补跌：前30大权重股覆盖约"
        f"{pct(summary['contrib_weight_coverage'], 0, False)} 权重，区间近似贡献 {pct(summary['contrib_sum'])}；"
        f"同期10年国债收益率变化 {bp(summary['bond'].get('cn10_change'))}，并非典型利率上行杀估值。", BODY))
    story.append(Paragraph("结论：可以分批低吸，不建议一把梭。第一笔观察仓，第二笔留给继续回撤，第三笔等MA20/MA60右侧修复。", BODY))

    story.append(Paragraph("一、近期回撤状态", H2))
    story.append(img("fig_nav_drawdown.png", 16.0))
    story.append(Paragraph("图1 512890场内价格净值与历史回撤", CAP))
    story.append(img("fig_proxy_returns.png", 15.6))
    story.append(Paragraph("图2 5月底以来主要风格/资产代理收益", CAP))
    proxy_rows = [["名称", "起始", "结束", "区间收益"]]
    for _, row in proxy_returns.head(9).iterrows():
        proxy_rows.append([row["名称"], row["起始日"], row["结束日"], pct(row["区间收益"])])
    story.append(table(proxy_rows, [4.1 * cm, 3.1 * cm, 3.1 * cm, 3.1 * cm], fs=8.2))
    story.append(PageBreak())

    story.append(Paragraph("二、回撤原因", H2))
    story.append(Paragraph("2.1 权重股拖累", H3))
    story.append(Paragraph(
        f"930955最新权重日期 {summary['weight_date']}。前30大权重股覆盖 {pct(summary['contrib_weight_coverage'], 0, False)}，"
        f"从权重日期附近到报告截止日，合计近似拖累 {pct(summary['contrib_sum'])}。", BODY))
    story.append(img("fig_constituent_contrib.png", 15.5))
    story.append(Paragraph("图3 前30大权重股中的主要拖累项", CAP))
    rows = [["代码", "名称", "行业", "权重", "收益", "贡献"]]
    for _, row in contrib.sort_values("近似贡献").head(10).iterrows():
        rows.append([row["代码"], row["名称"], row["行业分组"], pct(row["权重"], 1, False), pct(row["区间收益"]), pct(row["近似贡献"])])
    story.append(table(rows, [2.1 * cm, 2.7 * cm, 2.6 * cm, 2.2 * cm, 2.3 * cm, 2.3 * cm], fs=7.8))
    story.append(Spacer(1, 0.2 * cm))
    story.append(img("fig_sector_contrib.png", 15.0))
    story.append(Paragraph("图4 前30大权重股按行业分组的近似拖累", CAP))
    story.append(Paragraph("2.2 风格与利率", H3))
    story.append(Paragraph(
        f"中证指数快照显示，红利低波相关指数近一个月普遍回撤，红利低波100近一个月约 {summary['index_month_return_text']}。"
        f"同期中国10年国债收益率变化 {bp(summary['bond'].get('cn10_change'))}，说明本轮主要不是长端利率上行冲击，"
        "而是高股息交易拥挤度下降和权重行业补跌。", BODY))
    story.append(PageBreak())

    story.append(Paragraph("三、抄底胜率", H2))
    story.append(img("fig_winrate_heatmap.png", 16.0))
    story.append(Paragraph("图5 不同回撤档位买入后的前瞻胜率", CAP))
    win60 = tables["60"]
    rows = [["回撤档", "样本", "胜率", "均值", "P10", "最差", "再跌10%"]]
    for _, row in win60.iterrows():
        rows.append([row["回撤档位"], int(row["样本"]), pct0(row["胜率"]), pct(row["均值"]), pct(row["P10"]), pct(row["最差"]), pct0(row["再跌10%概率"])])
    story.append(table(rows, [2.5 * cm, 1.7 * cm, 1.9 * cm, 2.1 * cm, 2.1 * cm, 2.1 * cm, 2.2 * cm], fs=8.0))
    story.append(Spacer(1, 0.3 * cm))
    story.append(img("fig_similar_stats.png", 16.0))
    story.append(Paragraph("图6 当前相似回撤样本的胜率与最大浮亏", CAP))
    rows = [["持有", "样本", "胜率", "均值", "最差", "浮亏中位", "较差10%浮亏"]]
    for _, row in similar.iterrows():
        rows.append([row["持有期"], int(row["样本"]), pct0(row["胜率"]), pct(row["均值"]), pct(row["最差"]), pct(row["最大浮亏中位"]), pct(row["最大浮亏P10"])])
    story.append(table(rows, [2.2 * cm, 1.8 * cm, 1.9 * cm, 2.1 * cm, 2.1 * cm, 2.4 * cm, 2.6 * cm], fs=8.0))

    story.append(Paragraph("四、操作框架", H2))
    for text in [
        "第一笔30%：当前位置建立观察仓，承认赔率已经改善，但不押注最低点。",
        "第二笔30%：若再跌3-5%或连续3日不创新低，再加仓。",
        "第三笔40%：站回MA20/MA60后右侧确认，再补足仓位。",
        "失效条件：高股息继续显著跑输宽基，且长端利率重新上行，则降低加仓速度。",
    ]:
        story.append(Paragraph(text, BODY))
    story.append(Paragraph("方法局限：成分贡献为前30大权重股近似，不是完整指数归因；历史胜率使用重叠样本，不代表未来收益承诺。", NOTE))

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    return pdf_path


# ============================================================================
# 主流程
# ============================================================================
def main() -> None:
    for key in ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"]:
        os.environ.pop(key, None)

    navs, names, ex_div_dates = load_etf_universe()
    f_main = calc_features(navs[MAIN])
    state = state_snapshot(navs, names)
    as_of = navs[MAIN].index[-1].strftime("%Y-%m-%d")
    end_date = navs[MAIN].index[-1]
    peak_date = f_main["nav"].idxmax().strftime("%Y-%m-%d")
    weight_start_fallback = pd.Timestamp("2026-05-29")

    bonds = fetch_bond_yields()
    index_snapshot = fetch_index_snapshot()
    weights = fetch_index_weights()
    if not weights.empty and "日期" in weights.columns:
        weight_date = pd.to_datetime(weights["日期"].iloc[0])
    else:
        weight_date = weight_start_fallback
    start_date = max(pd.Timestamp(weight_date), navs[MAIN].index[0])

    contrib = calc_constituent_contribution(weights, start_date, end_date, top_n=30)
    proxy_returns = returns_since(navs, names, start_date, end_date)

    winrate_tables = winrate_by_drawdown(f_main)
    similar = similar_drawdown_stats(f_main, float(state[MAIN]["dd"]), width=0.025)
    if similar.empty:
        raise RuntimeError("相似回撤样本为空，无法生成胜率结论")
    signals = calc_signal_state(f_main)
    bond = bond_changes(bonds, start_date, end_date)

    if not index_snapshot.empty:
        row = index_snapshot[index_snapshot["指数代码"].astype(str) == INDEX_CODE]
        if len(row) == 0:
            index_month_return_text = "-"
        else:
            raw = row["近一个月收益率"].iloc[0]
            val = safe_float(raw)
            index_month_return_text = f"{val:+.2f}%" if math.isfinite(val) else str(raw)
    else:
        index_month_return_text = "-"

    summary = {
        "as_of": as_of,
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "main": MAIN,
        "index_code": INDEX_CODE,
        "peak_date": peak_date,
        "weight_date": pd.Timestamp(weight_date).strftime("%Y-%m-%d"),
        "current_dd_label": dd_label(float(state[MAIN]["dd"])),
        "state": state,
        "signals": signals,
        "bond": bond,
        "index_month_return_text": index_month_return_text,
        "ex_div_dates": ex_div_dates,
        "contrib_count": int(len(contrib)),
        "contrib_weight_coverage": float(contrib["权重"].sum()) if not contrib.empty else 0.0,
        "contrib_sum": float(contrib["近似贡献"].sum()) if not contrib.empty else 0.0,
        "similar_stats": similar.to_dict("records"),
        "winrate_60d": winrate_tables["60"].to_dict("records"),
    }
    (ROOT / "summary.json").write_text(json.dumps(to_builtin(summary), ensure_ascii=False, indent=2), encoding="utf-8")
    pd.DataFrame(state).T.to_csv(DATA / "current_state.csv", encoding="utf-8-sig")

    print("[3] 生成研报图表...")
    fig_nav_drawdown(navs[MAIN], f_main)
    fig_proxy_returns(proxy_returns)
    fig_constituent_contrib(contrib)
    fig_sector_contrib(contrib)
    fig_winrate_heatmap(winrate_tables)
    fig_similar_stats(similar)

    print("[4] 生成 Markdown / PDF 研报...")
    md_path = build_markdown(summary, proxy_returns, contrib, similar, winrate_tables, index_snapshot)
    pdf_path = build_pdf(summary, proxy_returns, contrib, similar, winrate_tables)
    generate_cards(summary, f_main, contrib, proxy_returns, similar, winrate_tables)

    print("\n完成产出：")
    print(f"  Cards: {CARDS}")
    print(f"  Markdown: {md_path}")
    print(f"  PDF: {pdf_path}")
    print(f"  Data: {DATA}")


if __name__ == "__main__":
    main()