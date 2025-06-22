import pytest
from services.field_correctors.basic_field_corrector import BasicFieldCorrector

bc = BasicFieldCorrector()


@pytest.mark.parametrize('key,value,expected', [
    ('email', ' TEST@EXAMPLE.COM ', 'test@example.com'),
    ('correo', 'bademail.com', None),
    ('teléfono', '55 123-45678', '5512345678'),
    ('teléfono', '55 123-4567', None),
    ('teléfono', '55 1234 56789', None),
    ('monto', '$1,234', '1234.00'),
    ('monto', '$1,000.50', '1000.50'),
    ('nombre', ' josé pérez ', 'José Pérez'),
    ('r.f.c.', ' abcd-010101-xx1 ', 'ABCD010101XX1'),
    ('rfc', 'BAD010101AA', None),
    ('curp', 'LOAJ800101HDFRRN09', 'LOAJ800101HDFRRN09'),
    ('curp', 'INVALIDCURP123', None),
    ('c.p.', ' 12,345 ', '12345'),
    ('otro', ' valor ', 'valor'),
])
def test_basic_field_corrector(key, value, expected):
    assert bc.correct(key, value) == expected
