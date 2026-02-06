import sqlite3
import os
import logging
from typing import Optional, List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "data/antigravity.db"):
        self.db_path = db_path
        self.ensure_db_directory()
        self.conn = None
        self.cursor = None

    def ensure_db_directory(self):
        """Ensure the directory for the database exists."""
        directory = os.path.dirname(self.db_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

    def connect(self):
        """Connect to the SQLite database and enable WAL mode."""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row  # Access columns by name
            self.cursor = self.conn.cursor()
            
            # Performance Optimizations (WAL Mode)
            self.conn.execute("PRAGMA journal_mode = WAL;")
            self.conn.execute("PRAGMA synchronous = NORMAL;")
            self.conn.execute("PRAGMA temp_store = MEMORY;")
            self.conn.execute("PRAGMA cache_size = -64000;") # ~64MB
            self.conn.execute("PRAGMA mmap_size = 30000000000;")
            
            logger.info(f"Connected to database at {self.db_path} with WAL mode enabled.")
            
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {e}")
            raise

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed.")

    def create_tables(self):
        """Create necessary tables if they don't exist."""
        if not self.conn:
            self.connect()

        try:
            # 1. OHLCV Data Table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS ohlcv_data (
                    symbol TEXT,
                    timestamp DATETIME,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    PRIMARY KEY (symbol, timestamp)
                );
            """)

            # 2. Trade Logs Table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS trade_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    symbol TEXT,
                    side TEXT, -- 'BUY' or 'SELL'
                    quantity INTEGER,
                    price REAL,
                    reason TEXT, -- e.g., 'Strategy', 'Stop_Loss', 'Time_Cut'
                    order_id TEXT
                );
            """)

            # 3. Strategy Parameters Table (Dynamic K)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS strategy_params (
                    date DATE,
                    symbol TEXT,
                    k_value REAL,
                    target_price REAL,
                    PRIMARY KEY (date, symbol)
                );
            """)
            
            self.conn.commit()
            logger.info("Tables created successfully.")
            
        except sqlite3.Error as e:
            logger.error(f"Error creating tables: {e}")
            self.conn.rollback()

    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Execute a read query."""
        if not self.conn:
            self.connect()
        try:
            cur = self.conn.execute(query, params)
            return cur.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Query failed: {e}")
            return []

    def execute_update(self, query: str, params: tuple = ()):
        """Execute a write query (INSERT, UPDATE, DELETE)."""
        if not self.conn:
            self.connect()
        try:
            self.conn.execute(query, params)
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Update failed: {e}")
            self.conn.rollback()
            raise

    def log_trade(self, symbol: str, side: str, qty: float, price: float, reason: str, order_id: str = None):
        """Log a trade execution."""
        query = """
            INSERT INTO trade_logs (symbol, side, quantity, price, reason, order_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        self.execute_update(query, (symbol, side, qty, price, reason, order_id))
        logger.debug(f"Logged trade: {side} {qty} {symbol} @ {price}")

if __name__ == "__main__":
    # Test initialization
    db = DatabaseManager()
    db.create_tables()
    db.close()
