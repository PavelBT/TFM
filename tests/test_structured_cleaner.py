from services.field_correctors.banorte_credito_cleaner import BanorteCreditoFieldCorrector


def test_transform_basic():
    cleaner = BanorteCreditoFieldCorrector()
    data = {
        'Nombre': ' juan ',
        'Apellido': 'perez',
        'email': 'TEST@MAIL.COM ',
        'teléfono': '55 123-45678',
        'sueldo mensual': '$1,000',
        'Sueldo Mensual Neto': '1.000,50',
        '36': '[X]',
        'femenino': '[ ]',
        'masculino': '[X]',
    }
    result = cleaner.transform(data)
    assert result['datos_personales']['nombre'] == 'Juan'
    assert result['contacto']['email'] == 'test@mail.com'
    assert result['finanzas']['sueldo_mensual'] == '1000.50'
    assert result['finanzas']['plazo_credito'] == '36'
    assert result['datos_personales']['genero'] == 'Masculino'


def test_transform_salary_variants():
    cleaner = BanorteCreditoFieldCorrector()
    data = {
        'sueldo mensual': '$40,000',
        'Sueldo Mensual Neto': '100.000.00',
    }
    result = cleaner.transform(data)
    assert result['finanzas']['sueldo_mensual'] == '100000.00'


def test_transform_salario_mensual():
    cleaner = BanorteCreditoFieldCorrector()
    data = {
        'salario mensual': '$5,000',
    }
    result = cleaner.transform(data)
    assert result['finanzas']['sueldo_mensual'] == '5000.00'


def test_transform_phone_variants():
    cleaner = BanorteCreditoFieldCorrector()
    data = {
        'telefono de casa': '55 1111 2222',
        'teléfono oficina': '55 3333 4444',
    }
    result = cleaner.transform(data)
    assert result['contacto']['telefono de casa'] == '5511112222'
    assert result['contacto']['telefono oficina'] == '5533334444'
