from fastapi import UploadFile
from models.data_response import DataResponse
from services.ocr.factory import get_ocr_service
from services.ocr.textract.ocrtextract import OcrTextract
from services.postprocessors.postprocessor import StructuredPostProcessor
from services.ai_refiners.factory import get_ai_refiner
import logging


class OCRProcessor:
    """Orchestrates OCR extraction and post-processing."""

    def __init__(self, service_name: str, refiner_type: str | None = None):
        self.service_name = service_name
        self.refiner_type = refiner_type
        self.service = get_ocr_service(self.service_name)

    async def process(self, file: UploadFile) -> DataResponse:
        if self.service_name == "aws":
            pipeline = OcrTextract()
            result = await pipeline.process(file)
        else:
            raise NotImplementedError(
                f"OCR service '{self.service_name}' is not supported"
            )

        # always clean and structure fields
        post = StructuredPostProcessor(result)
        result = post.process()

        # optional AI refinement of structured fields
        if self.refiner_type:
            try:
                refiner = get_ai_refiner(self.refiner_type)
                refined = refiner.refine(result.fields)
                if isinstance(refined, dict):
                    result.fields.update(refined)
            except Exception as e:
                logging.warning(f"[OCRProcessor] Error refining fields: {e}")

        return result
