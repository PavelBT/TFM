# app/services/aws_textract.py
import magic
import time
from typing import Dict
from fastapi import UploadFile
from interfaces.ocr_service import OCRService
from services.postprocessor_factory import get_postprocessor
from services.storage.s3_uploader import S3Uploader
from services.ocr.form_identifier import FormIdentifier

class AWSTextractOCRService(OCRService):
    def __init__(self, region_name="us-east-2", bucket_name="ocr-bucket-pbt-devop"):
        import boto3
        self.client = boto3.client("textract", region_name=region_name)
        self.bucket = bucket_name
        self.uploader = S3Uploader(bucket_name, region_name)

    async def analyze(self, file: UploadFile) -> Dict:
        contents = await file.read()
        mime_type = magic.from_buffer(contents, mime=True)
        is_pdf = mime_type == "application/pdf"

        # Construir nombre preliminar único
        timestamp = time.strftime("%Y%m%dT%H%M%SZ")
        base_name = file.filename.replace(" ", "_")
        s3_key = f"uploads/tmp-{timestamp}-{base_name}"

        # Subir archivo a S3
        self.uploader.upload_file(contents, s3_key)

        if is_pdf:
            start_response = self.client.start_document_analysis(
                DocumentLocation={"S3Object": {"Bucket": self.bucket, "Name": s3_key}},
                FeatureTypes=["FORMS"]
            )
            job_id = start_response["JobId"]

            status = "IN_PROGRESS"
            tries = 0
            while status == "IN_PROGRESS" and tries < 20:
                time.sleep(3)
                result = self.client.get_document_analysis(JobId=job_id)
                status = result["JobStatus"]
                tries += 1

            if status != "SUCCEEDED":
                raise RuntimeError(f"Textract job failed with status: {status}")

            blocks = result.get("Blocks", [])
        else:
            result = self.client.analyze_document(
                Document={"Bytes": contents},
                FeatureTypes=["FORMS"]
            )
            blocks = result.get("Blocks", [])

        # Detectar tipo de formulario
        form_type = FormIdentifier.identify_form(blocks) or "desconocido"

        # Renombrar el archivo con tipo correcto y re-subirlo
        new_s3_key = f"uploads/{form_type}-{timestamp}-{base_name}"
        self.uploader.upload_file(contents, new_s3_key)

        # Extraer campos
        fields = self._extract_fields(blocks)

        # Postprocesamiento con selector adecuado
        processor = get_postprocessor(refiner_type="gpt", form_type=form_type)
        cleaned_fields = processor.process(fields)

        return {
            "fields": cleaned_fields,
            "file_name": new_s3_key,
            "form_type": form_type
        }

    def _extract_fields(self, blocks: list) -> Dict[str, str]:
        key_map = {}
        value_map = {}
        block_map = {}

        for block in blocks:
            block_id = block["Id"]
            block_map[block_id] = block
            if block["BlockType"] == "KEY_VALUE_SET":
                if "KEY" in block.get("EntityTypes", []):
                    key_map[block_id] = block
                elif "VALUE" in block.get("EntityTypes", []):
                    value_map[block_id] = block

        field_dict = {}
        for key_block_id, key_block in key_map.items():
            key_text = self._get_text(key_block, block_map)
            value_text = ""

            for relationship in key_block.get("Relationships", []):
                if relationship["Type"] == "VALUE":
                    for value_id in relationship["Ids"]:
                        value_block = value_map.get(value_id)
                        if value_block:
                            value_text = self._get_text(value_block, block_map)

            if key_text:
                field_dict[key_text] = value_text

        return field_dict

    def _get_text(self, block: dict, block_map: dict) -> str:
        text = ""
        for rel in block.get("Relationships", []):
            if rel["Type"] == "CHILD":
                for child_id in rel["Ids"]:
                    word = block_map[child_id]
                    if word["BlockType"] == "WORD":
                        text += word["Text"] + " "
                    elif word["BlockType"] == "SELECTION_ELEMENT" and word["SelectionStatus"] == "SELECTED":
                        text += "[X] "
        return text.strip()