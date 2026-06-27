# bybit_master_project/tests/test_indicators.py
import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import indicators

class TestIndicators(unittest.TestCase):

    def test_rsi_insufficient_data(self):
        """Ha nincs elég adat, a függvénynek None-t kell visszaadnia"""
        short_prices = [100, 101, 102]
        rsi = indicators.calculate_rsi(short_prices, period=14)
        self.assertIsNone(rsi)

    def test_rsi_overbought(self):
        """Folyamatosan emelkedő áraknál az RSI-nek magasnak (70 felett) kell lennie"""
        # Generálunk 16 egymást követő emelkedő árat
        rising_prices = [100 + i for i in range(16)]
        rsi = indicators.calculate_rsi(rising_prices, period=14)
        self.assertIsNotNone(rsi)
        self.assertGreater(rsi, 70.0)

    def test_rsi_oversold(self):
        """Folyamatosan eső áraknál az RSI-nek alacsonynak (30 alatt) kell lennie"""
        # Generálunk 16 egymást követő eső árat
        falling_prices = [100 - i for i in range(16)]
        rsi = indicators.calculate_rsi(falling_prices, period=14)
        self.assertIsNotNone(rsi)
        self.assertLess(rsi, 30.0)

if __name__ == "__main__":
    unittest.main()
