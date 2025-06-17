import os
import json
from typing import Dict
import openai

from .model_service import GrammarCorrector
from .logger import get_logger


class ChatGPTRefiner:
    """Wrapper around OpenAI ChatGPT for refining text fields."""

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            openai.api_key = api_key

    def refine(self, fields: Dict[str, str]) -> Dict[str, str]:
        json_input = json.dumps(fields, ensure_ascii=False, indent=2)
        system_msg = (
            "Eres un asistente que corrige ortograf\u00eda y gram\u00e1tica en JSON. "
            "Devuelve \u00fanicamente el JSON corregido."
        )
        messages = [
            {"role": "system", "content": system_msg},
            {
                "role": "user",
                "content": f"Corrige este JSON manteniendo su estructura:\n{json_input}",
            },
        ]
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2,
                max_tokens=1000,
                response_format={"type": "json_object"},
            )
            text = response.choices[0].message.content.strip()
            return json.loads(text)
        except Exception as exc:
            self.logger.warning("GPT refinement failed: %s", exc)
            return fields


class CombinedRefiner:
    """Apply local grammar correction before delegating to ChatGPT."""

    def __init__(self, use_local_corrector: bool = True):
        self.logger = get_logger(self.__class__.__name__)
        self.use_local = use_local_corrector
        self.corrector = GrammarCorrector() if use_local_corrector else None
        self.gpt = ChatGPTRefiner()

    def refine(self, fields: Dict[str, str]) -> Dict[str, str]:
        current = fields
        if self.corrector:
            try:
                current = {k: self.corrector.correct(v) for k, v in fields.items()}
            except Exception as exc:
                self.logger.warning("Local correction failed: %s", exc)
                current = fields
        return self.gpt.refine(current)
