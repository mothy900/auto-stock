
import logging
from src.data.alpaca_interface import AlpacaInterface
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)

def debug():
    try:
        alpaca = AlpacaInterface()
        end = datetime.now()
        start = end - timedelta(days=5)
        print(f"Fetch bars for NVDA from {start} to {end}")
        df = alpaca.get_bars("NVDA", start, end)
        if df is None:
            print("Result is None")
        else:
            print(f"Result Shape: {df.shape}")
            print(df.head())
    except Exception as e:
        print(f"EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug()
