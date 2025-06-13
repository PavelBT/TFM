import logging
from models.data_response import DataResponse
from interfaces.postprocessor import PostProcessor
from services.postprocessors.postprocessor_factory import get_postprocessor
from services.ai_refiners.factory import get_ai_refiner

class StructuredPostProcessor(PostProcessor):
    def __init__(self, data: DataResponse, refiner_type):
        self.data = data
        form_type = data.get("form_type", None)
        self.corrector = get_postprocessor(form_type)
        self.refiner = get_ai_refiner(refiner_type)

    def _refine_section(self, section: str, content):
        """
        Intenta refinar una sección del formulario usando IA.
        En caso de fallo, devuelve el contenido original.
        """
        try:
            refined_result = self.refiner.refine({section: content})
            if isinstance(refined_result, dict) and section in refined_result:
                return refined_result[section]
            elif isinstance(refined_result, dict) and refined_result:
                return next(iter(refined_result.values()))
            else:
                return content
        except Exception as e:
            logging.warning(f"[PostProcessor] Error al refinar sección '{section}': {e}")
            return content

    def process(self) -> DataResponse:
        fields = self.data.get("fields")
        structured = self.corrector.process(fields)

        for section, content in structured.items():
            if isinstance(content, (dict, str)):
                structured[section] = self._refine_section(section, content)

        self.data["fields"] = structured
        return self.data
