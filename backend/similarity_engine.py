import re
from typing import Any, Dict, List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import settings
from gemini_engine import match_resume_to_job_with_gemini


# Compatibility state for the existing health endpoint.
# No local ML model is loaded here anymore.
model = None
model_loaded = False
model_name = settings.gemini_model


def load_semantic_model():
    """
    Compatibility wrapper retained for callers that still reference the old API.

    Semantic matching is now handled remotely by Gemini, so this function never
    imports or loads SentenceTransformer/PyTorch.
    """
    return None, False


def _calculate_deterministic_metrics(
    resume_text: str,
    jd_text: str,
    resume_skills: List[str],
) -> Dict[str, Any]:
    """Calculate lightweight, deterministic matching metrics."""
    from skill_extractor import extract_skills, get_flat_skills

    jd_skills_dict = extract_skills(jd_text)
    jd_skills = get_flat_skills(jd_skills_dict)

    res_skills_lower = {s.lower() for s in resume_skills}

    matched_skills = []
    missing_skills = []

    flat_jd_list = []
    for cat_skills in jd_skills_dict.values():
        flat_jd_list.extend(cat_skills)

    for skill in flat_jd_list:
        if skill.lower() in res_skills_lower:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    if flat_jd_list:
        skill_match_score = (len(matched_skills) / len(flat_jd_list)) * 100
    else:
        skill_match_score = 100.0

    stop_words = {
        "the", "and", "a", "of", "to", "in", "is", "for", "with", "on",
        "as", "at", "by", "an", "be", "this", "that", "from", "are",
    }
    resume_words = set(re.findall(r"\b[a-z]{3,}\b", resume_text.lower())) - stop_words
    jd_words = set(re.findall(r"\b[a-z]{3,}\b", jd_text.lower())) - stop_words

    keyword_intersection = resume_words.intersection(jd_words)
    if jd_words:
        keyword_match_score = (len(keyword_intersection) / len(jd_words)) * 100
    else:
        keyword_match_score = 100.0

    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
        tfidf_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0] * 100
    except Exception as exc:
        print(f"TF-IDF Vectorizer failed: {exc}")
        tfidf_sim = 0.0

    return {
        "skill_match_score": skill_match_score,
        "keyword_match_score": keyword_match_score,
        "tfidf_sim": float(tfidf_sim),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
    }


def calculate_similarity_metrics(
    resume_text: str,
    jd_text: str,
    resume_skills: List[str],
) -> Dict[str, Any]:
    """
    Calculate job matching metrics using Gemini semantic analysis plus
    lightweight deterministic metrics.

    Gemini is preferred for semantic understanding. TF-IDF remains the
    deterministic fallback when Gemini is unavailable or fails.
    """
    deterministic = _calculate_deterministic_metrics(
        resume_text,
        jd_text,
        resume_skills,
    )

    tfidf_sim = deterministic["tfidf_sim"]
    semantic_sim = tfidf_sim
    matched_skills = deterministic["matched_skills"]
    missing_skills = deterministic["missing_skills"]
    method_used = "TF-IDF Cosine Similarity (Fallback)"

    if settings.gemini_enabled and settings.gemini_api_key:
        try:
            gemini_match = match_resume_to_job_with_gemini(
                resume_text,
                jd_text,
            )
            semantic_sim = float(gemini_match.semantic_score)
            method_used = f"Gemini ({settings.gemini_model})"

            # Gemini can identify semantically equivalent concepts that the
            # lightweight taxonomy does not recognize. Keep taxonomy skills
            # intact and add only unique Gemini concepts.
            matched_skills = sorted(
                set(matched_skills)
                | set(gemini_match.matched_concepts)
            )
            missing_skills = sorted(
                set(missing_skills)
                | set(gemini_match.missing_concepts)
            )
        except Exception as exc:
            print(f"Gemini semantic matching failed: {exc}. Using TF-IDF fallback.")

    overall_match = (
        (0.40 * semantic_sim)
        + (0.30 * deterministic["skill_match_score"])
        + (0.20 * tfidf_sim)
        + (0.10 * deterministic["keyword_match_score"])
    )

    return {
        "overall_match": round(overall_match, 1),
        "keyword_match": round(deterministic["keyword_match_score"], 1),
        "tfidf_match": round(tfidf_sim, 1),
        "semantic_match": round(semantic_sim, 1),
        "matched_skills": sorted(set(matched_skills)),
        "missing_skills": sorted(set(missing_skills)),
        "method_used": method_used,
    }
