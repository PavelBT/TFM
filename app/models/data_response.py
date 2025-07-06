from typing import Dict, Any
from pydantic import BaseModel


class DataResponse(BaseModel):
    form_type: str
    filename: str
    # Use a generic mapping for fields returned to clients
    fields: Dict[str, Any]
