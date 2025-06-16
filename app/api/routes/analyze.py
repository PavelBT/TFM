# app/api/routes/analyze.py
import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from models.ocr_response import OCRResponse
from services.ocr_service_manager import OCRServiceManager

SERVICE_NAME = os.getenv("OCR_SERVICE", "aws")
REFINER_TYPE = os.getenv("REFINER_TYPE")

router = APIRouter()
ocr_manager = OCRServiceManager(SERVICE_NAME, REFINER_TYPE)


@router.post("/analyze", response_model=OCRResponse)
async def analyze_document(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded.")
    return await ocr_manager.analyze(file)
