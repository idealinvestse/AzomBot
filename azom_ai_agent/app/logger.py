import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional
import os


# Base directory two levels up from this file (project root)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'azom_ai_agent.log')
os.makedirs(LOG_DIR, exist_ok=True)

def init_logging(level: int | str = logging.INFO, log_to_console: bool = True) -> None:
    """Initialise root logger with both console and rotating file handlers.

    This function is *idempotent* – calling it multiple times will have effect
    only the first time.
    """
    root = logging.getLogger()
    if root.handlers:
        # Already configured – do nothing
        return

    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)

    root.setLevel(level)

    # Common formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')

    # Rotating file handler 5 MB × 5 files
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5)
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    # Optional console handler (stderr)
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root.addHandler(console_handler)


def get_logger(name: str):
    """Return a child logger after ensuring root logging is configured."""
    init_logging()  # safe no-op after first call
    return logging.getLogger(name)
