from unittest.mock import MagicMock
import sys
import types
import asyncio
from io import BytesIO

# Fake external modules before importing service
fake_genai = MagicMock()
fake_genai.types = MagicMock()
google_pkg = types.ModuleType('google')
google_pkg.generativeai = fake_genai
sys.modules.setdefault('google', google_pkg)
sys.modules.setdefault('google.generativeai', fake_genai)
sys.modules.setdefault('google.generativeai.types', fake_genai.types)
sys.modules.setdefault('magic', MagicMock())
fake_trp = types.ModuleType('trp')
sys.modules['trp'] = fake_trp

class DummyField:
    def __init__(self, key: str, value: str):
        self.key = types.SimpleNamespace(text=key)
        self.value = types.SimpleNamespace(text=value)

class DummyPage:
    def __init__(self, fields: list[DummyField]):
        self.form = types.SimpleNamespace(fields=fields)

class DummyDocument:
    def __init__(self, response):
        self.pages = [
            DummyPage([
                DummyField("Nombre", "Juan"),
                DummyField("Edad", "30"),
            ])
        ]

fake_trp.Document = DummyDocument

fake_boto3 = MagicMock()
fake_client = MagicMock()
fake_boto3.client.return_value = fake_client
sys.modules['boto3'] = fake_boto3

fake_trp = types.ModuleType('trp')

class _Field:
    def __init__(self, key, value):
        self.key = types.SimpleNamespace(text=key)
        self.value = types.SimpleNamespace(text=value)


class _Page:
    def __init__(self, fields):
        self.form = types.SimpleNamespace(fields=fields)


class Document:
    def __init__(self, response):
        self.pages = [_Page([_Field("Nombre", "Juan"), _Field("Edad", "30")])]


fake_trp.Document = Document
sys.modules['trp'] = fake_trp

import importlib
import services.ocr.textract.textract_service as textract_service_module
importlib.reload(textract_service_module)
import services.factory as factory_module
importlib.reload(factory_module)

from services.factory import get_ocr_service  # noqa: E402
from services.ocr.textract.textract_service import TextractOCRService  # noqa: E402
from services.ocr_processor import OCRProcessor  # noqa: E402
from models import OCRResponse  # noqa: E402
from fastapi import UploadFile  # noqa: E402
from starlette.datastructures import Headers  # noqa: E402

SAMPLE_RESPONSE = {
    "Blocks": [
        {"BlockType": "PAGE", "Id": "1", "Confidence": 99,
         "Geometry": {"BoundingBox": {"Width": 1, "Height": 1, "Left": 0, "Top": 0}, "Polygon": []}},
        {"BlockType": "WORD", "Id": "w1", "Text": "Nombre", "Confidence": 99,
         "Geometry": {"BoundingBox": {"Width": 0.1, "Height": 0.1, "Left": 0, "Top": 0}, "Polygon": []}},
        {"BlockType": "WORD", "Id": "w2", "Text": "Juan", "Confidence": 99,
         "Geometry": {"BoundingBox": {"Width": 0.1, "Height": 0.1, "Left": 0.2, "Top": 0}, "Polygon": []}},
        {"BlockType": "WORD", "Id": "w3", "Text": "Edad", "Confidence": 99,
         "Geometry": {"BoundingBox": {"Width": 0.1, "Height": 0.1, "Left": 0.3, "Top": 0}, "Polygon": []}},
        {"BlockType": "WORD", "Id": "w4", "Text": "30", "Confidence": 99,
         "Geometry": {"BoundingBox": {"Width": 0.1, "Height": 0.1, "Left": 0.4, "Top": 0}, "Polygon": []}},
        {"BlockType": "KEY_VALUE_SET", "Id": "kv1", "EntityTypes": ["KEY"], "Confidence": 99,
         "Geometry": {"BoundingBox": {"Width": 0.1, "Height": 0.1, "Left": 0, "Top": 0}, "Polygon": []},
         "Relationships": [{"Type": "VALUE", "Ids": ["kv2"]}, {"Type": "CHILD", "Ids": ["w1"]}]},
        {"BlockType": "KEY_VALUE_SET", "Id": "kv2", "EntityTypes": ["VALUE"], "Confidence": 99,
         "Geometry": {"BoundingBox": {"Width": 0.1, "Height": 0.1, "Left": 0.1, "Top": 0}, "Polygon": []},
         "Relationships": [{"Type": "CHILD", "Ids": ["w2"]}]},
        {"BlockType": "KEY_VALUE_SET", "Id": "kv3", "EntityTypes": ["KEY"], "Confidence": 99,
         "Geometry": {"BoundingBox": {"Width": 0.1, "Height": 0.1, "Left": 0.3, "Top": 0}, "Polygon": []},
         "Relationships": [{"Type": "VALUE", "Ids": ["kv4"]}, {"Type": "CHILD", "Ids": ["w3"]}]},
        {"BlockType": "KEY_VALUE_SET", "Id": "kv4", "EntityTypes": ["VALUE"], "Confidence": 99,
         "Geometry": {"BoundingBox": {"Width": 0.1, "Height": 0.1, "Left": 0.4, "Top": 0}, "Polygon": []},
         "Relationships": [{"Type": "CHILD", "Ids": ["w4"]}]},
    ],
    "DocumentMetadata": {"Pages": 1},
}


