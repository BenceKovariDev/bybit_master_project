# bybit_master_project/tests/test_database.py
import sys
import os
import unittest
import sqlite3

# Beállítjuk az elérési utat, hogy lássa a főmappát
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database

class TestDatabaseIntegration(unittest.TestCase):

    def setUp(self):
        """Minden egyes teszt előtt lefut: átállítjuk a botot egy ideiglenes teszt adatbázisra"""
        database.DB_NAME = "test_trading_bot.db"
        database.init_db()

    def tearDown(self):
        """Minden egyes teszt után lefut: letakarítja a tesztfájlt, hogy ne szemeteljen"""
        if os.path.exists("test_trading_bot.db"):
            os.remove("test_trading_bot.db")

    def test_save_and_load_position(self):
        """Ellenőrzi, hogy a pozíció elmentése és beolvasása sikeres-e"""
        # 1. Elmentünk egy teszt pozíciót
        database.save_position("BTCUSDT", 60000.0)
        
        # 2. Manuálisan ellenőrizzük, hogy benne van-e az adatbázisban
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT buy_price FROM active_positions WHERE symbol = 'BTCUSDT'")
        row = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(row)
        self.assertEqual(row["buy_price"], 60000.0)

    def test_delete_position(self):
        """Ellenőrzi, hogy eladáskor a pozíció törlődik-e az aktívak közül"""
        # Elmentjük, majd töröljük
        database.save_position("ETHUSDT", 1600.0)
        database.delete_position("ETHUSDT")
        
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM active_positions WHERE symbol = 'ETHUSDT'")
        row = cursor.fetchone()
        conn.close()
        
        self.assertIsNone(row)

if __name__ == "__main__":
    unittest.main()
