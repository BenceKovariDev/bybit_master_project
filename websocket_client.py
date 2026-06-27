# bybit_master_project/websocket_client.py
import asyncio
import json
import websockets

# A Bybit hivatalos, publikus WebSocket végpontja a V5-ös API-hoz
BYBIT_WS_URL = "wss://stream.bybit.com/v5/public/linear"

async def listen_to_bitcoin():
    """Aszinkron függvény, ami élőben hallgatja a Bybit hálózatát"""
    print(f"[INFO] Csatlakozás a Bybit WebSockethez: {BYBIT_WS_URL}")
    
    # Megnyitjuk a folyamatos csővezetéket (kapcsolatot)
    async with websockets.connect(BYBIT_WS_URL) as ws:
        print("[INFO] Sikeres csatlakozás!")
        
        # Létrehozzuk a feliratkozási kérelmet (Subscription Message)
        # Pontosan megmondjuk a Bybitnek, hogy a BTCUSDT ticker adataira vagyunk kíváncsiak
        subscribe_message = {
            "op": "subscribe",
            "args": ["tickers.BTCUSDT"]
        }
        
        # Elküldjük a kérelmet JSON formátumban a csövön keresztül
        await ws.send(json.dumps(subscribe_message))
        print("[INFO] Feliratkozási kérelem elküldve a BTCUSDT-re...")
        
        # Végtelen ciklusban várjuk az élő adatokat
        while True:
            # Az await kulcsszó megengedi a Pythonnak, hogy ne fagyassza le a rendszert,
            # miközben arra vár, hogy a tőzsde küldjön valami újat.
            response = await ws.recv()
            data = json.loads(response)
            
            # Megnézzük, hogy valódi árváltozás jött-e (nem csak egy rendszerüzenet)
            if "data" in data:
                ticker_data = data["data"]
                # Kiszedjük az aktuális utolsó árat
                if "lastPrice" in ticker_data:
                    price = ticker_data["lastPrice"]
                    print(f"[{data.get('ts')}] 🔥 ÉLŐ BTC ÁR: {price} USDT")

if __name__ == "__main__":
    # Az aszinkron függvényeket nem lehet simán meghívni, az asyncio eseményhuroknak kell futtatnia őket
    try:
        asyncio.run(listen_to_bitcoin())
    except KeyboardInterrupt:
        print("\n[INFO] Élő adatfolyam sikeresen leállítva.")
