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


class DummyRefiner:
    def __init__(self):
        self.calls = []

    def refine(self, fields):
        self.calls.append(fields.copy())
        return {k: v.upper() for k, v in fields.items()}


def test_structured_postprocessor_single_refine(monkeypatch):
    dummy_refiner = DummyRefiner()
    monkeypatch.setattr(
        "services.postprocessors.postprocessor.get_postprocessor",
        lambda form_type, structured=False: DummyPostProcessor(),
    )
    monkeypatch.setattr(
        "services.postprocessors.postprocessor.get_ai_refiner",
        lambda refiner_type: dummy_refiner,
    )

    data = {"fields": {"a": "x", "b": "y"}}
    processor = StructuredPostProcessor(data, refiner_type="gpt")
    result = processor.process()

    assert result["fields"] == {"a": "X", "b": "Y"}
    assert len(dummy_refiner.calls) == 1
    assert dummy_refiner.calls[0] == {"a": "x", "b": "y"}
