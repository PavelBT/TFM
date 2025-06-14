# Ruta: services/postprocessor_factory.py

from services.postprocessors.generic_postprocessor import GenericPostProcessor

def get_postprocessor(form_type: str = None):
    return GenericPostProcessor()
