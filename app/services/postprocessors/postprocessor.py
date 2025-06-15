"""Helpers to post-process OCR results into structured data."""

import logging
from models.data_response import DataResponse
from interfaces.postprocessor import PostProcessor
from services.postprocessors.postprocessor_factory import get_postprocessor
from services.ai_refiners.factory import get_ai_refiner

class StructuredPostProcessor(PostProcessor):
    def __init__(self, data: DataResponse, refiner_type, structured_output: bool = False):
        self.data = data
        form_type = data.get("form_type", None)
        self.corrector = get_postprocessor(form_type, structured=structured_output)
        self.refiner = get_ai_refiner(refiner_type)
        self.structured_output = structured_output


    def _refine_section(self, section: str, content):
        """Refina una sección del formulario usando IA."""
        try:
            refined_result = self.refiner.refine({section: content})
            if isinstance(refined_result, dict) and section in refined_result:
                return refined_result[section]
            elif isinstance(refined_result, dict) and refined_result:
                return next(iter(refined_result.values()))
        except Exception as e:
            logging.warning(
                f"[PostProcessor] Error al refinar sección '{section}': {e}"
            )
        return content

    def process(self) -> DataResponse:
        fields = self.data.get("fields")
        structured = self.corrector.process(fields)

        if self.structured_output:
            for section, content in structured.items():
                structured[section] = self._refine_section(section, content)
        else:
            try:
                refined = self.refiner.refine(structured)
                if isinstance(refined, dict):
                    structured.update(refined)
            except Exception as e:
                logging.warning(f"[PostProcessor] Error al refinar campos: {e}")

        self.data["fields"] = structured
        return self.data
