# bybit_master_project/async_main_bot.py
import asyncio
import json
import time
import os
import websockets
from config import TradingConfig
import database
import api_client
import indicators

BYBIT_WS_URL = "wss://stream.bybit.com/v5/public/linear"

my_positions = {}  # Új struktúra: {"BTCUSDT": {"buy_price": 60000, "current_sl_pct": -1.0, "trailing_activated": False}}
market_state = {}  
price_history = {}  
loop_count = 0
last_render_time = 0

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def render_async_dashboard():
    global loop_count
    clear_screen()
    
    print("=" * 75)
    print(f" 🛡️ DINAMIKUS RISK-MANAGED ROBOT | Frissítés #{loop_count}")
    print(f" Idő: {time.strftime('%Y-%m-%d %H:%M:%S')} | Kilépés: Ctrl+C")
    print("=" * 75)
    
    print(f"\n[1] ÉLŐ PIACI MONITOR & INDIKÁTOROK")
    print("-" * 75)
    print(f"{'COIN':<10} | {'ÁR':<12} | {'24H VÁLTOZÁS':<12} | {'ÉLŐ RSI (14)'}")
    print("-" * 75)
    for symbol in TradingConfig.WATCH_LIST:
        if symbol in market_state:
            coin = market_state[symbol]
            rsi_val = coin['rsi'] if coin['rsi'] is not None else "Gyűjtés..."
            print(f"{symbol:<10} | {coin['price']:<12.4f} | {coin['change']:+11.2f}% | {rsi_val}")
        else:
            print(f"{symbol:<10} | [Kapcsolódás...]")
    
    print(f"\n[2] AKTÍV POZÍCIÓK (Dinamikus Trailing Stop & TP)")
    print("-" * 75)
    print(f"{'COIN':<10} | {'VÉTELI ÁR':<12} | {'AKTUÁLIS SL':<12} | {'PROFIT / LOSS'}")
    print("-" * 75)
    
    if not my_positions:
        print("   Nincsenek aktív pozíciók. Stratégia figyelése...")
    else:
        for symbol, pos_data in my_positions.items():
            if symbol in market_state:
                curr_price = market_state[symbol]['price']
                buy_price = pos_data["buy_price"]
                pl = ((curr_price - buy_price) / buy_price) * 100
                
                # Kiírjuk, ha a Trailing Stop már be van élesítve
                sl_text = f"{pos_data['current_sl_pct']:+.1f}% (BE)" if pos_data['trailing_activated'] else f"{pos_data['current_sl_pct']:+.1f}%"
                print(f"{symbol:<10} | {buy_price:<12.4f} | {sl_text:<12} | {pl:+.2f}%")
            else:
                print(f"{symbol:<10} | {pos_data['buy_price']:<12.4f} | [Árra vár...]")
    print("=" * 75)

async def handle_market_update(symbol, price, change_24h):
    global loop_count, last_render_time
    loop_count += 1
    
    if symbol not in price_history:
        price_history[symbol] = []
    price_history[symbol].append(price)
    if len(price_history[symbol]) > 30:
        price_history[symbol].pop(0)
        
    rsi = indicators.calculate_rsi(price_history[symbol], period=14)
    market_state[symbol] = {"price": price, "change": change_24h, "rsi": rsi}
    
    # --- MENEDZSELÉSI LOGIKA (HA VAN NYITOTT POZÍCIÓ) ---
    if symbol in my_positions:
        pos = my_positions[symbol]
        profit_loss_percent = ((price - pos["buy_price"]) / pos["buy_price"]) * 100
        
        # 1. FIX TAKE-PROFIT ELÉRVE?
        if profit_loss_percent >= TradingConfig.TAKE_PROFIT_PCT:
            api_client.place_order(symbol, "Sell", qty=1)
            database.delete_position(symbol)
            database.log_trade("TAKE-PROFIT", symbol, price, f"Fix TP zárás: {profit_loss_percent:.2f}%")
            del my_positions[symbol]
            return

        # 2. TRAILING STOP AKTIVÁLÁSA (Breakeven-be húzás)
        if profit_loss_percent >= TradingConfig.TRAILING_TRIGGER_PCT and not pos["trailing_activated"]:
            pos["current_sl_pct"] = 0.0  # Felhúzzuk a Stop-Losst a nullára!
            pos["trailing_activated"] = True
            database.log_trade("TRAILING_ACTIVATE", symbol, price, "Stop-Loss nullába húzva (Breakeven)")

        # 3. STOP-LOSS KIVÁLTÁS (Akár a kezdő -1%, akár a felhúzott 0%)
        if profit_loss_percent <= pos["current_sl_pct"]:
            api_client.place_order(symbol, "Sell", qty=1)
            database.delete_position(symbol)
            trade_type = "TRAILING-STOP" if pos["trailing_activated"] else "STOP-LOSS"
            database.log_trade(trade_type, symbol, price, f"Zárás {profit_loss_percent:.2f}%-nál")
            del my_positions[symbol]
            return
            
    # --- VÉTELI LOGIKA ---
    elif change_24h >= TradingConfig.BUY_TRIGGER_PCT:
        if rsi is not None and rsi < 70.0:
            if len(my_positions) < TradingConfig.MAX_POSITIONS:
                api_client.place_order(symbol, "Buy", qty=1)
                
                # ÚJ: Struktúráltan mentjük el a kezdeti kockázati szinteket
                my_positions[symbol] = {
                    "buy_price": price,
                    "current_sl_pct": TradingConfig.INITIAL_STOP_LOSS_PCT,
                    "trailing_activated": False
                }
                database.save_position(symbol, price)
                database.log_trade("VÉTEL", symbol, price, f"Risk-Managed Vétel | RSI: {rsi}")

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
        # Adatbázisból való betöltéskor alapbeállításokkal indítunk
        my_positions[row["symbol"]] = {
            "buy_price": row["buy_price"],
            "current_sl_pct": TradingConfig.INITIAL_STOP_LOSS_PCT,
            "trailing_activated": False
        }
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
        print("\n[INFO] A Kockázatkezelő Robot leállt.")
