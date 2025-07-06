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
        # self.prompt = "Analyze the given document and carefully extract the information,\
        #     the language of the document is Spanish, the output format is JSON in plaintext,\
        #     you should identify the form_name only credito_personal, credito_hipotecario, solicitud_credito or desconocido,\
        #     containing the key <form_name> in first position. all text is in Spanish. Always the otput is a JSON with structured data by form section."
        self.prompt = '''Extrae la información clave del siguiente documento en español y devuélvela exclusivamente en formato JSON estructurado, siguiendo exactamente las secciones y alias indicados. 
        Si algún campo no aparece en el documento, plasmalo en el mismo formato siempre dentro de una seccion existente (no incluyas claves vacías ni valores `null`).

Puden ser 2 tipos de documentos: "credito_personal" o "credito_hipotecario", si no es ninguno de estos, devuelve el campo "form_name" con el valor "desconocido".
Todas las fechas deben ser devueltas como una sola cadena en el formato "dd/mm/aaaa". Por ejemplo:

"fecha_nacimiento": "01/01/1990"

La estructura deseada es (ejemkplo para "credito_personal"):

{
  "form_name": "credito_personal",
  "datos_solicitud": {
    "fecha_solicitud": "dd/mm/aaaa",
    "folio": "",
    "cliente_id": "",
    "ejecutivo_nombre": "",
    "numero_nomina": "",
    "zona": ""
  },
  "informacion_credito": {
    "monto_solicitado": "",
    "plazo_meses": ""
  },
  "datos_personales": {
    "nombre": "",
    "apellido_paterno": "",
    "apellido_materno": "",
    "fecha_nacimiento": "dd/mm/aaaa",
    "pais_nacimiento": "",
    "nacionalidad": "",
    "genero": "",
    "tipo_solicitud": "",
    "rfc": "",
    "curp": "",
    "grado_estudios": "",
    "telefono_casa": "",
    "telefono_celular": "",
    "email": "",
    "tipo_identificacion": "",
    "folio_identificacion": "",
    "estado_civil": "",
    "regimen_matrimonial": ""
  },
  "domicilio": {
    "tipo_propiedad": "",
    "direccion": "",
    "colonia": "",
    "municipio": "",
    "ciudad": "",
    "estado": "",
    "pais": "",
    "cp": "",
    "anios_residencia": "",
    "domicilio_anterior": ""
  },
  "empleo": {
    "empresa": "",
    "giro_empresa": "",
    "ocupacion": "",
    "puesto": "",
    "sueldo_mensual": "",
    "otros_ingresos": "",
    "fuente_otros_ingresos": "",
    "jefe_nombre_puesto": "",
    "telefono_oficina": "",
    "telefono_oficina_alt": "",
    "direccion_laboral": "",
    "empleo_anterior": ""
  },
  "referencias_personales": [
    {
      "nombre_completo": "",
      "telefono": "",
      "horario_llamada": "",
      "parentesco": ""
    }
  ]
}

para el caso de credito_hipotecario, deberas agregar la secciones: datos_inmueble, informacion_vendedor y servicios_adicionales.  

Responde exclusivamente con un JSON válido. No expliques nada. Usa el idioma y formato textual original del documento.'''

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
        print("Gemini response text:", text) ## Debugging line

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
