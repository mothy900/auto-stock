import sys
import os

print("="*50)
print("🔍 Environment Debugger")
print("="*50)

print(f"1. Current Working Directory (CWD): {os.getcwd()}")
print(f"2. Script Location: {os.path.abspath(__file__)}")

print("\n3. sys.path Content:")
for p in sys.path:
    print(f"   - {p}")

print("\n4. Checking Submodules:")
subdirs = ["src", "src/data", "src/agent", "src/strategy", "src/dashboard"]
for d in subdirs:
    exists = os.path.exists(d)
    has_init = os.path.exists(os.path.join(d, "__init__.py"))
    print(f"   - {d}: Exists={exists}, Has __init__.py={has_init}")

print("\n5. Attempting Import:")
try:
    from src.data.alpaca_interface import AlpacaInterface
    print("   ✅ SUCCESS: imported src.data.alpaca_interface")
except Exception as e:
    print(f"   ❌ FAILED: {e}")

print("="*50)
