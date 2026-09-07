import re
from typing import Dict, Any, List
from preprocessing import get_nlp

# Patterns for contact information
EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
PHONE_REGEX = re.compile(
    r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b|'  # standard US
    r'\b(?:\+?91[-.\s]?)?[789]\d{9}\b|'                                # Indian mobile
    r'\b(?:\+?\d{1,4}[-.\s]?)?\d{10,12}\b'                             # generic international
)
LINK_REGEX = re.compile(
    r'\b(?:github\.com|linkedin\.com/in|twitter\.com|portfolio|medium\.com|gitlab\.com)[\w\-\.\/]*\b|'
    r'https?://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(?:/\S*)?'
)

# Heading patterns for section extraction
SECTION_PATTERNS = {
    "summary": re.compile(r'\b(summary|objective|professional summary|executive summary|about me|profile|career objective|professional profile)\b', re.IGNORECASE),
    "education": re.compile(r'\b(education|academic background|academics|qualification|scholastic|studies|educational qualifications)\b', re.IGNORECASE),
    "experience": re.compile(r'\b(experience|work history|employment|professional background|work experience|career history|professional experience|professional history)\b', re.IGNORECASE),
    "projects": re.compile(r'\b(projects|academic projects|personal projects|key projects|selected projects|technical projects|development experience)\b', re.IGNORECASE),
    "skills": re.compile(r'\b(skills|technical skills|key skills|core competencies|expertise|technologies|proficiencies|areas of expertise|technical expertise)\b', re.IGNORECASE),
    "certifications": re.compile(r'\b(certifications|certifications & licenses|licenses|courses|accreditations|training|certifications and licenses)\b', re.IGNORECASE),
    "achievements": re.compile(r'\b(achievements|awards|accomplishments|honors|publications|extracurricular activities|extracurriculars|co-curriculars)\b', re.IGNORECASE),
}

def extract_personal_info(text: str) -> Dict[str, Any]:
    """
    Extracts name, email, phone number, location, and key links from resume text.
    """
    info = {
        "name": "",
        "email": "",
        "phone": "",
        "location": "",
        "links": []
    }
    
    # 1. Email extraction
    emails = EMAIL_REGEX.findall(text)
    if emails:
        info["email"] = emails[0]
        
    # 2. Phone extraction
    phones = PHONE_REGEX.findall(text)
    if phones:
        info["phone"] = phones[0].strip()
        
    # 3. Links extraction
    links = LINK_REGEX.findall(text)
    info["links"] = list(set(links))
    
    # 4. Name extraction heuristics
    nlp = get_nlp()
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Use spaCy NER to scan first 5 lines for PERSON entities
    candidate_names = []
    lines_to_check = lines[:5]
    for line in lines_to_check:
        # Skip lines that contain email, phone, or links
        if info["email"] in line or info["phone"] in line or any(l in line for l in info["links"]):
            continue
        # Skip lines containing common words
        if re.search(r'\b(resume|cv|curriculum vitae|page|profile|phone|email|address|contact)\b', line, re.IGNORECASE):
            continue
            
        doc = nlp(line)
        for ent in doc.ents:
            if ent.label_ == "PERSON" and len(ent.text.split()) >= 2 and len(ent.text.split()) <= 4:
                candidate_names.append(ent.text)
                
    if candidate_names:
        info["name"] = candidate_names[0]
    else:
        # Fallback to the first reasonable non-empty line that doesn't have contact info or resume titles
        for line in lines[:3]:
            if (len(line.split()) >= 2 and len(line.split()) <= 4 and 
                not EMAIL_REGEX.search(line) and 
                not PHONE_REGEX.search(line) and
                not re.search(r'\b(resume|cv|curriculum vitae|summary|skills|education)\b', line, re.IGNORECASE)):
                info["name"] = line
                break
                
    # 5. Location extraction using spaCy GPE/LOC tags in first 10 lines
    location_candidates = []
    for line in lines[:10]:
        doc = nlp(line)
        for ent in doc.ents:
            if ent.label_ in ("GPE", "LOC"):
                location_candidates.append(ent.text)
    if location_candidates:
        info["location"] = ", ".join(list(set(location_candidates)))
        
    return info

def detect_sections(text: str) -> Dict[str, str]:
    """
    Splits the resume text into standard sections based on heading patterns.
    """
    lines = text.split('\n')
    sections = {k: [] for k in SECTION_PATTERNS.keys()}
    current_section = None
    
    # Track headings index to partition text
    heading_indices = []
    
    for i, line in enumerate(lines):
        clean_line = line.strip()
        if not clean_line or len(clean_line.split()) > 5:
            continue
            
        # Check if the line matches any section heading pattern
        matched = False
        for sec_name, pattern in SECTION_PATTERNS.items():
            # Must be a boundary match (e.g. exactly "Skills" or "Work Experience" or at start of line)
            if pattern.search(clean_line):
                # Ensure it's not a false positive (e.g., "Excel skills" inside list)
                # By checking if it is uppercase, standalone, or has punctuation like ':' at the end
                is_heading = (
                    clean_line.isupper() or 
                    clean_line.endswith(':') or 
                    len(clean_line) < 25
                )
                if is_heading:
                    heading_indices.append((i, sec_name))
                    matched = True
                    break
                    
    # Reconstruct section text by grouping text between identified headers
    if not heading_indices:
        # Fallback: segment text by simple word scans if headers are not found
        return segment_sections_fallback(text)
        
    # Sort heading indices by order of appearance
    heading_indices.sort(key=lambda x: x[0])
    
    # Add start of document as implicit "summary" or header context
    first_index, first_sec = heading_indices[0]
    if first_index > 0:
        sections["summary"] = lines[:first_index]
        
    for idx in range(len(heading_indices)):
        curr_line_idx, sec_name = heading_indices[idx]
        next_line_idx = heading_indices[idx + 1][0] if idx + 1 < len(heading_indices) else len(lines)
        
        # Section text consists of lines between these headers
        section_lines = lines[curr_line_idx + 1 : next_line_idx]
        sections[sec_name].extend(section_lines)
        
    # Join text lines for each section
    final_sections = {}
    for sec, content in sections.items():
        joined = "\n".join(content).strip()
        if joined:
            final_sections[sec] = joined
            
    # If no summary section detected, look if we extracted header lines as summary
    if "summary" not in final_sections:
        # Check if we can find standard objective/summary keywords
        pass
        
    return final_sections

def segment_sections_fallback(text: str) -> Dict[str, str]:
    """
    Fallback method when distinct structural headings aren't found.
    Splits text by keyword blocks.
    """
    sections = {}
    lines = text.split('\n')
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
            
    return {k: "\n".join(v).strip() for k, v in sections.items() if v}
