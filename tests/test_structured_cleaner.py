from services.field_correctors.banorte_credito_cleaner import BanorteCreditoFieldCorrector


def test_transform_basic():
    cleaner = BanorteCreditoFieldCorrector()
    data = {
        'Nombre': ' juan ',
        'Apellido': 'perez',
        'email': 'TEST@MAIL.COM ',
        'teléfono': '55 123-45678',
        'sueldo mensual': '$1,000',
        '36': '[X]',
        'femenino': '[ ]',
        'masculino': '[X]',
    }
    result = cleaner.transform(data)
    assert result['datos_personales']['nombre'] == 'Juan'
    assert result['contacto']['email'] == 'test@mail.com'
    assert result['finanzas']['sueldo_mensual'] == '1000'
    assert result['plazo_credito'] == '36'
    assert result['genero'] == 'Masculino'
