# app/api/routes/analyze.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from services.ocr.factory import get_ocr_service
from models.data_response import DataResponse
from services.postprocessors.postprocessor import StructuredPostProcessor
import os

# Leer configuraciones de variables de entorno con valores por defecto
service_name = os.getenv("OCR_SERVICE", "aws")
refiner_type = os.getenv("REFINER_TYPE", "gpt")

router = APIRouter()

@router.post("/analyze", response_model=DataResponse)
async def analyze_document(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded.")
    
    # exteaccion por servicio de OCR
    service = get_ocr_service(service_name)
    data = await service.analyze(file)


    if "fields" not in data:
        raise HTTPException(status_code=500, detail="No fields extracted from the document.")
    else:
        # postprocesamiento de los campos extraídos
        processor = StructuredPostProcessor(data=data, refiner_type=refiner_type)
        processed_fields = processor.process()
        return processed_fields
