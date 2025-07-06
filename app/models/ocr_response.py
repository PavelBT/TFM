# app/models/ocr_response.py
from pydantic import BaseModel
from typing import Dict, Any


class OCRResponse(BaseModel):
    form_name: str
    # Allow nested dictionaries or mixed value types extracted from OCR
    fields: Dict[str, Any]
