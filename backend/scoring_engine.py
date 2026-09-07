from typing import Dict, List, Any, Optional

# Configure weights in one place for ease of adjustment
SCORING_WEIGHTS_WITH_JD = {
    "job_match": 0.30,
    "skills": 0.20,
    "experience": 0.15,
    "structure": 0.10,
    "education": 0.10,
    "projects": 0.10,
    "formatting": 0.05
}

def calculate_ats_score(
    sections: Dict[str, str], 
    skills: Dict[str, List[str]], 
    findings: List[Dict[str, Any]], 
    similarity_metrics: Optional[Dict[str, Any]] = None
) -> tuple[float, Dict[str, float]]:
    """
    Calculates a deterministic, explainable ATS score from 0 to 100.
    Returns:
        (total_score, breakdown_dictionary)
    """
    # 1. Skills Component Score (0-100)
    flat_skills_count = sum(len(lst) for cat, lst in skills.items() if cat != "soft_skills")
    soft_skills_count = len(skills.get("soft_skills", []))
    
    skills_score = 0.0
    if flat_skills_count >= 10:
        skills_score = 90.0
    elif flat_skills_count >= 6:
        skills_score = 75.0
    elif flat_skills_count >= 3:
        skills_score = 55.0
    elif flat_skills_count >= 1:
        skills_score = 35.0
        
    # Boost with soft skills (max +10)
    if soft_skills_count >= 3:
        skills_score += 10.0
    elif soft_skills_count >= 1:
        skills_score += 5.0
    skills_score = min(100.0, skills_score)

    # 2. Experience Component Score (0-100)
    experience_score = 0.0
    if "experience" in sections:
        experience_score = 100.0
        # Deduce points based on experience findings
        for f in findings:
            if f["category"] == "Dates" and "experience" in f["explanation"].lower():
                experience_score -= 20.0
            if f["category"] == "Content" and "action verbs" in f["explanation"].lower():
                experience_score -= 15.0
            if f["category"] == "Content" and "measurable results" in f["explanation"].lower():
                experience_score -= 15.0
        experience_score = max(30.0, experience_score)

    # 3. Structure Component Score (0-100)
    # Counts presence of essential sections
    detected_section_count = len(sections)
    if detected_section_count >= 6:
        structure_score = 100.0
    elif detected_section_count >= 4:
        structure_score = 80.0
    elif detected_section_count >= 3:
        structure_score = 60.0
    else:
        structure_score = 40.0

    # 4. Education Component Score (0-100)
    education_score = 0.0
    if "education" in sections:
        education_score = 100.0
        for f in findings:
            if f["category"] == "Dates" and "education" in f["explanation"].lower():
                education_score -= 20.0
        education_score = max(50.0, education_score)

    # 5. Projects Component Score (0-100)
    projects_score = 0.0
    if "projects" in sections:
        projects_score = 100.0
        # Check if project has findings
        for f in findings:
            if "projects" in f["explanation"].lower() and f["severity"] == "HIGH":
                projects_score -= 30.0
            elif "projects" in f["explanation"].lower() and f["severity"] == "MEDIUM":
                projects_score -= 15.0
        projects_score = max(40.0, projects_score)

    # 6. Formatting Component Score (0-100)
    formatting_score = 100.0
    for f in findings:
        if f["category"] == "Formatting":
            if f["severity"] == "MEDIUM":
                formatting_score -= 20.0
            elif f["severity"] == "LOW":
                formatting_score -= 10.0
        if f["category"] == "Contact" and f["severity"] == "HIGH":
            formatting_score -= 10.0  # missing contact fields counts as formatting/completeness errors
            
    formatting_score = max(30.0, formatting_score)

    # Determine weights
    if similarity_metrics and "overall_match" in similarity_metrics:
        # Job description was provided, include job match
        job_match_score = similarity_metrics["overall_match"]
        breakdown = {
            "job_match": round(job_match_score, 1),
            "skills": round(skills_score, 1),
            "experience": round(experience_score, 1),
            "structure": round(structure_score, 1),
            "education": round(education_score, 1),
            "projects": round(projects_score, 1),
            "formatting": round(formatting_score, 1),
        }
        
        # Calculate weighted sum
        total = sum(breakdown[key] * SCORING_WEIGHTS_WITH_JD[key] for key in SCORING_WEIGHTS_WITH_JD)
    else:
        # No job description, re-allocate the 30% of job_match proportionally to other sections
        # Total weights without job match = 0.70
        weights_no_jd = {k: v / 0.70 for k, v in SCORING_WEIGHTS_WITH_JD.items() if k != "job_match"}
        
        breakdown = {
            "skills": round(skills_score, 1),
            "experience": round(experience_score, 1),
            "structure": round(structure_score, 1),
            "education": round(education_score, 1),
            "projects": round(projects_score, 1),
            "formatting": round(formatting_score, 1),
        }
        
        total = sum(breakdown[key] * weights_no_jd[key] for key in weights_no_jd)
        
    return round(total, 1), breakdown
