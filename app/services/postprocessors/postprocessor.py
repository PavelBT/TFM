"""Helpers to post-process OCR results into structured data."""

from typing import Any, Dict, Union

from models.data_response import DataResponse
from interfaces.postprocessor import PostProcessor
from services.postprocessors.postprocessor_factory import get_postprocessor

class StructuredPostProcessor(PostProcessor):
    """Apply post-processing rules to OCR output."""

    def __init__(self, data: Union[DataResponse, Dict[str, Any]], structured_output: bool = False):
        self.data = data
        if isinstance(data, DataResponse):
            form_type = data.form_type
        else:
            form_type = data.get("form_type", None)
        self.corrector = get_postprocessor(form_type, structured=structured_output)
        self.structured_output = structured_output


    def process(self) -> Union[DataResponse, Dict[str, Any]]:
        if isinstance(self.data, DataResponse):
            fields = self.data.fields
        else:
            fields = self.data.get("fields")

        structured = self.corrector.process(fields)

        if isinstance(self.data, DataResponse):
            self.data.fields = structured
        else:
            self.data["fields"] = structured
        return self.data
