
import logging
from src.data.collector import DataCollector

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    print("---------------------------------------------------")
    print("   Antigravity Agent - Initial Data Ingestion")
    print("---------------------------------------------------")
    
    # Target Symbols from Report
    # Tech Stocks: NVDA, TSLA, AMD
    # Leveraged ETFs: TQQQ, SOXL
    targets = ["NVDA", "TSLA", "AMD", "TQQQ", "SOXL"]
    
    print(f"[*] Target Symbols: {targets}")
    print("[*] Collecting last 365 days of 1-minute bars...")
    print("    This may take a while depending on your internet connection.")
    
    collector = DataCollector()
    collector.collect_historical_data(targets, days=365)
    
    print("[+] Data collection complete.")

if __name__ == "__main__":
    main()
