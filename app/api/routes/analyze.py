from fastapi import APIRouter, UploadFile, File, HTTPException
from models.data_response import DataResponse
from services.ocr_processor import OCRProcessor

router = APIRouter()
processor = OCRProcessor()


@router.post("/analyze", response_model=DataResponse)
async def analyze_document(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded.")
    result = await processor.analyze(file)
    return DataResponse(form_type=result["form_type"], filename=file.filename, fields=result["fields"])
