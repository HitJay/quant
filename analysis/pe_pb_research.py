"""
PE/PB估值择时研究 — 回测脚本 v2
===================================
修复:
  - 多window/threshold组合测试 (含5年窗口)
  - 分别生成宽基和行业的独立价格矩阵
  - 增加calmar指标
  - 行业反转策略用所有5只ETF (含516160)
"""

import os, sys, json, argparse
import numpy as np
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quant.backtest.engine import BacktestEngine, BacktestConfig
from quant.backtest.metrics import annual_return, max_drawdown, sharpe, calmar, win_rate
from quant.strategies.base import Strategy, Signal

# ═══════════════════════════════════════════
# Data Fetching
# ═══════════════════════════════════════════

def fetch_etf_sina(symbol: str) -> pd.Series:
    import akshare as ak
    prefix_map = {"51": "sh", "58": "sh", "56": "sh", "15": "sz", "16": "sz", "18": "sz"}
    code = f"{prefix_map.get(symbol[:2], 'sh')}{symbol}"
    df = ak.fund_etf_hist_sina(symbol=code)
    df["date"] = pd.to_datetime(df["date"])
    return df.set_index("date").sort_index()["close"].rename(symbol)


def fetch_index_pe(symbol="沪深300") -> pd.Series:
    import akshare as ak
    df = ak.stock_index_pe_lg(symbol=symbol)
    df["date"] = pd.to_datetime(df["日期"])
    return df.set_index("date").sort_index()["滚动市盈率"].rename("PE_TTM")


def fetch_index_pb(symbol="沪深300") -> pd.Series:
    import akshare as ak
    df = ak.stock_index_pb_lg(symbol=symbol)
    df["date"] = pd.to_datetime(df["日期"])
    return df.set_index("date").sort_index()["市净率"].rename("PB")


# ═══════════════════════════════════════════
# Strategy: 宽基PE/PB百分位择时
# ═══════════════════════════════════════════

class PEPercentileTiming(Strategy):
    """PE/PB历史百分位择时 — 多参数支持"""

    def __init__(self, equity="510300", bond="511010",
                 val_series=None, pct_window=1260,  # default 5yr
                 low_pct=0.30, high_pct=0.70,
                 min_periods=252):
        self.equity = equity
        self.bond = bond
        self.val = val_series
        self.pct_window = pct_window
        self.low_pct = low_pct
        self.high_pct = high_pct
        self.min_periods = min_periods

    def _compute_pct(self, price_idx):
        """每次都重新计算百分位（不使用缓存，因为price_idx随时间增长）"""
        aligned = self.val.reindex(price_idx).dropna() if self.val is not None else None
        if aligned is None or len(aligned) < self.min_periods:
            return pd.Series(dtype=float)
        return aligned.rolling(self.pct_window, min_periods=self.min_periods).rank(pct=True)

    def get_signal(self, date, price_idx):
        pct = self._compute_pct(price_idx)
        try:
            val = float(pct.loc[:date].dropna().iloc[-1])
        except (IndexError, KeyError):
            return 0.5

        if val <= self.low_pct:
            return 1.0
        elif val >= self.high_pct:
            return 0.0
        return 1.0 - (val - self.low_pct) / (self.high_pct - self.low_pct)

    def rebalance(self, date, symbols, prices):
        w = max(0.0, min(1.0, self.get_signal(date, prices.index)))
        weights = {}
        if w > 0:
            weights[self.equity] = w
        if self.bond and w < 1.0:
            weights[self.bond] = 1.0 - w
        return Signal(date=str(date), weights=weights)


class PEPBCombined(Strategy):
    """PE+PB均值"""

    def __init__(self, pe_strat, pb_strat):
        self.pe = pe_strat
        self.pb = pb_strat

    def rebalance(self, date, symbols, prices):
        idx = prices.index
        w = (self.pe.get_signal(date, idx) + self.pb.get_signal(date, idx)) / 2
        w = max(0.0, min(1.0, w))
        weights = {}
        if w > 0:
            weights[self.pe.equity] = w
        if self.pe.bond and w < 1.0:
            weights[self.pe.bond] = 1.0 - w
        return Signal(date=str(date), weights=weights)


class BuyAndHold(Strategy):
    def __init__(self, sym="510300"):
        self.sym = sym

    def rebalance(self, date, symbols, prices):
        return Signal(date=str(date), weights={self.sym: 1.0})


class Fixed6040(Strategy):
    def rebalance(self, date, symbols, prices):
        return Signal(date=str(date), weights={"510300": 0.6, "511010": 0.4})


# ═══════════════════════════════════════════
# Strategy: 行业反转/动量
# ═══════════════════════════════════════════

