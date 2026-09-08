import pytest

from config import Settings


def test_development_cors_falls_back_to_localhost():
    settings = Settings(
        app_env="development",
        cors_origins="not-json",
    )

    assert settings.cors_list == ["http://localhost:5173"]


def test_production_cors_rejects_invalid_json():
    settings = Settings(
        app_env="production",
        jwt_secret_key="test-secret",
        cors_origins="not-json",
    )

    with pytest.raises(
        ValueError,
        match="CORS_ORIGINS must be valid JSON in production",
    ):
        _ = settings.cors_list


def test_production_cors_accepts_valid_origins():
    settings = Settings(
        app_env="production",
        jwt_secret_key="test-secret",
        cors_origins='["https://example.com"]',
    )

    assert settings.cors_list == ["https://example.com"]