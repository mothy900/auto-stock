import os
from datetime import datetime
from typing import List, Optional
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class AlpacaInterface:
    def __init__(self):
        self.api_key = os.getenv("ALPACA_API_KEY")
        self.secret_key = os.getenv("ALPACA_SECRET_KEY")
        self.base_url = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
        
        if not self.api_key or not self.secret_key:
            raise ValueError("Alpaca API credentials not found in environment variables.")

        # Initialize Trading Client
        self.trading_client = TradingClient(self.api_key, self.secret_key, paper=True)
        
        # Initialize Data Client
        self.data_client = StockHistoricalDataClient(self.api_key, self.secret_key)

    def get_account_info(self):
        """Get account details."""
        try:
            account = self.trading_client.get_account()
            return account
        except Exception as e:
            logger.error(f"Error fetching account info: {e}")
            raise

    def get_bars(self, symbol: str, start: datetime, end: datetime, timeframe: TimeFrame = TimeFrame.Minute):
        """Fetch historical bars."""
        request_params = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=timeframe,
            start=start,
            end=end,
            feed='iex'
        )
        try:
            bars = self.data_client.get_stock_bars(request_params)
            return bars.df if not bars.df.empty else None
        except Exception as e:
            logger.error(f"Error fetching bars for {symbol}: {e}")
            return None

    def submit_order(self, symbol: str, qty: float, side: str):
        """Submit a market order."""
        try:
            order_side = OrderSide.BUY if side.upper() == 'BUY' else OrderSide.SELL
            market_order_data = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=order_side,
                time_in_force=TimeInForce.DAY
            )
            order = self.trading_client.submit_order(order_data=market_order_data)
            logger.info(f"Order submitted: {side} {qty} {symbol}")
            return order
        except Exception as e:
            logger.error(f"Error submitting order: {e}")
            raise

    def get_market_status(self):
        """Check if market is open."""
        try:
            clock = self.trading_client.get_clock()
            return clock
        except Exception as e:
            logger.error(f"Error fetching market clock: {e}")
            return None

    def get_snapshot(self, symbol: str):
        """Fetch snapshot data which includes daily bar (Open, High, Low, Close)."""
        from alpaca.data.requests import StockSnapshotRequest
        try:
            req = StockSnapshotRequest(symbol_or_symbols=symbol, feed='iex')
            snapshot = self.data_client.get_stock_snapshot(req)
            return snapshot[symbol]
        except Exception as e:
            logger.error(f"Error fetching snapshot for {symbol}: {e}")
            return None

    def get_latest_price(self, symbol: str) -> float:
        """Fetch the latest trade price for a symbol."""
        from alpaca.data.requests import StockLatestTradeRequest
        try:
            request_params = StockLatestTradeRequest(symbol_or_symbols=symbol, feed='iex')
            trade = self.data_client.get_stock_latest_trade(request_params)
            return trade[symbol].price
        except Exception as e:
            logger.error(f"Error fetching latest price for {symbol}: {e}")
            raise

    def get_portfolio_history(self, period="1M", timeframe="1D"):
        """Fetch portfolio equity history."""
        from alpaca.trading.requests import GetPortfolioHistoryRequest
        try:
            req = GetPortfolioHistoryRequest(period=period, timeframe=timeframe)
            return self.trading_client.get_portfolio_history(req)
        except Exception as e:
            logger.error(f"Error fetching portfolio history: {e}")
            return None

if __name__ == "__main__":
    # verification
    try:
        alpaca = AlpacaInterface()
        acct = alpaca.get_account_info()
        print(f"Connected to Alpaca! Account Status: {acct.status}, Buying Power: ${acct.buying_power}")
    except Exception as e:
        print(f"Connection failed: {e}")
