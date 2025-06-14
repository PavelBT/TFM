import pytest
from app.services.field_correctors.basic_cleaner import BasicFieldCorrector

bc = BasicFieldCorrector()

@pytest.mark.parametrize('key,value,expected', [
    ('email', ' TEST@EXAMPLE.COM ', 'test@example.com'),
    ('correo', 'bademail.com', None),
    ('teléfono', '55 123-45678', '5512345678'),
    ('teléfono', '55 123-4567', None),
    ('monto', '$1,234', '1234'),
])
def test_basic_cleaner(key, value, expected):
    assert bc.correct(key, value) == expected

