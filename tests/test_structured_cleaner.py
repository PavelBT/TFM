from services.field_correctors.structured_cleaner import StructuredFieldCorrector


def test_transform_basic():
    cleaner = StructuredFieldCorrector()
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


def test_transform_direct_fields():
    cleaner = StructuredFieldCorrector()
    data = {
        'Nombre': 'Maria',
        'Plazo credito': '24',
        'Genero': 'Femenino',
        'Estado civil': 'Soltero',
        'Regimen matrimonial': '',
        'Tipo propiedad': 'Propia',
        'Otros ingresos': '',
        'Tipo ingreso': 'Asalariado',
    }
    result = cleaner.transform(data)
    assert result['plazo_credito'] == '24'
    assert result['genero'] == 'Femenino'
    assert result['estado_civil'] == 'Soltero'
    assert result['regimen_matrimonial'] == ''
    assert result['tipo_propiedad'] == 'Propia'
    assert result['otros_ingresos'] == ''
    assert result['tipo_ingreso'] == 'Asalariado'
