import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from services.ocr.textract.textract_layout_parser import TextractLayoutParser
from services.ocr.textract.banorte_layout_parser import BanorteLayoutParser


def test_layout_parser_collects_references():
    blocks = [
        {"Id": "1", "BlockType": "LINE", "Text": "REFERENCIAS PERSONALES", "Page": 1, "Geometry": {"BoundingBox": {"Top": 0.1, "Left": 0}}},
        {"Id": "2", "BlockType": "LINE", "Text": "Juan Perez", "TextType": "HANDWRITING", "Page": 1, "Geometry": {"BoundingBox": {"Top": 0.2, "Left": 0}}},
        {"Id": "3", "BlockType": "LINE", "Text": "Maria Lopez", "TextType": "HANDWRITING", "Page": 1, "Geometry": {"BoundingBox": {"Top": 0.3, "Left": 0}}},
        {"Id": "4", "BlockType": "LINE", "Text": "CLAUSULAS", "Page": 1, "Geometry": {"BoundingBox": {"Top": 0.4, "Left": 0}}},
    ]
    parser = TextractLayoutParser(blocks)
    sections = parser.parse()
    assert sections["referencias_personales"] == ["Juan Perez", "Maria Lopez"]


def test_banorte_layout_parser_sections():
    blocks = [
        {"Id": "1", "BlockType": "LINE", "Text": "INFORMACION DEL CREDITO", "Page": 1, "Geometry": {"BoundingBox": {"Top": 0.02, "Left": 0}}},
        {"Id": "2", "BlockType": "LINE", "Text": "10000", "TextType": "HANDWRITING", "Page": 1, "Geometry": {"BoundingBox": {"Top": 0.05, "Left": 0}}},
        {"Id": "3", "BlockType": "LINE", "Text": "12 meses", "TextType": "HANDWRITING", "Page": 1, "Geometry": {"BoundingBox": {"Top": 0.1, "Left": 0}}},
        {"Id": "4", "BlockType": "LINE", "Text": "INFORMACION PERSONAL", "Page": 1, "Geometry": {"BoundingBox": {"Top": 0.15, "Left": 0}}},
        {"Id": "5", "BlockType": "LINE", "Text": "Juan", "TextType": "HANDWRITING", "Page": 1, "Geometry": {"BoundingBox": {"Top": 0.2, "Left": 0}}},
        {"Id": "6", "BlockType": "LINE", "Text": "Perez", "TextType": "HANDWRITING", "Page": 1, "Geometry": {"BoundingBox": {"Top": 0.25, "Left": 0}}},
        {"Id": "7", "BlockType": "LINE", "Text": "DOMICILIO", "Page": 1, "Geometry": {"BoundingBox": {"Top": 0.3, "Left": 0}}},
        {"Id": "8", "BlockType": "LINE", "Text": "Av Siempre Viva", "TextType": "HANDWRITING", "Page": 1, "Geometry": {"BoundingBox": {"Top": 0.35, "Left": 0}}},
        {"Id": "9", "BlockType": "LINE", "Text": "Col Centro", "TextType": "HANDWRITING", "Page": 1, "Geometry": {"BoundingBox": {"Top": 0.4, "Left": 0}}},
        {"Id": "10", "BlockType": "LINE", "Text": "EMPLEO", "Page": 1, "Geometry": {"BoundingBox": {"Top": 0.5, "Left": 0}}},
        {"Id": "11", "BlockType": "LINE", "Text": "Empresa XYZ", "TextType": "HANDWRITING", "Page": 1, "Geometry": {"BoundingBox": {"Top": 0.55, "Left": 0}}},
        {"Id": "12", "BlockType": "LINE", "Text": "Puesto ABC", "TextType": "HANDWRITING", "Page": 1, "Geometry": {"BoundingBox": {"Top": 0.6, "Left": 0}}},
        {"Id": "13", "BlockType": "LINE", "Text": "REFERENCIAS PERSONALES", "Page": 2, "Geometry": {"BoundingBox": {"Top": 0.1, "Left": 0}}},
        {"Id": "14", "BlockType": "LINE", "Text": "Carlos Diaz", "TextType": "HANDWRITING", "Page": 2, "Geometry": {"BoundingBox": {"Top": 0.2, "Left": 0}}},
        {"Id": "15", "BlockType": "LINE", "Text": "555-1234", "TextType": "HANDWRITING", "Page": 2, "Geometry": {"BoundingBox": {"Top": 0.25, "Left": 0}}},
        {"Id": "16", "BlockType": "LINE", "Text": "CLAUSULAS", "Page": 2, "Geometry": {"BoundingBox": {"Top": 0.4, "Left": 0}}},
    ]
    parser = BanorteLayoutParser(blocks)
    sections = parser.parse()
    assert sections["informacion_del_credito"] == ["10000", "12 meses"]
    assert sections["informacion_personal"] == ["Juan", "Perez"]
    assert sections["domicilio"] == ["Av Siempre Viva", "Col Centro"]
    assert sections["empleo"] == ["Empresa XYZ", "Puesto ABC"]
    assert sections["referencias_personales"] == ["Carlos Diaz", "555-1234"]


def test_banorte_layout_parser_stops_long_lines():
    long_text = (
        "OPERATIVA DE HISTORIAL O INFORMACION CREDITICIA Y DE CUALQUIER OTRA "
        "NATURALEZA QUE LE SEA PROPORCIONADA POR MI O POR TERCEROS CON MI "
        "AUTORIZACION A CUALQUIERA DE LAS ENTIDADES FINANCIERAS DE BANCO "
        "MERCANTIL DEL"
    )
    blocks = [
        {"Id": "1", "BlockType": "LINE", "Text": "INFORMACION PERSONAL", "Page": 1,
         "Geometry": {"BoundingBox": {"Top": 0.1, "Left": 0}}},
        {"Id": "2", "BlockType": "LINE", "Text": "Nombre", "Page": 1,
         "Geometry": {"BoundingBox": {"Top": 0.15, "Left": 0}}},
        {"Id": "3", "BlockType": "LINE", "Text": "Juan", "Page": 1,
         "Geometry": {"BoundingBox": {"Top": 0.2, "Left": 0}}},
        {"Id": "4", "BlockType": "LINE", "Text": long_text, "Page": 1,
         "Geometry": {"BoundingBox": {"Top": 0.3, "Left": 0}}},
        {"Id": "5", "BlockType": "LINE", "Text": "DOMICILIO", "Page": 1,
         "Geometry": {"BoundingBox": {"Top": 0.4, "Left": 0}}},
        {"Id": "6", "BlockType": "LINE", "Text": "Calle 5", "Page": 1,
         "Geometry": {"BoundingBox": {"Top": 0.45, "Left": 0}}},
    ]
    parser = BanorteLayoutParser(blocks)
    sections = parser.parse()
    assert sections["informacion_personal"] == ["Nombre", "Juan"]
    assert sections["domicilio"] == ["Calle 5"]
