# bybit_master_project/kockazatkezeles.py
import sqlite3
import requests
import time

DB_NAME = "bybit_bot.db"

TAKE_PROFIT_PCT = 2.0  # 2% profitnal zarunk
STOP_LOSS_PCT = 1.0    # 1% vesztesegnel vagjuk a veszteseget

def nyitott_poziciok_ellenorzese(aktualis_piac_dict, place_order_funkcio):
    """Atnezi az adatbazisban levo NYITOTT poziciokat."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, order_id, szimbólum, irany, mennyiseg, nyito_ar FROM poziciok WHERE statusz = 'OPEN'")
    nyitott_poziciok = cursor.fetchall()
    
    for poz in nyitott_poziciok:
        db_id, order_id, szimbolum, irany, mennyiseg, nyito_ar = poz
        aktualis_ar = aktualis_piac_dict.get(szimbolum)
        if not aktualis_ar:
            continue
            
        if irany == "Buy":
            szazalekos_valtozas = ((aktualis_ar - nyito_ar) / nyito_ar) * 100
        else:
            szazalekos_valtozas = ((nyito_ar - aktualis_ar) / nyito_ar) * 100
            
        print(f"👀 Pozicio figyeles: {szimbolum} | Nyito: {nyito_ar} | Aktualis: {aktualis_ar} | PnL: {szazalekos_valtozas:.2f}%")
        
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
            zarasi_irany = "Sell" if irany == "Buy" else "Buy"
            valasz = place_order_funkcio(symbol=szimbolum, side=zarasi_irany, qty=mennyiseg)
            
            if valasz.get("retCode") == 0:
                pnl_dollar = (aktualis_ar - nyito_ar) * mennyiseg if irany == "Buy" else (nyito_ar - aktualis_ar) * mennyiseg
                cursor.execute("""
                    UPDATE poziciok 
                    SET statusz = 'CLOSED', zaro_ar = ?, pnl = ? 
                    WHERE id = ?
                """, (aktualis_ar, pnl_dollar, db_id))
                conn.commit()
                print(f"✅ Pozicio sikeresen lezarva az adatbazisban is.")
            else:
                print(f"❌ Hiba a tozsden valo zarasnal: {valasz.get('retMsg')}")
                
    conn.close()
