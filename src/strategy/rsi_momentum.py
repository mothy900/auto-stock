import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from src.strategy.base import BaseStrategy

logger = logging.getLogger(__name__)

class RSIMomentumStrategy(BaseStrategy):
    def __init__(self, symbol: str, rsi_period: int = 14, sma_period: int = 20):
        super().__init__(symbol, "RSIMomentum")
        self.rsi_period = rsi_period
        self.sma_period = sma_period
        self.daily_sma = None
        self.rsi = None
        self.prev_rsi = None

    def calculate_rsi(self, series: pd.Series, period: int = 14) -> float:
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        return 100 - (100 / (1 + rs)).iloc[-1]

    def on_market_open(self, daily_ohlcv: pd.DataFrame):
        """
        Calculates trend filter (SMA) and initial RSI.
        """
        if len(daily_ohlcv) < max(self.sma_period, self.rsi_period):
            return

        self.daily_sma = daily_ohlcv['close'].rolling(window=self.sma_period).mean().iloc[-1]
        
        # Calculate initial RSI (from yesterday's close)
        self.prev_rsi = self.calculate_rsi(daily_ohlcv['close'], self.rsi_period)
        
        logger.info(f"[{self.symbol}] {self.name} Initialized. SMA={self.daily_sma:.2f}, PrevRSI={self.prev_rsi:.2f}")

    def generate_signal(self, current_price: float, current_position: int = 0, avg_entry_price: float = 0.0, current_rsi: float = None) -> Optional[Dict[str, Any]]:
        """
        Buy: Price > SMA20 (Uptrend) AND RSI < 50 (Dip)
        Sell: RSI > 70 (Overbought) OR 5% Profit
        """
        # Note: current_rsi should ideally be passed in or calculated from intraday data.
        # For simplicity, if current_rsi is None, we skip or rely on external calculation.
        # In this architecture, assume 'current_price' is real-time. 
        # Calculating real-time RSI requires intraday bars. 
        # For this MVP, let's assume valid 'current_rsi' is passed or we approximate it?
        # Actually, let's assume the Executor calculates RSI or passes a sufficient data window.
        
        # If we can't calculate RSI, we can't trade.
        if current_rsi is None:
            # Fallback: We need RSI. If not passed, we can't determine.
            return None

        if self.daily_sma is None:
            return None

        # BUY Signal (Dip in Uptrend)
        if current_position == 0:
            if current_price > self.daily_sma: # Uptrend
                if 40 <= current_rsi <= 50: # Dip Zone
                    logger.info(f"[{self.symbol}] {self.name} BUY Signal. Price {current_price} > SMA, RSI {current_rsi:.1f}")
                    return {
                        "action": "BUY",
                        "price": current_price,
                        "reason": f"{self.name} (RSI Dip)"
                    }

        # SELL Signal
        elif current_position > 0:
            # Target Profit (5%)
            if avg_entry_price > 0:
                profit_pct = (current_price - avg_entry_price) / avg_entry_price
                if profit_pct >= 0.05:
                     return {
                        "action": "SELL",
                        "price": current_price,
                        "reason": f"{self.name} (Target 5%)" 
                     }
            
            # RSI Overbought
            if current_rsi >= 70:
                return {
                    "action": "SELL",
                    "price": current_price,
                    "reason": f"{self.name} (RSI > 70)" 
                }

        return None

    def on_market_close(self):
        self.daily_sma = None
