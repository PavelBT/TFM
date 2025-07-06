# services/ocr/gemini/gemini_service.py
import os
import asyncio
import tempfile
import json
import re
from fastapi import UploadFile
from interfaces.ocr_service import OCRService
from models import OCRResponse
from services.utils.logger import get_logger

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold

    # Configure the Google Generative AI library
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    models = genai.list_models()

    for m in models:
        print(m.name, m.supported_generation_methods)

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
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-2.0-pro-exp-02-05")
        self.prompt = "Analyze the given document and carefully extract the information, the language of the document is Spanish, the output format is JSON in plaintext organized by categories (example: {'datos personales': {'nombre': 'claudia', 'apellido': 'perez', ...} }): datos personales, contacto, empleo y finanzas (monto del credito, salario mensual, plazo del credito) ." if prompt is None else prompt
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
            genai.get_file(name=uploaded.name)
            response = self.model.generate_content(
                [uploaded, self.prompt],
                safety_settings=self.safety,
            )
            self.logger.debug("Gemini raw response: %s", response)
            return getattr(response, "text", "")

        text = await asyncio.to_thread(_generate)
        try:
            os.remove(tmp_path)
        except OSError:
            self.logger.warning("Temporary file could not be removed: %s", tmp_path)

        fields: dict[str, str] = {}
        match = re.search(r"\{.*\}", text, re.S)
        if match:
            try:
                payload = json.loads(match.group(0))
                for section in payload.values():
                    if isinstance(section, list):
                        for item in section:
                            label = item.get("label") or item.get("name") or item.get("key")
                            value = item.get("value")
                            if label is not None:
                                fields[label] = value
                    elif isinstance(section, dict):
                        for label, value in section.items():
                            fields[label] = value
            except Exception as exc:  # pragma: no cover - best effort
                self.logger.warning("Failed to parse Gemini JSON: %s", exc)
                fields = {"text": text}
        else:
            fields = {"text": text}

        return OCRResponse(form_name="text", fields=fields)
