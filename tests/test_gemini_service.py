from unittest.mock import MagicMock
import sys
import types
import asyncio
from io import BytesIO

# Provide fake generativeai module before importing the service
fake_genai = MagicMock()
fake_genai.types = MagicMock()
google_pkg = types.ModuleType('google')
google_pkg.generativeai = fake_genai
sys.modules.setdefault('google', google_pkg)
sys.modules.setdefault('google.generativeai', fake_genai)
sys.modules.setdefault('google.generativeai.types', fake_genai.types)
sys.modules.setdefault('magic', MagicMock())
sys.modules.setdefault('boto3', MagicMock())
sys.modules.setdefault('trp', MagicMock())

from services.factory import get_ocr_service  # noqa: E402
from services.ocr.gemini.gemini_service import GeminiOCRService  # noqa: E402
from services.ocr_processor import OCRProcessor  # noqa: E402
from models import OCRResponse  # noqa: E402
from fastapi import UploadFile  # noqa: E402
from starlette.datastructures import Headers  # noqa: E402


def test_factory_returns_gemini():
    service = get_ocr_service('gemini')
    assert isinstance(service, GeminiOCRService)


def test_gemini_analyze(monkeypatch):
    mock_model = MagicMock()
    mock_text = """```json\n{\n  \"datos personales\": [{\"label\": \"Nombre\", \"value\": \"Juan\"}]}\n```"""
    mock_response = MagicMock(text=mock_text)
    mock_model.generate_content.return_value = mock_response

    fake_file = MagicMock()
    fake_genai.upload_file.return_value = fake_file
    fake_genai.get_file.return_value = fake_file

    async def sync_to_thread(func, *a, **k):
        return func(*a, **k)

    monkeypatch.setattr(asyncio, "to_thread", sync_to_thread)

    service = GeminiOCRService(api_key='key')
    service.model = mock_model

    headers = Headers({'content-type': 'image/png'})
    upload = UploadFile(BytesIO(b'data'), filename='test.png', headers=headers)
    result = asyncio.run(service.analyze(upload))

    assert isinstance(result, OCRResponse)
    assert result.fields == {
        "datos personales": [{"label": "Nombre", "value": "Juan"}]
    }
    fake_genai.upload_file.assert_called()
    fake_genai.get_file.assert_called()
    mock_model.generate_content.assert_called()


def test_gemini_analyze_name_key(monkeypatch):
    mock_model = MagicMock()
    mock_text = """```json\n{\n  \"datos\": [{\"name\": \"Monto\", \"value\": \"100\"}]}\n```"""
    mock_response = MagicMock(text=mock_text)
    mock_model.generate_content.return_value = mock_response

    fake_file = MagicMock()
    fake_genai.upload_file.return_value = fake_file
    fake_genai.get_file.return_value = fake_file

    async def sync_to_thread(func, *a, **k):
        return func(*a, **k)

    monkeypatch.setattr(asyncio, "to_thread", sync_to_thread)

    service = GeminiOCRService(api_key='key')
    service.model = mock_model

    headers = Headers({'content-type': 'image/png'})
    upload = UploadFile(BytesIO(b'data'), filename='test.png', headers=headers)
    result = asyncio.run(service.analyze(upload))

    assert isinstance(result, OCRResponse)
    assert result.fields == {"datos": [{"name": "Monto", "value": "100"}]}
    fake_genai.upload_file.assert_called()
    fake_genai.get_file.assert_called()
    mock_model.generate_content.assert_called()


def test_processor_cleans_fields(monkeypatch):
    mock_model = MagicMock()
    mock_text = """```json
{\n  \"datos\": [{\"label\": \"Nombre\", \"value\": \"Ana\"}]}\n```"""
    mock_response = MagicMock(text=mock_text)
    mock_model.generate_content.return_value = mock_response

    fake_file = MagicMock()
    fake_genai.upload_file.return_value = fake_file
    fake_genai.get_file.return_value = fake_file

    async def sync_to_thread(func, *a, **k):
        return func(*a, **k)

    monkeypatch.setattr(asyncio, "to_thread", sync_to_thread)

    service = GeminiOCRService(api_key='key')
    service.model = mock_model

    def get_service(name=None):
        return service

    monkeypatch.setattr("services.ocr_processor.get_ocr_service", get_service)

    headers = Headers({'content-type': 'image/png'})
    upload = UploadFile(BytesIO(b'data'), filename='test.png', headers=headers)

    processor = OCRProcessor()
    result = asyncio.run(processor.analyze(upload))

    assert result == {"form_type": "", "fields": {"Nombre": "Ana"}}
