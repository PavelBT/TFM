# app/interfaces/ai_refiner.py
from abc import ABC, abstractmethod
from typing import Dict


class AIRefiner(ABC):
    """Interfaz abstracta para modelos de refinamiento de texto OCR."""

    @abstractmethod
    def refine(self, fields: Dict[str, str]) -> Dict[str, str]:
        """Recibe un diccionario de campos y devuelve la versión refinada."""
        pass
