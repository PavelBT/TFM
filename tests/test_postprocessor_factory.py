from services.postprocessors import get_postprocessor


def test_get_postprocessor_basic():
    p = get_postprocessor(form_type="other")
    assert p.__class__.__name__ == 'BasicPostProcessor'


def test_get_postprocessor_structured():
    p = get_postprocessor(form_type="credito_personal")
    assert p.__class__.__name__ == 'BanorteCreditoPostProcessor'


def test_get_postprocessor_hipotecario():
    p = get_postprocessor(form_type="credito_hipotecario")
    assert p.__class__.__name__ == 'BanorteHipotecarioPostProcessor'

