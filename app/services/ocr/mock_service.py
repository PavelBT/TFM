from typing import Dict
from fastapi import UploadFile
from interfaces.ocr_service import OCRService

class MockOCRService(OCRService):
    """Simple OCR service used for testing or development."""

    async def analyze(self, file: UploadFile) -> Dict:
        contents = await file.read()
        return {"fields": {"mock_text": contents.decode(errors='ignore')}}
