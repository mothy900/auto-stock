
import asyncio
import logging
import os
from src.agent.executor import TradingExecutor
from src.agent.scheduler import AgentScheduler
from dotenv import load_dotenv

# Setup Logging
import sys

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler("agent.log", mode='a', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ],
    force=True
)
logger = logging.getLogger("Main")

async def main():
    load_dotenv()
    
    print("---------------------------------------------------")
    print("   Antigravity Agent - Autonomous Trading System")
    print("---------------------------------------------------")
    
    # Configuration
    SYMBOLS = ["NVDA", "TSLA", "AMD", "TQQQ", "SOXL"]
    INVESTMENT_PER_SYMBOL = 50000.0 # Paper money
    
    logger.info(f"Target Symbols: {SYMBOLS}")
    
    # Initialize Components
    executor = TradingExecutor(SYMBOLS, INVESTMENT_PER_SYMBOL)
    scheduler = AgentScheduler(executor)
    
    # Start Scheduler
    # AsyncIOScheduler needs a running loop, which asyncio.run() provides
    scheduler.start()
    
    logger.info("System Online. Waiting for scheduled events...")
    
    # Keep Alive
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down...")
        executor.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
