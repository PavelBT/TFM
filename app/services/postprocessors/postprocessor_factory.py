from interfaces.postprocessor import PostProcessor
from .basic_postprocessor import BasicPostProcessor
from .form_postprocessor.banorte_credito_postprocessor import BanorteCreditoPostProcessor


def get_postprocessor(form_type: str) -> PostProcessor:
    if form_type == "credito_personal":  # validate this form type
        return BanorteCreditoPostProcessor()
    return BasicPostProcessor()
