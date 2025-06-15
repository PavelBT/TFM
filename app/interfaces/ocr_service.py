# app/interfaces/ocr_service.py
"""Base interface for OCR implementations."""

from abc import ABC, abstractmethod
from typing import Dict
from models.raw_ocr_response import RawOCRResponse
from fastapi import UploadFile

class OCRService(ABC):
    @abstractmethod
    async def analyze(self, file: UploadFile) -> RawOCRResponse:
        """Procesa un archivo y retorna la salida cruda del OCR"""
        pass
