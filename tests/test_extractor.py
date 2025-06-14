import sys
import json
from pathlib import Path
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

sys.modules.setdefault("magic", types.SimpleNamespace(from_buffer=lambda *a, **k: "application/pdf"))

from services.ocr.textract.textract_extractor import TextractFullExtractor


def test_textract_extractor_fields():
    with open(Path(__file__).resolve().parents[1] / "app" / "examples" / "analyzeDocResponse.json") as f:
        blocks = json.load(f)["Blocks"]
    extractor = TextractFullExtractor(blocks)
    fields = extractor.extract()
    assert "folio" in fields
    assert len(fields) > 0


def test_consecutive_fields_override_placeholder():
    extractor = TextractFullExtractor([])
    extractor.lines = [
        {"BlockType": "LINE", "Text": "E-mail"},
        {"BlockType": "LINE", "Text": "foo@bar.com"},
    ]
    extractor.field_dict = {"email": "VALUE_NOT_FOUND"}
    extractor._extract_consecutive_fields()
    assert extractor.field_dict["email"] == "foo@bar.com"


def test_checkboxes_override_selected():
    blocks = [
        {"Id": "w1", "BlockType": "WORD", "Text": "Casado"},
        {
            "Id": "sel1",
            "BlockType": "SELECTION_ELEMENT",
            "SelectionStatus": "SELECTED",
        },
        {
            "Id": "v1",
            "BlockType": "KEY_VALUE_SET",
            "EntityTypes": ["VALUE"],
            "Relationships": [{"Type": "CHILD", "Ids": ["sel1"]}],
        },
        {
            "Id": "k1",
            "BlockType": "KEY_VALUE_SET",
            "EntityTypes": ["KEY"],
            "Relationships": [
                {"Type": "CHILD", "Ids": ["w1"]},
                {"Type": "VALUE", "Ids": ["v1"]},
            ],
        },
    ]
    extractor = TextractFullExtractor(blocks)
    fields = extractor.extract()
    assert fields["casado"] == "Sí"


def test_inline_pairs_override_placeholder():
    extractor = TextractFullExtractor([])
    extractor.lines = [
        {"BlockType": "LINE", "Text": "Nombre: Juan"},
    ]
    extractor.field_dict = {"nombre": "VALUE_NOT_FOUND"}
    extractor._add_inline_pairs()
    assert extractor.field_dict["nombre"] == "Juan"


def test_kv_map_deduplicates_values():
    blocks = [
        {"Id": "kw", "BlockType": "WORD", "Text": "Folio"},
        {"Id": "v1w", "BlockType": "WORD", "Text": "123"},
        {"Id": "v2w", "BlockType": "WORD", "Text": "123"},
        {
            "Id": "v1",
            "BlockType": "KEY_VALUE_SET",
            "EntityTypes": ["VALUE"],
            "Relationships": [{"Type": "CHILD", "Ids": ["v1w"]}],
        },
        {
            "Id": "v2",
            "BlockType": "KEY_VALUE_SET",
            "EntityTypes": ["VALUE"],
            "Relationships": [{"Type": "CHILD", "Ids": ["v2w"]}],
        },
        {
            "Id": "k1",
            "BlockType": "KEY_VALUE_SET",
            "EntityTypes": ["KEY"],
            "Relationships": [
                {"Type": "CHILD", "Ids": ["kw"]},
                {"Type": "VALUE", "Ids": ["v1", "v2"]},
            ],
        },
    ]
    extractor = TextractFullExtractor(blocks)
    fields = extractor.extract()
    assert fields["folio"] == "123"
