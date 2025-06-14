from fastapi import UploadFile
from models.data_response import DataResponse
from services.ocr.form_identifier import FormIdentifier
from services.ocr.textract.textract_block_parser import TextractBlockParser
from services.ocr.textract.textract_layout_parser import TextractLayoutParser
from services.ocr.textract.banorte_layout_parser import BanorteLayoutParser
from services.postprocessors.postprocessor import StructuredPostProcessor
from interfaces.ocr_service import OCRService


class OcrTextract:
    """Pipeline to process documents using AWS Textract."""

    def __init__(self, service: OCRService, refiner_type: str = "gpt", track_sources: bool = False):
        self.service = service
        self.refiner_type = refiner_type
        self.track_sources = track_sources

    async def process(self, file: UploadFile) -> DataResponse:
        ocr_result = await self.service.analyze(file)
        blocks = ocr_result.get("blocks", [])
        if not blocks:
            raise RuntimeError("Textract returned no blocks")

        form_type = FormIdentifier.identify_form(blocks) or "desconocido"

        parser = TextractBlockParser(
            blocks,
            track_sources=self.track_sources,
            use_line_fallback=True,
        )
        fields = parser.extract()
        sources = parser.get_sources() if self.track_sources else None

        layout_parser = TextractLayoutParser(blocks)
        sections = layout_parser.parse()
        if sections:
            fields.update(sections)
            ocr_result["sections"] = sections

        if form_type == "banorte_credito":
            banorte_parser = BanorteLayoutParser(blocks)
            extra = banorte_parser.parse()
            if extra:
                fields.update(extra)

        data = {
            "form_type": form_type,
            "file_name": ocr_result.get("s3_path"),
            "fields": fields,
            "sources": sources,
            "sections": ocr_result.get("sections"),
        }

        processor = StructuredPostProcessor(data=data, refiner_type=self.refiner_type)
        return processor.process()
