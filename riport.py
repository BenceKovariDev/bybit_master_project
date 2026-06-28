# bybit_master_project/riport.py
import sqlite3

DB_NAME = "bybit_bot.db"

def statisztika_riport():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    print("=" * 70)
    print("📊 BYBIT MASTER BOT - ELO RENDSZER STATISZTIKA & MEMORIA")
    print("=" * 70)

    # 1. NYITOTT POZICIOK
    print("\n🟢 NYITOTT POZICIOK:")
    print(f"{'Erme':<12} | {'Irany':<6} | {'Mennyiseg':<10} | {'Nyito Ar':<10}")
    print("-" * 60)
    
    try:
        cursor.execute("SELECT order_id, szimbólum, irany, mennyiseg, nyito_ar FROM poziciok WHERE statusz = 'OPEN'")
        nyitottak = cursor.fetchall()
        if not nyitottak:
            print("Nincs jelenleg nyitott pozicio.")
        for poz in nyitottak:
            print(f"{poz[1]:<12} | {poz[2]:<6} | {poz[3]:<10} | {poz[4]:<10}")
    except sqlite3.OperationalError:
        print("A poziciok tabla meg nem jott letre.")

    # 2. LEZART POZICIOK ES PNL
    print("\n🔴 LEZART TRADEEK (HISTORIA):")
    print(f"{'Erme':<12} | {'Irany':<6} | {'Nyito':<8} | {'Zaro':<8} | {'PnL ($)':<8}")
    print("-" * 60)
    
    try:
        cursor.execute("SELECT szimbólum, irany, mennyiseg, nyito_ar, zaro_ar, pnl FROM poziciok WHERE statusz = 'CLOSED'")
        lezartak = cursor.fetchall()
        if not lezartak:
            print("Meg nem tortent poziciozaras.")
        for poz in lezartak:
            print(f"{poz[0]:<12} | {poz[1]:<6} | {poz[2]:<8} | {poz[3]:<8} | {poz[5]:+8.2f}$")
    except sqlite3.OperationalError:
        print("Meg nem tortent poziciozaras.")

    # 3. OSSZESITETT EREDMENYEK
    ossz_pnl, ossz_db = 0.0, 0
    try:
        cursor.execute("SELECT SUM(pnl), COUNT(id) FROM poziciok WHERE statusz = 'CLOSED'")
        sor = cursor.fetchone()
        if sor and sor[0] is not None:
            ossz_pnl = sor[0]
        if sor and sor[1] is not None:
            ossz_db = sor[1]
    except sqlite3.OperationalError:
        pass

    # 4. RENDSZERLOGOK BIZTONSAGI LEKERESE
    print("\n📝 UTOLSO 5 RENDSZERLOG:")
    print("-" * 60)
    try:
        cursor.execute("SELECT timestamp, uzenet FROM logok ORDER BY id DESC LIMIT 5")
        utolso_logok = cursor.fetchall()
        if not utolso_logok:
            print("A logok tabla meg ures.")
        for log in utolso_logok:
            print(f"[{log[0]}] {log[1]}")
    except sqlite3.OperationalError:
        print("A logok tabla meg ures vagy inicializalasra var.")

    print("=" * 70)
    print(f"💰 OSSZESITETT NETTO PROFIT: {ossz_pnl :+.2f}$ | Ossz trade: {ossz_db}")
    print("=" * 70)

    conn.close()

if __name__ == "__main__":
    statisztika_riport()
