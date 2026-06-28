# bybit_master_project/strategia.py
import indikatorok

# Egy szótár, amiben eltároljuk az érmék korábbi árait a memóriában
AR_TORTENET = {}

def elemzes_es_dontes(top_ermek_listaja):
    """
    Kiterjesztett strategia: Momentum + RSI szures.
    Csak akkor veszünk meg egy érmét, ha emelkedik, de az RSI alapján még NEM túlvetett!
    """
    global AR_TORTENET
    if not top_ermek_listaja:
        return None

    for erme in top_ermek_listaja:
        szimbolum = erme["szimbolum"]
        ar = erme["ar"]
        valtozas = erme["valtozas_24h"]
        
        # 1. ÁR-TÖRTÉNET GYŰJTÉSE
        if szimbolum not in AR_TORTENET:
            AR_TORTENET[szimbolum] = []
        
        # Hozzáadjuk az aktuális árat a listához
        AR_TORTENET[szimbolum].append(ar)
        
        # Maximum 30 árat tartunk meg a memóriában, hogy ne egye meg a telefont
        if len(AR_TORTENET[szimbolum]) > 30:
            AR_TORTENET[szimbolum].pop(0)
            
        # 2. RSI KISZÁMÍTÁSA
        # Kiszámoljuk az RSI-t. Ha még nincs elég adat (14 kör), 50-et kapunk vissza.
        aktualis_rsi = indikatorok.kalkulal_rsi(AR_TORTENET[szimbolum])
        
        # 3. FEJLETT STRATÉGIAI SZABÁLYOK
        # - Momentum: 24 órás változás 3% és 12% között van
        # - RSI szűrő: Az RSI 70 ALATT van (azaz NEM túlvetett az érme, van még benne tér felfelé!)
        if 3.0 <= valtozas <= 12.0:
            if aktualis_rsi < 70.0:
                print(f"🎯 Strategia talalat: {szimbolum} | Valtozas: {valtozas}% | RSI: {aktualis_rsi} -> VETEL!")
                return {
                    "szimbolum": szimbolum,
                    "irany": "Buy",
                    "ar": ar,
                    "ok": f"Momentum ({valtozas}%) + Biztonsagos RSI ({aktualis_rsi})"
                }
            else:
                print(f"⚠️ {szimbolum} emelkedik ({valtozas}%), de az RSI tul magas ({aktualis_rsi})! KISZŰRVE.")
                
    return None
