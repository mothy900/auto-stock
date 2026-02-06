import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from src.agent.executor import TradingExecutor
from src.data.collector import DataCollector

logger = logging.getLogger(__name__)

class AgentScheduler:
    def __init__(self, executor: TradingExecutor):
        self.executor = executor
        self.collector = DataCollector()
        self.scheduler = AsyncIOScheduler(timezone=timezone('US/Eastern'))
        
    def start(self):
        # 09:00 - Data Update & Init
        self.scheduler.add_job(
            self.daily_initialization,
            CronTrigger(hour=9, minute=0, day_of_week='mon-fri')
        )
        
        # 09:29 - Start Loop (slightly before open)
        self.scheduler.add_job(
            self.start_trading,
            CronTrigger(hour=9, minute=29, day_of_week='mon-fri')
        )
        
        # 15:55 - Time Cut (Liquidate)
        self.scheduler.add_job(
            self.liquidate_all,
            CronTrigger(hour=15, minute=55, day_of_week='mon-fri')
        )
        
        self.scheduler.start()
        logger.info("Agent Scheduler Started.")
        
        # Check if we missed the start (Late Start)
        self.scheduler.add_job(self.check_on_startup)

    async def check_on_startup(self):
        """Checks if the market is already open when the agent starts."""
        clock = self.executor.alpaca.get_market_status()
        if clock.is_open:
            logger.warning("Agent started during Market Hours! catching up...")
            await self.daily_initialization()
            await self.start_trading()
        else:
            logger.info(f"Market is Closed. Next Open: {clock.next_open}")

    async def daily_initialization(self):
        logger.info("Running Daily Initialization...")
        # 1. Collect last day's data to ensure we are up to date
        self.collector.collect_historical_data(self.executor.symbols, days=5)
        
        # 2. Initialize Strategy (Optimize K)
        await self.executor.initialize_day()

    async def start_trading(self):
        logger.info("Market Open Soon. Starting Trading Loop...")
        # Run the loop in a task
        asyncio.create_task(self.executor.run_loop())

    async def liquidate_all(self):
        logger.info("Market Closing Soon. Liquidating all positions...")
        self.executor.stop() # Stop buying
        
        # Sell everything
        for symbol in self.executor.symbols:
            try:
                pos = self.executor.alpaca.trading_client.get_open_position(symbol)
                qty = float(pos.qty)
                if qty > 0:
                    self.executor.alpaca.submit_order(symbol, qty, 'sell')
                    logger.info(f"Liquidated {symbol}: {qty}")
            except:
                pass # No position

if __name__ == "__main__":
    # Test Only
    logging.basicConfig(level=logging.INFO)
    
    # Mock Executor
    exec = TradingExecutor(["NVDA"])
    sched = AgentScheduler(exec)
    sched.start()
    
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
