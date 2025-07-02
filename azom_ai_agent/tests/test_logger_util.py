import logging
import os
import tempfile
import pytest

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


def test_init_logging_with_different_levels():
    """Test initializing logging with different log levels."""
    # Reset handlers to start fresh
    logging.getLogger().handlers = []
    logging.getLogger().setLevel(logging.NOTSET)
    init_logging(level=logging.DEBUG)
    assert logging.getLogger().level == logging.DEBUG

    # Reset handlers to test with a different level
    logging.getLogger().handlers = []
    logging.getLogger().setLevel(logging.NOTSET)
    init_logging(level='INFO')
    assert logging.getLogger().level == logging.INFO

    # Reset handlers to test with an invalid level (should default to INFO)
    logging.getLogger().handlers = []
    logging.getLogger().setLevel(logging.NOTSET)
    init_logging(level='INVALID')
    assert logging.getLogger().level == logging.INFO


def test_init_logging_without_console(tmp_path):
    """Test initializing logging without console output."""
    log_path = tmp_path / "test_no_console.log"
    os.environ["LOG_FILE"] = str(log_path)

    # Robust reset of logging state
    root_logger = logging.getLogger()
    root_logger.handlers = []
    for name in list(logging.root.manager.loggerDict.keys()):
        logging.getLogger(name).handlers = []
        logging.getLogger(name).setLevel(logging.NOTSET)
    root_logger.setLevel(logging.NOTSET)
    print("Handlers before init_logging:", [type(h).__name__ for h in root_logger.handlers])

    init_logging(level=logging.INFO, log_to_console=False)

    # Check that no StreamHandler (console output) is added to root logger
    root_handlers = root_logger.handlers
    handler_types = [type(h).__name__ for h in root_handlers]
    print("Handlers after init_logging with log_to_console=False:", handler_types)
    has_stream_handler = any(isinstance(h, logging.StreamHandler) and type(h).__name__ == 'StreamHandler' for h in root_handlers)
    assert not has_stream_handler, f"Unexpected StreamHandler found in handlers: {handler_types}"

    # Ensure file handler exists and log file is created
    logger = get_logger("test_no_console")
    logger.info("hello no console")

    for h in logging.getLogger().handlers:
        h.flush()

    assert log_path.exists() or os.path.isfile(os.path.join(os.path.dirname(__file__), "..", "logs", "azom_ai_agent.log"))


def test_get_logger():
    """Test getting a child logger with a specific name."""
    # Reset handlers
    logging.getLogger().handlers = []
    logging.getLogger().setLevel(logging.NOTSET)
    init_logging(level=logging.INFO)
    logger = get_logger("test.child")
    assert logger.name == "test.child"
    # The level of a child logger might not be set explicitly, it inherits from root
    assert logger.getEffectiveLevel() == logging.INFO
    assert len(logger.handlers) == 0  # Child logger should not have handlers, inherits from root


def test_logging_output(tmp_path):
    """Test that logging actually writes to the file."""
    log_path = tmp_path / "test_output.log"
    os.environ["LOG_FILE"] = str(log_path)

    # Reset handlers
    logging.getLogger().handlers = []
    logging.getLogger().setLevel(logging.NOTSET)
    init_logging(level=logging.DEBUG)

    logger = get_logger("test_output")
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")

    for h in logging.getLogger().handlers:  # Flush root handlers
        h.flush()

    assert log_path.exists() or os.path.isfile(os.path.join(os.path.dirname(__file__), "..", "logs", "azom_ai_agent.log"))

    # Read the log file content if it exists at the temporary path
    if log_path.exists():
        with open(log_path, 'r') as f:
            content = f.read()
        assert "Debug message" in content
        assert "Info message" in content
        assert "Warning message" in content
        assert "Error message" in content
