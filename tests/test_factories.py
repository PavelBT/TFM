import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
import types
sys.modules.setdefault("magic", types.SimpleNamespace(from_buffer=lambda *a, **k: "application/pdf"))

class _DummyClient:
    def put_object(self, **kwargs):
        pass
    def delete_object(self, **kwargs):
        pass

def _dummy_client(service, *a, **k):
    return _DummyClient()

sys.modules.setdefault("boto3", types.SimpleNamespace(client=_dummy_client))
sys.modules.setdefault("aioboto3", types.SimpleNamespace(client=_dummy_client))
sys.modules.setdefault("openai", types.ModuleType("openai"))
sys.modules.setdefault(
    "transformers",
    types.SimpleNamespace(pipeline=lambda *a, **k: lambda *args, **kwargs: [])
)

from services.ocr.factory import get_ocr_service
from services.ai_refiners.factory import get_ai_refiner
from services.ocr.textract.textract_ocr import AWSTextractOCRService
from services.ai_refiners.gpt_refiner import GPTRefiner
from services.ai_refiners.huggingface_refiner import HuggingFaceRefiner
from services.postprocessors.postprocessor_factory import get_postprocessor
from services.postprocessors.form_postprocessor.banorte_credito import BanorteCreditoPostProcessor


def test_get_ocr_service_default():
    service = get_ocr_service("aws")
    assert isinstance(service, AWSTextractOCRService)


def test_get_ocr_service_unknown():
    with pytest.raises(NotImplementedError):
        get_ocr_service("unknown")


def test_get_ai_refiner_gpt(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    refiner = get_ai_refiner("gpt")
    assert isinstance(refiner, GPTRefiner)


def test_get_ai_refiner_huggingface():
    refiner = get_ai_refiner("huggingface")
    assert isinstance(refiner, HuggingFaceRefiner)


def test_get_ai_refiner_invalid():
    with pytest.raises(ValueError):
        get_ai_refiner("invalid")


def test_get_postprocessor_banorte_credito():
    processor = get_postprocessor("banorte_credito")
    assert isinstance(processor, BanorteCreditoPostProcessor)
