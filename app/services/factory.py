# app/services/factory.py
"""Factory functions for OCR service implementations."""
from interfaces.ocr_service import OCRService
from services.ocr.aws_textract import AWSTextractOCRService
from services.ocr.mock_service import MockOCRService

_SERVICES = {
    "aws": AWSTextractOCRService,
    "mock": MockOCRService,
}

def get_ocr_service(service: str = "aws") -> OCRService:
    """Return an OCR service implementation."""
    try:
        return _SERVICES[service]()
    except KeyError:
        raise NotImplementedError(f"OCR service '{service}' is not implemented yet.")
