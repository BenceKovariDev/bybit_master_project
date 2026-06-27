# bybit_master_project/async_main_bot.py
import asyncio
import json
import time
import os
import websockets
from config import TradingConfig
import database
import api_client
import indicators  # ÚJ: Importáljuk a matematikai modult

BYBIT_WS_URL = "wss://stream.bybit.com/v5/public/linear"

my_positions = {}
market_state = {}  
price_history = {}  # ÚJ: Itt gyűjtjük a coinok ártörténetét az RSI számításhoz (pl. {"BTCUSDT": [60100, 60105...]})
loop_count = 0
last_render_time = 0

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def render_async_dashboard():
    global loop_count
    clear_screen()
    
    print("=" * 70)
    print(f" 📊 RSI-SZŰRT ASZINKRON ROBOT | Frissítés #{loop_count}")
    print(f" Idő: {time.strftime('%Y-%m-%d %H:%M:%S')} | Kilépés: Ctrl+C")
    print("=" * 70)
    
    print(f"\n[1] ÉLŐ PIACI MONITOR & INDIKÁTOROK")
    print("-" * 70)
    print(f"{'COIN':<10} | {'ÁR':<12} | {'24H VÁLTOZÁS':<12} | {'ÉLŐ RSI (14)'}")
    print("-" * 70)
    for symbol in TradingConfig.WATCH_LIST:
        if symbol in market_state:
            coin = market_state[symbol]
            rsi_val = coin['rsi'] if coin['rsi'] is not None else "Gyűjtés..."
            print(f"{symbol:<10} | {coin['price']:<12.4f} | {coin['change']:+11.2f}% | {rsi_val}")
        else:
            print(f"{symbol:<10} | [Kapcsolódás...]")
    
    print(f"\n[2] AKTÍV POZÍCIÓK")
    print("-" * 70)
    print(f"{'COIN':<12} | {'VÉTELI ÁR':<12} | {'PROFIT / LOSS'}")
    print("-" * 70)
    
    if not my_positions:
        print("   Nincsenek aktív pozíciók. Stratégia figyelése...")
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
    global loop_count, last_render_time
    loop_count += 1
    
    # 1. Ártörténet frissítése az RSI-hez
    if symbol not in price_history:
        price_history[symbol] = []
    
    price_history[symbol].append(price)
    
    # Nem kell végtelen sok árat tárolni, maximum 30 elég a memóriában
    if len(price_history[symbol]) > 30:
        price_history[symbol].pop(0)
        
    # 2. RSI kiszámítása az utolsó árakból
    rsi = indicators.calculate_rsi(price_history[symbol], period=14)
    
    # Elmentjük az állapotot az új RSI értékkel együtt
    market_state[symbol] = {"price": price, "change": change_24h, "rsi": rsi}
    
    # --- 3. ELADÁSI LOGIKA (STOP-LOSS) ---
    if symbol in my_positions:
        buy_price = my_positions[symbol]
        profit_loss_percent = ((price - buy_price) / buy_price) * 100
        
        if profit_loss_percent <= TradingConfig.STOP_LOSS_PCT:
            api_client.place_order(symbol, "Sell", qty=1)
            database.delete_position(symbol)
            database.log_trade("STOP-LOSS", symbol, price, f"RSI Bot SL: {profit_loss_percent:.2f}%")
            del my_positions[symbol]
            
    # --- 4. OKOSABB VÉTELI LOGIKA (Árfolyam + RSI szűrő!) ---
    elif change_24h >= TradingConfig.BUY_TRIGGER_PCT:
        # CSAK AKKOR VESZÜNK, ha az RSI már ki van számolva ÉS 70 alatt van (nincs túlvéve)
        if rsi is not None and rsi < 70.0:
            if len(my_positions) < TradingConfig.MAX_POSITIONS:
                api_client.place_order(symbol, "Buy", qty=1)
                my_positions[symbol] = price
                database.save_position(symbol, price)
                database.log_trade("VÉTEL", symbol, price, f"Okos Vétel | RSI: {rsi}")

    # Megjelenítés limitálása
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
        print("\n[INFO] Az RSI Robot leállt.")
