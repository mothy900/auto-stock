
import logging
from src.data.database import DatabaseManager
from src.strategy.volatility_breakout import VolatilityBreakoutStrategy
import pandas as pd
import matplotlib.pyplot as plt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_strategy_test():
    print("---------------------------------------------------")
    print("   Antigravity Agent - Strategy Backtest (Test)")
    print("---------------------------------------------------")
    
    db = DatabaseManager()
    symbol = "NVDA" # Test with NVDA
    
    # 1. Load Data from DB
    print(f"[*] Loading data for {symbol}...")
    # Fetch all data
    query = "SELECT * FROM ohlcv_data WHERE symbol = ? ORDER BY timestamp ASC"
    rows = db.execute_query(query, (symbol,))
    
    if not rows:
        print("[-] No data found. Please run collection first.")
        return

    # Convert to DataFrame
    df = pd.DataFrame([dict(row) for row in rows])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    
    # Resample to Daily for K optimization and core logic check
    daily_df = df.resample('D').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()
    
    print(f"[+] Loaded {len(daily_df)} daily bars.")
    
    # 2. Optimize K
    strategy = VolatilityBreakoutStrategy(symbol)
    print("[*] Running Dynamic K Optimization...")
    best_k = strategy.optimize_k(daily_df)
    print(f"[+] Optimal K for {symbol}: {best_k}")
    
    # 3. Simple Backtest Visualization
    # Let's apply this Best K to the whole period (Simplified, in reality K changes daily)
    df_test = daily_df.copy()
    df_test['range'] = (df_test['high'].shift(1) - df_test['low'].shift(1))
    df_test['target'] = df_test['open'] + df_test['range'] * best_k
    df_test['breakout'] = df_test['high'] > df_test['target']
    
    # Calculate returns: (Close - Target) / Target
    df_test['strategy_return'] = 0.0
    mask = df_test['breakout']
    df_test.loc[mask, 'strategy_return'] = (df_test['close'] - df_test['target']) / df_test['target']
    
    # Cumulative Return
    df_test['cum_return'] = (1 + df_test['strategy_return']).cumprod()
    df_test['buy_hold'] = (1 + df_test['close'].pct_change()).cumprod()
    
    final_return = df_test['cum_return'].iloc[-1]
    
    print(f"[+] Backtest Result (Static K={best_k}):")
    print(f"    - Final Return: {final_return:.2f}x")
    print(f"    - Win Rate: {len(df_test[df_test['strategy_return'] > 0]) / len(df_test[df_test['breakout']]):.2%}")
    
    # This is just a sanity check script, not a full backtester
    
if __name__ == "__main__":
    run_strategy_test()
