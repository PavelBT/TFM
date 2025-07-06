# services/ocr/gemini/gemini_service.py
import os
import asyncio
import tempfile
from fastapi import UploadFile
from interfaces.ocr_service import OCRService
from models import OCRResponse
from services.utils.logger import get_logger

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
except Exception:  # pragma: no cover - optional dependency may not be installed
    genai = None


class GeminiOCRService(OCRService):
    def __init__(self, api_key: str | None = None, model_name: str | None = None, prompt: str | None = None):
        self.logger = get_logger(self.__class__.__name__)
        self.api_key = (
            api_key
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_AI_STUDIO_API_KEY", "")
        )
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-2.5-pro-exp-03-25")
        self.prompt = prompt or os.getenv("GEMINI_PROMPT", "Extract the text from the document")
        if genai:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            self.safety = {
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            }
        else:  # pragma: no cover - library not available
            self.model = None
            self.safety = {}

    async def analyze(self, file: UploadFile) -> OCRResponse:
        self.logger.info("Analyzing file with Gemini: %s", file.filename)
        if not genai or not self.model:
            raise RuntimeError(
                "google-generativeai library is required for GeminiOCRService"
            )

        # Save file to a temporary location because `upload_file` expects a path
        with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        def _generate() -> str:
            uploaded = genai.upload_file(path=tmp_path, display_name=file.filename)
            # Retrieve the file just like in the example
            genai.get_file(name=uploaded.name)
            response = self.model.generate_content(
                [uploaded, self.prompt],
                safety_settings=self.safety,
            )
            return getattr(response, "text", "")

        text = await asyncio.to_thread(_generate)
        try:
            os.remove(tmp_path)
        except OSError:
            self.logger.warning("Temporary file could not be removed: %s", tmp_path)
        return OCRResponse(form_name="text", fields={"text": text})
