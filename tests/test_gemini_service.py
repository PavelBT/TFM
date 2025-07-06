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

from services.factory import get_ocr_service  # noqa: E402
from services.ocr.gemini.gemini_service import GeminiOCRService  # noqa: E402
from models import OCRResponse  # noqa: E402
from fastapi import UploadFile  # noqa: E402
from starlette.datastructures import Headers  # noqa: E402


def test_factory_returns_gemini():
    service = get_ocr_service('gemini')
    assert isinstance(service, GeminiOCRService)


def test_gemini_analyze(monkeypatch):
    mock_model = MagicMock()
    mock_response = MagicMock(text='hello')
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
    assert result.fields['text'] == 'hello'
    fake_genai.upload_file.assert_called()
    fake_genai.get_file.assert_called()
    mock_model.generate_content.assert_called()
