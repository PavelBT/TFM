# Ruta: services/postprocessor_factory.py

from services.postprocessors.generic_postprocessor import GenericPostProcessor
from services.postprocessors.form_postprocessor import BanorteCreditoPostProcessor
from services.postprocessors.structured_output_postprocessor import (
    StructuredOutputPostProcessor,
)
def get_postprocessor(form_type: str | None = None, structured: bool = False):
    """Return an appropriate postprocessor implementation."""

    if structured:
        return StructuredOutputPostProcessor()
    if form_type == "banorte_credito":
        return BanorteCreditoPostProcessor()
    return GenericPostProcessor()
