from services.utils.logger import get_logger


class DatabaseClient:
    """Placeholder database client."""

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    def save_form(self, form_type: str, fields: dict) -> None:
        """Temporary stub that logs received data."""
        self.logger.info("Saving form of type '%s' with %d fields", form_type, len(fields))

