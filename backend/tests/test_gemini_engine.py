import pytest

import gemini_engine


class FakeResponse:
    text = '{"summary":"Strong Python resume","strengths":["Projects"],"weaknesses":[],"relevant_skills":["Python"],"missing_skills":[],"recommendations":["Add measurable outcomes"],"evidence":[{"category":"skills","statement":"Python is listed","confidence":0.98}]}'
    parsed = None


class FakeModels:
    def __init__(self):
        self.calls = []

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        return FakeResponse()


class FakeClient:
    def __init__(self):
        self.models = FakeModels()


def test_gemini_client_is_lazy(monkeypatch):
    gemini_engine._client = None
    fake_client = FakeClient()
    monkeypatch.setattr(gemini_engine, "_create_client", lambda: fake_client)
    monkeypatch.setattr(gemini_engine.settings, "gemini_api_key", "test-key")

    assert gemini_engine._client is None
    assert gemini_engine.get_client() is fake_client
    assert gemini_engine.get_client() is fake_client


def test_gemini_structured_output_is_validated(monkeypatch):
    fake_client = FakeClient()
    gemini_engine._client = fake_client

    monkeypatch.setattr(gemini_engine.settings, "gemini_enabled", True)
    monkeypatch.setattr(gemini_engine.settings, "gemini_model", "gemini-test")

    result = gemini_engine.analyze_resume_with_gemini(
        "Python developer with FastAPI experience.",
        "Looking for a Python developer.",
    )

    assert result.summary == "Strong Python resume"
    assert result.relevant_skills == ["Python"]
    assert result.evidence[0].confidence == pytest.approx(0.98)
    assert fake_client.models.calls[0]["model"] == "gemini-test"


def test_gemini_disabled_does_not_call_client(monkeypatch):
    monkeypatch.setattr(gemini_engine.settings, "gemini_enabled", False)

    with pytest.raises(RuntimeError, match="disabled"):
        gemini_engine.analyze_resume_with_gemini("resume")
