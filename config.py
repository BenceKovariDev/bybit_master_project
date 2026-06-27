# bybit_master_project/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class TradingConfig:
    # Biztonsági kulcsok (a .env fájlból)
    API_KEY = os.getenv("BYBIT_API_KEY", "")
    API_SECRET = os.getenv("BYBIT_API_SECRET", "")
    
    # Bybit API specifikus fix beállítások
    API_URL = "https://api.bybit.com/v5/market/tickers"
    CATEGORY = "linear"
    
    # Kereskedési stratégia beállításai
    MAX_POSITIONS = 3
    BUY_TRIGGER_PCT = 2.0  # +2% emelkedésnél veszünk
    STOP_LOSS_PCT = -1.0   # -1% esésnél eladunk
    REFRESH_RATE_SECONDS = 5
