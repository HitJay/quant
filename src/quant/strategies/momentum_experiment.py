"""Momentum Experiment Strategy — parameterized momentum/contrarian backtest"""

from quant.strategies.base import Signal, Strategy
from quant.factors.momentum import momentum_scores


class MomentumExperiment(Strategy):
    """
    Parameterized momentum/contrarian strategy for research experiments.
    
    Args:
        window: Lookback window in trading days (e.g., 5, 10, 20, 60, 120, 250)
        top_n: Number of top performers to hold
        reverse: If True, pick worst performers (contrarian); if False, pick best (momentum)
        universe: Optional UniverseConfig (not used in rebalance, for compatibility)
    """
    
    def __init__(self, window: int = 60, top_n: int = 1, reverse: bool = False, universe=None):
        self.window = window
        self.top_n = top_n
        self.reverse = reverse
        self.universe = universe
    
    def rebalance(self, date, symbols: list[str], prices) -> Signal:
        """
        Generate rebalance signal based on momentum scores.
        
        Args:
            date: Current rebalance date
            symbols: List of symbols to consider
            prices: Price DataFrame up to date
            
        Returns:
            Signal with equal-weighted allocation to top_n symbols
        """
        # Calculate momentum scores for all symbols
        scores = momentum_scores(prices, symbols, date, self.window)
        
        # If no valid scores (insufficient data), return empty weights
        if not scores:
            return Signal(date=str(date), weights={})
        
        # Sort symbols by score
        # reverse=False (momentum): pick highest scores (descending)
        # reverse=True (contrarian): pick lowest scores (ascending)
        sorted_syms = sorted(scores.keys(), key=lambda s: scores[s], reverse=not self.reverse)
        
        # Pick top_n
        selected = sorted_syms[:self.top_n]
        
        # Equal weight
        weight = 1.0 / len(selected)
        weights = {sym: weight for sym in selected}
        
        return Signal(date=str(date), weights=weights)
