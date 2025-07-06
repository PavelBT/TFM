from unittest.mock import MagicMock
import sys
import types
import asyncio
from io import BytesIO

# Provide fake generativeai module before importing the service
fake_genai = MagicMock()
google_pkg = types.ModuleType('google')
google_pkg.generativeai = fake_genai
sys.modules.setdefault('google', google_pkg)
sys.modules.setdefault('google.generativeai', fake_genai)
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

    service = GeminiOCRService(api_key='key')
    service.model = mock_model

    headers = Headers({'content-type': 'image/png'})
    upload = UploadFile(BytesIO(b'data'), filename='test.png', headers=headers)
    result = asyncio.run(service.analyze(upload))

    assert isinstance(result, OCRResponse)
    assert result.fields['text'] == 'hello'
