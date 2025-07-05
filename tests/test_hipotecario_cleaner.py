from services.field_correctors.hipotecario_cleaner import HipotecarioFieldCorrector


def test_transform_basic():
    cleaner = HipotecarioFieldCorrector()
    data = {
        "Nombre": " juan ",
        "Apellido paterno": "perez",
        "Telefono Celular": "55 1234 5678",
        "dia": "01",
        "mes": "02",
        "ano": "1990",
    }
    result = cleaner.transform(data)
    assert result["datos_personales"]["nombre"] == "Juan"
    assert result["contacto"]["telefono_celular"] == "5512345678"
    assert result["datos_personales"]["fecha_nacimiento"] == "1990-02-01"


def test_transform_aliases():
    cleaner = HipotecarioFieldCorrector()
    data = {
        "Nombre(s)": " Ana Maria ",
        "1er apellido": "Lopez",
        "2do apellido": "Hernandez",
        "CURP": "LOAJ800101HDFRRN09",
        "RFC con Homoclave": "ABCD900101XX1",
    }
    result = cleaner.transform(data)
    assert result["datos_personales"]["nombre"] == "Ana Maria"
    assert result["datos_personales"]["apellido_paterno"] == "Lopez"
    assert result["datos_personales"]["apellido_materno"] == "Hernandez"
    assert result["datos_personales"]["curp"] == "LOAJ800101HDFRRN09"
    assert result["datos_personales"]["rfc"] == "ABCD900101XX1"


def test_transform_razon_social_and_trailing_digits():
    cleaner = HipotecarioFieldCorrector()
    data = {
        "Nombre / Razón social": "Juan Perez",
        "Teléfono celular452 147 1121": "",
    }
    result = cleaner.transform(data)
    assert result["datos_personales"]["nombre"] == "Juan Perez"
    assert result["contacto"]["telefono_celular"] == "4521471121"

