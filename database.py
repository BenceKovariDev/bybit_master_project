# bybit_master_project/database.py
import sqlite3
import time

DB_NAME = "trading_bot.db"

def get_connection():
    """Létrehoz egy kapcsolatot az adatbázissal"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Létrehozza a szükséges táblákat, ha még nem léteznek"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Tábla az aktív pozícióknak
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS active_positions (
            symbol TEXT PRIMARY KEY,
            buy_price REAL NOT NULL,
            buy_time TEXT NOT NULL
        )
    """)
    
    # 2. Tábla a lezárt tranzakciók történelmének (Megtisztítva a hibás kommenttől!)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trade_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            type TEXT NOT NULL,
            symbol TEXT NOT NULL,
            price REAL NOT NULL,
            message TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()

def save_position(symbol, buy_price):
    """Elment egy új nyitott pozíciót az adatbázisba"""
    conn = get_connection()
    cursor = conn.cursor()
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    try:
        cursor.execute(
            "INSERT OR REPLACE INTO active_positions (symbol, buy_price, buy_time) VALUES (?, ?, ?)",
            (symbol, buy_price, timestamp)
        )
        conn.commit()
    finally:
        conn.close()

def delete_position(symbol):
    """Törli a pozíciót, ha eladtuk"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM active_positions WHERE symbol = ?", (symbol,))
        conn.commit()
    finally:
        conn.close()

def log_trade(trade_type, symbol, price, message):
    """Bejegyez egy tranzakciót a történelembe"""
    conn = get_connection()
    cursor = conn.cursor()
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    try:
        cursor.execute(
            "INSERT INTO trade_history (timestamp, type, symbol, price, message) VALUES (?, ?, ?, ?, ?)",
            (timestamp, trade_type, symbol, price, message)
        )
        conn.commit()
    finally:
        conn.close()
