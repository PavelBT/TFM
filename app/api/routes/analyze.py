from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from models.data_response import DataResponse
from services.ocr_processor import OCRProcessor

router = APIRouter()
processor = OCRProcessor()


@router.post("/analyze", response_model=DataResponse)
async def analyze_document(
    file: UploadFile = File(...),
    ocr_service: str | None = Form(None),
    use_refiner: bool | None = Form(None),
):
    """Analyze a document using the selected OCR backend."""

    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    result = await processor.analyze(
        file, ocr_service=ocr_service, use_refiner=use_refiner
    )

    return DataResponse(
        form_type=result["form_type"],
        filename=file.filename,
        fields=result["fields"],
    )
