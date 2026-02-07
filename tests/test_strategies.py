import unittest
import pandas as pd
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.strategy.bollinger_reversion import BollingerReversionStrategy
from src.strategy.rsi_momentum import RSIMomentumStrategy

class TestStrategies(unittest.TestCase):
    def setUp(self):
        # Create mock OHLCV data for 30 days
        dates = pd.date_range(start='2024-01-01', periods=30)
        self.mock_data = pd.DataFrame({
            'open': [100] * 30,
            'high': [105] * 30,
            'low': [95] * 30,
            'close': [100] * 30
        }, index=dates)
        
        # Make the last day have specific close for SMA calculation
        # SMA 20 of 100 is 100.
        # Std Dev of constant 100 is 0. 
        # Let's add some volatility
        import numpy as np
        np.random.seed(42)
        random_prices = np.random.normal(100, 2, 30)
        self.mock_data['close'] = random_prices
        
    def test_bollinger_reversion(self):
        strat = BollingerReversionStrategy("TEST", period=20, std_dev=2.0)
        strat.on_market_open(self.mock_data)
        
        self.assertIsNotNone(strat.upper_band)
        self.assertIsNotNone(strat.lower_band)
        
        # Helper to print calculated bands
        print(f"SMA: {strat.sma}, Upper: {strat.upper_band}, Lower: {strat.lower_band}")
        
        # Test BUY (Price < Lower Band)
        signal = strat.generate_signal(strat.lower_band - 1.0, current_position=0)
        self.assertIsNotNone(signal)
        self.assertEqual(signal['action'], 'BUY')
        
        # Test SELL (Price > Upper Band)
        signal = strat.generate_signal(strat.upper_band + 1.0, current_position=1, avg_entry_price=100)
        self.assertIsNotNone(signal)
        self.assertEqual(signal['action'], 'SELL')
        
        # Test NO ACTION (Middle)
        signal = strat.generate_signal(strat.sma, current_position=0)
        self.assertIsNone(signal)

    def test_rsi_momentum(self):
        strat = RSIMomentumStrategy("TEST", sma_period=20)
        strat.on_market_open(self.mock_data)
        
        self.assertIsNotNone(strat.daily_sma)
        
        # Test BUY: Price > SMA (Uptrend) AND RSI < 50
        price_uptrend = strat.daily_sma + 5.0
        rsi_dip = 45.0
        
        signal = strat.generate_signal(price_uptrend, current_position=0, current_rsi=rsi_dip)
        self.assertIsNotNone(signal)
        self.assertEqual(signal['action'], 'BUY')
        
        # Test NO BUY: Price < SMA (Downtrend)
        price_downtrend = strat.daily_sma - 5.0
        signal = strat.generate_signal(price_downtrend, current_position=0, current_rsi=rsi_dip)
        self.assertIsNone(signal)
        
        # Test SELL: RSI > 70
        signal = strat.generate_signal(price_uptrend, current_position=1, avg_entry_price=100, current_rsi=75)
        self.assertIsNotNone(signal)
        self.assertEqual(signal['action'], 'SELL')

if __name__ == '__main__':
    unittest.main()
