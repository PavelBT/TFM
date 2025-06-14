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
