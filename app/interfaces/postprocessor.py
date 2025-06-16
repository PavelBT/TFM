# app/interfaces/postprocessor.py
from abc import ABC, abstractmethod
from typing import Dict


class PostProcessor(ABC):
    """Interfaz base para postprocesadores OCR."""

    @abstractmethod
    def process(self, fields: Dict[str, str]) -> Dict:
        """Procesa los resultados planos del OCR."""
        pass
