import os
import re
from typing import Dict, Any, Set, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Global SentenceTransformer model reference
model = None
model_loaded = False
model_name = os.getenv("SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2")

def load_semantic_model():
    """
    Lazy loads the sentence transformer model.
    If it fails, sets the loaded flag to False.
    """
    global model, model_loaded
    if model_loaded:
        return model, True
        
    use_semantic = os.getenv("USE_SEMANTIC_TRANSFORMERS", "true").lower() == "true"
    if not use_semantic:
        return None, False
        
    try:
        from sentence_transformers import SentenceTransformer
        print(f"Loading SentenceTransformer model '{model_name}'...")
        # This will download the model to cache on first use
        model = SentenceTransformer(model_name)
        model_loaded = True
        return model, True
    except Exception as e:
        print(f"Could not load SentenceTransformer ({e}). Falling back to TF-IDF cosine similarity.")
        model_loaded = False
        return None, False

def calculate_similarity_metrics(resume_text: str, jd_text: str, resume_skills: List[str]) -> Dict[str, Any]:
    """
    Calculates various similarity metrics between resume and job description.
    Includes keyword overlap, TF-IDF cosine similarity, skill matching, and semantic similarity.
    """
    # 1. Parse Job Description skills using the taxonomy
    from skill_extractor import extract_skills, get_flat_skills
    jd_skills_dict = extract_skills(jd_text)
    jd_skills = get_flat_skills(jd_skills_dict)
    
    # Flat list of resume skills
    res_skills_lower = {s.lower() for s in resume_skills}
    
    # Calculate skill overlaps
    matched_skills = []
    missing_skills = []
    
    # We map back the lowercase matches to their proper capitalization in the JD
    flat_jd_list = []
    for cat_skills in jd_skills_dict.values():
        flat_jd_list.extend(cat_skills)
        
    for skill in flat_jd_list:
        if skill.lower() in res_skills_lower:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)
            
    # Skill match score: percentage of JD skills matched
    if flat_jd_list:
        skill_match_score = (len(matched_skills) / len(flat_jd_list)) * 100
    else:
        skill_match_score = 100.0  # No skills in JD to match against
        
    # 2. Keyword/Word Overlap Similarity
    # Clean text to alphanumeric lowercase words, remove short words
    stop_words = {"the", "and", "a", "of", "to", "in", "is", "for", "with", "on", "as", "at", "by", "an", "be", "this", "that", "from", "are"}
    resume_words = set(re.findall(r'\b[a-z]{3,}\b', resume_text.lower())) - stop_words
    jd_words = set(re.findall(r'\b[a-z]{3,}\b', jd_text.lower())) - stop_words
    
    keyword_intersection = resume_words.intersection(jd_words)
    if jd_words:
        keyword_match_score = (len(keyword_intersection) / len(jd_words)) * 100
    else:
        keyword_match_score = 100.0

    # 3. TF-IDF Cosine Similarity
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
        tfidf_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0] * 100
    except Exception as e:
        print(f"TF-IDF Vectorizer failed: {e}")
        tfidf_sim = 0.0

    # 4. Semantic Similarity
    semantic_sim = tfidf_sim  # Default fallback
    semantic_model, loaded = load_semantic_model()
    method_used = "TF-IDF Cosine Similarity (Fallback)"
    
    if loaded and semantic_model is not None:
        try:
            # Generate embeddings
            embeddings = semantic_model.encode([resume_text, jd_text])
            # Calculate cosine similarity between embeddings
            vec1 = embeddings[0].reshape(1, -1)
            vec2 = embeddings[1].reshape(1, -1)
            sim_val = cosine_similarity(vec1, vec2)[0][0]
            # Convert -1..1 range to 0..100
            semantic_sim = float(max(0, sim_val) * 100)
            method_used = f"SentenceTransformers ({model_name})"
        except Exception as e:
            print(f"Semantic similarity calculation failed: {e}")
            method_used = "TF-IDF Cosine Similarity (Fallback)"
            
    # Overall job match score is a weighted average of:
    # 40% Semantic Similarity, 30% Skill Match, 20% TF-IDF Cosine, 10% Keyword Overlap
    overall_match = (
        (0.40 * semantic_sim) + 
        (0.30 * skill_match_score) + 
        (0.20 * tfidf_sim) + 
        (0.10 * keyword_match_score)
    )

    return {
        "overall_match": round(overall_match, 1),
        "keyword_match": round(keyword_match_score, 1),
        "tfidf_match": round(tfidf_sim, 1),
        "semantic_match": round(semantic_sim, 1),
        "matched_skills": sorted(list(set(matched_skills))),
        "missing_skills": sorted(list(set(missing_skills))),
        "method_used": method_used
    }
