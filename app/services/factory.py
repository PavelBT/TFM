# app/services/factory.py
from services.ocr.gemini import GeminiOCRService
from interfaces.ocr_service import OCRService


def get_ocr_service(service: str | None = None) -> OCRService:
    """Return the configured OCR service.

    Only Gemini is supported in this simplified version.
    """
    return GeminiOCRService()
