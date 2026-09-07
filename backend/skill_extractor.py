import re
from typing import Dict, List, Set

SKILL_TAXONOMY = {
    "programming": [
        "Python", "Java", "C++", "C#", "C", "JavaScript", "TypeScript", "Go", "Rust", 
        "Kotlin", "Swift", "Scala", "Ruby", "PHP", "Perl", "R", "Dart"
    ],
    "web": [
        "HTML", "CSS", "React", "Next.js", "Node.js", "Express", "Angular", "Vue", "Vue.js",
        "Tailwind CSS", "Tailwind", "Bootstrap", "Django", "Flask", "FastAPI", "Spring Boot", 
        "ASP.NET", "GraphQL", "jQuery", "Sass"
    ],
    "ai_ml": [
        "Machine Learning", "Deep Learning", "NLP", "Natural Language Processing", "Computer Vision", 
        "TensorFlow", "PyTorch", "scikit-learn", "Pandas", "NumPy", "Keras", "OpenCV", "Hugging Face", 
        "LLM", "Large Language Models", "LangChain", "Reinforcement Learning", "SciPy", "Neural Networks"
    ],
    "data": [
        "SQL", "PostgreSQL", "MySQL", "MongoDB", "Power BI", "Tableau", "Redis", "Elasticsearch", 
        "Spark", "Apache Spark", "Hadoop", "Hive", "Data Engineering", "ETL", "Oracle", "SQLite", 
        "DynamoDB", "Cassandra", "Data Warehousing", "Snowflake"
    ],
    "cloud_devops": [
        "AWS", "Azure", "GCP", "Google Cloud", "Docker", "Kubernetes", "Git", "GitHub", "GitLab", 
        "Jenkins", "CI/CD", "Terraform", "Ansible", "Linux", "Bash", "Nginx", "Apache", 
        "Prometheus", "Grafana", "AWS Lambda"
    ],
    "soft_skills": [
        "Communication", "Leadership", "Teamwork", "Problem Solving", "Critical Thinking", 
        "Time Management", "Adaptability", "Collaboration", "Presentation", "Creativity", 
        "Organization", "Mentoring", "Negotiation", "Conflict Resolution", "Project Management"
    ]
}

# Compile patterns for efficiency
def compile_skill_patterns() -> Dict[str, List[tuple]]:
    """
    Compiles regex patterns for skills in the taxonomy.
    Short or single-letter skills are matched case-sensitively.
    """
    compiled = {}
    for category, skills in SKILL_TAXONOMY.items():
        patterns = []
        for skill in skills:
            # Determine case sensitivity: short names like C, R, Go, AWS, SQL
            case_insensitive = True
            if len(skill) <= 2 or skill.isupper():
                case_insensitive = False
                
            # Escape skill name for safe regex
            escaped = re.escape(skill)
            
            # Handle special cases like Next.js, C++
            if "++" in skill:
                pattern_str = r'\bc\+\+\b'
                case_insensitive = True
            elif "#" in skill:
                pattern_str = r'\bc#\b'
                case_insensitive = True
            elif "." in skill:
                pattern_str = rf'\b{escaped}\b'
            else:
                pattern_str = rf'\b{escaped}\b'
                
            flags = re.IGNORECASE if case_insensitive else 0
            patterns.append((skill, re.compile(pattern_str, flags)))
        compiled[category] = patterns
    return compiled

SKILL_PATTERNS = compile_skill_patterns()

def extract_skills(text: str) -> Dict[str, List[str]]:
    """
    Extracts skills from text categorized by programming, web, ai_ml, data, cloud_devops, soft_skills.
    """
    extracted = {cat: [] for cat in SKILL_TAXONOMY.keys()}
    
    for category, patterns in SKILL_PATTERNS.items():
        found_skills = set()
        for skill_name, pattern in patterns:
            if pattern.search(text):
                # Clean up synonyms/variants
                canonical_name = skill_name
                if skill_name == "Vue.js":
                    canonical_name = "Vue"
                elif skill_name == "Tailwind CSS":
                    canonical_name = "Tailwind"
                elif skill_name == "Apache Spark":
                    canonical_name = "Spark"
                elif skill_name == "Google Cloud":
                    canonical_name = "GCP"
                elif skill_name == "Natural Language Processing":
                    canonical_name = "NLP"
                elif skill_name == "Large Language Models":
                    canonical_name = "LLM"
                    
                found_skills.add(canonical_name)
        extracted[category] = sorted(list(found_skills))
        
    return extracted

def get_flat_skills(skills_dict: Dict[str, List[str]]) -> Set[str]:
    """
    Flattens skill dictionary to a set of strings.
    """
    flat = set()
    for skills in skills_dict.values():
        for skill in skills:
            flat.add(skill.lower())
    return flat
