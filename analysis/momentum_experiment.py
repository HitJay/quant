"""
Momentum Chasing Experiment Runner
===================================
Run parameterized momentum experiments across different ETF universes and windows.

Usage:
    cd /mnt/d/vscode/quant
    unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
    python analysis/momentum_experiment.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from quant.data.cache import Cache
from quant.data.fetcher import ETFDataFetcher
from quant.strategies.momentum_experiment import MomentumExperiment
from quant.backtest.engine import BacktestEngine
from quant.backtest.metrics import (
    annual_return,
    max_drawdown,
    sharpe,
    win_rate,
)
from quant.universe.config import UniverseConfig


# Experiment configuration
UNIVERSES = {
    "broad": {
        "name": "Broad Market (CSI300+CSI500)",
        "codes": ["510300", "510500"],
        "bench": "510300",
    },
    "sector": {
        "name": "Sector ETFs",
        "codes": ["515030", "512010", "159928", "512880", "512660", "516160"],
        "bench": "510300",
    },
    "commodity": {
        "name": "Commodity ETFs",
        "codes": ["518880", "159985", "159981", "510990"],
        "bench": "518880",
    },
}

WINDOWS = [5, 10, 20, 60, 120, 250]
START_DATE = "2018-01-01"
END_DATE = "2026-05-28"


def load_data(codes: list[str], cache: Cache) -> pd.DataFrame:
    """Load and merge price data for given codes"""
    fetcher = ETFDataFetcher()
    data = {}
    for code in codes:
        try:
            df = fetcher.fetch_or_cache(code, START_DATE, END_DATE, cache=cache)
            data[code] = df["close"]
            print(f"  ✓ Loaded {code}: {len(df)} days")
        except Exception as e:
            print(f"  ✗ Failed {code}: {e}")
    
    prices = pd.DataFrame(data).dropna()
    print(f"  Merged: {len(prices)} trading days")
    return prices


def run_single_experiment(
    universe_name: str,
    universe_config: dict,
    window: int,
    reverse: bool,
    prices: pd.DataFrame,
    cache: Cache,
) -> dict:
    """Run a single momentum experiment"""
    codes = universe_config["codes"]
    bench_code = universe_config["bench"]
    
    # Filter prices to only include codes in this universe
    avail_codes = [c for c in codes if c in prices.columns]
    if len(avail_codes) < 2:
        return None
    
    universe = UniverseConfig(etf_codes=avail_codes)
    prices_subset = prices[avail_codes]
    
    # Create strategy
    strategy_name = f"{'Reverse' if reverse else 'Momentum'}_{window}d"
    strategy = MomentumExperiment(
        window=window,
        top_n=1,
        reverse=reverse,
        universe=universe,
    )
    
    # Run backtest
    engine = BacktestEngine()
    result = engine.run(strategy, prices_subset, avail_codes)
    
    # Calculate metrics
    nav = result.nav_series
    if len(nav) < 2:
        return None
    
    ann_ret = annual_return(nav)
    max_dd = max_drawdown(nav)
    sharpe_ratio = sharpe(nav)
    win = win_rate(nav)
    total_ret = result.total_return
    
    # Benchmark
    bench = prices[bench_code].reindex(nav.index).ffill().dropna()
    bench_nav = bench / bench.iloc[0]
    bench_ret = bench.iloc[-1] / bench.iloc[0] - 1
    yrs = (bench.index[-1] - bench.index[0]).days / 365.25
    bench_ann = (1 + bench_ret) ** (1 / yrs) - 1 if yrs > 0 else 0
    
    return {
        "universe": universe_name,
        "universe_full": universe_config["name"],
        "window": window,
        "strategy": strategy_name,
        "reverse": reverse,
        "annual_return": ann_ret,
        "max_drawdown": max_dd,
        "sharpe": sharpe_ratio,
        "win_rate": win,
        "total_return": total_ret,
        "bench_annual": bench_ann,
        "bench_total": bench_ret,
        "alpha": ann_ret - bench_ann,
        "nav_series": nav,
        "bench_series": bench,
    }


def run_all_experiments():
    """Run full experiment matrix"""
    print("=" * 70)
    print("MOMENTUM CHASING EXPERIMENT")
    print("=" * 70)
    print(f"Period: {START_DATE} to {END_DATE}")
    print(f"Windows: {WINDOWS}")
    print(f"Universes: {list(UNIVERSES.keys())}")
    print()
    
    # Setup
    cache_dir = Path("./data/cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache = Cache(str(cache_dir))
    
    # Load all data first
    print("Loading data...")
    all_codes = []
    for cfg in UNIVERSES.values():
        all_codes.extend(cfg["codes"])
    all_codes.append("510300")  # Benchmark
    all_codes = list(set(all_codes))
    
    prices = load_data(all_codes, cache)
    print()
    
    # Run experiments
    results = []
    total = len(UNIVERSES) * len(WINDOWS) * 2  # momentum + reverse
    
    for universe_name, universe_config in UNIVERSES.items():
        print(f"\nUniverse: {universe_config['name']}")
        print("-" * 70)
        
        for window in WINDOWS:
            for reverse in [False, True]:
                strategy_type = "Reverse" if reverse else "Momentum"
                print(f"  Running {strategy_type} window={window}d...", end=" ")
                
                result = run_single_experiment(
                    universe_name,
                    universe_config,
                    window,
                    reverse,
                    prices,
                    cache,
                )
                
                if result:
                    results.append(result)
                    print(f"✓ Ann={result['annual_return']:.1%}, DD={result['max_drawdown']:.1%}")
                else:
                    print("✗ Skipped (insufficient data)")
    
    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    # Save results
    output_dir = Path("./output/momentum-experiment")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    csv_path = output_dir / "results.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n✓ Results saved to {csv_path}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    # Best momentum
    momentum_df = df[~df["reverse"]].copy()
    if len(momentum_df) > 0:
        best = momentum_df.loc[momentum_df["annual_return"].idxmax()]
        print(f"\nBest Momentum Strategy:")
        print(f"  Universe: {best['universe_full']}")
        print(f"  Window: {best['window']} days")
        print(f"  Annual Return: {best['annual_return']:.2%}")
        print(f"  Max Drawdown: {best['max_drawdown']:.2%}")
        print(f"  Sharpe: {best['sharpe']:.2f}")
        print(f"  Alpha: {best['alpha']:.2%}")
    
    # Best reverse
    reverse_df = df[df["reverse"]].copy()
    if len(reverse_df) > 0:
        best_rev = reverse_df.loc[reverse_df["annual_return"].idxmax()]
        print(f"\nBest Reverse Strategy:")
        print(f"  Universe: {best_rev['universe_full']}")
        print(f"  Window: {best_rev['window']} days")
        print(f"  Annual Return: {best_rev['annual_return']:.2%}")
        print(f"  Max Drawdown: {best_rev['max_drawdown']:.2%}")
        print(f"  Sharpe: {best_rev['sharpe']:.2f}")
        print(f"  Alpha: {best_rev['alpha']:.2%}")
    
    # Heatmap data
    print("\n\nHeatmap Data (Annual Return %):")
    print("-" * 70)
    heatmap = df.pivot_table(
        index=["universe", "reverse"],
        columns="window",
        values="annual_return",
    )
    print(heatmap.map(lambda x: f"{x:.1%}" if pd.notna(x) else "N/A"))
    
    return df


if __name__ == "__main__":
    df = run_all_experiments()
    print("\n✓ Experiment complete!")
