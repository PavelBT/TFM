from services.utils.normalization import normalize_key


def test_normalize_key_basic():
    assert normalize_key('  Nombre Completo ') == 'nombre_completo'
    assert normalize_key('email') == 'email'
    assert normalize_key('Teléfono-1') == 'telefono_1'
    assert normalize_key('r.f.c.') == 'rfc'
    assert normalize_key('Nombre / Apellido') == 'nombre/apellido'
