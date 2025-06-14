"""Helpers to post-process OCR results into structured data."""

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
        sources = self.data.get("sources")
        sections = self.data.get("sections")
        structured = self.corrector.process(fields)

        try:
            refined = self.refiner.refine(structured)
            if isinstance(refined, dict):
                structured.update(refined)
        except Exception as e:
            logging.warning(f"[PostProcessor] Error al refinar campos: {e}")

        self.data["fields"] = structured
        if sources is not None:
            self.data["sources"] = sources
        if sections is not None:
            self.data["sections"] = sections
        return self.data
