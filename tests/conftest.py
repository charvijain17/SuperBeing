"""Shared pytest configuration that prevents tests from reading real credentials."""

from collections.abc import Callable

import pytest

from app.config import Settings, get_settings
from app.main import app


def make_test_settings(**overrides: object) -> Settings:
    """Build Settings with every value explicit, bypassing OS env and .env files."""
    values: dict[str, object] = {
        "app_name": "SuperBeing Test API",
        "app_version": "test",
        "environment": "test",
        "app_api_key": None,
        "openai_api_key": None,
        "anthropic_api_key": None,
        "google_api_key": None,
        "openai_model": "test-openai-model",
        "anthropic_model": "test-anthropic-model",
        "gemini_model": "test-gemini-model",
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


@pytest.fixture
def clean_settings() -> Callable[..., Settings]:
    return make_test_settings


@pytest.fixture(autouse=True)
def isolate_fastapi_settings() -> None:
    """Ensure every endpoint test uses keyless settings and clean dependency state."""
    def override_get_settings() -> Settings:
        return make_test_settings()

    get_settings.cache_clear()
    app.dependency_overrides[get_settings] = override_get_settings
    yield
    app.dependency_overrides.clear()
    get_settings.cache_clear()
