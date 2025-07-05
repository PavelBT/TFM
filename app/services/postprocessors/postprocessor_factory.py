from interfaces.postprocessor import PostProcessor
from .basic_postprocessor import BasicPostProcessor
from .form_postprocessor.banorte_credito_postprocessor import BanorteCreditoPostProcessor
from .form_postprocessor.banorte_hipotecario_postprocessor import BanorteHipotecarioPostProcessor


def get_postprocessor(form_type: str) -> PostProcessor:
    if form_type == "credito_personal":
        return BanorteCreditoPostProcessor()
    if form_type == "credito_hipotecario":
        return BanorteHipotecarioPostProcessor()
    return BasicPostProcessor()
