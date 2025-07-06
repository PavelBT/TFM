# services/ocr/gemini/gemini_service.py
import os
import asyncio
from fastapi import UploadFile
from interfaces.ocr_service import OCRService
from models import OCRResponse
from services.utils.logger import get_logger

try:
    import google.generativeai as genai
except Exception:  # pragma: no cover - optional dependency may not be installed
    genai = None


class GeminiOCRService(OCRService):
    def __init__(self, api_key: str | None = None, model_name: str | None = None):
        self.logger = get_logger(self.__class__.__name__)
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "models/gemini-pro-vision")
        if genai:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        else:  # pragma: no cover - library not available
            self.model = None

    async def analyze(self, file: UploadFile) -> OCRResponse:
        self.logger.info("Analyzing file with Gemini: %s", file.filename)
        contents = await file.read()
        if not genai or not self.model:
            raise RuntimeError("google-generativeai library is required for GeminiOCRService")

        def _generate() -> str:
            response = self.model.generate_content([
                {"mime_type": file.content_type or "image/png", "data": contents}
            ])
            return getattr(response, "text", "")

        text = await asyncio.to_thread(_generate)
        return OCRResponse(form_name="text", fields={"text": text})
