# bybit_master_project/strategia.py

def elemzes_es_dontes(top_ermek_listaja):
    """
    Atnezi a top ermeket, es kivalasztja azt, ami a legalkalmasabb a kereskedesre.
    Visszater egy (szimbolum, irany, aktualis_ar) parossal, ha talal jo beszallot.
    """
    if not top_ermek_listaja:
        return None

    for erme in top_ermek_listaja:
        szimbolum = erme["szimbolum"]
        ar = erme["ar"]
        valtozas = erme["valtozas_24h"]
        forgalom = erme["forgalom"]
        
        # STRATEGIAI SZABALY: 
        # Ha az erme bent van a top forgalomban, es az elmult 24 oraban 
        # minimum 3%-ot, de maximum 12%-ot emelkedett (tehat kitoroben van, de meg nem ment el a hajo)
        if 3.0 <= valtozas <= 12.0:
            print(f"🎯 Strategia talalat: {szimbolum} | Valtozas: {valtozas}% -> VETEL jel!")
            return {
                "szimbolum": szimbolum,
                "irany": "Buy",
                "ar": ar,
                "ok": f"Momentum kitores ({valtozas}%)"
            }
            
    # Ha egyik erme sem felel meg a kriteriumoknak
    return None
