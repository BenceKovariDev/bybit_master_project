# bybit_master_project/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class TradingConfig:
    API_KEY = os.getenv("BYBIT_API_KEY", "")
    API_SECRET = os.getenv("BYBIT_API_SECRET", "")
    
    API_URL = "https://api.bybit.com/v5/market/tickers"
    CATEGORY = "linear"
    
    MAX_POSITIONS = 3
    BUY_TRIGGER_PCT = 2.0  
    
    # --- ÚJ KOCKÁZATKEZELÉSI BEÁLLÍTÁSOK ---
    INITIAL_STOP_LOSS_PCT = -1.0  # Kezdő stop-loss (ha azonnal esni kezd)
    TAKE_PROFIT_PCT = 2.0        # Fix profitcél (itt azonnal zárunk és zsebre tesszük a pénzt)
    TRAILING_TRIGGER_PCT = 1.0   # Ha elérjük az 1% profitot, a Stop-Loss felugrik 0%-ra (Breakeven)!
    
    REFRESH_RATE_SECONDS = 5
    WATCH_LIST = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT"]
