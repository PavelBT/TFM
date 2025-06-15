from fastapi import UploadFile
from models.data_response import DataResponse
from services.ocr.form_identifier import FormIdentifier
from services.ocr.textract.textract_block_parser import TextractBlockParser
from services.ocr.textract.textract_layout_parser import TextractLayoutParser
from services.ocr.textract.textract_ocr import AWSTextractOCRService
from models.raw_ocr_response import RawOCRResponse


class OcrTextract:
    """Pipeline to process documents using AWS Textract."""

    def __init__(self):
        self.service = AWSTextractOCRService()

    async def process(self, file: UploadFile) -> DataResponse:
        ocr_result: RawOCRResponse = await self.service.analyze(file)
        blocks = ocr_result.blocks
        if not blocks:
            raise RuntimeError("Textract returned no blocks")

        form_type = FormIdentifier.identify_form(blocks) or "desconocido"

        parser = TextractBlockParser(blocks, use_line_fallback=True)
        fields = parser.extract()

        layout_parser = TextractLayoutParser(blocks)
        sections = layout_parser.parse()
        if sections:
            fields.update(sections)

        data = {
            "form_type": form_type,
            "file_name": ocr_result.s3_path,
            "fields": fields,
        }

        return DataResponse(**data)
