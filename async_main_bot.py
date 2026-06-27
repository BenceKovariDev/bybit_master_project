# bybit_master_project/async_main_bot.py
import asyncio
import json
import time
import os
import websockets
from config import TradingConfig
import database

BYBIT_WS_URL = "wss://stream.bybit.com/v5/public/linear"

# Globális változók a memóriában
my_positions = {}
loop_count = 0
last_render_time = 0

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def render_async_dashboard(current_coin, current_price, current_change):
    """Villámgyorsan kirajzolja az aktuális állapotot a terminálra"""
    global loop_count
    clear_screen()
    
    print("=" * 70)
    print(f" 🔥 ASZINKRON WEBSOCKET ROBOT | Frissítés #{loop_count}")
    print(f" Idő: {time.strftime('%Y-%m-%d %H:%M:%S')} | Kilépés: Ctrl+C")
    print("=" * 70)
    
    print(f"\n[1] ÉLŐ PIACI MONITOR")
    print("-" * 70)
    print(f"-> {current_coin:<10} | Aktuális Ár: {current_price:<10.4f} | 24h Változás: {current_change:+.2f}%")
    
    print(f"\n[2] AKTÍV POZÍCIÓK (Adatbázisból menedzselve)")
    print("-" * 70)
    print(f"{'COIN':<12} | {'VÉTELI ÁR':<12} | {'PROFIT / LOSS'}")
    print("-" * 70)
    
    if not my_positions:
        print("   Nincsenek aktív pozíciók. Élő belépőre várás...")
    else:
        for symbol, buy_price in my_positions.items():
            # Mivel most csak BTC-t hallgatunk példaként
            if symbol == current_coin:
                pl = ((float(current_price) - buy_price) / buy_price) * 100
                print(f"{symbol:<12} | {buy_price:<12.4f} | {pl:+.2f}%")
            else:
                print(f"{symbol:<12} | {buy_price:<12.4f} | [Várakozás árfrissítésre...]")
    print("=" * 70)

async def handle_market_update(symbol, price, change_24h):
    """Itt fut le a kereskedési logika minden egyes beérkező árra, azonnal!"""
    global loop_count, last_render_time
    loop_count += 1
    
    # --- 1. ELADÁSI (STOP-LOSS) LOGIKA ---
    if symbol in my_positions:
        buy_price = my_positions[symbol]
        profit_loss_percent = ((price - buy_price) / buy_price) * 100
        
        if profit_loss_percent <= TradingConfig.STOP_LOSS_PCT:
            print(f"\n[!] !!! STOP-LOSS ELÉRVE !!! {symbol} eladva {price} áron ({profit_loss_percent:.2f}%)")
            database.delete_position(symbol)
            database.log_trade("STOP-LOSS", symbol, price, f"Aszinkron SL eladás: {profit_loss_percent:.2f}%")
            del my_positions[symbol]
            
    # --- 2. VÉTELI LOGIKA ---
    elif change_24h >= TradingConfig.BUY_TRIGGER_PCT:
        if len(my_positions) < TradingConfig.MAX_POSITIONS:
            my_positions[symbol] = price
            print(f"\n[*] *** ASZINKRON VÉTEL *** {symbol} megvéve {price} áron!")
            database.save_position(symbol, price)
            database.log_trade("VÉTEL", symbol, price, "Aszinkron WebSocket vétel")

    # --- 3. MEGJELENÍTÉS LIMITÁLÁSA (hogy ne villogjon másodpercenként 10-szer a kijelző)
    current_time = time.time()
    if current_time - last_render_time >= 0.5:
        render_async_dashboard(symbol, price, change_24h)
        last_render_time = current_time

async def start_async_bot():
    """Elindítja az aszinkron kapcsolatot és az adatbázis-betöltést"""
    global my_positions
    print("[INFO] Adatbázis inicializálása...")
    database.init_db()
    
    print("[INFO] Korábbi pozíciók betöltése az adatbázisból...")
    # Betöltjük a meglévő pozíciókat a memóriába
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT symbol, buy_price FROM active_positions")
    for row in cursor.fetchall():
        my_positions[row["symbol"]] = row["buy_price"]
    conn.close()

    print(f"[INFO] Csatlakozás a WebSocket-hez: {BYBIT_WS_URL}")
    async with websockets.connect(BYBIT_WS_URL) as ws:
        # Feliratkozunk a BTCUSDT-re
        subscribe_message = {
            "op": "subscribe",
            "args": ["tickers.BTCUSDT"]
        }
        await ws.send(json.dumps(subscribe_message))
        print("[INFO] Feliratkozva a BTCUSDT élő adatfolyamra!")
        
        while True:
            response = await ws.recv()
            data = json.loads(response)
            
            if "data" in data:
                ticker_data = data["data"]
                if "lastPrice" in ticker_data and "price24hPcnt" in ticker_data:
                    current_price = float(ticker_data["lastPrice"])
                    # A Bybit tizedes törtként adja meg a százalékot (pl. 0.02 = 2%), szorozzuk meg 100-zal
                    change_24h = float(ticker_data["price24hPcnt"]) * 100
                    
                    # Átadjuk az adatot a logikának feldolgozásra
                    await handle_market_update("BTCUSDT", current_price, change_24h)

if __name__ == "__main__":
    try:
        asyncio.run(start_async_bot())
    except KeyboardInterrupt:
        print("\n[INFO] Az Aszinkron Robot biztonságosan leállt.")
