from services.postprocessors import get_postprocessor


def test_get_postprocessor_basic():
    p = get_postprocessor(structured=False)
    assert p.__class__.__name__ == 'BasicPostProcessor'


def test_get_postprocessor_structured():
    p = get_postprocessor(structured=True, refiner_type=None)
    assert p.__class__.__name__ == 'StructuredOutputPostProcessor'
