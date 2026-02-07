import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from src.strategy.base import BaseStrategy

logger = logging.getLogger(__name__)

class BollingerReversionStrategy(BaseStrategy):
    def __init__(self, symbol: str, period: int = 20, std_dev: float = 2.0):
        super().__init__(symbol, "BollingerReversion")
        self.period = period
        self.std_dev = std_dev
        self.upper_band = None
        self.lower_band = None
        self.sma = None

    def on_market_open(self, daily_ohlcv: pd.DataFrame):
        """
        Calculates Bollinger Bands based on recent history.
        """
        if len(daily_ohlcv) < self.period:
            logger.warning(f"[{self.symbol}] Not enough data for Bollinger Bands ({len(daily_ohlcv)} < {self.period})")
            return

        # Calculate Bands
        close_prices = daily_ohlcv['close']
        self.sma = close_prices.rolling(window=self.period).mean().iloc[-1]
        std = close_prices.rolling(window=self.period).std().iloc[-1]
        
        self.upper_band = self.sma + (std * self.std_dev)
        self.lower_band = self.sma - (std * self.std_dev)
        
        logger.info(f"[{self.symbol}] {self.name} Initialized. SMA={self.sma:.2f}, Upper={self.upper_band:.2f}, Lower={self.lower_band:.2f}")

    def generate_signal(self, current_price: float, current_position: int = 0, avg_entry_price: float = 0.0) -> Optional[Dict[str, Any]]:
        """
        Buy: Price touches/breaks Lower Band
        Sell: Price touches/breaks Upper Band or SMA (Mean Reversion)
        """
        if self.upper_band is None or self.lower_band is None:
            return None

        # BUY Signal (Oversold)
        if current_position == 0:
            if current_price <= self.lower_band:
                logger.info(f"[{self.symbol}] {self.name} BUY Signal. Price {current_price} <= Lower Band {self.lower_band}")
                return {
                    "action": "BUY",
                    "price": current_price,
                    "reason": f"{self.name} (Oversold)"
                }

        # SELL Signal (Overbought or Mean Reverted)
        elif current_position > 0:
            # Profit Take / Mean Reversion
            if current_price >= self.sma: # Touch Middle Band (Conservative) or Upper Band
                # Let's aim for SMA as first target for high win rate
                logger.info(f"[{self.symbol}] {self.name} SELL Signal. Price {current_price} >= SMA {self.sma}")
                return {
                    "action": "SELL",
                    "price": current_price,
                    "reason": f"{self.name} (Mean Reversion)"
                }
            
            # Stop Loss (if needed, e.g. -5%)
            if avg_entry_price > 0:
                 loss_pct = (current_price - avg_entry_price) / avg_entry_price
                 if loss_pct <= -0.05:
                     return {
                        "action": "SELL",
                        "price": current_price,
                        "reason": f"{self.name} (Stop Loss -5%)" 
                     }

        return None

    def on_market_close(self):
        self.upper_band = None
        self.lower_band = None
