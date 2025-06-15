import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from services.ocr.textract.textract_layout_parser import TextractLayoutParser


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


