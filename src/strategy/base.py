from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseStrategy(ABC):
    def __init__(self, symbol: str):
        self.symbol = symbol

    @abstractmethod
    def generate_signal(self, market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyzes market data and returns a trading signal.
        
        Args:
            market_data: A dictionary containing 'current_price', 'ohlcv', etc.
            
        Returns:
            A dictionary with 'action' ('BUY'/'SELL'), 'quantity', 'reason' or None.
        """
        pass

    @abstractmethod
    def on_market_open(self):
        """Called when the market opens."""
        pass

    @abstractmethod
    def on_market_close(self):
        """Called when the market closes."""
        pass
