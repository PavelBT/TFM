# app/interfaces/ocr_service.py
from abc import ABC, abstractmethod
from fastapi import UploadFile
from models import OCRResponse


class OCRService(ABC):
    @abstractmethod
    async def analyze(self, file: UploadFile) -> OCRResponse:
        """Procesa un archivo y retorna los datos extraídos"""
        pass
