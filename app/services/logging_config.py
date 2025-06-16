import logging


def setup_logging(level: int = logging.INFO) -> None:
    """Configure root logging format and level."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        force=True,
    )


