import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """Return a logger with basic configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s - %(name)s: %(message)s",
        stream=sys.stdout,
    )
    return logging.getLogger(name)
