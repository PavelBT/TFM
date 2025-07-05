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


def test_parser_prefers_later_non_empty_value():
    blocks = [
        {
            'Id': '1',
            'BlockType': 'KEY_VALUE_SET',
            'EntityTypes': ['KEY'],
            'Relationships': [{'Type': 'CHILD', 'Ids': ['1w']}, {'Type': 'VALUE', 'Ids': ['2']}]
        },
        {'Id': '1w', 'BlockType': 'WORD', 'Text': 'E-mail'},
        {
            'Id': '2',
            'BlockType': 'KEY_VALUE_SET',
            'EntityTypes': ['VALUE'],
            'Relationships': [{'Type': 'CHILD', 'Ids': ['2w']}]
        },
        {'Id': '2w', 'BlockType': 'WORD', 'Text': 'bad'},
        {
            'Id': '3',
            'BlockType': 'KEY_VALUE_SET',
            'EntityTypes': ['KEY'],
            'Relationships': [{'Type': 'CHILD', 'Ids': ['3w']}, {'Type': 'VALUE', 'Ids': ['4']}]
        },
        {'Id': '3w', 'BlockType': 'WORD', 'Text': 'E-mail'},
        {
            'Id': '4',
            'BlockType': 'KEY_VALUE_SET',
            'EntityTypes': ['VALUE'],
            'Relationships': [{'Type': 'CHILD', 'Ids': ['4w']}]
        },
        {'Id': '4w', 'BlockType': 'WORD', 'Text': 'good@example.com'}
    ]

    parser = TextractBlockParser()
    result = parser.parse(blocks)
    assert result['E-mail'] == 'good@example.com'


def test_parser_adjacent_lines_pairing():
    blocks = [
        {'Id': '1', 'BlockType': 'LINE', 'Text': 'Ingreso mensual'},
        {'Id': '2', 'BlockType': 'LINE', 'Text': '$5,000'}
    ]

    parser = TextractBlockParser()
    result = parser.parse(blocks)
    assert result['Ingreso mensual'] == '$5,000'
