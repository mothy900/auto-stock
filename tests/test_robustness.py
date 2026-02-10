import asyncio
import logging
from unittest.mock import MagicMock, patch
from src.agent.executor import TradingExecutor

# Setup logging to see what's happening
logging.basicConfig(level=logging.INFO)

async def test_error_handling():
    print("\n--- Testing Robot Robustness (Error Handling) ---")
    
    # Setup mock executor
    symbols = ["NVDA"]
    executor = TradingExecutor(symbols, investment_per_symbol=1000)
    
    # 1. Mock AlpacaInterface.get_open_position to RAISE AN EXCEPTION (Simulation of API Error)
    executor.alpaca.get_open_position = MagicMock(side_effect=Exception("Alpaca API Timeout/Error!"))
    executor.alpaca.get_latest_price = MagicMock(return_value=1.0)
    
    # 2. Mock submit_order to verify it's NOT called
    executor.alpaca.submit_order = MagicMock()
    
    print("Testing Loop with API Exception...")
    # Run one tick of the loop manually (we need to stop the loop)
    executor.running = True
    
    # We'll use a timeout to stop the loop since run_loop is 'while True'
    try:
        await asyncio.wait_for(executor.run_loop(), timeout=3)
    except asyncio.TimeoutError:
        print("Loop timed out as expected (it's a continuous loop).")
    except Exception as e:
        print(f"Loop crashed unexpectedly: {e}")

    # 3. VERIFICATION
    # If the fix works, 'Skipping NVDA due to position fetch error' should have been logged,
    # and submit_order should NOT have been called because we 'continued' the loop.
    if executor.alpaca.submit_order.called:
        print("❌ FAILED: submit_order was called even though API error occurred!")
    else:
        print("✅ PASSED: submit_order was NOT called during API fetch error.")

if __name__ == "__main__":
    asyncio.run(test_error_handling())
