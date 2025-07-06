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

DEFAULT_PROMPT_FILE = os.path.join(os.path.dirname(__file__), "system_prompt.txt")

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
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-2.0-pro-exp-02-05")
        self.prompt = self._load_prompt(prompt)

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

    def _load_prompt(self, prompt: str | None) -> str:
        if prompt is not None:
            return prompt
        prompt_file = os.getenv("GEMINI_PROMPT_FILE", DEFAULT_PROMPT_FILE)
        try:
            with open(prompt_file, "r", encoding="utf-8") as fh:
                return fh.read()
        except OSError as exc:  # pragma: no cover - best effort
            self.logger.warning("Prompt file could not be read: %s", exc)
            return ""

    async def _save_temp_file(self, file: UploadFile) -> str:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
            tmp.write(await file.read())
            return tmp.name

    def _generate_text(self, tmp_path: str, filename: str) -> str:
        uploaded = genai.upload_file(path=tmp_path, display_name=filename)
        genai.get_file(name=uploaded.name)
        response = self.model.generate_content(
            [uploaded, self.prompt],
            safety_settings=self.safety,
        )
        self.logger.debug("Gemini raw response: %s", response)
        return getattr(response, "text", "")

    def _cleanup_temp_file(self, path: str) -> None:
        try:
            os.remove(path)
        except OSError:
            self.logger.warning("Temporary file could not be removed: %s", path)

    def _parse_text(self, text: str) -> dict[str, str]:
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
        return fields

    async def analyze(self, file: UploadFile) -> OCRResponse:
        self.logger.info("Analyzing file with Gemini: %s", file.filename)
        if not genai or not self.model:
            raise RuntimeError(
                "google-generativeai library is required for GeminiOCRService"
            )
        tmp_path = await self._save_temp_file(file)
        try:
            text = await asyncio.to_thread(self._generate_text, tmp_path, file.filename)
        finally:
            self._cleanup_temp_file(tmp_path)

        fields = self._parse_text(text)
        return OCRResponse(form_name="text", fields=fields)
