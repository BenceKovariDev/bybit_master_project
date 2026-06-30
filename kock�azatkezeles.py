# bybit_master_project/kockazatkezeles.py
import sqlite3
import requests
import time

DB_NAME = "bybit_bot.db"

TAKE_PROFIT_PCT = 2.0  # 2% profitnal zarunk
STOP_LOSS_PCT = 1.0    # 1% vesztesegnel vagjuk a veszteseget

def nyitott_poziciok_ellenorzese(aktualis_piac_dict, place_order_funkcio):
    """
    Atnezi az adatbazisban lévő NYITOTT poziciokat, es ha az ar elerte 
    a TP-t vagy SL-t, automatikusan lezarja a tőzsdén es az adatbazisban is.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Lekerjuk a nyitott poziciokat
    cursor.execute("SELECT id, order_id, szimbólum, irany, mennyiseg, nyito_ar FROM poziciok WHERE statusz = 'OPEN'")
    nyitott_poziciok = cursor.fetchall()
    
    for poz in nyitott_poziciok:
        db_id, order_id, szimbolum, irany, mennyiseg, nyito_ar = poz
        
        # Megkeressuk az erme aktualis arat a friss piaci adatok között
        aktualis_ar = aktualis_piac_dict.get(szimbolum)
        if not aktualis_ar:
            continue  # Ha nincs friss arunk errol az ermerol, ugorjuk at
            
        # Kiszamoljuk az aktualis elmozdulast szazalekban
        if irany == "Buy":
            szazalekos_valtozas = ((aktualis_ar - nyito_ar) / nyito_ar) * 100
        else: # Sell/Short eseten (ha kesobb bevezetjuk)
            szazalekos_valtozas = ((nyito_ar - aktualis_ar) / nyito_ar) * 100
            
        print(f"👀 Pozicio figyeles: {szimbolum} | Nyito: {nyito_ar} | Aktualis: {aktualis_ar} | PnL: {szazalekos_valtozas:.2f}%")
        
        # DONTES A ZARASROL
        zarasi_szandek = False
        zarasi_ok = ""
        
        if szazalekos_valtozas >= TAKE_PROFIT_PCT:
            zarasi_szandek = True
            zarasi_ok = f"TAKE PROFIT (+{szazalekos_valtozas:.2f}%)"
        elif szazalekos_valtozas <= -STOP_LOSS_PCT:
            zarasi_szandek = True
            zarasi_ok = f"STOP LOSS ({szazalekos_valtozas:.2f}%)"
            
        if zarasi_szandek:
            print(f"🚨 {zarasi_ok} ELERVE! Pozicio zarasa: {szimbolum}")
            
            # Ellentetes iranyu megbizast kuldunk a zarasra (Ha Buy volt, most Sell-el zarjuk)
            zarasi_irany = "Sell" if irany == "Buy" else "Buy"
            valasz = place_order_funkcio(symbol=szimbolum, side=zarasi_irany, qty=mennyiseg)
            
            if valasz.get("retCode") == 0:
                pnl_dollar = (aktualis_ar - nyito_ar) * mennyiseg if irany == "Buy" else (nyito_ar - aktualis_ar) * mennyiseg
                
                # Frissitjuk az adatbazisban a poziciot CLOSED-ra
                cursor.execute("""
                    UPDATE poziciok 
                    SET statusz = 'CLOSED', zaro_ar = ?, pnl = ? 
                    WHERE id = ?
                """, (aktualis_ar, pnl_dollar, db_id))
                conn.commit()
                print(f"✅ Pozicio sikeresen lezarva az adatbazisban is. Profit/Loss: {pnl_dollar}$")
            else:
                print(f"❌ Hiba a tőzsdén valo zarasnal: {valasz.get('retMsg')}")
                
    conn.close()
