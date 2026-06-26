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
        # Csak a USDT párokat nézzük, de a stabil coint kiszűrjük
        if symbol.endswith("USDT") and symbol != "USDCUSDT":
            valid_coins.append({
                "symbol": symbol,
                "turnover": float(ticker.get("turnover24h", 0)),
                "price": float(ticker.get("lastPrice", 0)),
                "change_24h": float(ticker.get("price24hPcnt", 0)) * 100
            })
    # Forgalom szerint csökkenő sorrendbe rakjuk
    valid_coins.sort(key=lambda x: x["turnover"], reverse=True)
    return valid_coins[:50]

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def render_dashboard(loop_count, current_market, my_positions):
    """Kizárólag a terminálos felület megjelenítéséért felel"""
    clear_screen()
    print("=" * 70)
    print(f" BYBIT MASTER BOT | LÉPÉSRŐL LÉPÉSRE TANNYAG | Frissítés #{loop_count}")
    print(f" Idő: {time.strftime('%Y-%m-%d %H:%M:%S')} | Kilépés: Ctrl+C")
    print("=" * 70)
    
    print(f"\n[1] AKTÍV POZÍCIÓK (Stop-Loss: {TradingConfig.STOP_LOSS_PCT}%)")
    print("-" * 70)
    if not my_positions:
        print("   Nincsenek aktív pozíciók. Megfelelő belépő keresése...")
    else:
        for symbol, buy_price in my_positions.items():
            print(f"-> {symbol:<12} | Vétel: {buy_price:<10.4f}")
            
    print("\n[2] PIACI MONITOR (Top 3 legnagyobb forgalmú coin)")
    print("-" * 70)
    for coin in current_market[:3]:
        print(f"-> {coin['symbol']:<10} | Ár: {coin['price']:<10.4f} | Változás: {coin['change_24h']:+.2f}%")
    print("=" * 70)

def start_bot():
    my_positions = {}
    loop_count = 0

    while True:
        # Meghívjuk az api_client.py-ban megírt biztonságos függvényt
        raw_data = fetch_top_market_data()
        
        if not raw_data:
            time.sleep(TradingConfig.REFRESH_RATE_SECONDS)
            continue
            
        loop_count += 1
        current_market = process_market_data(raw_data)
        
        # TODO: A következő leckében ide építjük be a vételi/eladási logikát!
        
        render_dashboard(loop_count, current_market, my_positions)
        time.sleep(TradingConfig.REFRESH_RATE_SECONDS)

if __name__ == "__main__":
    try:
        start_bot()
    except KeyboardInterrupt:
        print("\n\n[INFO] A tanuló robot sikeresen leállt. Folytatjuk a jegyzetelést!")
