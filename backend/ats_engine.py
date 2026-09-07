import re
from typing import Dict, List, Any

# Standard strong action verbs for resumes
STRONG_ACTION_VERBS = {
    "led", "managed", "supervised", "directed", "steered", "spearheaded", "orchestrated",
    "developed", "designed", "engineered", "built", "implemented", "created", "constructed",
    "optimized", "improved", "enhanced", "boosted", "maximized", "streamlined", "accelerated",
    "reduced", "decreased", "cut", "saved", "minimized", "eliminated",
    "launched", "established", "instituted", "pioneered", "founded", "introduced",
    "analyzed", "evaluated", "assessed", "investigated", "researched", "formulated",
    "negotiated", "secured", "acquired", "generated", "produced", "delivered"
}

# Date detection regex (e.g. 2021, '21, Jan 2020, Present, etc.)
DATE_PATTERN = re.compile(
    r'\b(?:19|20)\d{2}\b|'                      # 4-digit years (e.g., 2023)
    r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(?:19|20)?\d{2}\b|' # Month Year
    r'\b(?:present|current|ongoing|active)\b',  # Present status
    re.IGNORECASE
)

# Numeric metrics check (e.g. 50%, $10k, 5x, 100+ users, etc.)
METRIC_PATTERN = re.compile(
    r'\b\d+(?:\.\d+)?%|'                        # percentages (e.g. 98%, 15.5%)
    r'\b\$\d+(?:\.\d+)?(?:k|m|b)?\b|'            # monetary amounts (e.g. $50k, $2M)
    r'\b\d+\s*(?:\+|plus)?\s*(?:percent|users|customers|clients|downloads|servers|visitors|seconds|ms|hours|days|weeks|months|years|pages|countries|usd|inr|million|billion|datasets|records|rows|accuracy|f1|epochs)\b|'
    r'\b\d+x\b',                                # multiplier (e.g. 5x)
    re.IGNORECASE
)

