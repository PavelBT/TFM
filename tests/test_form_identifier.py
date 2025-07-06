import json
from services.ocr.form_identifier import FormIdentifier


def test_extract_and_identify_form():
    with open('app/examples/analyzeDocCreditoPersonal.json', encoding='utf-8') as f:
        data = json.load(f)
    form_name = FormIdentifier.extract_name_from_blocks(data['Blocks'])
    assert 'CRÉDITO PERSONAL BANORTE' in form_name
    form_type = FormIdentifier.identify(form_name)
    assert form_type == 'credito_personal'

    form_type_blocks = FormIdentifier.identify_from_blocks(data['Blocks'])
    assert form_type_blocks == 'credito_personal'


def test_identify_unknown():
    assert FormIdentifier.identify('some random text') == 'unknown'
