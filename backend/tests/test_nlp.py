import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlp_engine import extract_personal_info, detect_sections
from skill_extractor import extract_skills

SAMPLE_RESUME = """
Jane Doe
Email: jane.doe@webdev.com | Phone: 123-456-7890 | Location: San Francisco, CA

Professional Summary
Experienced Frontend Engineer with solid skills in React and JavaScript.

Education
B.S. in Computer Science - Stanford University

Experience
Software Engineer - WebCo (2022 - Present)
- Developed responsive web applications using HTML, CSS, and TypeScript.
"""

def test_personal_info_extraction():
    info = extract_personal_info(SAMPLE_RESUME)
    assert "jane.doe@webdev.com" == info["email"]
    assert "123-456-7890" == info["phone"]
    assert "Jane Doe" in info["name"]

def test_section_detection():
    sections = detect_sections(SAMPLE_RESUME)
    assert "summary" in sections or "skills" in sections or "education" in sections or "experience" in sections
    assert "education" in sections
    assert "experience" in sections

def test_skill_extraction():
    skills = extract_skills(SAMPLE_RESUME)
    assert "React" in skills["web"]
    assert "HTML" in skills["web"]
    assert "TypeScript" in skills["programming"]
