import logging
import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    """Immutable server configuration loaded from environment variables."""

    toshl_token: str
    base_url: str = "https://api.toshl.com"
    log_level: int = field(default=logging.WARNING)


def get_settings() -> Settings:
    """Read configuration from environment, failing fast if TOSHL_TOKEN is absent."""
    token = os.environ.get("TOSHL_TOKEN")
    if not token:
        raise RuntimeError("TOSHL_TOKEN environment variable is required")
    log_level_name = os.environ.get("LOG_LEVEL", "WARNING").upper()
    log_level = getattr(logging, log_level_name, logging.WARNING)
    return Settings(toshl_token=token, log_level=log_level)
