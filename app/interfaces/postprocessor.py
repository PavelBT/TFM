# app/postprocessing/interfaces/postprocessor.py

from abc import ABC, abstractmethod
from typing import Dict
from models.data_response import DataResponse

class PostProcessor(ABC):
    """
    Interfaz base para todos los postprocesadores de OCR.
    """

    @abstractmethod
    def process(self, data: DataResponse) -> DataResponse:
        """
        Procesa los resultados planos extraídos por OCR y devuelve una estructura limpia o enriquecida.

        :param data: Diccionario plano de campos extraídos por OCR
        :return: Diccionario procesado y potencialmente estructurado
        """
        pass
