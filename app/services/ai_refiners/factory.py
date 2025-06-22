# app/services/ai_refiners/factory.py
from interfaces.ai_refiner import AIRefiner
import os
from services.ai_refiners.remote_refiner import RemoteRefiner


def get_ai_refiner(_: str | None = None) -> AIRefiner:
    """Return the remote refiner pointing to the ai_models service."""
    base_url = os.getenv("AI_MODELS_URL", "http://ai_models:8080")
    return RemoteRefiner(base_url=base_url)


