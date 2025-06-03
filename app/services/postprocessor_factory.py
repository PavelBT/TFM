# Ruta: services/postprocessor_factory.py

from services.postprocessor import StructuredPostProcessor
from services.postprocessors.banorte_credito import BanorteCreditoPostProcessor


def get_postprocessor(refiner_type: str, form_type: str = None):
    if form_type == "banorte_credito":
        return BanorteCreditoPostProcessor(refiner_type=refiner_type)
    # Placeholder para otros formularios en el futuro
    return StructuredPostProcessor(refiner_type=refiner_type)