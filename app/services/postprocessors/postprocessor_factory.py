# Ruta: services/postprocessor_factory.py

from services.postprocessors.generic_postprocessor import GenericPostProcessor
from services.postprocessors.form_postprocessor import BanorteCreditoPostProcessor

def get_postprocessor(form_type: str = None):
    if form_type == "banorte_credito":
        return BanorteCreditoPostProcessor()
    return GenericPostProcessor()
