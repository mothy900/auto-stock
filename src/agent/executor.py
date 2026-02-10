import logging
import asyncio
import pandas as pd
from datetime import datetime
from typing import List, Dict
from src.data.alpaca_interface import AlpacaInterface
from src.data.database import DatabaseManager
from src.strategy.base import BaseStrategy
from src.strategy.volatility_breakout import VolatilityBreakoutStrategy
from src.strategy.bollinger_reversion import BollingerReversionStrategy
from src.strategy.rsi_momentum import RSIMomentumStrategy

logger = logging.getLogger(__name__)

class TradingExecutor:
    def __init__(self, symbols: List[str], investment_per_symbol: float = 10000.0):
        self.symbols = symbols
        self.investment_per_symbol = investment_per_symbol
        self.alpaca = AlpacaInterface()
        self.db = DatabaseManager()
        
        # Initialize Strategies
        self.strategies: List[BaseStrategy] = []
        for s in symbols:
            self.strategies.append(VolatilityBreakoutStrategy(s))
            self.strategies.append(BollingerReversionStrategy(s))
            self.strategies.append(RSIMomentumStrategy(s))
        self.running = False

    async def initialize_day(self):
        """Pre-market routine: Optimize K and set Targets."""
        logger.info("Initializing Agent for the day...")
        
        # 1. Update Market Data is assumed done by Scheduler/Collector separately
        # Here we just load what we have from DB to optimize K
        
        for strategy in self.strategies:
            symbol = strategy.symbol
            try:
                # Load recent daily data for K optimization
                query = """
                    SELECT * FROM ohlcv_data 
                    WHERE symbol = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 30
                """
                rows = self.db.execute_query(query, (symbol,))
                if not rows:
                    logger.warning(f"No data for {symbol}, skipping optimization.")
                    continue
                    
                df = pd.DataFrame([dict(row) for row in rows])
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)
                df.sort_index(inplace=True)
                
                # Resample to Daily if data is minute-level
                # Assuming ohlcv_data is 1-min, we need daily for the strategy
                daily_df = df.resample('D').agg({
                    'open': 'first', 
                    'high': 'max', 
                    'low': 'min', 
                    'close': 'last'
                }).dropna()

                # Optimize K (only for VolatilityBreakout)
                if isinstance(strategy, VolatilityBreakoutStrategy):
                    best_k = strategy.optimize_k(daily_df)
                
                # Set Initial State (Range calculation)
                # We pass the full daily_df so it can pick the last closed day
                strategy.on_market_open(daily_df)
                
            except Exception as e:
                logger.error(f"Error initializing {symbol}: {e}")

    async def run_loop(self):
        """Main Trading Loop."""
        self.running = True
        logger.info("Starting Trading Loop...")
        
        while self.running:
            try:
                # 0. Check Market Status
                clock = self.alpaca.get_market_status()
                if not clock.is_open:
                    logger.info("Market is closed. Waiting...")
                    await asyncio.sleep(60)
                    continue

                for strategy in self.strategies:
                    symbol = strategy.symbol
                    # 1. Get Real-time Data
                    # We can use Alpaca's get_latest_trade or bar
                    # For breakout, we check current price against target
                    
                    # Note: Optimization - In a real high-freq scenario we use Websocket.
                    # For this 'loop' based approach, polling snapshots is easier to implement first.
                    try:
                        current_price = self.alpaca.get_latest_price(symbol)
                    except Exception:
                        continue
                    
                    # Special Case logic removed (redundant)

                    # 2. Update Strategy Target if needed (requires Open price)
                    if hasattr(strategy, 'update_target') and strategy.target_price is None and strategy.range_k is not None:
                        # Try to get today's opening bar
                        # If simple, we can just wait for the first bar. 
                        # Let's simplify: In paper trading, we might assume Open is available after 9:30
                        # Try to get today's opening bar using Snapshot (Real-time IEX)
                        snapshot = self.alpaca.get_snapshot(symbol)
                        if snapshot and snapshot.daily_bar:
                            open_price = snapshot.daily_bar.open
                            strategy.update_target(open_price)
                    
                    # 3. Generate Signal
                    # Improved Position Fetching: Skip on API error instead of assuming zero.
                    try:
                        pos = self.alpaca.get_open_position(symbol)
                        if pos:
                            current_qty = float(pos.qty)
                            avg_entry_price = float(pos.avg_entry_price)
                        else:
                            current_qty = 0
                            avg_entry_price = 0.0
                    except Exception as e:
                        logger.error(f"⚠️  Skipping {symbol} due to position fetch error: {e}")
                        continue
                    
                    # Calculate RSI if needed
                    current_rsi = None
                    if isinstance(strategy, RSIMomentumStrategy):
                         # TODO: Implement RSI calculation using alpaca.get_bars
                         # For now, let's skip or try to get basics.
                         # Real implementation needs historical bars. 
                         pass

                    signal = strategy.generate_signal(current_price, current_qty, avg_entry_price, current_rsi=current_rsi) if isinstance(strategy, RSIMomentumStrategy) else strategy.generate_signal(current_price, current_qty, avg_entry_price)
                    
                    # 4. Execute
                    if signal:
                        if signal['action'] == 'BUY':
                            # Calculate Qty
                            # quantity = self.investment_per_symbol / current_price
                            # Round down to int
                            qty = int(self.investment_per_symbol // current_price)
                            
                            if qty > 0:
                                order = self.alpaca.submit_order(symbol, qty, 'buy')
                                logger.info(f"EXECUTED BUY {symbol}: {qty} @ {current_price} ({strategy.name})")
                                self.db.log_trade(symbol, 'BUY', qty, current_price, signal['reason'], str(order.id) if hasattr(order, 'id') else None, strategy.name)
                        
                        elif signal['action'] == 'SELL':
                            order = self.alpaca.submit_order(symbol, current_qty, 'sell')
                            logger.info(f"EXECUTED SELL {symbol}: {current_qty} @ {current_price} ({strategy.name})")
                            self.db.log_trade(symbol, 'SELL', current_qty, current_price, signal['reason'], str(order.id) if hasattr(order, 'id') else None, strategy.name)

                await asyncio.sleep(1) # 1 sec Tick
                
                # Heartbeat Log every 10 seconds (More frequent updates)
                if int(datetime.now().second) % 10 == 0:
                    for s in self.strategies:
                        if isinstance(s, VolatilityBreakoutStrategy) and s.target_price:
                             # Log the check process
                            condition = "BUY" if self.alpaca.get_latest_price(s.symbol) >= s.target_price else "WAIT"
                            logger.info(f"🔍 [{s.symbol}] {s.name} Check: Current {self.alpaca.get_latest_price(s.symbol):.2f} vs Target {s.target_price:.2f} -> {condition}")
                        else:
                            logger.info(f"[{s}] Initializing...")
                    await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                await asyncio.sleep(5)

    def stop(self):
        self.running = False
        logger.info("Stopping Executor...")
