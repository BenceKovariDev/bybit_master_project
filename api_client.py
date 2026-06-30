# bybit_master_project/api_client.py
import requests
import time
import hmac
import hashlib
import json
from config import TradingConfig

def fetch_top_market_data():
    """Publikus adatok lekérése a monitorozáshoz"""
    params = {"category": TradingConfig.CATEGORY}
    try:
        market_url = "https://api.bybit.com/v5/market/tickers"
        response = requests.get(market_url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json().get("result", {}).get("list", [])
    except Exception:
        return []
    return []

def generate_signature(timestamp, api_key, api_secret, recv_window, payload_str):
    """Létrehozza a Bybit által megkövetelt HMAC-SHA256 biztonsági aláírást"""
    param_str = timestamp + api_key + recv_window + payload_str
    return hmac.new(
        bytes(api_secret, "utf-8"),
        bytes(param_str, "utf-8"),
        hashlib.sha256
    ).hexdigest()

def place_order(symbol, side, qty):
    """
    Valódi Market megbízást küld a Bybit tőzsdére megtisztított kulcsokkal.
    """
    # Kényszerített tisztítás (.strip()), hogy a láthatatlan karakterek ne rontsák el!
    api_key = str(TradingConfig.API_KEY).strip().replace('"', '').replace("'", "")
    api_secret = str(TradingConfig.API_SECRET).strip().replace('"', '').replace("'", "")

    if not api_key or not api_secret:
        print(f"[SZIMULÁCIÓ] {side} parancs elküldve: {qty} {symbol}")
        return {"retCode": 0, "result": {"orderId": "mock_order_12345"}}

    url = TradingConfig.API_URL
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    
    payload = {
        "category": TradingConfig.CATEGORY,
        "symbol": symbol,
        "side": side,
        "orderType": "Market",
        "qty": str(qty),
        "timeInForce": "GTC"
    }
    
    payload_str = json.dumps(payload, separators=(',', ':'))

    signature = generate_signature(
        timestamp, 
        api_key, 
        api_secret, 
        recv_window, 
        payload_str
    )

    headers = {
        "Content-Type": "application/json",
        "X-Bybit-API-Key": api_key,
        "X-Bybit-Sign": signature,
        "X-Bybit-Timestamp": timestamp,
        "X-Bybit-Recv-Window": recv_window
    }

    try:
        response = requests.post(url, headers=headers, data=payload_str, timeout=10)
        response_json = response.json()
        
        with open("bybit_api.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"--- PARANCS: {side} {qty} {symbol} ---\n")
            log_file.write(f"Idő: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_file.write(f"Válasz: {json.dumps(response_json, indent=2)}\n")
            log_file.write("="*50 + "\n")
            
        return response_json
    except Exception as e:
        print(f"[HIBA] API hiba történt: {e}")
        return None
