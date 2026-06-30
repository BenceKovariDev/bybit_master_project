# bybit_master_project/test_order.py
import requests
import time
import hmac
import hashlib
import json
import os
from dotenv import load_dotenv

load_dotenv()

print("🚀 XRP POZÍCIÓ MEGNYITÁSA - VÉGLEGES ABSZOLÚT SIKER...")

api_key = os.getenv("BYBIT_API_KEY", "").strip()
api_secret = os.getenv("BYBIT_API_SECRET", "").strip()

url = "https://api-demo.bybit.com/v5/order/create"
timestamp = str(int(time.time() * 1000))
recv_window = "5000"

# Minden paraméter szigorúan ABC sorrendben, ahogy a Bybit hibaüzenete kérte!
payload = {
    "api_key": api_key,
    "category": "linear",
    "orderType": "Market",
    "positionIdx": 0,
    "qty": "10",
    "recv_window": recv_window,
    "side": "Buy",
    "symbol": "XRPUSDT",
    "timeInForce": "GTC",
    "timestamp": timestamp
}

# JAVÍTVA: Itt sima szövegként szerepel az XRPUSDT, nem változóként!
sign_string = f"api_key={api_key}&category=linear&orderType=Market&positionIdx=0&qty=10&recv_window={recv_window}&side=Buy&symbol=XRPUSDT&timeInForce=GTC&timestamp={timestamp}"

signature = hmac.new(
    bytes(api_secret, "utf-8"),
    bytes(sign_string, "utf-8"),
    hashlib.sha256
).hexdigest()

# Beletesszük a generált aláírást is a JSON-ba
payload["sign"] = signature

headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    print("\n📥 BYBIT MEGBÍZÁS VÁLASZ:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"\n❌ Hálózati hiba: {e}")