def test_factory_returns_textract():
    service = get_ocr_service("textract")
    assert service.__class__.__name__ == "TextractOCRService"


def test_textract_analyze(monkeypatch):
    fake_client.start_document_analysis.return_value = {"JobId": "1"}
    fake_client.get_document_analysis.return_value = {
        "JobStatus": "SUCCEEDED",
        **SAMPLE_RESPONSE,
    }

    service = TextractOCRService(bucket="bucket")

    async def sync_to_thread(func, *a, **k):
        return func(*a, **k)

    monkeypatch.setattr(asyncio, "to_thread", sync_to_thread)

    async def fake_sleep(*a, **k):
        return None

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    headers = Headers({"content-type": "application/pdf"})
    upload = UploadFile(BytesIO(b"data"), filename="test.pdf", headers=headers)
    result = asyncio.run(service.analyze(upload))

    assert isinstance(result, OCRResponse)
    assert result.fields == {"Nombre": "Juan", "Edad": "30"}
    fake_client.start_document_analysis.assert_called()
    fake_client.get_document_analysis.assert_called()
    fake_client.put_object.assert_called()
    fake_client.delete_object.assert_called()


def test_processor_with_textract(monkeypatch):
    fake_client.start_document_analysis.return_value = {"JobId": "1"}
    fake_client.get_document_analysis.return_value = {
        "JobStatus": "SUCCEEDED",
        **SAMPLE_RESPONSE,
    }
    service = TextractOCRService(bucket="bucket")

    def get_service(name=None):
        return service

    monkeypatch.setattr("services.ocr_processor.get_ocr_service", get_service)

    mock_refiner = MagicMock()

    async def refine(fields, prompt=None):
        return OCRResponse(form_name="credito", fields=fields)

    mock_refiner.refine.side_effect = refine

    monkeypatch.setattr(
        "services.ocr_processor.GeminiRefinerService", lambda *a, **k: mock_refiner
    )

    async def sync_to_thread(func, *a, **k):
        return func(*a, **k)

    monkeypatch.setattr(asyncio, "to_thread", sync_to_thread)

    async def fake_sleep(*a, **k):
        return None

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    headers = Headers({"content-type": "application/pdf"})
    upload = UploadFile(BytesIO(b"data"), filename="test.pdf", headers=headers)

    processor = OCRProcessor()
    result = asyncio.run(processor.analyze(upload))

    assert result == {"form_type": "credito", "fields": {"Nombre": "Juan", "Edad": "30"}}
    mock_refiner.refine.assert_called_with({"Nombre": "Juan", "Edad": "30"})
    fake_client.start_document_analysis.assert_called()
    fake_client.get_document_analysis.assert_called()
    fake_client.put_object.assert_called()
    fake_client.delete_object.assert_called()


def test_processor_with_textract_no_refiner(monkeypatch):
    """Refiner can be disabled via parameter."""
    fake_client.start_document_analysis.return_value = {"JobId": "1"}
    fake_client.get_document_analysis.return_value = {
        "JobStatus": "SUCCEEDED",
        **SAMPLE_RESPONSE,
    }
    service = TextractOCRService(bucket="bucket")

    def get_service(name=None):
        return service

    monkeypatch.setattr("services.ocr_processor.get_ocr_service", get_service)

    mock_refiner = MagicMock()
    monkeypatch.setattr(
        "services.ocr_processor.GeminiRefinerService", lambda *a, **k: mock_refiner
    )

    async def sync_to_thread(func, *a, **k):
        return func(*a, **k)

    monkeypatch.setattr(asyncio, "to_thread", sync_to_thread)

    async def fake_sleep(*a, **k):
        return None

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    headers = Headers({"content-type": "application/pdf"})
    upload = UploadFile(BytesIO(b"data"), filename="test.pdf", headers=headers)

    processor = OCRProcessor()
    result = asyncio.run(processor.analyze(upload, use_refiner=False))

    assert result == {"form_type": "", "fields": {"Nombre": "Juan", "Edad": "30"}}
    mock_refiner.refine.assert_not_called()
