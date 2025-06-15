import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
sys.modules.setdefault("openai", types.ModuleType("openai"))
sys.modules.setdefault(
    "transformers",
    types.SimpleNamespace(pipeline=lambda *a, **k: lambda *args, **kwargs: []),
)

from services.postprocessors.postprocessor import StructuredPostProcessor


class DummyPostProcessor:
    def process(self, fields):
        return fields


def test_structured_postprocessor_basic(monkeypatch):
    monkeypatch.setattr(
        "services.postprocessors.postprocessor.get_postprocessor",
        lambda form_type, structured=False: DummyPostProcessor(),
    )
    data = {"fields": {"a": "x", "b": "y"}}
    processor = StructuredPostProcessor(data)
    result = processor.process()

    assert result["fields"] == {"a": "x", "b": "y"}
