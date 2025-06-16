# app/services/ai_refiners/huggingface_refiner.py
from typing import Dict
from transformers import pipeline
from interfaces.ai_refiner import AIRefiner
from services.utils.logger import get_logger


class HuggingFaceRefiner(AIRefiner):
    """Refinador basado en modelo T5 ajustado a español para corrección."""

    def __init__(self, model_name: str = "dreuxx26/Multilingual-grammar-Corrector-using-mT5-small"):
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info("Cargando modelo: %s", model_name)
        self.corrector = pipeline("text2text-generation", model=model_name, tokenizer=model_name)

    def refine(self, fields: Dict[str, str]) -> Dict[str, str]:
        refined = {}
        for key, value in fields.items():
            if not value or len(value.strip()) < 2:
                refined[key] = value
                continue
            try:
                prompt = f"corregir: {value}"
                result = self.corrector(prompt, max_length=128, do_sample=False)
                output = result[0]["generated_text"].strip()
                self.logger.info("%s - ORIG: %s → CORREGIDO: %s", key, value, output)
                refined[key] = output
            except Exception as e:
                self.logger.warning("Error al refinar campo '%s': %s", key, e)
                refined[key] = value
        return refined

