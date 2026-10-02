import re
from typing import Dict, Any

from preprocessing import get_nlp

# Patterns for contact information
EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
PHONE_REGEX = re.compile(
    r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b|"
    r"\b(?:\+?91[-.\s]?)?[789]\d{9}\b|"
    r"\b(?:\+?\d{1,4}[-.\s]?)?\d{10,12}\b"
)
LINK_REGEX = re.compile(
    r"\b(?:github\.com|linkedin\.com/in|twitter\.com|portfolio|medium\.com|gitlab\.com)[\w\-\.\/]*\b|"
    r"https?://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(?:/\S*)?"
)

SECTION_PATTERNS = {
    "summary": re.compile(r"\b(summary|objective|professional summary|executive summary|about me|profile|career objective|professional profile)\b", re.IGNORECASE),
    "education": re.compile(r"\b(education|academic background|academics|qualification|scholastic|studies|educational qualifications)\b", re.IGNORECASE),
    "experience": re.compile(r"\b(experience|work history|employment|professional background|work experience|career history|professional experience|professional history)\b", re.IGNORECASE),
    "projects": re.compile(r"\b(projects|academic projects|personal projects|key projects|selected projects|technical projects|development experience)\b", re.IGNORECASE),
    "skills": re.compile(r"\b(skills|technical skills|key skills|core competencies|expertise|technologies|proficiencies|areas of expertise|technical expertise)\b", re.IGNORECASE),
    "certifications": re.compile(r"\b(certifications|certifications & licenses|licenses|courses|accreditations|training|certifications and licenses)\b", re.IGNORECASE),
    "achievements": re.compile(r"\b(achievements|awards|accomplishments|honors|publications|extracurricular activities|extracurriculars|co-curriculars)\b", re.IGNORECASE),
}


def _heuristic_entities(line: str):
    """Return simple PERSON/GPE-like candidates without a local NLP model."""
    words = line.split()
    candidates = []

    if 2 <= len(words) <= 4 and all(re.match(r"^[A-Z][A-Za-z'.-]*$", word) for word in words):
        candidates.append(("PERSON", line))

    location_match = re.search(
        r"\b([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,2}),\s*([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)?)\b",
        line,
    )
    if location_match:
        candidates.append(("GPE", location_match.group(0)))

    return candidates


def extract_personal_info(text: str) -> Dict[str, Any]:
    info = {"name": "", "email": "", "phone": "", "location": "", "links": []}

    emails = EMAIL_REGEX.findall(text)
    if emails:
        info["email"] = emails[0]

    phones = PHONE_REGEX.findall(text)
    if phones:
        info["phone"] = phones[0].strip()

    info["links"] = list(set(LINK_REGEX.findall(text)))

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    candidate_names = []
    location_candidates = []

    for line in lines[:10]:
        if info["email"] in line or info["phone"] in line or any(link in line for link in info["links"]):
            continue
        if re.search(r"\b(resume|cv|curriculum vitae|page|profile|phone|email|address|contact)\b", line, re.IGNORECASE):
            continue

        for label, value in _heuristic_entities(line):
            if label == "PERSON" and len(value.split()) <= 4:
                candidate_names.append(value)
            elif label == "GPE":
                location_candidates.append(value)

    if candidate_names:
        info["name"] = candidate_names[0]
    else:
        for line in lines[:3]:
            if (
                2 <= len(line.split()) <= 4
                and not EMAIL_REGEX.search(line)
                and not PHONE_REGEX.search(line)
                and not re.search(r"\b(resume|cv|curriculum vitae|summary|skills|education)\b", line, re.IGNORECASE)
            ):
                info["name"] = line
                break

    if location_candidates:
        info["location"] = ", ".join(dict.fromkeys(location_candidates))

    return info


def detect_sections(text: str) -> Dict[str, str]:
    lines = text.split("\n")
    sections = {k: [] for k in SECTION_PATTERNS.keys()}
    heading_indices = []

    for i, line in enumerate(lines):
        clean_line = line.strip()
        if not clean_line or len(clean_line.split()) > 5:
            continue

        for sec_name, pattern in SECTION_PATTERNS.items():
            if pattern.search(clean_line):
                is_heading = clean_line.isupper() or clean_line.endswith(":") or len(clean_line) < 25
                if is_heading:
                    heading_indices.append((i, sec_name))
                    break

    if not heading_indices:
        return segment_sections_fallback(text)

    heading_indices.sort(key=lambda x: x[0])
    first_index, _ = heading_indices[0]
    if first_index > 0:
        sections["summary"] = lines[:first_index]

    for idx, (line_index, sec_name) in enumerate(heading_indices):
        next_line_index = heading_indices[idx + 1][0] if idx + 1 < len(heading_indices) else len(lines)
        sections[sec_name].extend(lines[line_index + 1:next_line_index])

    return {
        sec: "\n".join(content).strip()
        for sec, content in sections.items()
        if "\n".join(content).strip()
    }


def segment_sections_fallback(text: str) -> Dict[str, str]:
    sections = {}
    lines = text.split("\n")
    current_sec = "summary"
    sections[current_sec] = []

    for line in lines:
        matched = False
        for sec_name, pattern in SECTION_PATTERNS.items():
            if pattern.search(line) and len(line.split()) < 4:
                current_sec = sec_name
                sections[current_sec] = []
                matched = True
                break
        if not matched:
            sections[current_sec].append(line)

    return {
        k: "\n".join(v).strip()
        for k, v in sections.items()
        if "\n".join(v).strip()
    }
