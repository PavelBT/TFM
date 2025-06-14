# app/api/routes/analyze.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from models.data_response import DataResponse
from services.ocr.ocr_processor import OCRProcessor
import os

# Leer configuraciones de variables de entorno con valores por defecto
service_name = os.getenv("OCR_SERVICE", "aws")
refiner_type = os.getenv("REFINER_TYPE", "gpt")

router = APIRouter()


@router.post("/analyze", response_model=DataResponse)
async def analyze_document(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    processor = OCRProcessor(service_name, refiner_type)
    result = await processor.process(file)
    return result
