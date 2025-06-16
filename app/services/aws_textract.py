# app/services/aws_textract.py
import asyncio
import boto3
import magic
import tempfile
from typing import Dict
from fastapi import UploadFile
from ..interfaces.ocr_service import OCRService


class AWSTextractOCRService(OCRService):
    def __init__(self, region_name: str = "us-east-2", bucket_name: str = "ocr-bucket-pbt-devop"):
        self.client = boto3.client("textract", region_name=region_name)
        self.s3 = boto3.client("s3", region_name=region_name)
        self.bucket = bucket_name

    async def analyze(self, file: UploadFile) -> Dict:
        contents = await file.read()
        mime_type = magic.from_buffer(contents, mime=True)

        is_pdf = mime_type == "application/pdf"

        if is_pdf:
            s3_key = f"uploads/{file.filename}"
            await asyncio.to_thread(self.s3.put_object, Bucket=self.bucket, Key=s3_key, Body=contents)

            start_response = await asyncio.to_thread(
                self.client.start_document_analysis,
                DocumentLocation={"S3Object": {"Bucket": self.bucket, "Name": s3_key}},
                FeatureTypes=["FORMS"],
            )
            job_id = start_response["JobId"]

            status = "IN_PROGRESS"
            tries = 0
            result = None
            while status == "IN_PROGRESS" and tries < 20:
                await asyncio.sleep(3)
                result = await asyncio.to_thread(self.client.get_document_analysis, JobId=job_id)
                status = result["JobStatus"]
                tries += 1

            if status != "SUCCEEDED":
                raise RuntimeError(f"Textract job failed with status: {status}")

            blocks = result.get("Blocks", []) if result else []
            fields = self._extract_fields(blocks)

            await asyncio.to_thread(self.s3.delete_object, Bucket=self.bucket, Key=s3_key)

            return {"fields": fields}

        result = await asyncio.to_thread(
            self.client.analyze_document,
            Document={"Bytes": contents},
            FeatureTypes=["FORMS"],
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
