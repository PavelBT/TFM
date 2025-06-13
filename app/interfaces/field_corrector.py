# app/interfaces/field_corrector.py

from abc import ABC, abstractmethod
from typing import Optional

class FieldCorrector(ABC):
    """
    Interfaz abstracta para aplicar correcciones a valores individuales de campos OCR.
    """

    @abstractmethod
    def correct(self, key: str, value: str) -> Optional[str]:
        """
        Recibe el nombre de campo y su valor, y devuelve el valor corregido.
        Si se desea descartar el campo, puede retornar None.

        :param key: Nombre del campo OCR
        :param value: Valor extraído
        :return: Valor corregido o None si se descarta
        """
        pass
