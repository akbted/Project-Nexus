"""
Tests for settings module (PROJECTSETTINGS and get_settings).

Concepts learned:
- monkeypatch: pytest's built-in way to mock env vars, sys.argv, etc.
- How to reset singleton state between tests
- Testing Pydantic BaseSettings validation
"""
import pytest
import src.config.settings as settings_module
from pydantic import ValidationError


# ============================================================================
# HELPER: Reset the singleton between tests
# ============================================================================
# The settings module has a global _instance variable.
# If we don't reset it, one test's settings leak into the next test.
# We use autouse=True so this runs BEFORE every test in this file.

@pytest.fixture(autouse=True)
def reset_settings_singleton():
    """Reset the settings singleton before each test."""
    settings_module._instance = None
    yield  # test runs here
    settings_module._instance = None


# ============================================================================
# SETTINGS TESTS
# ============================================================================

def test_settings_loads_from_env(monkeypatch):
    """
    Can PROJECTSETTINGS load values from environment variables?

    monkeypatch.setenv() temporarily sets an env var for this test only.
    After the test, pytest restores the original env.
    """
    monkeypatch.setenv("OPENPROJECT_TOKEN", "test-token-123")
    monkeypatch.setenv("OPENPROJECT_APIROOT", "http://localhost:8080")

    settings = settings_module.PROJECTSETTINGS()

    assert settings.OPENPROJECT_TOKEN == "test-token-123"
    assert settings.OPENPROJECT_APIROOT == "http://localhost:8080"
    assert settings.app_name == "OpenProject MCP"  # has default value


def test_settings_missing_token_raises(monkeypatch):
    """
    Does PROJECTSETTINGS raise an error when required fields are missing?

    OPENPROJECT_TOKEN is a required field (no default value).
    If neither env vars nor .env file provide it, Pydantic raises ValidationError.

    Lesson: We must also disable the .env file, otherwise Pydantic loads
    values from .env even when env vars are deleted. We pass _env_file=None
    to tell PydanticSettings to ignore the .env file.
    """
    monkeypatch.delenv("OPENPROJECT_TOKEN", raising=False)
    monkeypatch.delenv("OPENPROJECT_APIROOT", raising=False)

    with pytest.raises(ValidationError):
        settings_module.PROJECTSETTINGS(_env_file=None)


def test_settings_extra_fields_ignored(monkeypatch):
    """
    Does extra='ignore' in model_config work?

    Our settings class has extra='ignore', which means any extra env vars
    should be silently ignored, not raise an error.
    """
    monkeypatch.setenv("OPENPROJECT_TOKEN", "test-token")
    monkeypatch.setenv("OPENPROJECT_APIROOT", "http://localhost:8080")
    monkeypatch.setenv("SOME_RANDOM_EXTRA_VAR", "should-be-ignored")

    settings = settings_module.PROJECTSETTINGS()

    assert settings.OPENPROJECT_TOKEN == "test-token"
    # The extra var should not cause an error (extra="ignore")


def test_get_settings_returns_same_instance(monkeypatch):
    """
    Does get_settings() always return the same instance?

    This is the Singleton pattern — calling get_settings() multiple times
    should return the exact same object, not create new ones.
    """
    monkeypatch.setenv("OPENPROJECT_TOKEN", "test-token")
    monkeypatch.setenv("OPENPROJECT_APIROOT", "http://localhost:8080")

    settings1 = settings_module.get_settings()
    settings2 = settings_module.get_settings()

    # 'is' checks if they're the SAME object in memory (not just equal)
    assert settings1 is settings2


def test_get_settings_returns_projectsettings_type(monkeypatch):
    """
    Does get_settings() return a PROJECTSETTINGS instance?
    """
    monkeypatch.setenv("OPENPROJECT_TOKEN", "test-token")
    monkeypatch.setenv("OPENPROJECT_APIROOT", "http://localhost:8080")

    settings = settings_module.get_settings()

    assert isinstance(settings, settings_module.PROJECTSETTINGS)
