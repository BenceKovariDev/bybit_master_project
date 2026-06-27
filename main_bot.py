# bybit_master_project/main_bot.py
import time
import os
import hmac
import hashlib
import json
import requests
from dotenv import load_dotenv

# Projekt specifikus modulok importálása (biztonságos fallback-kel)
try:
    from api_kliens import fetch_top_market_data
except ImportError:
    def fetch_top_market_data():
        return [{"szimbólum": "XRPUSDT", "24 órás forgalom": "1500000", "utolsó ár": "0.55", "price24hPcnt": "2.5"}]

load_dotenv()

API_KEY = os.getenv("BYBIT_API_KEY", "").strip()
API_SECRET = os.getenv("BYBIT_API_SECRET", "").strip()
BASE_URL = "https://api-demo.bybit.com"

LOOP_INTERVAL = 10  # Hány másodpercenként frissüljön a bot

def folyamatpiaci_adatok(nyers_jegyek):
    """Feldolgozza és megszűri a Bybitről kapott nyers adatokat."""
    érvényes_érmék = []
    for ketyegő in nyers_jegyek:
        szimbólum = ketyegő.get("szimbólum", ketyegő.get("symbol", ""))
        if szimbólum.endswith("USDT") and szimbólum != "USDcusdt":
            érvényes_érmék.append({
                "szimbólum": szimbólum,
                "forgalom": float(ketyegő.get("24 órás forgalom", ketyegő.get("turnover24h", 0))),
                "ár": float(ketyegő.get("utolsó ár", ketyegő.get("lastPrice", 0))),
                "változás_24h": float(ketyegő.get("price24hPcnt", ketyegő.get("price24hPcnt", 0)))
            })
    érvényes_érmék.sort(key=lambda x: x["forgalom"], reverse=True)
    return érvényes_érmék[:50]

def tiszta_képernyő():
    """Letisztítja a terminált az operációs rendszernek megfelelően."""
    os.system('cls' if os.name == 'nt' else 'clear')

def render_műszerfal(ciklusok_számlálása, jelenlegi_piac):
    """Kizárólag a terminálos felület képéért felel."""
    tiszta_képernyő()
    print("=" * 70)
    print(f"🤖 BYBIT MASTER BOT | LÉPÉSRŐL LÉPÉSRE TANANYAG ÉS ÉLES RENDSZER")
    print(f"🕒 Idő: {time.strftime('%Y-%m-%d %H:%M:%S')}\t| Ciklus: {ciklusok_számlálása}")
    print("=" * 70)
    if jelenlegi_piac:
        print(f"🔥 Top Kereskedett Érme: {jelenlegi_piac[0]['szimbólum']} | Ár: {jelenlegi_piac[0]['ár']}")
    print("-" * 70)

def biztonsagos_egyenleg_lekerdezes():
    """Felhasználói egyenleg lekérése Bybit V5 GET URL-aláírással (UserLAnd bypass)."""
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    
    # JAVÍTVA: Pontosan az az összefűzés, amit a Bybit logja kért!
    query_string = f"accountType=UNIFIED&api_key={API_KEY}&recv_window={recv_window}&timestamp={timestamp}"
    
    signature = hmac.new(
        bytes(API_SECRET, "utf-8"),
        bytes(query_string, "utf-8"),
        hashlib.sha256
    ).hexdigest()
    
    url = f"{BASE_URL}/v5/account/wallet-balance?{query_string}&sign={signature}"
    try:
        res = requests.get(url, timeout=10)
        return res.json()
    except Exception as e:
        return {"retCode": -1, "retMsg": str(e)}

def place_order_v5(symbol, side, qty, category="linear", order_type="Market"):
    """Bombabiztos Bybit V5 POST megbízásküldés beágyazott JSON hitelesítéssel."""
    url = f"{BASE_URL}/v5/order/create"
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"

    payload = {
        "api_key": API_KEY,
        "category": category,
        "orderType": order_type,
        "positionIdx": 0,
        "qty": str(qty),
        "recv_window": recv_window,
        "side": side,
        "symbol": symbol,
        "timeInForce": "GTC",
        "timestamp": timestamp
    }

    sign_string = f"api_key={API_KEY}&category={category}&orderType={order_type}&positionIdx=0&qty={qty}&recv_window={recv_window}&side={side}&symbol={symbol}&timeInForce=GTC&timestamp={timestamp}"

    signature = hmac.new(
        bytes(API_SECRET, "utf-8"),
        bytes(sign_string, "utf-8"),
        hashlib.sha256
    ).hexdigest()

    payload["sign"] = signature
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        return {"retCode": -1, "retMsg": f"Hálózati hiba: {str(e)}"}

# --- FŐ PROGRAMCIKLUS ---
if __name__ == "__main__":
    ciklus_szamlalo = 0
    print("🚀 Kezdődik a fő bot inicializálása...")
    
    egyenleg_adat = biztonsagos_egyenleg_lekerdezes()
    if egyenleg_adat.get("retCode") == 0:
        print("✅ Bybit V5 API Kapcsolat sikeresen felépítve!")
    else:
        print(f"⚠️ Figyelem, az egyenleg lekérés hibát jelzett: {egyenleg_adat.get('retMsg')}")
    
    time.sleep(2)

    while True:
        try:
            ciklus_szamlalo += 1
            
            nyers_adatok = fetch_top_market_data()
            piac_aktiv = folyamatpiaci_adatok(nyers_adatok)
            
            render_műszerfal(ciklus_szamlalo, piac_aktiv)
            
            time.sleep(LOOP_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n🛑 A bot futása felhasználó által leállítva.")
            break
        except Exception as hiba:
            print(f"❌ Hiba történt a főciklusban: {hiba}")
            time.sleep(5)
