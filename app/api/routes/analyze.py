# app/api/routes/analyze.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.factory import get_ocr_service
from app.models.ocr_response import OCRResponse
from app.services.postprocessor import StructuredPostProcessor

service_name = "aws"  # "aws"
refiner_type = "gpt"  # "gpt", "huggingface" or None

router = APIRouter()

@router.post("/analyze", response_model=OCRResponse)
async def analyze_document(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded.")
    
    service = get_ocr_service(service_name)
    raw_fields = await service.analyze(file)
    if refiner_type is None:
        return raw_fields
    else:
        processor = StructuredPostProcessor(refiner_type=refiner_type)
        processed_fields = processor.process(raw_fields["fields"])

        return {"fields": processed_fields}
