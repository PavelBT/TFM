# ai_models/app/interfaces/model_service.py
from abc import ABC, abstractmethod

class TextCorrectionService(ABC):
    @abstractmethod
    def correct(self, text: str) -> str:
        pass
