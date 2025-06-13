# Ruta: services/postprocessor_factory.py

from services.field_correctors.generic_cleaner import GenericFieldCleaner
from services.postprocessors.form_postprocessor.banorte_credito import BanorteCreditoPostProcessor


def get_postprocessor(form_type: str = None):
    if form_type == "banorte_credito":
        return BanorteCreditoPostProcessor()
    # Placeholder para otros formularios en el futuro
    return GenericFieldCleaner()
