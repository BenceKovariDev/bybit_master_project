# bybit_master_project/api_client.py
import requests
import time
import hmac
import hashlib
import json
from config import TradingConfig

def fetch_top_market_data():
    """Publikus adatok lekérése (ez változatlan marad)"""
    params = {"category": TradingConfig.CATEGORY}
    try:
        response = requests.get(TradingConfig.API_URL, params=params, timeout=10)
        if response.status_code == 200:
            return response.json().get("result", {}).get("list", [])
    except Exception:
        return []
    return []

def generate_signature(timestamp, api_key, api_secret, recv_window, payload_str):
    """Létrehozza a Bybit által elvárt HMAC-SHA256 biztonsági aláírást"""
    param_str = timestamp + api_key + recv_window + payload_str
    return hmac.new(
        bytes(api_secret, "utf-8"),
        bytes(param_str, "utf-8"),
        hashlib.sha256
    ).hexdigest()

def place_order(symbol, side, qty):
    """
    Valódi Market (Piaci áras) megbízást küld a Bybit tőzsdére.
    side: 'Buy' vagy 'Sell'
    qty: A megvásárolni/eladni kívánt mennyiség (pl. 0.01 BTC vagy 10 XRP)
    """
    # Ha nincsenek megadva kulcsok, csak teszt módban szimuláljuk
    if not TradingConfig.API_KEY or not TradingConfig.API_SECRET:
        print(f"[SZIMULÁCIÓ] {side} parancs elküldve: {qty} {symbol}")
        return {"retCode": 0, "result": {"orderId": "mock_order_12345"}}

    # A Bybit V5 éles privát végpontja
    url = "https://api.bybit.com/v5/order/create"
    
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    
    # A parancs adatai JSON formátumban
    payload = {
        "category": TradingConfig.CATEGORY,
        "symbol": symbol,
        "side": side,
        "orderType": "Market",
        "qty": str(qty),
        "timeInForce": "GTC"
    }
    payload_str = json.dumps(payload)

    # Generáljuk az egyedi aláírást ehhez a kéréshez
    signature = generate_signature(
        timestamp, 
        TradingConfig.API_KEY, 
        TradingConfig.API_SECRET, 
        recv_window, 
        payload_str
    )

    # A Bybit által megkövetelt speciális HTTP fejlécek
    headers = {
        "X-BMT-APIKEY": TradingConfig.API_KEY,
        "X-BMT-SIGN": signature,
        "X-BMT-TIMESTAMP": timestamp,
        "X-BMT-RECV-WINDOW": recv_window,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, data=payload_str, timeout=10)
        return response.json()
    except Exception as e:
        print(f"[HIBA] Nem sikerült elküldeni a parancsot: {e}")
        return None
