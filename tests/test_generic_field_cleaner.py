from services.field_correctors.generic_field_cleaner import GenericFieldCleaner


def test_generic_cleaner():
    cleaner = GenericFieldCleaner()
    data = {
        'email': ' TEST@EXAMPLE.COM ',
        'monto': '1O0',
        'telefono': '55 123-45678',
        'nombre': ' juan ',
        'otro': ' valor '
    }
    result = cleaner.clean(data)
    assert result['email'] == 'test@example.com'
    assert result['monto'] == '100'
    assert result['telefono'] == '5512345678'
    assert result['nombre'] == 'Juan'
    assert result['otro'] == 'valor'
