from typing import Dict, Union
from pydantic import BaseModel


class DataResponse(BaseModel):
    form_type: str
    filename: str
    fields: Dict[str, Union[str, Dict[str, str], int, float, None]]
