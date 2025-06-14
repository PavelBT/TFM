# app/services/factory.py
from app.services.aws_textract import AWSTextractOCRService
from app.interfaces.ocr_service import OCRService

def get_ocr_service(service: str = "aws") -> OCRService:
    if service == "aws":
        return AWSTextractOCRService()
    else:
        raise NotImplementedError(
            f"OCR service '{service}' is not implemented yet."
        )

