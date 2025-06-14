"""Asynchronous wrapper around AWS Textract for OCR extraction.

This service uploads the received file to S3 and launches a Textract analysis
job. When the job finishes the detected blocks are post processed to extract
key/value pairs. All blocking operations are executed in a thread pool to avoid
blocking the event loop.
"""
# app/services/aws_textract.py
import magic
import time
import asyncio
from fastapi.concurrency import run_in_threadpool
from models.data_response import DataResponse
from fastapi import UploadFile
from interfaces.ocr_service import OCRService
from services.storage.s3_uploader import S3Uploader
from services.ocr.form_identifier import FormIdentifier
from services.ocr.textract.textract_extractor import TextractExtractor

class AWSTextractOCRService(OCRService):
    
    def __init__(self, region_name="us-east-2", bucket_name="ocr-bucket-pbt-devop"):
        import boto3
        self.client = boto3.client("textract", region_name=region_name)
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

        # Subir archivo a S3 sin bloquear el loop
        await run_in_threadpool(self.uploader.upload_file, contents, s3_key)

        if is_pdf:
            start_response = await run_in_threadpool(
                self.client.start_document_analysis,
                DocumentLocation={"S3Object": {"Bucket": self.bucket, "Name": s3_key}},
                FeatureTypes=["FORMS"]
            )
            job_id = start_response["JobId"]

            status = "IN_PROGRESS"
            tries = 0
            result = {}
            while status == "IN_PROGRESS" and tries < 20:
                await asyncio.sleep(3)
                result = await run_in_threadpool(
                    self.client.get_document_analysis, JobId=job_id
                )
                status = result["JobStatus"]
                tries += 1

            if status != "SUCCEEDED":
                raise RuntimeError(f"Textract job failed with status: {status}")

            blocks = result.get("Blocks", [])
            next_token = result.get("NextToken")
            while next_token:
                result = await run_in_threadpool(
                    self.client.get_document_analysis,
                    JobId=job_id,
                    NextToken=next_token,
                )
                blocks.extend(result.get("Blocks", []))
                next_token = result.get("NextToken")
        else:
            result = await run_in_threadpool(
                self.client.analyze_document,
                Document={"Bytes": contents},
                FeatureTypes=["FORMS"]
            )
            blocks = result.get("Blocks", [])
            next_token = result.get("NextToken")
            while next_token:
                result = await run_in_threadpool(
                    self.client.analyze_document,
                    Document={"Bytes": contents},
                    FeatureTypes=["FORMS"],
                    NextToken=next_token,
                )
                blocks.extend(result.get("Blocks", []))
                next_token = result.get("NextToken")

        # Detectar tipo de formulario
        form_type = FormIdentifier.identify_form(blocks) or "desconocido"

        # Renombrar el archivo con tipo correcto y re-subirlo
        new_s3_key = f"uploads/{form_type}-{timestamp}-{base_name}"
        await run_in_threadpool(self.uploader.upload_file, contents, new_s3_key)
        # Eliminar el archivo temporal
        await run_in_threadpool(self.uploader.delete_file, s3_key)

        # USAMOS el extractor
        extractor = TextractExtractor(blocks)
        fields = extractor.extract()

        return {
            "form_type": form_type,
            "file_name": new_s3_key,
            "fields": fields
            
        }
