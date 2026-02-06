import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from src.strategy.base import BaseStrategy

logger = logging.getLogger(__name__)

class VolatilityBreakoutStrategy(BaseStrategy):
    def __init__(self, symbol: str, initial_k: float = 0.5):
        super().__init__(symbol)
        self.k = initial_k
        self.target_price = None
        self.prev_close = None
        self.range_k = None  # Fix: Initialize to avoid AttributeError
        
    def on_market_open(self, daily_ohlcv: pd.DataFrame):
        """
        Calculates the target price for the day.
        Should be called before or at market open.
        
        Args:
            daily_ohlcv: DataFrame containing at least yesterday's data.
        """
        if daily_ohlcv.empty:
            logger.warning(f"No OHLCV data for {self.symbol}. Cannot set target.")
            return

        # Get yesterday's data
        # Assuming daily_ohlcv is sorted by date ascending
        last_row = daily_ohlcv.iloc[-1]
        self.prev_close = last_row['close']
        
        # Calculate Range (High - Low)
        price_range = last_row['high'] - last_row['low']
        
        # Calculate 20-day SMA (Trend Filter)
        if len(daily_ohlcv) >= 20:
            self.sma_20 = daily_ohlcv['close'].rolling(window=20).mean().iloc[-1]
        else:
            self.sma_20 = 0 # Fallback: No filter if not enough data
        
        # We need today's open price to set the target. 
        # In a live setting, this might be passed from the first bar of the day or pre-market.
        # But for 'Volatility Breakout', usually:
        # Target = Today_Open + Range * K
        # We will set the range part here and add Open when we get the first tick/bar.
        self.range_k = price_range * self.k
        
        logger.info(f"[{self.symbol}] Strategy Initialized. K={self.k}, Range={price_range}, SMA20={self.sma_20:.2f}")

    def update_target(self, current_open: float):
        """Sets the final target price using today's open."""
        if self.range_k is None:
            return
            
        self.target_price = current_open + self.range_k
        logger.info(f"[{self.symbol}] Target Price Set: {self.target_price:.2f} (Open: {current_open} + Range*K: {self.range_k})")

    def generate_signal(self, current_price: float, current_position: int = 0, avg_entry_price: float = 0.0) -> Optional[Dict[str, Any]]:
        """
        Checks if current price breaks out the target OR hits stop loss.
        """
        # 1. STOP LOSS CHECK (-3%)
        if current_position > 0 and avg_entry_price > 0:
            loss_pct = (current_price - avg_entry_price) / avg_entry_price
            if loss_pct <= -0.03: # -3% Stop Loss
                logger.warning(f"[{self.symbol}] STOP LOSS ACTIVATED! Current: {current_price}, Entry: {avg_entry_price} ({loss_pct:.2%})")
                return {
                    "action": "SELL",
                    "price": current_price,
                    "reason": "Stop Loss (-3%)"
                }

        if self.target_price is None:
            return None

        # 2. BUY SIGNAL (Breakout + Trend Filter)
        # Only buy if Price > Target AND Price > SMA 20 (Trend Filter)
        if current_position == 0 and current_price >= self.target_price:
            # Trend Filter Check
            if self.sma_20 > 0 and current_price < self.sma_20:
                 # Ensure we don't spam logs? Or maybe log once.
                 # logger.info(f"[{self.symbol}] Target hit but below SMA20 ({self.sma_20}). No Buy.")
                 return None
            
            logger.info(f"[{self.symbol}] Breakout! Price {current_price} >= Target {self.target_price} (SMA20 OK)")
            return {
                "action": "BUY",
                "price": current_price,
                "reason": "Volatility Breakout"
            }
            
        return None

    def optimize_k(self, history: pd.DataFrame) -> float:
        """
        Finds the best K value (0.3 to 0.9) based on recent history (e.g., 20 days).
        Returns the optimal K.
        """
        best_k = 0.5
        best_return = -float('inf')
        
        # Simple grid search 
        # Range updated: 0.3 ~ 0.9 (Avoid noise 0.1, 0.2)
        for k in [x * 0.1 for x in range(3, 10)]: # 0.3 ~ 0.9
            total_return = 1.0
            
            # Simple vector backtest
            # Shift data to align "Yesterday" with "Today"
            df = history.copy()
            df['prev_high'] = df['high'].shift(1)
            df['prev_low'] = df['low'].shift(1)
            df['range'] = df['prev_high'] - df['prev_low']
            df['target'] = df['open'] + df['range'] * k
            
            # Identify breakout days: High > Target
            # Return = (Close - Target) / Target if High > Target else 0 (assuming buy at Target)
            # Make sure we don't divide by zero or look ahead
            
            # Condition: Did price hit target?
            # We assume we buy AT target price, and sell at close.
            # So profit = (Close - Target) / Target
            
            df['is_breakout'] = df['high'] >= df['target']
            df['daily_return'] = np.where(df['is_breakout'], (df['close'] - df['target']) / df['target'], 0)
            
            # Cumulative return
            # fee adjustment could be added here
            cum_ret = (1 + df['daily_return']).prod()
            
            if cum_ret > best_return:
                best_return = cum_ret
                best_k = k
                
        logger.info(f"[{self.symbol}] Optimized K: {best_k} (Return: {best_return:.2%})")
        self.k = best_k
        return best_k

    def on_market_close(self):
        self.target_price = None
