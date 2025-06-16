import openai
import json
import logging
from typing import Dict, Union
from ..interfaces.ai_refiner import AIRefiner


class GPTRefiner(AIRefiner):
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        openai.api_key = self.api_key
        logging.basicConfig(level=logging.INFO)
        logging.info(f"[GPTRefiner] Modelo {model} listo.")

    def refine(self, fields: Dict[str, Union[str, Dict[str, str]]]) -> Dict[str, Union[str, Dict[str, str]]]:
        try:
            json_input = json.dumps(fields, ensure_ascii=False, indent=2)
            prompt = (
                "Corrige ortografía y gramática en el siguiente JSON.\n"
                "Devuelve el mismo JSON corregido y con la misma estructura:\n\n"
                f"{json_input}"
            )

            response = openai.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.2,
            )

            corrected_text = response.choices[0].message.content.strip()

            try:
                corrected_json = json.loads(corrected_text)
                logging.info("[GPTRefiner] Corrección completada.")
                return corrected_json
            except json.JSONDecodeError:
                logging.warning("[GPTRefiner] GPT no devolvió JSON válido, se usa original.")
                return fields
        except Exception as e:
            logging.warning(f"[GPTRefiner] Error al refinar JSON completo: {e}")
            return fields
