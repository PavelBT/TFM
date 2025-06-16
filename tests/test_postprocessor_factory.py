from services.postprocessors import get_postprocessor


def test_get_postprocessor_basic():
    p = get_postprocessor(form_type="other")
    assert p.__class__.__name__ == 'BasicPostProcessor'


def test_get_postprocessor_structured():
    p = get_postprocessor(form_type="banorte_credito")
    assert p.__class__.__name__ == 'BanorteCreditoPostProcessor'
