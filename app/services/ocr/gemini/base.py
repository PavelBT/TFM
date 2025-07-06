# services/ocr/gemini/base.py
"""Common Gemini service functionality."""
import os
import json
import tempfile
from fastapi import UploadFile
from services.utils.logger import get_logger

DEFAULT_PROMPT_FILE = os.path.join(os.path.dirname(__file__), "system_prompt.txt")

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
except Exception:  # pragma: no cover - optional dependency may not be installed
    genai = None


class GeminiBaseService:
    """Base class with shared helpers for Gemini services."""

    def __init__(self, api_key: str | None = None, model_name: str | None = None, prompt: str | None = None) -> None:
        self.logger = get_logger(self.__class__.__name__)
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_AI_STUDIO_API_KEY", "")
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-2.0-pro-exp-02-05")
        self.prompt_system = self._load_prompt(prompt)
        if genai:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name, system_instruction=self.prompt_system)
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
        try:
            with open(DEFAULT_PROMPT_FILE, "r", encoding="utf-8") as fh:
                return fh.read()
        except OSError as exc:  # pragma: no cover - best effort
            self.logger.warning("Prompt file could not be read: %s", exc)
            return ""

    async def _save_temp_file(self, file: UploadFile) -> str:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
            tmp.write(await file.read())
            return tmp.name

    def _cleanup_temp_file(self, path: str) -> None:
        try:
            os.remove(path)
        except OSError:
            self.logger.warning("Temporary file could not be removed: %s", path)

    def _parse_text(self, text: str) -> dict[str, str]:
        try:
            json_string = text.strip()
            if json_string.startswith("```json"):
                json_string = json_string[len("```json"):].strip()
            if json_string.endswith("```"):
                json_string = json_string[:-len("```")].strip()
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            self.logger.error("JSON parsing error: %s", e)
            return {}

    def _generate_from_file(self, tmp_path: str, filename: str, prompt: str) -> str:
        uploaded = genai.upload_file(path=tmp_path, display_name=filename)
        genai.get_file(name=uploaded.name)
        response = self.model.generate_content([uploaded, prompt], safety_settings=self.safety)
        self.logger.debug("Gemini raw response: %s", response)
        return getattr(response, "text", "")

    def _generate_from_text(self, data: str, prompt: str) -> str:
        response = self.model.generate_content([prompt, data], safety_settings=self.safety)
        self.logger.debug("Gemini refine response: %s", response)
        return getattr(response, "text", "")
