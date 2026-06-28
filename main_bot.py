# bybit_master_project/main_bot.py
import time
import os
import hmac
import hashlib
import json
import requests
from dotenv import load_dotenv

# Projekt specifikus modulok importalasa
import adatbazis
import strategia
import kockazatkezeles

try:
    from api_kliens import fetch_top_market_data
except ImportError:
    def fetch_top_market_data():
        return [{"szimbólum": "XRPUSDT", "24 órás forgalom": "1500000", "utolsó ár": "0.55", "price24hPcnt": "2.5"}]

load_dotenv()

API_KEY = os.getenv("BYBIT_API_KEY", "").strip()
API_SECRET = os.getenv("BYBIT_API_SECRET", "").strip()
BASE_URL = "https://api-demo.bybit.com"

LOOP_INTERVAL = 10  # Frissitesi idokoz masodpercben

def folyamatpiaci_adatok(nyers_jegyek):
    """Feldolgozza es megszuri a Bybitrol kapott nyers adatokat."""
    ervenyes_ermek = []
    for ketyego in nyers_jegyek:
        szimbolum = ketyego.get("szimbólum", ketyego.get("symbol", ""))
        if szimbolum.endswith("USDT") and szimbolum != "USDcusdt":
            ervenyes_ermek.append({
                "szimbolum": szimbolum,
                "forgalom": float(ketyego.get("24 órás forgalom", ketyego.get("turnover24h", 0))),
                "ar": float(ketyego.get("utolsó ár", ketyego.get("lastPrice", 0))),
                "valtozas_24h": float(ketyego.get("price24hPcnt", ketyego.get("price24hPcnt", 0)))
            })
    ervenyes_ermek.sort(key=lambda x: x["forganom" if "forganom" in x else "forgalom"], reverse=True)
    return ervenyes_ermek[:50]

def tiszta_kepernyo():
    """Letisztitja a terminalt."""
    os.system('cls' if os.name == 'nt' else 'clear')

def render_muszerfal(ciklusok_szamalasa, jelenlegi_piac):
    """A terminalos felulet kirajzolasa."""
    tiszta_kepernyo()
    print("=" * 70)
    print(f"🤖 BYBIT MASTER BOT | LEPESROL LEPESRE TANANYAG ES ELES RENDSZER")
    print(f"🕒 Ido: {time.strftime('%Y-%m-%d %H:%M:%S')}\t| Ciklus: {ciklusok_szamalasa}")
    print("=" * 70)
    if jelenlegi_piac:
        print(f"🔥 Top Kereskedett Erme: {jelenlegi_piac[0]['szimbolum']} | Ar: {jelenlegi_piac[0]['ar']}")
    print("-" * 70)

def biztonsagos_egyenleg_lekerdezes():
    """Felhasznaloi egyenleg lekerese Bybit V5 GET URL-alairassal."""
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    
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
    """Bybit V5 POST megbizaskuldes beagyazott JSON hitelesitessel."""
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
        return {"retCode": -1, "retMsg": f"Halozati hiba: {str(e)}"}

# --- FO PROGRAMCIKLUS ---
if __name__ == "__main__":
    ciklus_szamlalo = 0
    print("🚀 Kezdodik a fo bot inicializalasa...")
    
    egyenleg_adat = biztonsagos_egyenleg_lekerdezes()
    if egyenleg_adat.get("retCode") == 0:
        print("✅ Bybit V5 API Kapcsolat sikeresen felepitve!")
        adatbazis.log_mentes(0, "Bot sikeresen elindult, API kapcsolat OK.")
    else:
        print(f"⚠️ Figyelem, az egyenleg lekeres hibat jelzett: {egyenleg_adat.get('retMsg')}")
    
    time.sleep(2)

    while True:
        try:
            ciklus_szamlalo += 1
            
            # 1. Friss piaci adatok lekerese
            nyers_adatok = fetch_top_market_data()
            piac_aktiv = folyamatpiaci_adatok(nyers_adatok)
            
            # 2. Muszerfal frissitese
            render_muszerfal(ciklus_szamlalo, piac_aktiv)
            
            # Egy gyors szotart (dict) epitunk a friss arakbol a kockazatkezelesnek
            piaci_arak_dict = {erme["szimbolum"]: erme["ar"] for erme in piac_aktiv}
            
            # 3. KOCKAZATKEZELES: Meglevo nyitott poziciok ellenorzese es lezarasa (SL/TP)
            kockazatkezeles.nyitott_poziciok_ellenorzese(piaci_arak_dict, place_order_v5)
            
            # 4. STRATEGIAI DONTES HOZATAL (Uj poziciok keresese)
            jelzes = strategia.elemzes_es_dontes(piac_aktiv)
            if jelzes:
                print(f"🚀 Kereskedesi jel erkezett: {jelzes['szimbolum']} -> {jelzes['irany']} (Ar: {jelzes['ar']})")
                teszt_qty = 1 
                
                valasz = place_order_v5(symbol=jelzes['szimbolum'], side=jelzes['irany'], qty=teszt_qty)
                
                if valasz.get("retCode") == 0:
                    order_id = valasz.get("result", {}).get("orderId", "UNKNOWN")
                    print(f"✅ SIKERES RENDELÉS! Bybit OrderID: {order_id}")
                    
                    adatbazis.pozicio_mentes(
                        order_id=order_id,
                        szimbólum=jelzes['szimbolum'],
                        irany=jelzes['irany'],
                        mennyiseg=teszt_qty,
                        nyito_ar=jelzes['ar']
                    )
                    adatbazis.log_mentes(ciklus_szamlalo, f"VETEL: {jelzes['szimbolum']} sikeresen vegrehajtva. ID: {order_id}")
                else:
                    print(f"❌ Bybit elutasitotta a rendelest: {valasz.get('retMsg')}")
                    adatbazis.log_mentes(ciklus_szamlalo, f"RENDELES HIBA: {jelzes['szimbolum']} - {valasz.get('retMsg')}")
            
            if ciklus_szamlalo % 10 == 0:
                adatbazis.log_mentes(ciklus_szamlalo, f"Bot fut, jelenlegi top erme: {piac_aktiv[0]['szimbolum']}")
            
            time.sleep(LOOP_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n🛑 A bot futasa felhasznalo altal leallitva.")
            adatbazis.log_mentes(ciklus_szamlalo, "Bot manualisan leallitva.")
            break
        except Exception as hiba:
            print(f"❌ Hiba tortent a fociklusban: {hiba}")
            time.sleep(5)
