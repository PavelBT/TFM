# app/services/factory.py
import os
from services.ocr.gemini import GeminiOCRService
from services.ocr.textract import TextractOCRService
from interfaces.ocr_service import OCRService


def get_ocr_service(service: str | None = None) -> OCRService:
    """Return the configured OCR service."""

    name = (service or os.getenv("OCR_SERVICE", "gemini")).lower()
    if name == "textract":
        return TextractOCRService()
    return GeminiOCRService()
