"""HuggingFace based refiner used for grammar correction."""

import logging
logging.basicConfig(level=logging.INFO)

from transformers import pipeline
from typing import Dict
from interfaces.ai_refiner import AIRefiner

class HuggingFaceRefiner(AIRefiner):
    """
    Refinador basado en modelo T5 ajustado a español para corrección ortográfica y de estilo.
    """
    def __init__(self, model_name="dreuxx26/Multilingual-grammar-Corrector-using-mT5-small"):
        print(f"[IA] Cargando modelo: {model_name}")
        self.corrector = pipeline("text2text-generation", model=model_name, tokenizer=model_name)

    def refine(self, fields: Dict[str, str]) -> Dict[str, str]:
        refined = {}

        for key, value in fields.items():
            if not value or len(value.strip()) < 2:
                refined[key] = value
                continue

            try:
                # Prompt compatible con T5
                prompt = f"corregir: {value}"
                result = self.corrector(prompt, max_length=128, do_sample=False)
                output = result[0]['generated_text'].strip()
                logging.info(f"[IA] {key} - ORIG: {value} → CORREGIDO: {output}")
                refined[key] = result[0]['generated_text'].strip()

            except Exception as e:
                logging.warning(f"Error al refinar campo '{key}': {e}")
                refined[key] = value

        return refined
