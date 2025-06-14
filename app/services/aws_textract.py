# app/services/aws_textract.py
import boto3
import magic
import json
import time
from pathlib import Path
from typing import Dict
from fastapi import UploadFile
from interfaces.ocr_service import OCRService

class AWSTextractOCRService(OCRService):
    def __init__(self, region_name="us-east-2", bucket_name="ocr-bucket-pbt-devop"):
        self.client = boto3.client("textract", region_name=region_name)
        self.s3 = boto3.client("s3", region_name=region_name)
        self.bucket = bucket_name

        dataset_path = Path(__file__).resolve().parents[1] / "training" / "textract_adapter_dataset.jsonl"
        queries = []
        try:
            with open(dataset_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    queries.extend(data.get("queries", []))
        except FileNotFoundError:
            queries = []

        # Textract permite un máximo de 30 consultas por petición. El dataset
        # incluye 33, por lo que limitamos la lista para evitar errores de
        # "InvalidParameterException" al llamar a StartDocumentAnalysis.
        self.queries = queries[:30]

    async def analyze(self, file: UploadFile) -> Dict:
        contents = await file.read()
        mime_type = magic.from_buffer(contents, mime=True)

        is_pdf = mime_type == "application/pdf"

        if is_pdf:
            # Subir a S3
            s3_key = f"uploads/{file.filename}"
            self.s3.put_object(Bucket=self.bucket, Key=s3_key, Body=contents)

            # Iniciar análisis asincrónico
            start_response = self.client.start_document_analysis(
                DocumentLocation={"S3Object": {"Bucket": self.bucket, "Name": s3_key}},
                FeatureTypes=["FORMS", "QUERIES"],
                QueriesConfig={"Queries": self.queries}
            )
            job_id = start_response["JobId"]

            # Esperar a que el análisis termine
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
            fields = self._extract_fields(blocks)
        
            # Eliminar después de procesar
            self.s3.delete_object(Bucket=self.bucket, Key=s3_key)

            return {"fields": fields}
        

        else:
            # Procesar como imagen directamente
            result = self.client.analyze_document(
                Document={"Bytes": contents},
                FeatureTypes=["FORMS", "QUERIES"],
                QueriesConfig={"Queries": self.queries}
            )
            fields = self._extract_fields(result.get("Blocks", []))
            return {"fields": fields}

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