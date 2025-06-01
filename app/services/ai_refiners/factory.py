# app/services/ai_refiners/factory.py

from interfaces.ai_refiner import AIRefiner
from services.ai_refiners.gpt_refiner import GPTRefiner
from services.ai_refiners.huggingface_refiner import HuggingFaceRefiner
import os

def get_ai_refiner(refiner_type) -> AIRefiner:
    refiner_type = refiner_type.lower()

    if refiner_type == "gpt":
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        return GPTRefiner(api_key=api_key, model=model)

    elif refiner_type == "huggingface":
        model_name = os.getenv("HF_MODEL_NAME", "dreuxx26/Multilingual-grammar-Corrector-using-mT5-small")
        return HuggingFaceRefiner(model_name=model_name)

    else:
        raise ValueError(f"[AIRefinerFactory] Tipo de refinador no soportado: '{refiner_type}'")