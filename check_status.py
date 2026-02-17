import asyncio
import pandas as pd
from datetime import datetime, timedelta
from src.data.alpaca_interface import AlpacaInterface, load_dotenv
from src.strategy.volatility_breakout import VolatilityBreakoutStrategy
from src.strategy.bollinger_reversion import BollingerReversionStrategy
from src.strategy.rsi_momentum import RSIMomentumStrategy
from src.data.database import DatabaseManager
import alpaca.data.requests as alpaca_requests

async def check_status():
    load_dotenv()
    alpaca = AlpacaInterface()
    symbols = ["NVDA", "TSLA", "DUK", "SGRY"] # Key symbols to check
    
    print("\n🔎 Multi-Strategy Verification (Live Market Data)\n" + "="*60)
    
    for symbol in symbols:
        try:
            # 1. Get Data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            df = alpaca.get_bars(symbol, start_date, end_date)
            
            if df is None or df.empty:
                print(f"[{symbol}] No data found.")
                continue

            if isinstance(df.index, pd.MultiIndex):
                df = df.reset_index(level=0, drop=True) 
            
            daily_df = df.resample('D').agg({
                'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'
            }).dropna()
            
            current_price = alpaca.get_latest_price(symbol)
            
            # 2. Volatility Breakout
            vb = VolatilityBreakoutStrategy(symbol)
            vb.on_market_open(daily_df[:-1])
            # Estimate target with current open or fallback to last close if open not in daily_df
            today_open = daily_df.iloc[-1]['open'] 
            vb.update_target(today_open)
            vb_signal = vb.generate_signal(current_price)
            
            # 3. Bollinger Reversion
            br = BollingerReversionStrategy(symbol)
            br.on_market_open(daily_df[:-1])
            br_signal = br.generate_signal(current_price)
            
            # 4. RSI Momentum
            rsi = RSIMomentumStrategy(symbol)
            rsi.on_market_open(daily_df[:-1])
            # For verification, we approximate RSI from daily data (not perfect but works for test)
            approx_rsi = rsi.calculate_rsi(df['close'], rsi.rsi_period)
            rsi_signal = rsi.generate_signal(current_price, current_rsi=approx_rsi)

            print(f"[{symbol}] Current: ${current_price:.2f}")
            
            # Output Results
            def fmt_signal(sig): return f"🔥 {sig['action']}" if sig else "💤 WAIT"
            
            print(f"  - VolatilityBreakout: {fmt_signal(vb_signal)} (Target: ${vb.target_price:.2f})")
            print(f"  - BollingerReversion: {fmt_signal(br_signal)} (Bands: {br.lower_band:.2f} - {br.upper_band:.2f})")
            print(f"  - RSIMomentum:        {fmt_signal(rsi_signal)} (RSI: {approx_rsi:.1f}, SMA: {rsi.daily_sma:.2f})")
            print("-" * 60)
            
        except Exception as e:
            print(f"[{symbol}] Error: {e}")

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.getcwd())
    asyncio.run(check_status())
