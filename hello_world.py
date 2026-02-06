
import logging
from src.data.alpaca_interface import AlpacaInterface
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_test():
    print("---------------------------------------------------")
    print("   Antigravity Agent - Hello World Connection Test")
    print("---------------------------------------------------")
    
    try:
        # 1. Initialize Interface
        print("[*] Connecting to Alpaca Paper Trading...")
        alpaca = AlpacaInterface()
        
        # 2. Check Account
        account = alpaca.get_account_info()
        print(f"[+] Connection Successful!")
        print(f"    - Account Number: {account.account_number}")
        print(f"    - Status: {account.status}")
        print(f"    - Buying Power: ${float(account.buying_power):,.2f}")
        print(f"    - Cash: ${float(account.cash):,.2f}")
        
        # 3. Check Market Status
        clock = alpaca.get_market_status()
        print(f"[*] Market Status: {'OPEN' if clock.is_open else 'CLOSED'}")
        print(f"    - Next Open: {clock.next_open}")
        print(f"    - Next Close: {clock.next_close}")

        # 4. Dry Run Order (Optional - Uncomment to test)
        # symbol = "AAPL"
        # qty = 1
        # print(f"[*] Submitting Dry Run Order: Buy {qty} {symbol}...")
        # order = alpaca.submit_order(symbol, qty, "buy")
        # print(f"[+] Order Submitted! ID: {order.id}")
        
    except Exception as e:
        print(f"[-] Error: {e}")
        print("\nPlease check your .env file and ensure ALPACA_API_KEY and ALPACA_SECRET_KEY are correct.")

if __name__ == "__main__":
    run_test()
