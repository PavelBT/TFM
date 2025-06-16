# app/services/ai_refiners/factory.py
import os
from ..interfaces.ai_refiner import AIRefiner
from .gpt_refiner import GPTRefiner
from .huggingface_refiner import HuggingFaceRefiner


def get_ai_refiner(refiner_type: str | None) -> AIRefiner | None:
    if not refiner_type:
        return None
    refiner_type = refiner_type.lower()

    if refiner_type == "gpt":
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        return GPTRefiner(api_key=api_key, model=model)
    if refiner_type == "huggingface":
        model_name = os.getenv("HF_MODEL_NAME", "dreuxx26/Multilingual-grammar-Corrector-using-mT5-small")
        return HuggingFaceRefiner(model_name=model_name)

    raise ValueError(f"[AIRefinerFactory] Tipo de refinador no soportado: '{refiner_type}'")
