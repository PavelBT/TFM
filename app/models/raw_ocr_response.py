from typing import Any, Dict, List
from pydantic import BaseModel

class RawOCRResponse(BaseModel):
    """Raw output from OCR services."""

    blocks: List[Dict[str, Any]]
    s3_path: str
    mime_type: str
