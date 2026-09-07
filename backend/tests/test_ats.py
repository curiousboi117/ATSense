import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ats_engine import run_ats_checks
from scoring_engine import calculate_ats_score

def test_ats_checks():
    text = "Short text"
    sections = {}
    personal_info = {"name": "", "email": "", "phone": ""}
    
    findings = run_ats_checks(text, sections, personal_info)
    severities = [f["severity"] for f in findings]
    
    # Missing education, experience, contact, and short text should trigger HIGH severities
    assert "HIGH" in severities
    
def test_score_range():
    sections = {"education": "B.S. degree", "experience": "Worked at Google for 5 years"}
    skills = {"programming": ["Python", "C++"], "web": ["React"]}
    findings = []
    
    score, breakdown = calculate_ats_score(sections, skills, findings)
    assert 0 <= score <= 100
    assert "skills" in breakdown
    assert "formatting" in breakdown
