from services.ocr.textract.textract_block_parser import TextractBlockParser


def test_parser_combines_lines():
    blocks = [
        {
            'Id': '1',
            'BlockType': 'KEY_VALUE_SET',
            'EntityTypes': ['KEY'],
            'Relationships': [{'Type': 'CHILD', 'Ids': ['1w']}, {'Type': 'VALUE', 'Ids': ['2']}]
        },
        {'Id': '1w', 'BlockType': 'WORD', 'Text': 'Nombre'},
        {
            'Id': '2',
            'BlockType': 'KEY_VALUE_SET',
            'EntityTypes': ['VALUE'],
            'Relationships': [{'Type': 'CHILD', 'Ids': ['2w']}]
        },
        {'Id': '2w', 'BlockType': 'WORD', 'Text': 'Juan'},
        {'Id': '3', 'BlockType': 'LINE', 'Text': 'Apellido: Perez'},
        {'Id': '4', 'BlockType': 'LINE', 'Text': 'Telefono    1234567890'}
    ]
    parser = TextractBlockParser()
    result = parser.parse(blocks)
    assert result['Nombre'] == 'Juan'
    assert result['Apellido'] == 'Perez'
    assert result['Telefono'] == '1234567890'


def test_parser_prefers_first_value():
    blocks = [
        {
            'Id': 'k1',
            'BlockType': 'KEY_VALUE_SET',
            'EntityTypes': ['KEY'],
            'Relationships': [
                {'Type': 'CHILD', 'Ids': ['kw1', 'kw2']},
                {'Type': 'VALUE', 'Ids': ['v1']},
            ],
        },
        {'Id': 'kw1', 'BlockType': 'WORD', 'Text': 'Sueldo'},
        {'Id': 'kw2', 'BlockType': 'WORD', 'Text': 'mensual'},
        {
            'Id': 'v1',
            'BlockType': 'KEY_VALUE_SET',
            'EntityTypes': ['VALUE'],
            'Relationships': [{'Type': 'CHILD', 'Ids': ['vw1']}],
        },
        {'Id': 'vw1', 'BlockType': 'WORD', 'Text': '$40,000'},
        {
            'Id': 'k2',
            'BlockType': 'KEY_VALUE_SET',
            'EntityTypes': ['KEY'],
            'Relationships': [
                {'Type': 'CHILD', 'Ids': ['kw1', 'kw2']},
                {'Type': 'VALUE', 'Ids': ['v2']},
            ],
        },
        {
            'Id': 'v2',
            'BlockType': 'KEY_VALUE_SET',
            'EntityTypes': ['VALUE'],
            'Relationships': [{'Type': 'CHILD', 'Ids': ['vw2']}],
        },
        {'Id': 'vw2', 'BlockType': 'WORD', 'Text': '$'},
    ]

    parser = TextractBlockParser()
    result = parser.parse(blocks)
    assert result['Sueldo mensual'] == '$40,000'


def test_parser_prefers_longer_value():
    blocks = [
        {
            'Id': 'k1',
            'BlockType': 'KEY_VALUE_SET',
            'EntityTypes': ['KEY'],
            'Relationships': [
                {'Type': 'CHILD', 'Ids': ['kw1']},
                {'Type': 'VALUE', 'Ids': ['v1']},
            ],
        },
        {'Id': 'kw1', 'BlockType': 'WORD', 'Text': 'Año'},
        {
            'Id': 'v1',
            'BlockType': 'KEY_VALUE_SET',
            'EntityTypes': ['VALUE'],
            'Relationships': [{'Type': 'CHILD', 'Ids': ['vw1']}],
        },
        {'Id': 'vw1', 'BlockType': 'WORD', 'Text': '90'},
        {
            'Id': 'k2',
            'BlockType': 'KEY_VALUE_SET',
            'EntityTypes': ['KEY'],
            'Relationships': [
                {'Type': 'CHILD', 'Ids': ['kw1']},
                {'Type': 'VALUE', 'Ids': ['v2']},
            ],
        },
        {
            'Id': 'v2',
            'BlockType': 'KEY_VALUE_SET',
            'EntityTypes': ['VALUE'],
            'Relationships': [{'Type': 'CHILD', 'Ids': ['vw2']}],
        },
        {'Id': 'vw2', 'BlockType': 'WORD', 'Text': '2015'},
    ]

    parser = TextractBlockParser()
    result = parser.parse(blocks)
    assert result['Año'] == '2015'

