# bybit_master_project/indikatorok.py

def kalkulal_rsi(arak_listaja, periodus=14):
    """
    Kiszamolja a Relativ Ero Indexet (RSI) egy adott arlistabol.
    Tiszta Python implementacio a gyorsasag es a kompatibilitas vegett.
    """
    if len(arak_listaja) <= periodus:
        # Ha nincs eleg adatunk, egy semleges 50-es ertekkel terunk vissza
        return 50.0

    novekedesek = []
    csokkenesek = []

    # Kiszamoljuk az egymast koveto arak kulonbseget
    for i in range(1, len(arak_listaja)):
        kulonbseg = arak_listaja[i] - arak_listaja[i-1]
        if kulonbseg > 0:
            novekedesek.append(kulonbseg)
            csokkenesek.append(0)
        else:
            novekedesek.append(0)
            csokkenesek.append(abs(kulonbseg))

    # Elso atlagok kiszamitasa
    atlag_nyereseg = sum(novekedesek[:periodus]) / periodus
    atlag_veszteseg = sum(csokkenesek[:periodus]) / periodus

    if atlag_veszteseg == 0:
        return 100.0

    # Wilder-fele simitott atlagolas a maradeknak
    for i in range(periodus, len(novekedesek)):
        atlag_nyereseg = (atlag_nyereseg * (periodus - 1) + novekedesek[i]) / periodus
        atlag_veszteseg = (atlag_veszteseg * (periodus - 1) + csokkenesek[i]) / periodus

    if atlag_veszteseg == 0:
        return 100.0

    rs = atlag_nyereseg / atlag_veszteseg
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 2)
