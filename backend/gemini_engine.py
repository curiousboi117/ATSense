from typing import List, Optional

from pydantic import BaseModel, Field

from config import settings


class GeminiEvidence(BaseModel):
    """A factual piece of resume/JD evidence returned by Gemini."""

    category: str = Field(description="Evidence category, such as skills, experience, or education.")
    statement: str = Field(description="A concise factual statement grounded in the supplied text.")
    confidence: float = Field(ge=0.0, le=1.0, description="Model confidence from 0 to 1.")


class GeminiResumeInsights(BaseModel):
    """Structured Gemini output used as evidence for downstream deterministic logic."""

    summary: str = Field(description="A concise factual summary of the resume.")
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    relevant_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    evidence: List[GeminiEvidence] = Field(default_factory=list)


class GeminiJobMatch(BaseModel):
    """Structured semantic matching evidence for a resume against a job description."""

    semantic_score: float = Field(
        ge=0.0,
        le=100.0,
        description="Semantic alignment from 0 to 100 based only on the supplied resume and job description.",
    )
    matched_concepts: List[str] = Field(default_factory=list)
    missing_concepts: List[str] = Field(default_factory=list)
    rationale: str = Field(description="Short factual explanation of the semantic match.")


_client = None


def _create_client():
    """Create the Google GenAI client only when a Gemini call is actually needed."""
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    from google import genai

    return genai.Client(api_key=settings.gemini_api_key)


def get_client():
    """Return a lazily-created, process-local Gemini client."""
    global _client

    if _client is None:
        _client = _create_client()

    return _client


def _generate_structured(
    prompt: str,
    response_schema: type[BaseModel],
) -> BaseModel:
    """Generate and validate a structured Gemini response."""
    client = get_client()

    from google.genai import types

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_schema,
        ),
    )

    if getattr(response, "parsed", None) is not None:
        return response_schema.model_validate(response.parsed)

    if not getattr(response, "text", None):
        raise RuntimeError("Gemini returned an empty response.")

    return response_schema.model_validate_json(response.text)


def analyze_resume_with_gemini(
    resume_text: str,
    job_description: Optional[str] = None,
) -> GeminiResumeInsights:
    """Analyze resume text with Gemini and return validated structured evidence."""
    if not settings.gemini_enabled:
        raise RuntimeError("Gemini integration is disabled.")

    prompt = f"""
You are an evidence extraction engine for ATSense.
Analyze ONLY the supplied resume and optional job description.
Do not invent facts. Keep every evidence statement grounded in the input.
Do not calculate an ATS score; ATSense's deterministic scoring engine owns the final score.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description or "No job description provided."}

Return structured evidence for resume quality, relevant skills, missing skills, and actionable recommendations.
""".strip()

    return _generate_structured(prompt, GeminiResumeInsights)  # type: ignore[return-value]


def match_resume_to_job_with_gemini(
    resume_text: str,
    job_description: str,
) -> GeminiJobMatch:
    """Compare a resume and job description using Gemini without loading a local model."""
    if not settings.gemini_enabled:
        raise RuntimeError("Gemini integration is disabled.")

    if not job_description.strip():
        raise ValueError("Job description cannot be empty.")

    prompt = f"""
You are the semantic matching engine for ATSense.
Compare ONLY the supplied resume and job description.

Rules:
- Do not invent qualifications, experience, or skills.
- Judge semantic alignment, including equivalent terminology and related responsibilities.
- Return a semantic alignment score from 0 to 100.
- List the most important concepts clearly supported by both texts as matched_concepts.
- List important job requirements that are not supported by the resume as missing_concepts.
- Keep the rationale concise and factual.
- Do not calculate ATSense's final score.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}
""".strip()

    return _generate_structured(prompt, GeminiJobMatch)  # type: ignore[return-value]
