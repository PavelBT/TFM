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
    assert result['finanzas']['ingresos_mensuales'] == '1000.50'
    assert result['finanzas']['plazo_credito'] == '36'
    assert result['datos_personales']['genero'] == 'Masculino'


def test_transform_salary_variants():
    cleaner = BanorteCreditoFieldCorrector()
    data = {
        'sueldo mensual': '$40,000',
        'Sueldo Mensual Neto': '100.000.00',
    }
    result = cleaner.transform(data)
    assert result['finanzas']['ingresos_mensuales'] == '100000.00'


def test_transform_special_fields():
    cleaner = BanorteCreditoFieldCorrector()
    data = {
        'RFC con Homoclave': 'ABCD900101XX1',
        'Telefono Celular': '55 123 45678',
        'Telefono de casa': '55 321 7654',
        'Email': 'USER@MAIL.COM',
        'dia': '01',
        'mes': '02',
        'ano': '1990',
    }
    result = cleaner.transform(data)
    assert result['datos_personales']['rfc'] == 'ABCD900101XX1'
    assert result['contacto']['telefono_celular'] == '5512345678'
    assert result['contacto']['telefono_casa'] == '553217654'
    assert result['contacto']['email'] == 'user@mail.com'
    assert result['datos_personales']['fecha_nacimiento'] == '1990-02-01'
