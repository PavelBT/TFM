from services.postprocessors.form_postprocessor.banorte_credito_postprocessor import BanorteCreditoPostProcessor


def test_postprocessor_normalizes_keys():
    data = {
        "empresa donde trabaja": "CNDH",
        "puesto que ocupa actualmente en la empresa": "Asistente Gerente",
        "email": "claudia.gonzalez90@gmail.com",
        "telefono celular": "4433148781",
        "telefono de casa": "4432251501",
        "tipo_ingreso": "Asalariado",
        "plazo_credito": "24",
        "sueldo mensual": "40000.00",
        "tipo_propiedad": "Propia",
        "monto solicitado": "100000.00",
        "apellido paterno": "González",
        "apellido materno": "Reyes",
        "rfc con homoclave": "GORC900101X25",
        "nombre(s) (sin abreviaturas)": "Claudia",
    }

    processor = BanorteCreditoPostProcessor()
    result = processor.process(data)

    assert result["datos_personales"]["nombre"] == "Claudia"
    assert result["datos_personales"]["apellido_paterno"] == "González"
    assert result["datos_personales"]["apellido_materno"] == "Reyes"
    assert result["datos_personales"]["rfc"] == "GORC900101X25"
    assert result["finanzas"]["ingresos_mensuales"] == "40000.00"
    assert result["finanzas"]["monto_solicitado"] == "100000.00"
    assert result["contacto"]["email"] == "claudia.gonzalez90@gmail.com"
    assert result["contacto"]["telefono_celular"] == "4433148781"
    assert result["contacto"]["telefono_casa"] == "4432251501"
