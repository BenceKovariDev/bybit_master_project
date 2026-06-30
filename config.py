# bybit_master_project/config.py
import os
from dotenv import load_dotenv

# Kényszerítjük a .env beolvasását
load_dotenv()

class TradingConfig:
    API_KEY = os.getenv("BYBIT_API_KEY", "")
    API_SECRET = os.getenv("BYBIT_API_SECRET", "")
    
    # A Bybit Demo számla privát megbízáskezelő URL-je! (Külön sorban)
    API_URL = "https://api-demo.bybit.com/v5/order/create"
    CATEGORY = "linear"
    
    MAX_POSITIONS = 3
    BUY_TRIGGER_PCT = 2.0  
    
    INITIAL_STOP_LOSS_PCT = -1.0  
    TAKE_PROFIT_PCT = 2.0        
    TRAILING_TRIGGER_PCT = 1.0   
    
    REFRESH_RATE_SECONDS = 5
    WATCH_LIST = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT"]
