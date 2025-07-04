# app/services/factory.py
from services.ocr.textract.aws_service import AWSTextractOCRService
from interfaces.ocr_service import OCRService


def get_ocr_service(service: str = "aws") -> OCRService:
    if service == "aws":
        return AWSTextractOCRService()
    else:
        raise NotImplementedError(f"OCR service '{service}' is not implemented yet.")
