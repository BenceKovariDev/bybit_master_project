# bybit_master_project/api_client.py
import requests
import sys
from config import TradingConfig

def fetch_top_market_data():
    """Lekéri a Bybitről a legfrissebb piaci adatokat biztonságos hibakezeléssel"""
    params = {"category": TradingConfig.CATEGORY}
    
    try:
        # Időtúllépés (timeout) beállítása, hogy ne fagyjon le a kód, ha a szerver nem válaszol
        response = requests.get(TradingConfig.API_URL, params=params, timeout=10)
        
        # Ha a HTTP státuszkód nem 200 (pl. 404 vagy 500 hiba), itt hibát dob a program
        response.raise_for_status() 
        
        data = response.json()
        
        # Ellenőrizzük a Bybit saját belső válaszkódját (0 = Sikeres)
        if data.get("retCode") == 0:
            return data["result"]["list"]
        else:
            print(f"[BYBIT API HIBA] Kód: {data.get('retCode')} - {data.get('retMsg')}", file=sys.stderr)
            return []
            
    except requests.exceptions.RequestException as network_error:
        # Ha nincs net, vagy megszakadt a kapcsolat, itt kapjuk el
        print(f"[HÁLÓZATI HIBA] Sikertelen kapcsolódás: {network_error}", file=sys.stderr)
        return []
