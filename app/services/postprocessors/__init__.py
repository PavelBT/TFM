from .postprocessor_factory import get_postprocessor
from .basic_postprocessor import BasicPostProcessor
from .form_postprocessor.banorte_credito_postprocessor import BanorteCreditoPostProcessor
from .form_postprocessor.banorte_hipotecario_postprocessor import BanorteHipotecarioPostProcessor

__all__ = [
    "get_postprocessor",
    "BasicPostProcessor",
    "BanorteCreditoPostProcessor",
    "BanorteHipotecarioPostProcessor",
]
