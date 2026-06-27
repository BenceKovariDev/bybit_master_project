# bybit_master_project/async_main_bot.py
import asyncio
import json
import time
import os
import websockets
from config import TradingConfig
import database
import api_client  # ÚJ: Importáljuk az API klienst a parancsküldéshez

BYBIT_WS_URL = "wss://stream.bybit.com/v5/public/linear"

my_positions = {}
market_state = {}  
loop_count = 0
last_render_time = 0

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def render_async_dashboard():
    global loop_count
    clear_screen()
    
    print("=" * 70)
    print(f" 🔥 ASZINKRON API-KAPCSOLT ROBOT | Frissítés #{loop_count}")
    print(f" Idő: {time.strftime('%Y-%m-%d %H:%M:%S')} | Kilépés: Ctrl+C")
    print("=" * 70)
    
    print(f"\n[1] ÉLŐ PIACI MONITOR (Figyelt coinok)")
    print("-" * 70)
    for symbol in TradingConfig.WATCH_LIST:
        if symbol in market_state:
            coin = market_state[symbol]
            print(f"-> {symbol:<10} | Ár: {coin['price']:<10.4f} | 24h Változás: {coin['change']:+.2f}%")
        else:
            print(f"-> {symbol:<10} | [Kapcsolódás...]")
    
    print(f"\n[2] AKTÍV POZÍCIÓK (Élő API és Adatbázis szinkron)")
    print("-" * 70)
    print(f"{'COIN':<12} | {'VÉTELI ÁR':<12} | {'PROFIT / LOSS'}")
    print("-" * 70)
    
    if not my_positions:
        print("   Nincsenek aktív pozíciók. Élő belépőre várás...")
    else:
        for symbol, buy_price in my_positions.items():
            if symbol in market_state:
                curr_price = market_state[symbol]['price']
                pl = ((curr_price - buy_price) / buy_price) * 100
                print(f"{symbol:<12} | {buy_price:<12.4f} | {pl:+.2f}%")
            else:
                print(f"{symbol:<12} | {buy_price:<12.4f} | [Árra vár...]")
    print("=" * 70)

async def handle_market_update(symbol, price, change_24h):
    """Eseményvezérelt logika valós API parancsküldéssel"""
    global loop_count, last_render_time
    loop_count += 1
    
    market_state[symbol] = {"price": price, "change": change_24h}
    
    # --- 1. VALÓDI/SZIMULÁLT ELADÁSI LOGIKA (STOP-LOSS) ---
    if symbol in my_positions:
        buy_price = my_positions[symbol]
        profit_loss_percent = ((price - buy_price) / buy_price) * 100
        
        if profit_loss_percent <= TradingConfig.STOP_LOSS_PCT:
            # ÚJ: Parancsot küldünk a Bybitnek, hogy adjon el mindent (Sell) ebből a coinból
            # Példaként fix 1-es mennyiséggel tesztelünk
            api_client.place_order(symbol, "Sell", qty=1)
            
            database.delete_position(symbol)
            database.log_trade("STOP-LOSS", symbol, price, f"API SL Eladás: {profit_loss_percent:.2f}%")
            del my_positions[symbol]
            
    # --- 2. VALÓDI/SZIMULÁLT VÉTELI LOGIKA ---
    elif change_24h >= TradingConfig.BUY_TRIGGER_PCT:
        if len(my_positions) < TradingConfig.MAX_POSITIONS:
            # ÚJ: Parancsot küldünk a Bybitnek, hogy vegyen (Buy) ebből a coinból
            api_client.place_order(symbol, "Buy", qty=1)
            
            my_positions[symbol] = price
            database.save_position(symbol, price)
            database.log_trade("VÉTEL", symbol, price, "API WebSocket Vétel")

    current_time = time.time()
    if current_time - last_render_time >= 0.3:
        render_async_dashboard()
        last_render_time = current_time

async def start_async_bot():
    global my_positions
    database.init_db()
    
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT symbol, buy_price FROM active_positions")
    for row in cursor.fetchall():
        my_positions[row["symbol"]] = row["buy_price"]
    conn.close()

    async with websockets.connect(BYBIT_WS_URL) as ws:
        args_list = [f"tickers.{symbol}" for symbol in TradingConfig.WATCH_LIST]
        subscribe_message = {"op": "subscribe", "args": args_list}
        await ws.send(json.dumps(subscribe_message))
        
        while True:
            response = await ws.recv()
            data = json.loads(response)
            
            if "data" in data and "topic" in data:
                symbol = data["topic"].split(".")[-1]
                ticker_data = data["data"]
                
                if "lastPrice" in ticker_data and "price24hPcnt" in ticker_data:
                    current_price = float(ticker_data["lastPrice"])
                    change_24h = float(ticker_data["price24hPcnt"]) * 100
                    await handle_market_update(symbol, current_price, change_24h)

if __name__ == "__main__":
    try:
        asyncio.run(start_async_bot())
    except KeyboardInterrupt:
        print("\n[INFO] Az API-kapcsolt robot leállt.")
