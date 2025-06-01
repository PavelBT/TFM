# app/api/routes/analyze.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from services.factory import get_ocr_service
from models.ocr_response import OCRResponse

router = APIRouter()

@router.post("/analyze", response_model=OCRResponse)
async def analyze_document(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded.")
    
    service = get_ocr_service("aws")
    result = await service.analyze(file)
    return result