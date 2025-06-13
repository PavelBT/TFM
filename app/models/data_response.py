# app/models/data_response.py
from pydantic import BaseModel
from typing import Dict, Any

class DataResponse(BaseModel):
    form_type: str
    file_name: str
    fields: Dict[str, Any]
