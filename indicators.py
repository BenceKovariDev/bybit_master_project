# bybit_master_project/indicators.py

def calculate_rsi(prices, period=14):
    """
    Kiszámítja az RSI értéket egy adott ársorozatból.
    prices: egy lista az egymást követő árakkal (legalább period + 1 darab kell)
    """
    if len(prices) <= period:
        return None  # Nincs elég adatunk a számításhoz
        
    gains = []
    losses = []
    
    # 1. Kiszámoljuk az árváltozásokat (nyereség vagy veszteség)
    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
            
    # 2. Vesszük az utolsó 'period' (pl. 14) darab árváltozás átlagát
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100  # Ha nem volt semmi veszteség, az RSI a maximumon van
        
    # 3. Kiszámoljuk a Relatív Erőt (RS) és az RSI-t
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 2)
