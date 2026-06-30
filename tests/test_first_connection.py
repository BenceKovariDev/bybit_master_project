def test_environment_is_working():
    """Ellenőrzi, hogy a pytest környezet sikeresen fut-e."""
    setup_status = True
    assert setup_status is True

def test_basic_math():
    """Alapvető matematikai ellenőrzés a tesztfuttató működésének validálásához."""
    assert 1 + 1 == 2
