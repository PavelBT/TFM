from interfaces.postprocessor import PostProcessor
from .basic_postprocessor import BasicPostProcessor
from .structured_output_postprocessor import StructuredOutputPostProcessor


def get_postprocessor(structured: bool = True, refiner_type: str | None = None) -> PostProcessor:
    if structured:
        return StructuredOutputPostProcessor(refiner_type)
    return BasicPostProcessor()
