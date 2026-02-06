import asyncio
import pandas as pd
from datetime import datetime, timedelta
from src.data.alpaca_interface import AlpacaInterface
from src.strategy.volatility_breakout import VolatilityBreakoutStrategy
from src.data.database import DatabaseManager

async def check_status():
    alpaca = AlpacaInterface()
    db = DatabaseManager()
    symbols = ["NVDA", "TSLA", "AMD", "TQQQ", "SOXL", "INOD", "PLTR", "DUK", "TIGR", "PAYO", "HROW", "SGRY"]
    
    print("\n🔎 Manual Strategy Check (Live Market Data)\n" + "="*50)
    
    for symbol in symbols:
        try:
            # 1. Get Daily Data for Target Calculation
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            # get_bars returns a DataFrame (or None)
            df = alpaca.get_bars(symbol, start_date, end_date)
            
            if df is None or df.empty:
                print(f"[{symbol}] No data found.")
                continue

            # Alpaca returns MultiIndex (symbol, timestamp) even for single symbol
            if isinstance(df.index, pd.MultiIndex):
                df = df.reset_index(level=0, drop=True) 
            
            # Resample to Daily
            daily_df = df.resample('D').agg({
                'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'
            }).dropna()
            
            # 2. Setup Strategy
            strat = VolatilityBreakoutStrategy(symbol)
            best_k = strat.optimize_k(daily_df[:-1]) # Optimize on past data
            
            # Set Target based on *Yesterday's* close/range and *Today's* Open
            # But wait, logic is: Target = Today_Open + (Prev_High - Prev_Low) * K
            # We need Today's Open.
            
            # Get Current Price & Today's Open
            latest_trade = alpaca.get_latest_price(symbol)
            today_bar = alpaca.data_client.get_stock_latest_bar(
                from_alpaca.data.requests.StockLatestBarRequest(symbol_or_symbols=symbol)
            ).popitem()[1] # returns dict {symbol: bar}
            
            today_open = today_bar.open
            
            # Manual Target Calc
            last_day = daily_df.iloc[-2] # Yesterday (assuming today is in df? maybe not yet if partial)
            # Actually, alpaca get_bars might not have today's full candle.
            # Let's rely on daily_df being up to yesterday.
            
            prev_range = last_day['high'] - last_day['low']
            target = today_open + prev_range * best_k
            
            status = "🔥 BUY SIGNAL" if latest_trade >= target else "💤 WAIT"
            diff = target - latest_trade
            
            print(f"[{symbol}]")
            print(f"  K: {best_k:.2f}")
            print(f"  Target: ${target:.2f} (Open ${today_open:.2f} + Range ${prev_range:.2f} * K)")
            print(f"  Current: ${latest_trade:.2f}")
            print(f"  Result: {status} (Diff: ${diff:.2f})")
            print("-" * 30)
            
        except Exception as e:
            print(f"[{symbol}] Error: {e}")

if __name__ == "__main__":
    from src.data.alpaca_interface import load_dotenv
    load_dotenv()
    # Fix imports for manual run
    import sys
    import os
    sys.path.append(os.getcwd())
    
    # Fix the missing import inside the function
    import alpaca.data.requests as from_alpaca 
    
    asyncio.run(check_status())
