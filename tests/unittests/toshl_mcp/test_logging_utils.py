import logging
import sys

import pytest

from toshl_mcp.logging_utils import (
    _create_stream_handler,
    _get_log_level,
    logging_context,
)


def test_get_log_level_default() -> None:
    assert _get_log_level(0) == logging.WARNING


def test_get_log_level_info() -> None:
    assert _get_log_level(1) == logging.INFO


def test_get_log_level_debug() -> None:
    assert _get_log_level(2) == logging.DEBUG
    assert _get_log_level(99) == logging.DEBUG


def test_create_stream_handler_uses_stderr() -> None:
    handler = _create_stream_handler(logging.INFO)
    assert handler.stream is sys.stderr


def test_create_stream_handler_level() -> None:
    handler = _create_stream_handler(logging.DEBUG)
    assert handler.level == logging.DEBUG


def test_logging_context_yields_logger() -> None:
    logger = logging.getLogger("test.context")
    with logging_context(logger, verbose=1) as log:
        assert log is logger


def test_logging_context_sets_level() -> None:
    logger = logging.getLogger("test.level")
    with logging_context(logger, verbose=1):
        assert logger.level == logging.INFO


def test_logging_context_removes_handler_on_exit() -> None:
    logger = logging.getLogger("test.cleanup")
    handlers_before = len(logger.handlers)
    with logging_context(logger, verbose=0):
        assert len(logger.handlers) == handlers_before + 1
    assert len(logger.handlers) == handlers_before


def test_logging_context_writes_to_stderr_not_stdout(
    capsys: pytest.CaptureFixture[str],
) -> None:
    logger = logging.getLogger("test.stderr")
    with logging_context(logger, verbose=1):
        logger.info("test message to stderr")
    captured = capsys.readouterr()
    assert "test message to stderr" in captured.err
    assert "test message to stderr" not in captured.out
