import dataclasses
import logging

import pytest

from toshl_mcp.config import Settings, get_settings


def test_get_settings_with_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TOSHL_TOKEN", "mytoken")
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    settings = get_settings()
    assert settings.toshl_token == "mytoken"
    assert settings.base_url == "https://api.toshl.com"
    assert settings.log_level == logging.WARNING


def test_get_settings_missing_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TOSHL_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="TOSHL_TOKEN"):
        get_settings()


def test_get_settings_log_level(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TOSHL_TOKEN", "tok")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    settings = get_settings()
    assert settings.log_level == logging.DEBUG


def test_get_settings_invalid_log_level_falls_back(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TOSHL_TOKEN", "tok")
    monkeypatch.setenv("LOG_LEVEL", "NOTLEVEL")
    settings = get_settings()
    assert settings.log_level == logging.WARNING


def test_settings_is_frozen() -> None:
    s = Settings(toshl_token="tok")
    with pytest.raises(dataclasses.FrozenInstanceError):
        s.toshl_token = "other"  # type: ignore[misc]
