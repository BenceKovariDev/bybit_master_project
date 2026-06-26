# bybit_master_project/config.py

class TradingConfig:
    """A kereskedő robot globális beállításai"""
    
    # API beállítások
    API_URL = "https://api.bybit.com/v5/market/tickers"
    CATEGORY = "spot"
    
    # Stratégia beállítások
    MAX_POSITIONS = 3          # Egyszerre maximum ennyi coint tarthat a robot
    STOP_LOSS_PCT = -1.0       # Ha a profit eléri a -1%-ot, azonnal eladunk (Védelmi vonal)
    BUY_TRIGGER_PCT = 2.0      # Ha egy coin 2%-ot emelkedik 24h alatt, megvesszük
    
    # Rendszer beállítások
    REFRESH_RATE_SECONDS = 5   # Hány másodpercenként frissítsen a monitor
