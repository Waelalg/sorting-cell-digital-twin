# common/logging_config.py

import logging


def configure_logging(level: int = logging.INFO) -> None:
    """
    Configure root logging for the project.

    This should be called once at startup (CLI or API).
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
