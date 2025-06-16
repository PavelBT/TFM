from services.utils.normalization import normalize_key


def test_normalize_key_basic():
    assert normalize_key('  Nombre Completo ') == 'nombre_completo'
    assert normalize_key('email') == 'email'
    assert normalize_key('Teléfono-1') == 'tel_fono_1'
