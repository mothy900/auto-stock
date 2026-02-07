import sys
import os
# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import logging
from src.agent.executor import TradingExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IntegrationTest")

async def main():
    logger.info("Starting Integration Test (5 seconds)...")
    
    # Use a subset of symbols for testing
    symbols = ['NVDA', 'TSLA'] # Reduce load
    executor = TradingExecutor(symbols)
    
    # Start the loop in a task
    task = asyncio.create_task(executor.run_loop())
    
    # Wait for 5 seconds
    await asyncio.sleep(5)
    
    # Stop
    logger.info("Stopping Executor...")
    executor.stop()
    await task
    logger.info("Integration Test Complete.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