def test_parser_keeps_other_fields_with_duplicates():
    blocks = [
        {'Id': 'ek1', 'BlockType': 'KEY_VALUE_SET', 'EntityTypes': ['KEY'], 'Relationships': [{'Type': 'CHILD', 'Ids': ['ew1']}, {'Type': 'VALUE', 'Ids': ['ev1']}]},
        {'Id': 'ew1', 'BlockType': 'WORD', 'Text': 'E-mail'},
        {'Id': 'ev1', 'BlockType': 'KEY_VALUE_SET', 'EntityTypes': ['VALUE'], 'Relationships': [{'Type': 'CHILD', 'Ids': ['evw1']}]} ,
        {'Id': 'evw1', 'BlockType': 'WORD', 'Text': 'a@example.com'},
        {'Id': 'ek2', 'BlockType': 'KEY_VALUE_SET', 'EntityTypes': ['KEY'], 'Relationships': [{'Type': 'CHILD', 'Ids': ['ew1']}, {'Type': 'VALUE', 'Ids': ['ev2']}]},
        {'Id': 'ev2', 'BlockType': 'KEY_VALUE_SET', 'EntityTypes': ['VALUE'], 'Relationships': [{'Type': 'CHILD', 'Ids': ['evw2']}]} ,
        {'Id': 'evw2', 'BlockType': 'WORD', 'Text': ''},
        {'Id': 'fk1', 'BlockType': 'KEY_VALUE_SET', 'EntityTypes': ['KEY'], 'Relationships': [{'Type': 'CHILD', 'Ids': ['fw1', 'fw2']}, {'Type': 'VALUE', 'Ids': ['fv1']}]},
        {'Id': 'fw1', 'BlockType': 'WORD', 'Text': 'Entidad'},
        {'Id': 'fw2', 'BlockType': 'WORD', 'Text': 'Federativa/Estado'},
        {'Id': 'fv1', 'BlockType': 'KEY_VALUE_SET', 'EntityTypes': ['VALUE'], 'Relationships': [{'Type': 'CHILD', 'Ids': ['fvw1']}]} ,
        {'Id': 'fvw1', 'BlockType': 'WORD', 'Text': 'Mich'},
        {'Id': 'fk2', 'BlockType': 'KEY_VALUE_SET', 'EntityTypes': ['KEY'], 'Relationships': [{'Type': 'CHILD', 'Ids': ['fw1', 'fw2']}, {'Type': 'VALUE', 'Ids': ['fv2']}]},
        {'Id': 'fv2', 'BlockType': 'KEY_VALUE_SET', 'EntityTypes': ['VALUE'], 'Relationships': [{'Type': 'CHILD', 'Ids': ['fvw2']}]} ,
        {'Id': 'fvw2', 'BlockType': 'WORD', 'Text': ''},
        {'Id': 'tk1', 'BlockType': 'KEY_VALUE_SET', 'EntityTypes': ['KEY'], 'Relationships': [{'Type': 'CHILD', 'Ids': ['tw1']}, {'Type': 'VALUE', 'Ids': ['tv1']}]},
        {'Id': 'tw1', 'BlockType': 'WORD', 'Text': 'Telefono'},
        {'Id': 'tv1', 'BlockType': 'KEY_VALUE_SET', 'EntityTypes': ['VALUE'], 'Relationships': [{'Type': 'CHILD', 'Ids': ['tvw1']}]} ,
        {'Id': 'tvw1', 'BlockType': 'WORD', 'Text': '12345'},
    ]
    parser = TextractBlockParser()
    result = parser.parse(blocks)
    assert result['E-mail'] == 'a@example.com'
    assert result['Entidad Federativa/Estado'] == 'Mich'
    assert result['Telefono'] == '12345'
