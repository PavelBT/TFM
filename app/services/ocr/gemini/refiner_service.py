# services/ocr/gemini/refiner_service.py
"""Gemini based refinement service."""
import asyncio
import json
from models import OCRResponse
from .base import GeminiBaseService, genai


class GeminiRefinerService(GeminiBaseService):
    """Refine OCR extracted fields using Gemini."""

    def __init__(self, api_key: str | None = None, model_name: str | None = None, prompt: str | None = None) -> None:
        super().__init__(api_key=api_key, model_name=model_name, prompt=prompt)
        self.refine_prompt = (
            "Refina el siguiente JSON extraído con OCR. "
            "Devuelve únicamente el JSON estructurado según las indicaciones."
            "Deberas parsear los campos de seleccion y checkbox como listas, "
            "por ejemplo: plazo de credito: 24 meses , si 24: SELECTED, estado civial: casado, si casado: SELECTED "
        )

    async def refine(self, fields: dict, prompt: str | None = None) -> OCRResponse:
        self.logger.info("Refining fields with Gemini")
        if not genai or not self.model:
            raise RuntimeError(
                "google-generativeai library is required for GeminiRefinerService"
            )
        payload = json.dumps(fields, ensure_ascii=False)
        user_prompt = prompt or self.refine_prompt
        text = await asyncio.to_thread(self._generate_from_text, payload, user_prompt)
        parsed = self._parse_text(text)
        form_name = parsed.pop("form_name", "")
        return OCRResponse(form_name=form_name, fields=parsed)
