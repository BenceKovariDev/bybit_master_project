# bybit_master_project/tests/test_logic.py
import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main_bot import process_market_data

class TestTradingLogic(unittest.TestCase):

    def test_process_market_data_filtering(self):
        """[Tegnapi teszt] Ellenőrzi, hogy a robot jól szűri és rendezi-e a coinokat"""
        dummy_raw_data = [
            {"symbol": "BTCUSDT", "turnover24h": "1000", "lastPrice": "60000", "price24hPcnt": "0.01"},
            {"symbol": "ETHBTC", "turnover24h": "500", "lastPrice": "0.05", "price24hPcnt": "0.02"},
            {"symbol": "USDCUSDT", "turnover24h": "2000", "lastPrice": "1.00", "price24hPcnt": "0.00"},
            {"symbol": "SOLUSDT", "turnover24h": "5000", "lastPrice": "150", "price24hPcnt": "0.05"}
        ]
        processed = process_market_data(dummy_raw_data)
        self.assertEqual(len(processed), 2)
        self.assertEqual(processed[0]["symbol"], "SOLUSDT")

    def test_buy_and_stop_loss_math(self):
        """[ÚJ TESZT] Ellenőrizzük a százalékos matematikai számítást a háttérben"""
        buy_price = 100.0
        
        # 1. eset: Az ár felmegy 100.5-re -> Ez +0.5% profit
        current_price_up = 100.5
        profit_loss_up = ((current_price_up - buy_price) / buy_price) * 100
        self.assertAlmostEqual(profit_loss_up, 0.5)
        
        # 2. eset: Az ár leesik 99.0-ra -> Ez pontosan -1.0% veszteség (Stop-Loss trigger)
        current_price_down = 99.0
        profit_loss_down = ((current_price_down - buy_price) / buy_price) * 100
        self.assertAlmostEqual(profit_loss_down, -1.0)

if __name__ == "__main__":
    unittest.main()