class SectorRotation(Strategy):
    """买过去N月最强(动量)或最弱(反转)的K个行业"""

    def __init__(self, lookback_months=3, hold_n=2, mode="momentum"):
        self.lb = lookback_months
        self.n = hold_n
        self.mode = mode  # "momentum" or "reversal"

    def rebalance(self, date, symbols, prices):
        idx = prices.index
        pos = idx.get_loc(date)
        start_pos = max(0, pos - self.lb * 21)
        start_date = idx[start_pos]

        rets = {}
        for s in symbols:
            if s not in prices.columns:
                continue
            try:
                sv = prices.loc[start_date, s]
                ev = prices.loc[date, s]
                if pd.notna(sv) and pd.notna(ev) and sv > 0:
                    rets[s] = ev / sv - 1
            except (KeyError, IndexError):
                continue

        if not rets:
            return Signal(date=str(date), weights={})

        if self.mode == "reversal":
            ranked = sorted(rets, key=rets.get)  # worst first
        else:
            ranked = sorted(rets, key=rets.get, reverse=True)  # best first

        sel = ranked[:self.n]
        w = 1.0 / len(sel)
        return Signal(date=str(date), weights={s: w for s in sel})


class EqualWeight(Strategy):
    def rebalance(self, date, symbols, prices):
        active = [s for s in symbols if s in prices.columns and pd.notna(prices.loc[date, s])]
        if not active:
            return Signal(date=str(date), weights={})
        w = 1.0 / len(active)
        return Signal(date=str(date), weights={s: w for s in active})


# ═══════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════

def metrics(result, name):
    nav = result.nav_series
    return {
        "name": name,
        "annual_return": round(annual_return(nav) * 100, 2),
        "max_drawdown": round(max_drawdown(nav) * 100, 2),
        "sharpe": round(sharpe(nav), 2),
        "calmar": round(calmar(nav), 2),
        "win_rate": round(win_rate(nav) * 100, 1),
        "total_return": round(result.total_return * 100, 2),
        "start": str(nav.index[0].date()),
        "end": str(nav.index[-1].date()),
        "years": round((nav.index[-1] - nav.index[0]).days / 365.25, 1),
    }


# ═══════════════════════════════════════════
# Main
# ═══════════════════════════════════════════

def run_market_timing_sweep(pe, pb, price_df):
    """多参数PE/PB择时扫描"""
    engine = BacktestEngine(BacktestConfig(rebalance_freq="monthly"))
    symbols = ["510300", "511010"]

    windows = [1260, 1890, 2520]  # 5yr, 7.5yr, 10yr
    thresholds = [(0.20, 0.80), (0.30, 0.70), (0.25, 0.75)]
    indicators = ["PE", "PB"]

    results = {}
    navs = {}

    # Benchmarks
    for name, s in [("买入持有", BuyAndHold()), ("60/40固定", Fixed6040())]:
        r = engine.run(s, price_df, symbols)
        results[name] = metrics(r, name)
        navs[name] = r.nav_series

    # PE variants
    for w in windows:
        for lo, hi in thresholds:
            name = f"PE_{w//252}y_{int(lo*100)}_{int(hi*100)}"
            s = PEPercentileTiming(val_series=pe, pct_window=w, low_pct=lo, high_pct=hi)
            try:
                r = engine.run(s, price_df, symbols)
                results[name] = metrics(r, name)
                navs[name] = r.nav_series
            except Exception as e:
                results[name] = {"name": name, "error": str(e)}

    # PB variants
    for w in windows:
        for lo, hi in thresholds:
            name = f"PB_{w//252}y_{int(lo*100)}_{int(hi*100)}"
            s = PEPercentileTiming(val_series=pb, pct_window=w, low_pct=lo, high_pct=hi)
            try:
                r = engine.run(s, price_df, symbols)
                results[name] = metrics(r, name)
                navs[name] = r.nav_series
            except Exception as e:
                results[name] = {"name": name, "error": str(e)}

    # PE+PB best combo (5yr, 30/70)
    pe_s = PEPercentileTiming(val_series=pe, pct_window=1260, low_pct=0.30, high_pct=0.70)
    pb_s = PEPercentileTiming(val_series=pb, pct_window=1260, low_pct=0.30, high_pct=0.70)
    combined = PEPBCombined(pe_s, pb_s)
    r = engine.run(combined, price_df, symbols)
    results["PE+PB联合_5y_30_70"] = metrics(r, "PE+PB联合_5y_30_70")
    navs["PE+PB联合_5y_30_70"] = r.nav_series

    return results, navs