def run_ats_checks(text: str, sections: Dict[str, str], personal_info: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Runs structural, formatting, and content-wise ATS rule checks on the resume.
    """
    findings = []
    
    # 1. Check Document Length
    word_count = len(text.split())
    if word_count < 100:
        findings.append({
            "category": "Structure",
            "severity": "HIGH",
            "explanation": "Your resume is extremely short (under 100 words).",
            "recommendation": "Expand your resume by adding details about your experience, education, projects, and skills to provide a complete profile."
        })
    elif word_count < 300:
        findings.append({
            "category": "Structure",
            "severity": "MEDIUM",
            "explanation": f"Your resume is relatively short ({word_count} words).",
            "recommendation": "Add more depth to your experience and project descriptions. Aim for at least 400-600 words for a standard resume."
        })
    elif word_count > 1500:
        findings.append({
            "category": "Structure",
            "severity": "MEDIUM",
            "explanation": f"Your resume is overly long ({word_count} words).",
            "recommendation": "Ensure your resume is concise and ideally constrained to 1-2 pages. Condense verbose descriptions and remove outdated experiences."
        })

    # 2. Check Personal / Contact Info
    if not personal_info.get("name"):
        findings.append({
            "category": "Contact",
            "severity": "HIGH",
            "explanation": "Could not clearly identify your name at the beginning of the resume.",
            "recommendation": "Place your full name at the very top of your resume in a clear, large font."
        })
    if not personal_info.get("email"):
        findings.append({
            "category": "Contact",
            "severity": "HIGH",
            "explanation": "Missing contact email address.",
            "recommendation": "Include a professional email address (e.g., name@domain.com) clearly in your header."
        })
    if not personal_info.get("phone"):
        findings.append({
            "category": "Contact",
            "severity": "HIGH",
            "explanation": "Missing phone number.",
            "recommendation": "Provide a phone number with country code so recruiters can contact you easily."
        })
    if not personal_info.get("location"):
        findings.append({
            "category": "Contact",
            "severity": "LOW",
            "explanation": "Missing location/address information (City, State, or Country).",
            "recommendation": "Include at least your City and State/Country in your contact header to clarify relocation needs."
        })
    if not personal_info.get("links"):
        findings.append({
            "category": "Contact",
            "severity": "MEDIUM",
            "explanation": "No professional links (LinkedIn, GitHub, Portfolio) detected.",
            "recommendation": "Add clickable links to your LinkedIn profile and GitHub (if technical) to showcase your work."
        })

    # 3. Check Crucial Sections
    if not sections.get("education"):
        findings.append({
            "category": "Structure",
            "severity": "HIGH",
            "explanation": "Missing Education section.",
            "recommendation": "Create a dedicated 'Education' section detailing your degrees, institution names, majors, and graduation years."
        })
    if not sections.get("experience"):
        findings.append({
            "category": "Structure",
            "severity": "HIGH",
            "explanation": "Missing Experience / Work History section.",
            "recommendation": "Create a 'Professional Experience' or 'Work History' section listing your roles, responsibilities, and achievements chronologically."
        })
    if not sections.get("skills"):
        findings.append({
            "category": "Structure",
            "severity": "HIGH",
            "explanation": "Missing explicit Skills section.",
            "recommendation": "Create a structured 'Skills' section grouping technical tools, frameworks, and programming languages to help ATS parses detect them."
        })
    if not sections.get("projects"):
        findings.append({
            "category": "Structure",
            "severity": "MEDIUM",
            "explanation": "Missing Projects section.",
            "recommendation": "For academic and technical profiles, projects are critical. Add a 'Projects' section showing technologies applied in real scenarios."
        })

    # 4. Check Date Formats & Years in Experience / Education
    has_experience = "experience" in sections
    has_education = "education" in sections
    
    if has_experience:
        exp_text = sections["experience"]
        if not DATE_PATTERN.search(exp_text):
            findings.append({
                "category": "Dates",
                "severity": "MEDIUM",
                "explanation": "No employment dates/years detected in your Experience section.",
                "recommendation": "Add clear start and end dates (Month/Year format) to all job positions to establish timeline coherence."
            })
            
    if has_education:
        edu_text = sections["education"]
        if not DATE_PATTERN.search(edu_text):
            findings.append({
                "category": "Dates",
                "severity": "MEDIUM",
                "explanation": "No graduation years or educational dates detected in your Education section.",
                "recommendation": "Include your graduation month and year (or expected graduation date) next to each degree."
            })

    # 5. Action Verbs Check
    all_exp_proj_text = ""
    if has_experience:
        all_exp_proj_text += sections["experience"] + " "
    if "projects" in sections:
        all_exp_proj_text += sections["projects"]
        
    if all_exp_proj_text.strip():
        words_lower = [w.strip(".,;:()\"'").lower() for w in all_exp_proj_text.split()]
        action_verb_matches = [w for w in words_lower if w in STRONG_ACTION_VERBS]
        
        if len(action_verb_matches) < 3:
            findings.append({
                "category": "Content",
                "severity": "MEDIUM",
                "explanation": "Very few strong action verbs (e.g., 'Led', 'Developed', 'Optimized') were found in your experience/project descriptions.",
                "recommendation": "Start bullet points with strong action verbs rather than passive phrases like 'Responsible for' or 'Helped with'."
            })

    # 6. Measurable Achievements / Quantifiable Metrics Check
    if all_exp_proj_text.strip():
        metrics = METRIC_PATTERN.findall(all_exp_proj_text)
        if len(metrics) == 0:
            findings.append({
                "category": "Content",
                "severity": "MEDIUM",
                "explanation": "Your experience and project descriptions lack measurable results or quantifiable metrics.",
                "recommendation": "Recruiters and ATS favor impact-oriented descriptions. Add metrics such as accuracy rates, percentage improvements, processing time speedup, users served, or budget savings."
            })
        elif len(metrics) < 2:
            findings.append({
                "category": "Content",
                "severity": "LOW",
                "explanation": "Your resume has very few quantified metrics (only 1 detected).",
                "recommendation": "Try to back up at least 2-3 bullet points with numeric impact (e.g., 'Improved model F1-score by 12%', 'Reduced api latency by 20%')."
            })

    # 7. Formatting & Special Characters Check
    total_chars = len(text)
    if total_chars > 0:
        special_chars = len(re.findall(r'[^a-zA-Z0-9\s\.,;:\-@#\+&\*\(\)\{\}\[\]/\\\"\'%\$\?!]', text))
        special_char_percentage = (special_chars / total_chars) * 100
        if special_char_percentage > 4.0:
            findings.append({
                "category": "Formatting",
                "severity": "MEDIUM",
                "explanation": f"High density of unusual special characters ({special_char_percentage:.1f}%).",
                "recommendation": "Avoid decorative symbols, fancy bullet points, or non-standard characters that can break ATS text extractors. Use standard circular/square bullets."
            })
            
    # 8. Repeated Keywords (Key Stuffing Checker)
    if word_count > 0:
        words = [w.strip(".,;:()\"'").lower() for w in text.split() if len(w) > 3]
        word_counts = {}
        for w in words:
            word_counts[w] = word_counts.get(w, 0) + 1
            
        stuffed_words = [w for w, count in word_counts.items() if count > 20 and w not in {
            "with", "from", "that", "this", "their", "will", "have", "using", "project", "experience", "skills", "system", "data", "development", "management"
        }]
        
        if stuffed_words:
            findings.append({
                "category": "Formatting",
                "severity": "LOW",
                "explanation": f"Possible keyword stuffing. The words {stuffed_words[:3]} are repeated excessively.",
                "recommendation": "Avoid repeating keywords artificially. Integrate tools and concepts naturally into your job descriptions and context."
            })

    return findings
