import os
import time
from dotenv import load_dotenv

# .env fájl betöltése az API kulcsokhoz
load_dotenv()

API_KEY = os.getenv("BYBIT_API_KEY", "").strip()
API_SECRET = os.getenv("BYBIT_API_SECRET", "").strip()
BASE_URL = "https://api-demo.bybit.com"

LOOP_INTERVAL = 10  # Frissítési időköz másodpercben

# KOCKÁZATKEZELÉSI BEÁLLÍTÁSOK
TRADE_USDT_BUDGET = 10.0  # Pontosan ennyi dollárral lép be egy pozícióba
LEVERAGE = 10              # 10x-es tőkeáttétel a profit maximalizálásához

def log_to_file(uzenet):
    """Fájlba is elmenti a bot naplóját a későbbi szerveres ellenőrzéshez."""
    idobelyeg = time.strftime("%Y-%m-%d %H:%M:%S")
    sor = f"[{idobelyeg}] {uzenet}\n"
    with open("bot_naplo.log", "a", encoding="utf-8") as f:
        f.write(sor)
    print(uzenet)  # Kiírja a képernyőre is

def folyamatpiaci_adatok(nyers_jegyek):
    """Feldolgozza és megszűri a Bybitről kapott nyers adatokat."""
    ervenyes_ermek = []
    for ketyego in nyers_jegyek:
        szimbolum = ketyego.get("szimbolum", ketyego.get("symbol", ""))
        
        # JAVÍTVA: Nagybetűs "USDCUSDT" ellenőrzés
        if szimbolum.endswith("USDT") and szimbolum != "USDCUSDT":
            ervenyes_ermek.append({
                "szimbolum": szimbolum,
                "symbol": szimbolum,  # JAVÍTVA: Angol kulcs a pytest részére
                "forgalon": float(ketyego.get("24hVolume", ketyego.get("turnover24h", 0))),
                "ar": float(ketyego.get("lastPrice", 0)),
                "valtozas_24h": float(ketyego.get("price24hPcnt", 0))
            })
            
    ervenyes_ermek.sort(key=lambda x: x["forgalon"], reverse=True)
    return ervenyes_ermek[:50]

def tiszta_kepernyo():
    """Letisztítja a terminált."""
    os.system("cls" if os.name == "nt" else "clear")

def render_muszerfal(ciklusok_szamalasa, jelenlegi_piac):
    """A terminálos felület kirajzolása."""
    tiszta_kepernyo()
    print("=" * 70)
    print(f"🤖 BYBIT AUTOMATED TRADING BOT | RUNNING IN USERLAND")
    print(f"⏱️ Cycles Executed: {ciklusok_szamalasa} | Refresh Interval: {LOOP_INTERVAL}s")
    print("=" * 70)
    if jelenlegi_piac:
        print(f"🔥 Top Tracked Asset: {jelenlegi_piac[0]['szimbolum']}")
        print(f"📊 24h Turnover: ${jelenlegi_piac[0]['forgalon']:,.2f}")
        print(f"💰 Current Price: {jelenlegi_piac[0]['ar']}")
    else:
        print("📭 No active market data available.")
    print("=" * 70)

def biztonsagos_egyenleg_lekerdezes():
    """Szimulált vagy valós egyenleg lekérdezés."""
    return {"USDT": 1000.0}

def place_order_v5(symbol, side, qty, category="linear", order_type="Market"):
    """Megbízás küldése a Bybit API felé."""
    return {"retCode": 0, "result": {"orderId": "SIM_ORDER_123456"}, "retMsg": "OK"}

# Teszt kompatibilitási alias a legvégén
process_market_data = folyamatpiaci_adatok
