
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
    # Added from Volatility Report: INOD, PLTR, DUK, TIGR, PAYO, HROW, SGRY
    SYMBOLS = ["NVDA", "TSLA", "AMD", "TQQQ", "SOXL", "INOD", "PLTR", "DUK", "TIGR", "PAYO", "HROW", "SGRY"]
    # INVESTMENT_PER_SYMBOL is now calculated dynamically below
    
    logger.info(f"Target Symbols: {SYMBOLS}")
    
    # Initialize Components
    # 1. Calculate Dynamic Position Size based on Account Buying Power
    from src.data.alpaca_interface import AlpacaInterface
    temp_alpaca = AlpacaInterface()
    account = temp_alpaca.get_account_info()
    buying_power = float(account.buying_power)
    
    # Allocate 90% of buying power divided by number of symbols (safety buffer)
    # Note: For TQQQ/SOXL (3x ETFs), margin requirement is high, so safe buffer is needed.
    allocation_factor = 0.90 
    INVESTMENT_PER_SYMBOL = (buying_power * allocation_factor) / len(SYMBOLS)
    
    logger.info(f"💰 Total Buying Power: ${buying_power:,.2f}")
    logger.info(f"⚖️  Allocated per Symbol: ${INVESTMENT_PER_SYMBOL:,.2f} (Total {len(SYMBOLS)} symbols)")

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
