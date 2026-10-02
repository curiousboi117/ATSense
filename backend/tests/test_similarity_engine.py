import pytest

import similarity_engine


class FakeGeminiMatch:
    semantic_score = 82.0
    matched_concepts = ["FastAPI", "REST APIs"]
    missing_concepts = ["Kubernetes"]
    rationale = "The resume supports Python API development but not Kubernetes."


def test_similarity_uses_gemini_when_enabled(monkeypatch):
    monkeypatch.setattr(similarity_engine.settings, "gemini_enabled", True)
    monkeypatch.setattr(similarity_engine.settings, "gemini_api_key", "test-key")
    monkeypatch.setattr(
        similarity_engine,
        "match_resume_to_job_with_gemini",
        lambda resume, jd: FakeGeminiMatch(),
    )

    result = similarity_engine.calculate_similarity_metrics(
        "Python developer with FastAPI and REST APIs experience.",
        "Need Python, FastAPI, REST APIs and Kubernetes.",
        ["Python", "FastAPI"],
    )

    assert result["semantic_match"] == 82.0
    assert result["method_used"] == "Gemini (gemini-2.5-flash)"
    assert "FastAPI" in result["matched_skills"]
    assert "REST APIs" in result["matched_skills"]
    assert "Kubernetes" in result["missing_skills"]


def test_similarity_falls_back_to_tfidf_when_gemini_fails(monkeypatch):
    monkeypatch.setattr(similarity_engine.settings, "gemini_enabled", True)
    monkeypatch.setattr(similarity_engine.settings, "gemini_api_key", "test-key")

    def fail_gemini(*args, **kwargs):
        raise RuntimeError("Gemini unavailable")

    monkeypatch.setattr(
        similarity_engine,
        "match_resume_to_job_with_gemini",
        fail_gemini,
    )

    result = similarity_engine.calculate_similarity_metrics(
        "Python developer",
        "Python developer",
        ["Python"],
    )

    assert result["method_used"] == "TF-IDF Cosine Similarity (Fallback)"
    assert result["semantic_match"] == result["tfidf_match"]


def test_similarity_never_loads_sentence_transformer():
    model, loaded = similarity_engine.load_semantic_model()

    assert model is None
    assert loaded is False
