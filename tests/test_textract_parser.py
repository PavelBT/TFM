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
