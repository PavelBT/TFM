# Ruta: services/postprocessor_factory.py

from services.postprocessors.basic_postprocessor import BasicPostProcessor
from services.postprocessors.structured_output_postprocessor import (
    StructuredOutputPostProcessor,
)


def get_postprocessor(form_type: str | None = None, structured: bool = False):
    """Return an appropriate postprocessor implementation."""

    if structured:
        return StructuredOutputPostProcessor()
    return BasicPostProcessor()
