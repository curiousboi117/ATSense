import os
import requests
import json
from typing import List, Dict, Any

def generate_recommendations(
    text: str, 
    sections: Dict[str, str], 
    personal_info: Dict[str, Any], 
    findings: List[Dict[str, Any]],
    job_description: str = ""
) -> List[str]:
    """
    Generates structured, actionable recommendations.
    Uses rule-based extraction as base, and enhances using OpenAI or Gemini APIs if key is available.
    """
    # 1. Start with rule-based recommendations extracted from findings
    recommendations = []
    
    # Track categories to avoid duplicate types of suggestions
    seen_recommendations = set()
    for finding in findings:
        rec = finding["recommendation"]
        if rec not in seen_recommendations:
            recommendations.append(rec)
            seen_recommendations.add(rec)
            
    # 2. Add domain-specific academic/professional guidelines if not already covered
    if "skills" in sections:
        skills_text = sections["skills"].lower()
        if "git" not in skills_text and "github" not in skills_text:
            rec = "Add Git/GitHub to your Cloud/DevOps skills. Version control is a core requirement for almost all modern software engineering and data science roles."
            if rec not in seen_recommendations:
                recommendations.append(rec)
                
    if "projects" in sections:
        proj_text = sections["projects"].lower()
        if not any(kw in proj_text for kw in ["deploy", "aws", "docker", "gcp", "azure", "heroku", "vercel"]):
            rec = "Describe how your projects were deployed. Mentioning deployment tools (like Docker, AWS, or Vercel) demonstrates full-cycle software capability."
            if rec not in seen_recommendations:
                recommendations.append(rec)

    # 3. If JD is provided, check for major skill gaps and recommend additions
    if job_description:
        # We can append skill-matching suggestions
        pass

    # 4. Optional LLM enhancement
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if openai_key:
        enhanced = get_openai_suggestions(openai_key, text, job_description, recommendations)
        if enhanced:
            return enhanced
    elif gemini_key:
        enhanced = get_gemini_suggestions(gemini_key, text, job_description, recommendations)
        if enhanced:
            return enhanced
            
    return recommendations

def get_openai_suggestions(api_key: str, resume_text: str, jd_text: str, base_recommendations: List[str]) -> List[str]:
    """
    Calls OpenAI Chat API to generate 4-5 high-quality, personalized bullet-point suggestions.
    """
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    prompt = (
        "You are an expert technical recruiter and ATS auditor. Analyze this resume text and target job description (if provided). "
        "Provide exactly 5 highly actionable, specific, and professional recommendations to improve this resume's ATS compatibility and content. "
        "Focus on phrasing, tech stack, metrics, structure, and action verbs. Make sure the advice is concrete, not generic.\n\n"
        f"Resume Text (Truncated):\n{resume_text[:2000]}\n\n"
        f"Job Description (Truncated):\n{jd_text[:1500] if jd_text else 'None Provided'}\n\n"
        "Return a JSON array of strings, for example: [\"Recommendation 1\", \"Recommendation 2\"]. Do not return markdown headers or formatting outside the JSON."
    )
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a professional assistant that outputs raw JSON array of strings."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=8)
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"].strip()
            # Clean possible markdown block markers
            if content.startswith("```"):
                content = re.sub(r'^```(?:json)?\n|```$', '', content, flags=re.MULTILINE).strip()
            suggestions = json.loads(content)
            if isinstance(suggestions, list) and all(isinstance(s, str) for s in suggestions):
                return suggestions
    except Exception as e:
        print(f"Failed to fetch suggestions from OpenAI: {e}")
    return []

def get_gemini_suggestions(api_key: str, resume_text: str, jd_text: str, base_recommendations: List[str]) -> List[str]:
    """
    Calls Google Gemini API to generate suggestions.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    prompt = (
        "You are an expert technical recruiter and ATS auditor. Analyze this resume text and target job description (if provided). "
        "Provide exactly 5 highly actionable, specific, and professional recommendations to improve this resume's ATS compatibility and content. "
        "Focus on phrasing, tech stack, metrics, structure, and action verbs. Make sure the advice is concrete, not generic.\n\n"
        f"Resume Text (Truncated):\n{resume_text[:2000]}\n\n"
        f"Job Description (Truncated):\n{jd_text[:1500] if jd_text else 'None Provided'}\n\n"
        "Return a JSON array of strings, for example: [\"Recommendation 1\", \"Recommendation 2\"]. Do not return markdown block markers, just raw JSON."
    )
    
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=8)
        if response.status_code == 200:
            result = response.json()
            content = result["candidates"][0]["content"]["parts"][0]["text"].strip()
            suggestions = json.loads(content)
            if isinstance(suggestions, list) and all(isinstance(s, str) for s in suggestions):
                return suggestions
    except Exception as e:
        print(f"Failed to fetch suggestions from Gemini: {e}")
    return []
