import sys
import types
import asyncio
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from services.ocr.textract.textract_ocr import AWSTextractOCRService

class DummyUploader:
    def __init__(self):
        self.deleted = False
    def upload_file(self, *a, **k):
        pass
    def delete_file(self, *a, **k):
        self.deleted = True

class DummyClient:
    def start_document_analysis(self, **kwargs):
        return {"JobId": "1"}
    def get_document_analysis(self, JobId=None, NextToken=None):
        return {"JobStatus": "SUCCEEDED", "Blocks": [], "NextToken": None}

async def _run_in_threadpool(func, *a, **k):
    return func(*a, **k)

@pytest.mark.asyncio
async def test_s3_file_deleted(monkeypatch):
    dummy_uploader = DummyUploader()
    monkeypatch.setattr("services.ocr.textract.textract_ocr.S3Uploader", lambda *a, **k: dummy_uploader)
    monkeypatch.setitem(sys.modules, "magic", types.SimpleNamespace(from_buffer=lambda *a, **k: "application/pdf"))
    monkeypatch.setitem(sys.modules, "boto3", types.SimpleNamespace(client=lambda *a, **k: DummyClient()))
    monkeypatch.setattr("services.ocr.textract.textract_ocr.run_in_threadpool", _run_in_threadpool)

    service = AWSTextractOCRService()
    file = types.SimpleNamespace(filename="doc.pdf", read=lambda: b"data")
    await service.analyze(file)
    assert dummy_uploader.deleted

