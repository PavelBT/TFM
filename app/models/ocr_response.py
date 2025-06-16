# app/models/ocr_response.py
from pydantic import BaseModel
from typing import Dict, Union


class OCRResponse(BaseModel):
    form_name: str
    fields: Dict[str, Union[str, Dict[str, str]]]
