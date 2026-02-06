import asyncio
import logging
from typing import List, Callable, Awaitable
from alpaca.data.live import StockDataStream
from alpaca.data.models import Trade, Bar
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class StreamClient:
    def __init__(self, symbols: List[str], data_handler: Callable[[dict], Awaitable[None]]):
        self.api_key = os.getenv("ALPACA_API_KEY")
        self.secret_key = os.getenv("ALPACA_SECRET_KEY")
        self.symbols = symbols
        self.data_handler = data_handler
        
        self.stream = StockDataStream(self.api_key, self.secret_key)

    async def _trade_handler(self, data: Trade):
        """Internal handler for trade updates."""
        try:
            # Normalize to dict for easier processing
            trade_data = {
                'type': 'trade',
                'symbol': data.symbol,
                'price': data.price,
                'size': data.size,
                'timestamp': data.timestamp
            }
            await self.data_handler(trade_data)
        except Exception as e:
            logger.error(f"Error processing trade: {e}")

    async def _bar_handler(self, data: Bar):
        """Internal handler for bar updates (if needed)."""
        pass

    def run(self):
        """Starts the websocket stream (blocking)."""
        logger.info(f"Starting generic stream for {self.symbols}...")
        
        # Subscribe to trades
        self.stream.subscribe_trades(self._trade_handler, *self.symbols)
        
        # Run
        try:
            self.stream.run()
        except Exception as e:
            logger.error(f"Stream error: {e}")

    async def run_async(self):
        """Starts the websocket stream (async)."""
        logger.info(f"Starting async stream for {self.symbols}...")
        self.stream.subscribe_trades(self._trade_handler, *self.symbols)
        await self.stream.stop() # Ensure clean state if needed? No, run handles loop.
        # Note: alpaca-py stream.run() is blocking. For async integration, 
        # we might need to run it in an executor or use the async support if available.
        # Actually StockDataStream uses websockets library which is async but wrapped.
        # Let's stick to simple run() for now, or check if we need a custom loop.
        await self.stream._run_forever()

if __name__ == "__main__":
    # Test
    async def printer(data):
        print(f"Received: {data}")

    client = StreamClient(["AAPL"], printer)
    # client.run() # Blocking
