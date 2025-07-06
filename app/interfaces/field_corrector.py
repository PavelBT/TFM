# app/interfaces/field_corrector.py
from abc import ABC, abstractmethod
from typing import Optional, Any


class FieldCorrector(ABC):
    """Interfaz para aplicar correcciones a valores individuales."""

    @abstractmethod
    def correct(self, key: str, value: Any) -> Optional[str]:
        """Recibe el nombre del campo y retorna el valor corregido o None."""
        pass
