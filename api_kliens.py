# bybit_master_project/api_kliens.py
import requests

def fetch_top_market_data():
    """
    Lekéri a Bybit V5 API-ról az összes lineáris (határidős/perpetual) érme 
    legfrissebb piaci adatait (ár, 24 órás forgalom, árváltozás).
    """
    url = "https://api-demo.bybit.com/v5/market/tickers"
    # Kifejezetten a lineáris (USDT-ben elszámolt) piacot kérjük le
    params = {
        "category": "linear"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get("retCode") == 0:
            nyers_lista = data.get("result", {}).get("list", [])
            feldolgozott_lista = []
            
            # Átkonvertáljuk a Bybit V5 kulcsait olyan formátumra, 
            # amilyet a main_bot.py magyarított változója vár
            for coin_data in nyers_lista:
                feldolgozott_lista.append({
                    "szimbólum": coin_data.get("symbol", ""),
                    "24 órás forgalom": coin_data.get("turnover24h", 0),
                    "utolsó ár": coin_data.get("lastPrice", 0),
                    "price24hPcnt": coin_data.get("price24hPcnt", 0)
                })
            return processed_list_or_data(feldolgozott_lista)
        else:
            print(f"⚠️ Bybit API Hiba az adatlekérésnél: {data.get('retMsg')}")
            return []
            
    except Exception as e:
        print(f"❌ Hálózati hiba az api_kliens-ben: {e}")
        return []

def processed_list_or_data(lista):
    # Biztonsági mentőöv, ha üres lenne az eredmény
    return lista if lista else [{"szimbólum": "XRPUSDT", "24 órás forgalom": "1500000", "utolsó ár": "0.55", "price24hPcnt": "2.5"}]