def run_sector_sweep(price_df, sectors):
    """行业反转vs动量多参数扫描"""
    engine = BacktestEngine(BacktestConfig(rebalance_freq="monthly"))

    results = {}
    navs = {}

    # Benchmark
    r = engine.run(EqualWeight(), price_df, sectors)
    results["等权持有"] = metrics(r, "等权持有")
    navs["等权持有"] = r.nav_series

    # Sweep lookback windows and hold_n
    for lb in [1, 3, 6, 12]:
        for n in [2, 3]:
            for mode in ["reversal", "momentum"]:
                mode_cn = "反转" if mode == "reversal" else "动量"
                name = f"{mode_cn}{lb}月_hold{n}"
                s = SectorRotation(lookback_months=lb, hold_n=n, mode=mode)
                try:
                    r = engine.run(s, price_df, sectors)
                    results[name] = metrics(r, name)
                    navs[name] = r.nav_series
                except Exception as e:
                    results[name] = {"name": name, "error": str(e)}

    return results, navs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output/pe_pb_research")
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    # ── Fetch data ──
    print("📊 Fetching ETF prices (Sina)...")
    etf_data = {}
    for s in ["510300", "511010", "512880", "512690", "159995", "516160", "512980"]:
        try:
            etf_data[s] = fetch_etf_sina(s)
            print(f"  {s}: {len(etf_data[s])}d, {etf_data[s].index[0].date()}~{etf_data[s].index[-1].date()}")
        except Exception as e:
            print(f"  {s}: FAILED - {e}")

    all_prices = pd.DataFrame(etf_data)
    market_prices = all_prices[["510300", "511010"]].dropna()
    sector_prices = all_prices[["512880", "512690", "159995", "516160", "512980"]].dropna()
    print(f"  宽基: {market_prices.shape} | 行业: {sector_prices.shape}")

    print("📊 Fetching PE/PB...")
    pe = fetch_index_pe("沪深300")
    pb = fetch_index_pb("沪深300")
    print(f"  PE: {len(pe)}d, {pe.index[0].date()}~{pe.index[-1].date()}")
    print(f"  PB: {len(pb)}d, {pb.index[0].date()}~{pb.index[-1].date()}")

    # ── Study 1: Market PE/PB Timing ──
    print("\n📈 Study 1: 宽基PE/PB百分位择时")
    print("=" * 60)
    mt_results, mt_navs = run_market_timing_sweep(pe, pb, market_prices)
    for name, m in mt_results.items():
        if "error" in m:
            print(f"  ❌ {name}: {m['error']}")
        else:
            print(f"  {name}: 年化{m['annual_return']:>6.1f}% 回撤{m['max_drawdown']:>5.1f}% "
                  f"夏普{m['sharpe']:>5.2f} 卡玛{m['calmar']:>5.2f}")

    # ── Study 2: Sector Value vs Momentum ──
    print("\n📈 Study 2: 行业反转vs动量")
    print("=" * 60)
    sr_results, sr_navs = run_sector_sweep(sector_prices, list(sector_prices.columns))
    for name, m in sr_results.items():
        if "error" in m:
            print(f"  ❌ {name}: {m['error']}")
        else:
            print(f"  {name}: 年化{m['annual_return']:>6.1f}% 回撤{m['max_drawdown']:>5.1f}% "
                  f"夏普{m['sharpe']:>5.2f} 卡玛{m['calmar']:>5.2f}")

    # ── Save ──
    output = {
        "meta": {
            "title": "PE/PB估值择时研究",
            "generated": datetime.now().isoformat(),
        },
        "market_timing": mt_results,
        "sector_rotation": sr_results,
        "pe_now": {"value": round(float(pe.iloc[-1]), 2),
                    "pct": round(float(pe.rank(pct=True).iloc[-1]) * 100, 1),
                    "min": round(float(pe.min()), 2),
                    "max": round(float(pe.max()), 2)},
        "pb_now": {"value": round(float(pb.iloc[-1]), 2),
                    "pct": round(float(pb.rank(pct=True).iloc[-1]) * 100, 1),
                    "min": round(float(pb.min()), 2),
                    "max": round(float(pb.max()), 2)},
    }
    with open(f"{args.output_dir}/results.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    for name, nav in {**mt_navs, **sr_navs}.items():
        sname = name.replace("/", "_").replace(" ", "_").replace("+", "_")
        nav.to_csv(f"{args.output_dir}/nav_{sname}.csv")

    pe.to_csv(f"{args.output_dir}/pe_series.csv")
    pb.to_csv(f"{args.output_dir}/pb_series.csv")

    print(f"\n✅ Done → {args.output_dir}/")
    return output


if __name__ == "__main__":
    main()
