# bybit_master_project/tests/test_logic.py
import sys
import os
import unittest

# Ez a két sor azért kell, hogy a háttérben elérjük a felette lévő mappában lévő fájlokat
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main_bot import process_market_data

class TestTradingLogic(unittest.TestCase):

    def test_process_market_data_filtering(self):
        """Teszteljük, hogy a robot jól szűri-e a piaci adatokat"""
        
        # 1. Összerakunk egy "kamu" tőzsdei adatot (Mock data)
        dummy_raw_data = [
            {"symbol": "BTCUSDT", "turnover24h": "1000", "lastPrice": "60000", "price24hPcnt": "0.01"},
            {"symbol": "ETHBTC", "turnover24h": "500", "lastPrice": "0.05", "price24hPcnt": "0.02"}, # Ezt ki kell szűrnie (nem USDT)
            {"symbol": "USDCUSDT", "turnover24h": "2000", "lastPrice": "1.00", "price24hPcnt": "0.00"}, # Ezt is ki kell szűrnie
            {"symbol": "SOLUSDT", "turnover24h": "5000", "lastPrice": "150", "price24hPcnt": "0.05"}  # Ennek kell az első helyre kerülnie a nagy forgalom miatt
        ]
        
        # 2. Lefuttatjuk rajta a függvényünket
        processed = process_market_data(dummy_raw_data)
        
        # 3. Ellenőrzések (Assertions)
        # Csak a BTCUSDT és SOLUSDT maradhatott meg (hossz = 2)
        self.assertEqual(len(processed), 2)
        
        # A SOLUSDT forgalma nagyobb (5000 > 1000), így annak kell az első helyen lennie
        self.assertEqual(processed[0]["symbol"], "SOLUSDT")
        self.assertEqual(processed[1]["symbol"], "BTCUSDT")

if __name__ == "__main__":
    unittest.main()
