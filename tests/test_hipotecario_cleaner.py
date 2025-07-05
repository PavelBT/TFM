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

