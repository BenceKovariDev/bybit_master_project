# bybit_master_project/adatbazis.py
import sqlite3
import os

DB_NAME = "bybit_bot.db"

def inicializal_adatbazis():
    """Létrehozza az adatbázist és a szükséges táblákat, ha még nem léteznek."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tábla a megnyitott és lezárt pozícióknak
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS poziciok (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT UNIQUE,
            szimbólum TEXT,
            irany TEXT,
            mennyiseg REAL,
            nyito_ar REAL,
            zaro_ar REAL,
            pnl REAL,
            statusz TEXT, -- 'OPEN' vagy 'CLOSED'
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tábla a bot napi/ciklus szintű naplózásához (statisztika)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bot_logok (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ciklus_szam INTEGER,
            uzenet TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print("✨ SQLite Adatbázis és a táblák sikeresen inicializálva!")

def pozicio_mentes(order_id, szimbólum, irany, mennyiseg, nyito_ar):
    """Elment egy újonnan megnyitott pozíciót."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO poziciok (order_id, szimbólum, irany, mennyiseg, nyito_ar, statusz)
            VALUES (?, ?, ?, ?, ?, 'OPEN')
        """, (order_id, szimbólum, irany, mennyiseg, nyito_ar))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ Hiba a pozíció mentésekor: {e}")

def log_mentes(ciklus_szam, uzenet):
    """Elment egy eseményt a bot naplójába."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO bot_logok (ciklus_szam, uzenet) VALUES (?, ?)", (ciklus_szam, uzenet))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ Hiba a log mentésekor: {e}")

# Automatikusan lefuttatjuk az inicializálást, ha a modult importálják
inicializal_adatbazis()
