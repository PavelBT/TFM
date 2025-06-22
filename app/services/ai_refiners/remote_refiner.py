from typing import Dict
import requests

from interfaces.ai_refiner import AIRefiner
from services.utils.logger import get_logger


class RemoteRefiner(AIRefiner):
    """Refiner that delegates processing to an external API."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.logger = get_logger(self.__class__.__name__)

    def refine(self, fields: Dict[str, str]) -> Dict[str, str]:
        try:
            resp = requests.post(f"{self.base_url}/refine", json={"fields": fields}, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return data.get("fields", fields)
        except Exception as exc:
            self.logger.warning("Remote refinement failed: %s", exc)
            return fields
