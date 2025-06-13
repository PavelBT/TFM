"""Asynchronous wrapper around AWS Textract for OCR extraction.

This service uploads the received file to S3 and launches a Textract analysis
job. When the job finishes the detected blocks are post processed to extract
key/value pairs. Using :mod:`aioboto3` prevents blocking the event loop while we
wait for the Textract job to complete.
"""

import asyncio
import time
import magic
from models.data_response import DataResponse
from fastapi import UploadFile
from interfaces.ocr_service import OCRService
from services.storage.s3_uploader import S3Uploader
from services.ocr.form_identifier import FormIdentifier
from services.ocr.textract.textract_extractor import TextractFullExtractor
import aioboto3

class AWSTextractOCRService(OCRService):
    """Service that orchestrates OCR extraction using AWS Textract."""

    def __init__(self, region_name: str = "us-east-2", bucket_name: str = "ocr-bucket-pbt-devop"):
        self.region = region_name
        self.bucket = bucket_name
        self.uploader = S3Uploader(bucket_name, region_name)

    async def analyze(self, file: UploadFile) -> DataResponse:
        contents = await file.read()
        mime_type = magic.from_buffer(contents, mime=True)
        is_pdf = mime_type == "application/pdf"

        # Construir nombre preliminar único
        timestamp = time.strftime("%Y%m%dT%H%M%SZ")
        base_name = file.filename.replace(" ", "_")
        s3_key = f"uploads/tmp-{timestamp}-{base_name}"

        # Subir archivo a S3
        self.uploader.upload_file(contents, s3_key)

        async with aioboto3.client("textract", region_name=self.region) as client:
            if is_pdf:
                start_response = await client.start_document_analysis(
                    DocumentLocation={"S3Object": {"Bucket": self.bucket, "Name": s3_key}},
                    FeatureTypes=["FORMS"]
                )
                job_id = start_response["JobId"]

                status = "IN_PROGRESS"
                tries = 0
                result = None
                while status == "IN_PROGRESS" and tries < 20:
                    await asyncio.sleep(3)
                    result = await client.get_document_analysis(JobId=job_id)
                    status = result["JobStatus"]
                    tries += 1

                if status != "SUCCEEDED":
                    raise RuntimeError(f"Textract job failed with status: {status}")

                blocks = result.get("Blocks", []) if result else []
            else:
                result = await client.analyze_document(
                    Document={"Bytes": contents},
                    FeatureTypes=["FORMS"]
                )
                blocks = result.get("Blocks", [])

        # Detectar tipo de formulario
        form_type = FormIdentifier.identify_form(blocks) or "desconocido"

        # Renombrar el archivo con tipo correcto y re-subirlo
        new_s3_key = f"uploads/{form_type}-{timestamp}-{base_name}"
        self.uploader.upload_file(contents, new_s3_key)
        # Eliminar el archivo temporal
        self.uploader.delete_file(s3_key)

        # USAMOS el extractor
        extractor = TextractFullExtractor(blocks)
        fields = extractor.extract()

        return {
            "form_type": form_type,
            "file_name": new_s3_key,
            "fields": fields
            
        }
