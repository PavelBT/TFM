# app/interfaces/ai_refiner.py

from abc import ABC, abstractmethod
from typing import Dict


class AIRefiner(ABC):
    """
    Interfaz abstracta para aplicar modelos de IA que refinen campos OCR.
    El refinamiento incluye correcciones ortográficas, normalización,
    desambiguación o transformación semántica según el modelo usado.
    """

    @abstractmethod
    def refine(self, fields: Dict[str, str]) -> Dict[str, str]:
        """
        Recibe un diccionario de campos {clave: valor} extraídos del OCR
        y devuelve un nuevo diccionario con campos corregidos.
        """
        pass
