# services/ocr/gemini/ocr_service.py
"""Gemini based OCR service."""
import asyncio
from fastapi import UploadFile
from interfaces.ocr_service import OCRService
from models import OCRResponse
from .base import GeminiBaseService, genai


class GeminiOCRService(GeminiBaseService, OCRService):
    """Extract fields from documents using Gemini."""

    def __init__(self, api_key: str | None = None, model_name: str | None = None, prompt: str | None = None) -> None:
        super().__init__(api_key=api_key, model_name=model_name, prompt=prompt)
        self.prompt = (
            "Identifica y extra los datos precisos del fomulario. "
            "Devuelve un JSON con los campos y sus valores. Si no hay datos, "
            "devuelve un JSON vacío."
        )

    async def analyze(self, file: UploadFile) -> OCRResponse:
        self.logger.info("Analyzing file with Gemini: %s", file.filename)
        if not genai or not self.model:
            raise RuntimeError(
                "google-generativeai library is required for GeminiOCRService"
            )
        tmp_path = await self._save_temp_file(file)
        try:
            text = await asyncio.to_thread(
                self._generate_from_file, tmp_path, file.filename, self.prompt
            )
        finally:
            self._cleanup_temp_file(tmp_path)

        fields = self._parse_text(text)
        form_name = fields.pop("form_name", "")

        return OCRResponse(form_name=form_name, fields=fields)
