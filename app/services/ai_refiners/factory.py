# app/services/ai_refiners/factory.py
from interfaces.ai_refiner import AIRefiner
import os


def get_ai_refiner(refiner_type: str | None) -> AIRefiner | None:
    if not refiner_type:
        return None
    refiner_type = refiner_type.lower()

    if refiner_type == "gpt":
        from services.ai_refiners.gpt_refiner import GPTRefiner
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        return GPTRefiner(api_key=api_key, model=model)

    if refiner_type == "huggingface":
        from services.ai_refiners.huggingface_refiner import HuggingFaceRefiner
        model_name = os.getenv("HF_MODEL_NAME", "dreuxx26/Multilingual-grammar-Corrector-using-mT5-small")
        return HuggingFaceRefiner(model_name=model_name)


