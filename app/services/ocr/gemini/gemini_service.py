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
        self.prompt_system = self._load_prompt(prompt)
        self.prompt = (
            "Identifica y extra los datos precisos del fomulario. "
            "Devuelve un JSON con los campos y sus valores. Si no hay datos, "
            "devuelve un JSON vacío."
        )
        self.refine_prompt = (
            "Refina el siguiente JSON extraído con OCR. "
            "Devuelve únicamente el JSON estructurado según las indicaciones."
            "Deberas parsear los campos de seleccion y checkbox como listas, " \
            "por ejemplo: plazo de credito: 24 meses , si 24: SELECTED, estado civial: casado, si casado: SELECTED " \
        )

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
        prompt_file = DEFAULT_PROMPT_FILE
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

    def _generate_refine(self, data: str, prompt: str) -> str:
        response = self.model.generate_content(
            [prompt, data],
            safety_settings=self.safety,
        )
        self.logger.debug("Gemini refine response: %s", response)
        return getattr(response, "text", "")

    def _cleanup_temp_file(self, path: str) -> None:
        try:
            os.remove(path)
        except OSError:
            self.logger.warning("Temporary file could not be removed: %s", path)

    def _parse_text(self, text: str) -> dict[str, str]:
        try:
            json_string = text.strip() # Elimina espacios en blanco al inicio/fin
            if json_string.startswith("```json"):
                json_string = json_string[len("```json"):].strip()
            if json_string.endswith("```"):
                json_string = json_string[:-len("```")].strip()

            parsed_json = json.loads(json_string)
            return parsed_json
        except json.JSONDecodeError as e:
            self.logger.error("JSON parsing error: %s", e)
            return {}
        
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
        form_name = fields.pop("form_name", "")

        return OCRResponse(form_name=form_name, fields=fields)

    async def refine(self, fields: dict, prompt: str | None = None) -> OCRResponse:
        """Refine extracted fields using Gemini."""
        self.logger.info("Refining fields with Gemini")
        if not genai or not self.model:
            raise RuntimeError(
                "google-generativeai library is required for GeminiOCRService"
            )
        payload = json.dumps(fields, ensure_ascii=False)
        user_prompt = prompt or self.refine_prompt
        text = await asyncio.to_thread(self._generate_refine, payload, user_prompt)
        parsed = self._parse_text(text)
        form_name = parsed.pop("form_name", "")
        return OCRResponse(form_name=form_name, fields=parsed)
    
