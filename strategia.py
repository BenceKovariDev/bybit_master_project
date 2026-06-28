# bybit_master_project/strategia.py
import indikatorok

# Egy szotar, amiben eltaroljuk az ermek korabbi arait a memoriaban
AR_TORTENET = {}

def elemzes_es_dontes(top_ermek_listaja):
    """
    Kiterjesztett Profi Strategia: Momentum + RSI Szures + SMA Trendkovetes.
    Csak akkor vasarolunk, ha emelkedik, az RSI szerint nincs tulfujva,
    ES a rovid tavu trend (SMA 5) a hosszu tavu trend (SMA 20) felett van!
    """
    global AR_TORTENET
    if not top_ermek_listaja:
        return None

    for erme in top_ermek_listaja:
        szimbolum = erme["szimbolum"]
        ar = erme["ar"]
        valtozas = erme["valtozas_24h"]
        
        # 1. AR-TORTENET GYUJTESE
        if szimbolum not in AR_TORTENET:
            AR_TORTENET[szimbolum] = []
        
        AR_TORTENET[szimbolum].append(ar)
        
        # Maximum 35 arat tartunk meg a memoriaban az SMA 20-hoz
        if len(AR_TORTENET[szimbolum]) > 35:
            AR_TORTENET[szimbolum].pop(0)
            
        # Ha meg nincs eleg adatunk a teljes elemzeshez, megiszunk egy kavet
        if len(AR_TORTENET[szimbolum]) < 20:
            continue
            
        # 2. INDIKATOROK KISZAMITASA
        aktualis_rsi = indikatorok.kalkulal_rsi(AR_TORTENET[szimbolum])
        sma_gyors = indikatorok.kalkulal_sma(AR_TORTENET[szimbolum], periodus=5)
        sma_lassu = indikatorok.kalkulal_sma(AR_TORTENET[szimbolum], periodus=20)
        
        # 3. SZUPER-STRATEGIAI SZABALYRENDSZER
        # - Momentum: 3% es 12% kozotti 24h emelkedes
        if 3.0 <= valtozas <= 12.0:
            # - RSI ellenorzes: nem lehet 70 felett (nem tulfujt)
            if aktualis_rsi < 70.0:
                # - SMA Trend szuro: a gyors mozoatlag a lassu felett van (bika irany)
                if sma_gyors > sma_lassu:
                    print(f"🎯 SZUPER TALALAT: {szimbolum} | RSI: {aktualis_rsi} | SMA Trend: OK -> VETEL!")
                    return {
                        "szimbolum": szimbolum,
                        "irany": "Buy",
                        "ar": ar,
                        "ok": f"RSI({aktualis_rsi}) + SMA Trend Kovetes"
                    }
                else:
                    # Ha emelkedik is, de a mikro-trend mar lefele tart
                    print(f"⏳ {szimbolum} emelkedik, de az SMA mikro-trend meg gyenge. Varakozas...")
            else:
                print(f"⚠️ {szimbolum} emelkedik, de az RSI tul magas ({aktualis_rsi})! KISZURVE.")
                
    return None
