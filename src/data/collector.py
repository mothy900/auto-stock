import logging
from datetime import datetime, timedelta
import pandas as pd
from typing import List
from src.data.alpaca_interface import AlpacaInterface
from src.data.database import DatabaseManager
from alpaca.data.timeframe import TimeFrame

logger = logging.getLogger(__name__)

class DataCollector:
    def __init__(self):
        self.alpaca = AlpacaInterface()
        self.db = DatabaseManager()
        self.db.create_tables()

    def collect_historical_data(self, symbols: List[str], days: int = 365):
        """
        Collects historical 1-minute bars for the given symbols and saves to DB.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        logger.info(f"Starting data collection for {symbols} from {start_date.date()} to {end_date.date()}")

        for symbol in symbols:
            try:
                logger.info(f"Fetching data for {symbol}...")
                df = self.alpaca.get_bars(
                    symbol=symbol,
                    start=start_date,
                    end=end_date,
                    timeframe=TimeFrame.Minute
                )
                
                if df is not None and not df.empty:
                    self.save_to_db(symbol, df)
                    logger.info(f"Successfully saved {len(df)} rows for {symbol}.")
                else:
                    logger.warning(f"No data found for {symbol}.")
                    
            except Exception as e:
                logger.error(f"Failed to collect data for {symbol}: {e}")

    def save_to_db(self, symbol: str, df: pd.DataFrame):
        """
        Saves the dataframe to SQLite ohlcv_data table.
        df index is expected to be timestamp, or multi-index (symbol, timestamp).
        """
        try:
            # Reset index to get timestamp as a column if it's in the index
            data = df.reset_index()
            
            # Alpaca get_bars returns MultiIndex (symbol, timestamp) usually
            if 'symbol' not in data.columns:
                data['symbol'] = symbol
                
            # Filter columns ensuring they exist
            required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            
            # Rename columns to lowercase if necessary (Alpaca returns lowercase usually, but good to be safe)
            data.columns = [c.lower() for c in data.columns]
            
            # Prepare list of tuples for insertion
            records = []
            for _, row in data.iterrows():
                records.append((
                    symbol,
                    row['timestamp'].to_pydatetime(), # Ensure python datetime
                    row['open'],
                    row['high'],
                    row['low'],
                    row['close'],
                    row['volume']
                ))

            # Upsert using REPLACE INTO or INSERT OR REPLACE
            if records:
                # We need to use the execute_update method carefully or raw connection
                # Since DatabaseManager.execute_update takes a query and params, we can do batch insert manually or loop
                # For performance, let's use executemany via the connection object directly exposed or add a method
                # Adding a batch insert method to DatabaseManager would be cleaner, but for now accessing conn is okay
                # or we loop (slower) or we use a big query.
                # Let's use a batch insert query
                
                query = """
                INSERT OR REPLACE INTO ohlcv_data (symbol, timestamp, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                
                if not self.db.conn:
                    self.db.connect()
                    
                self.db.conn.executemany(query, records)
                self.db.conn.commit()
                
        except Exception as e:
            logger.error(f"Error saving data to DB: {e}")
            raise

if __name__ == "__main__":
    # Test Run
    logging.basicConfig(level=logging.INFO)
    collector = DataCollector()
    collector.collect_historical_data(["AAPL"], days=1)
