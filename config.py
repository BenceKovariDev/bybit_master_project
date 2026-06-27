# bybit_master_project/config.py
import os
from dotenv import load_dotenv

# Betöltjük a .env fájl tartalmát a környezeti változók közé
load_dotenv()

class TradingConfig:
    # Biztonságos kulcskezelés: ha nincs a .env-ben, egy üres stringet ad vissza
    API_KEY = os.getenv("BYBIT_API_KEY", "")
    API_SECRET = os.getenv("BYBIT_API_SECRET", "")
    
    # Kereskedési beállítások
    MAX_POSITIONS = 3
    BUY_TRIGGER_PCT = 2.0  # +2% emelkedésnél veszünk
    STOP_LOSS_PCT = -1.0   # -1% esésnél eladunk
    REFRESH_RATE_SECONDS = 5
