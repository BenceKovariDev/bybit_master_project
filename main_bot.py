# bybit_master_project/main_bot.py
import time
import os
from config import TradingConfig
from api_client import fetch_top_market_data
# Importáljuk az adatbázis funkcióit
import database

def process_market_data(raw_tickers):
    """Feldolgozza és megszűri a Bybitről kapott nyers adatokat"""
    valid_coins = []
    for ticker in raw_tickers:
        symbol = ticker.get("symbol", "")
        if symbol.endswith("USDT") and symbol != "USDCUSDT":
            valid_coins.append({
                "symbol": symbol,
                "turnover": float(ticker.get("turnover24h", 0)),
                "price": float(ticker.get("lastPrice", 0)),
                "change_24h": float(ticker.get("price24hPcnt", 0)) * 100
            })
    valid_coins.sort(key=lambda x: x["turnover"], reverse=True)
    return valid_coins[:50]

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def render_dashboard(loop_count, current_market, my_positions, trade_log):
    """Kizárólag a terminálos felület megjelenítéséért felel"""
    clear_screen()
    market_dict = {coin["symbol"]: coin for coin in current_market}
    
    print("=" * 70)
    print(f" BYBIT MASTER BOT | LÉPÉSRŐL LÉPÉSRE TANNYAG | Frissítés #{loop_count}")
    print(f" Idő: {time.strftime('%Y-%m-%d %H:%M:%S')} | Kilépés: Ctrl+C")
    print("=" * 70)
    
    print(f"\n[1] AKTÍV POZÍCIÓK (Adatbázisból védve | SL: {TradingConfig.STOP_LOSS_PCT}%)")
    print("-" * 70)
    print(f"{'COIN':<12} | {'VÉTELI ÁR':<12} | {'AKTUÁLIS ÁR':<12} | {'PROFIT / LOSS'}")
    print("-" * 70)
    
    if not my_positions:
        print("   Nincsenek aktív pozíciók. Megfelelő belépő keresése...")
    else:
        for symbol, buy_price in my_positions.items():
            curr_price = market_dict[symbol]["price"] if symbol in market_dict else buy_price
            pl = ((curr_price - buy_price) / buy_price) * 100
            print(f"{symbol:<12} | {buy_price:<12.4f} | {curr_price:<12.4f} | {pl:+.2f}%")
            
    print("\n[2] PIACI MONITOR (Top 3 legnagyobb forgalmú coin)")
    print("-" * 70)
    for coin in current_market[:3]:
        print(f"-> {coin['symbol']:<10} | Ár: {coin['price']:<10.4f} | Változás: {coin['change_24h']:+.2f}%")
        
    print("\n[3] UTOLSÓ TRANZAKCIÓK (Élő Adatbázis Log)")
    print("-" * 70)
    if not trade_log:
        print("   Még nem történt tranzakció ebben a menetben.")
    else:
        for log in trade_log[-4:]:
            print(log)
    print("=" * 70)

def load_positions_from_db():
    """Betölti a korábban elmentett nyitott pozíciókat az adatbázisból"""
    positions = {}
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT symbol, buy_price FROM active_positions")
    rows = cursor.fetchall()
    for row in rows:
        positions[row["symbol"]] = row["buy_price"]
    conn.close()
    return positions

def start_bot():
    # 1. LÉPÉS: Inicializáljuk az adatbázis tábláit, ha még nem léteznek
    database.init_db()
    
    # 2. LÉPÉS: Betöltjük az elmentett pozíciókat (Így nem felejt a bot!)
    my_positions = load_positions_from_db()
    
    trade_log = []
    loop_count = 0

    while True:
        raw_data = fetch_top_market_data()
        if not raw_data:
            time.sleep(TradingConfig.REFRESH_RATE_SECONDS)
            continue
            
        loop_count += 1
        current_market = process_market_data(raw_data)
        market_dict = {coin["symbol"]: coin for coin in current_market}
        
        # --- 1. ELADÁSI (STOP-LOSS) LOGIKA ---
        for symbol in list(my_positions.keys()):
            if symbol in market_dict:
                buy_price = my_positions[symbol]
                current_price = market_dict[symbol]["price"]
                profit_loss_percent = ((current_price - buy_price) / buy_price) * 100
                
                if profit_loss_percent <= TradingConfig.STOP_LOSS_PCT:
                    log_msg = f"[{time.strftime('%H:%M:%S')}] !!! STOP-LOSS !!! Eladva: {symbol} ({profit_loss_percent:.2f}%)"
                    trade_log.append(log_msg)
                    
                    # ADATBÁZIS MŰVELETEK ELADÁSKOR: Törlés az aktívak közül, bejegyzés a történelembe
                    database.delete_position(symbol)
                    database.log_trade("STOP-LOSS", symbol, current_price, log_msg)
                    
                    del my_positions[symbol]
        
        # --- 2. VÉTELI LOGIKA ---
        for symbol, coin_info in market_dict.items():
            if coin_info["change_24h"] >= TradingConfig.BUY_TRIGGER_PCT and symbol not in my_positions:
                if len(my_positions) < TradingConfig.MAX_POSITIONS:
                    my_positions[symbol] = coin_info["price"]
                    log_msg = f"[{time.strftime('%H:%M:%S')}] *** VÉTEL *** {symbol} megvéve: {coin_info['price']:.4f}"
                    trade_log.append(log_msg)
                    
                    # ADATBÁZIS MŰVELETEK VÉTELKOR: Mentés az aktívak közé, bejegyzés a történelembe
                    database.save_position(symbol, coin_info["price"])
                    database.log_trade("VÉTEL", symbol, coin_info["price"], log_msg)
        
        # --- 3. MEGJELENÍTÉS ---
        render_dashboard(loop_count, current_market, my_positions, trade_log)
        time.sleep(TradingConfig.REFRESH_RATE_SECONDS)

if __name__ == "__main__":
    try:
        start_bot()
    except KeyboardInterrupt:
        print("\n\n[INFO] A tanuló robot sikeresen leállt. Az adatok az adatbázisban biztonságban vannak!")
