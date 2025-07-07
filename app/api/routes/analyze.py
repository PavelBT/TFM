from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from models.data_response import DataResponse
from services.ocr_processor import OCRProcessor

router = APIRouter()


@router.post("/analyze", response_model=DataResponse)
async def analyze_document(
    file: UploadFile = File(...),
    ocr_service: str | None = Form(None),
    use_refiner: bool | None = Form(None),
):
    """Analyze a document using the selected OCR service.

    This endpoint temporarily accepts ``ocr_service`` and ``use_refiner``
    parameters so that the front-end can choose between Gemini and
    Textract and optionally disable the refiner. Environment variables
    remain the fallback configuration.
    """

    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    processor = OCRProcessor(service_name=ocr_service, use_refiner=use_refiner)
    result = await processor.analyze(file)
    return DataResponse(
        form_type=result["form_type"],
        filename=file.filename,
        fields=result["fields"],
    )
