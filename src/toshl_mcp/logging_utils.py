import logging
import logging.handlers
import queue
import sys
from collections.abc import Iterator
from contextlib import contextmanager

_VERBOSE_DEBUG = 2


def _get_log_level(verbose: int) -> int:
    """Map verbosity count (0/1/2+) to a logging level constant."""
    if verbose >= _VERBOSE_DEBUG:
        return logging.DEBUG
    if verbose == 1:
        return logging.INFO
    return logging.WARNING


def _create_stream_handler(level: int) -> logging.StreamHandler:  # type: ignore[type-arg]
    """Build a stderr StreamHandler — stdout is reserved for the MCP protocol."""
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    return handler


@contextmanager
def logging_context(
    logger: logging.Logger, verbose: int = 0
) -> Iterator[logging.Logger]:
    """Context manager for non-blocking async-safe logging using QueueHandler.

    Configures logger with QueueHandler so logging never blocks async operations.
    QueueListener handles I/O in a separate thread. Always writes to stderr —
    never stdout, which is reserved for the MCP stdio protocol.

    Args:
        logger: The logger instance to configure.
        verbose: Verbosity level (0=WARNING, 1=INFO, 2=DEBUG).

    Yields:
        The configured logger instance.
    """
    level = _get_log_level(verbose)
    logger.setLevel(level)

    log_queue: queue.Queue[logging.LogRecord] = queue.Queue(-1)

    stream_handler = _create_stream_handler(level)
    queue_handler = logging.handlers.QueueHandler(log_queue)
    logger.addHandler(queue_handler)

    queue_listener = logging.handlers.QueueListener(
        log_queue, stream_handler, respect_handler_level=True
    )

    try:
        queue_listener.start()
        logger.debug("Logging initialized at level %s", logging.getLevelName(level))
        yield logger
    finally:
        queue_listener.stop()
        logger.removeHandler(queue_handler)
