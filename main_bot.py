# bybit_master_project/main_bot.py
import time
import os
from config import TradingConfig
from api_client import fetch_top_market_data

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
    
    print(f"\n[1] AKTÍV POZÍCIÓK (Stop-Loss védelmi vonal: {TradingConfig.STOP_LOSS_PCT}%)")
    print("-" * 70)
    print(f"{'COIN':<12} | {'VÉTELI ÁR':<12} | {'AKTUÁLIS ÁR':<12} | {'PROFIT / LOSS'}")
    print("-" * 70)
    
    if not my_positions:
        print("   Nincsenek aktív pozíciók. Megfelelő belépő keresése...")
    else:
        for symbol, buy_price in my_positions.items():
            # Megkeressük az aktuális árat a piacból
            curr_price = market_dict[symbol]["price"] if symbol in market_dict else buy_price
            pl = ((curr_price - buy_price) / buy_price) * 100
            print(f"{symbol:<12} | {buy_price:<12.4f} | {curr_price:<12.4f} | {pl:+.2f}%")
            
    print("\n[2] PIACI MONITOR (Top 3 legnagyobb forgalmú coin)")
    print("-" * 70)
    for coin in current_market[:3]:
        print(f"-> {coin['symbol']:<10} | Ár: {coin['price']:<10.4f} | Változás: {coin['change_24h']:+.2f}%")
        
    print("\n[3] UTOLSÓ TRANZAKCIÓK (Trade Log)")
    print("-" * 70)
    if not trade_log:
        print("   Még nem történt tranzakció.")
    else:
        for log in trade_log[-4:]: # Csak az utolsó 4 eseményt mutatjuk
            print(log)
    print("=" * 70)

def start_bot():
    my_positions = {}
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
                
                # Ha eléri vagy átlépi a stop-loss limitet (-1%)
                if profit_loss_percent <= TradingConfig.STOP_LOSS_PCT:
                    trade_log.append(f"[{time.strftime('%H:%M:%S')}] !!! STOP-LOSS !!! Eladva: {symbol} ({profit_loss_percent:.2f}%)")
                    del my_positions[symbol]
        
        # --- 2. VÉTELI LOGIKA ---
        for symbol, coin_info in market_dict.items():
            # Ha emelkedik a trigger szint felett (+2%) és még nincs benne pozíciónk
            if coin_info["change_24h"] >= TradingConfig.BUY_TRIGGER_PCT and symbol not in my_positions:
                # És van még hely a maximális pozícióknak (max 3)
                if len(my_positions) < TradingConfig.MAX_POSITIONS:
                    my_positions[symbol] = coin_info["price"]
                    trade_log.append(f"[{time.strftime('%H:%M:%S')}] *** VÉTEL *** {symbol} megvéve: {coin_info['price']:.4f}")
        
        # --- 3. MEGJELENÍTÉS ---
        render_dashboard(loop_count, current_market, my_positions, trade_log)
        time.sleep(TradingConfig.REFRESH_RATE_SECONDS)

if __name__ == "__main__":
    try:
        start_bot()
    except KeyboardInterrupt:
        print("\n\n[INFO] A tanuló robot sikeresen leállt. Folytatjuk a jegyzetelést!")
