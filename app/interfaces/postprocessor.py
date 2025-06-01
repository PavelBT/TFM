# app/postprocessing/interfaces/postprocessor.py

from abc import ABC, abstractmethod
from typing import Dict

class PostProcessor(ABC):
    """
    Interfaz base para todos los postprocesadores de OCR.
    """

    @abstractmethod
    def process(self, fields: Dict[str, str]) -> Dict:
        """
        Procesa los resultados planos extraídos por OCR y devuelve una estructura limpia o enriquecida.

        :param fields: Diccionario plano de campos extraídos por OCR
        :return: Diccionario procesado y potencialmente estructurado
        """
        pass