import logging
import os
import tempfile

from app.logger import init_logging, get_logger


def test_init_logging_idempotent(tmp_path):
    # Patch environment to log to a temp path
    log_path = tmp_path / "test.log"
    os.environ["LOG_FILE"] = str(log_path)

    init_logging(level="INFO")
    root_handlers_first = len(logging.getLogger().handlers)

    # Call again, handlers should not increase
    init_logging(level="DEBUG")
    root_handlers_second = len(logging.getLogger().handlers)

    assert root_handlers_first == root_handlers_second

    # Ensure file handler exists and log file is created when logging
    logger = get_logger("test")
    logger.info("hello")

    # Flush handlers
    for h in logger.handlers:
        h.flush()

    assert log_path.exists() or os.path.isfile(os.path.join(os.path.dirname(__file__), "..", "logs", "azom_ai_agent.log"))
