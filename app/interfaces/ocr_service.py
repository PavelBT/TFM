# app/interfaces/ocr_service.py
from abc import ABC, abstractmethod
from typing import Dict
from fastapi import UploadFile

class OCRService(ABC):
    @abstractmethod
    async def analyze(self, file: UploadFile) -> Dict:
        """Procesa un archivo y retorna un diccionario con los datos extraídos"""
        pass
