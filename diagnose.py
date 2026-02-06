import sys
import os
import time
from datetime import datetime
import pytz
from src.data.alpaca_interface import AlpacaInterface

print("="*50)
print(f"🩺 ANTIGRAVITY DIAGNOSTIC TOOL - {datetime.now()}")
print("="*50)

# 1. Check Python Path
print("[1/4] Checking Environment...")
try:
    import src.data.alpaca_interface
    print("   ✅ Modules found.")
except ImportError as e:
    print(f"   ❌ Module Error: {e}")
    sys.exit(1)

# 2. Check Alpaca Connection & Clock
print("\n[2/4] Checking Market Status (Alpaca API)...")
try:
    alpaca = AlpacaInterface()
    clock = alpaca.get_market_status()
    print(f"   🕒 Server Time: {datetime.now(pytz.timezone('US/Eastern'))}")
    print(f"   🏛️ Market Open: {clock.is_open}")
    print(f"   🔜 Next Open: {clock.next_open}")
    print(f"   🔙 Next Close: {clock.next_close}")
    
    if clock.is_open:
        print("   ✅ Market is OPEN. Bot should be running.")
    else:
        print("   ⚠️ Market is CLOSED. Bot is sleeping.")
        
except Exception as e:
    print(f"   ❌ API Connection Failed: {e}")

# 3. Check Log File Activity
print("\n[3/4] Checking Log File Activity (agent.log)...")
log_file = "agent.log"
if os.path.exists(log_file):
    last_mod = os.path.getmtime(log_file)
    last_mod_time = datetime.fromtimestamp(last_mod)
    size = os.path.getsize(log_file)
    print(f"   📂 File Size: {size} bytes")
    print(f"   ⏰ Last Modified: {last_mod_time} (Server Local Time)")
    
    # Read last 5 lines
    print("\n   📜 Last 5 Log Lines:")
    print("-" * 30)
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines[-5:]:
            print("   " + line.strip())
    print("-" * 30)
else:
    print("   ❌ agent.log Not Found!")

print("\n[4/4] Process Check")
os.system("ps -ef | grep main.py | grep -v grep")

print("\nDONE.")
