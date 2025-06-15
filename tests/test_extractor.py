import sys
import json
from pathlib import Path
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

sys.modules.setdefault("magic", types.SimpleNamespace(from_buffer=lambda *a, **k: "application/pdf"))

from services.ocr.textract.textract_block_parser import TextractBlockParser


def test_textract_extractor_fields():
    with open(Path(__file__).resolve().parents[1] / "app" / "examples" / "analyzeDocResponse.json") as f:
        blocks = json.load(f)["Blocks"]
    extractor = TextractBlockParser(blocks)
    fields = extractor.extract()
    assert "folio" in fields
    assert len(fields) > 0


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
    extractor = TextractBlockParser(blocks)
    fields = extractor.extract()
    assert fields["casado"] == "Sí"




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
    extractor = TextractBlockParser(blocks)
    fields = extractor.extract()
    assert fields["folio"] == "123"


def test_line_fallback_supplements_missing_values():
    blocks = [
        {"Id": "kw", "BlockType": "WORD", "Text": "E-mail"},
        {"Id": "k1", "BlockType": "KEY_VALUE_SET", "EntityTypes": ["KEY"], "Relationships": [{"Type": "CHILD", "Ids": ["kw"]}]},
        {"Id": "l1", "BlockType": "LINE", "Text": "E-mail: user@example.com"},
    ]
    extractor = TextractBlockParser(blocks, use_line_fallback=True)
    fields = extractor.extract()
    assert fields["email"] == "user@example.com"

