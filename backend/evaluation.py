import os
import re
from typing import Dict, List, Set, Any
from nlp_engine import extract_personal_info, detect_sections
from skill_extractor import extract_skills, get_flat_skills

# Synthetic test dataset of resumes with ground truth labels for academic evaluation
EVALUATION_DATASET = [
    {
        "id": 1,
        "name": "Synthetic Student Resume (AI/ML Engineer)",
        "text": """
John Doe
Email: john.doe@email.com | Phone: +91 9876543210 | Location: Bangalore, India
LinkedIn: linkedin.com/in/johndoe | GitHub: github.com/johndoe

Professional Summary
Highly motivated AI/ML Engineer with 2+ years of experience building machine learning models. Proficient in Python, TensorFlow, PyTorch, and NLP.

Education
Bachelor of Technology in Artificial Intelligence & Data Science
XYZ Institute of Technology, Bangalore | 2020 - 2024 (GPA: 9.2/10)

Experience
Machine Learning Intern - TechSolutions Inc. (Jan 2023 - Present)
- Developed and optimized a custom NLP pipeline using SpaCy and PyTorch, increasing classification accuracy by 15%.
- Maintained cloud deployment scripts using Docker and AWS Lambda.
- Designed SQL databases to store and preprocess large structured datasets.

Projects
Iterative Academic Search Engine (Fall 2023)
- Built a semantic search engine using FastAPI, SQLite, and Sentence Transformers (all-MiniLM-L6-v2).
- Achieved a cosine similarity matching latency under 50ms for a database of 10k records.

Skills
- Programming: Python, C++, SQL, Go
- Frameworks: TensorFlow, PyTorch, scikit-learn, FastAPI, React
- Tools: Git, GitHub, Docker, AWS, Linux
- Soft Skills: Teamwork, Problem Solving, Communication
""",
        "ground_truth": {
            "name": "John Doe",
            "email": "john.doe@email.com",
            "phone": "+91 9876543210",
            "sections": {"summary", "education", "experience", "projects", "skills"},
            "skills": {"python", "c++", "sql", "go", "tensorflow", "pytorch", "scikit-learn", "fastapi", "react", "git", "github", "docker", "aws", "linux", "teamwork", "problem solving", "communication", "nlp", "spacy"}
        }
    },
    {
        "id": 2,
        "name": "Synthetic Full-Stack Developer",
        "text": """
Jane Smith
jane.smith@webdev.org | 123-456-7890 | Seattle, WA
portfolio: github.com/janesmith

Objective
Passionate Web Developer looking to apply design engineering and web standards at scale.

Work Experience
Frontend Engineer - WebCraft Corp (March 2022 - July 2024)
- Engineered responsive React and Next.js interfaces with Tailwind CSS styling.
- Streamlined team workflows by implementing CI/CD pipelines in GitLab and deploying to GCP.
- Collaborated in an agile team using Git version control and project management tools.

Education
B.S. Computer Science - University of Washington (Graduated 2022)

Skills
Technical Skills: React, Next.js, Node.js, Express, JavaScript, TypeScript, HTML, CSS, Tailwind, MongoDB, PostgreSQL, Git, GitLab, GCP, Docker
Soft Skills: Collaboration, Leadership, Critical Thinking
""",
        "ground_truth": {
            "name": "Jane Smith",
            "email": "jane.smith@webdev.org",
            "phone": "123-456-7890",
            "sections": {"summary", "education", "experience", "skills"},
            "skills": {"react", "next.js", "node.js", "express", "javascript", "typescript", "html", "css", "tailwind", "mongodb", "postgresql", "git", "gitlab", "gcp", "docker", "collaboration", "leadership", "critical thinking"}
        }
    }
]

def calculate_precision_recall_f1(retrieved: Set[Any], ground_truth: Set[Any]) -> Dict[str, float]:
    """
    Computes standard Precision, Recall, and F1 metrics.
    """
    if not retrieved and not ground_truth:
        return {"precision": 100.0, "recall": 100.0, "f1": 100.0}
    if not retrieved or not ground_truth:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
        
    tp = len(retrieved.intersection(ground_truth))
    fp = len(retrieved - ground_truth)
    fn = len(ground_truth - retrieved)
    
    precision = (tp / (tp + fp)) * 100 if (tp + fp) > 0 else 0.0
    recall = (tp / (tp + fn)) * 100 if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    
    return {
        "precision": round(precision, 2),
        "recall": round(recall, 2),
        "f1": round(f1, 2)
    }

def run_evaluation() -> Dict[str, Any]:
    """
    Performs NLP evaluation comparing extraction results against the synthetic ground truth dataset.
    """
    results = {
        "name_accuracy": 0.0,
        "email_accuracy": 0.0,
        "phone_accuracy": 0.0,
        "sections": {"precision": 0.0, "recall": 0.0, "f1": 0.0},
        "skills": {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    }
    
    total_samples = len(EVALUATION_DATASET)
    name_hits = 0
    email_hits = 0
    phone_hits = 0
    
    section_metrics_list = []
    skills_metrics_list = []
    
    for sample in EVALUATION_DATASET:
        text = sample["text"]
        gt = sample["ground_truth"]
        
        # 1. Personal info accuracy
        extracted_info = extract_personal_info(text)
        
        if extracted_info["name"].strip().lower() == gt["name"].strip().lower():
            name_hits += 1
        if extracted_info["email"].strip().lower() == gt["email"].strip().lower():
            email_hits += 1
            
        # Clean phone numbers for loose comparison
        clean_ext = re.sub(r'\D', '', extracted_info["phone"])
        clean_gt = re.sub(r'\D', '', gt["phone"])
        if clean_ext in clean_gt or clean_gt in clean_ext:
            phone_hits += 1
            
        # 2. Section detection accuracy
        detected_sections = set(detect_sections(text).keys())
        sec_metrics = calculate_precision_recall_f1(detected_sections, gt["sections"])
        section_metrics_list.append(sec_metrics)
        
        # 3. Skills extraction accuracy
        extracted_skills_dict = extract_skills(text)
        extracted_skills_flat = get_flat_skills(extracted_skills_dict)
        
        skills_metrics = calculate_precision_recall_f1(extracted_skills_flat, gt["skills"])
        skills_metrics_list.append(skills_metrics)
        
    # Calculate macro averages
    results["name_accuracy"] = round((name_hits / total_samples) * 100, 2)
    results["email_accuracy"] = round((email_hits / total_samples) * 100, 2)
    results["phone_accuracy"] = round((phone_hits / total_samples) * 100, 2)
    
    for metric in ["precision", "recall", "f1"]:
        results["sections"][metric] = round(sum(x[metric] for x in section_metrics_list) / total_samples, 2)
        results["skills"][metric] = round(sum(x[metric] for x in skills_metrics_list) / total_samples, 2)
        
    return results

if __name__ == "__main__":
    print("="*60)
    print("ATSense NLP Pipeline Academic Evaluation Metrics")
    print("="*60)
    metrics = run_evaluation()
    print(f"Name Extraction Accuracy:  {metrics['name_accuracy']}%")
    print(f"Email Extraction Accuracy: {metrics['email_accuracy']}%")
    print(f"Phone Extraction Accuracy: {metrics['phone_accuracy']}%")
    print("-" * 60)
    print("Section Detection (Macro Average):")
    print(f"  Precision: {metrics['sections']['precision']}%")
    print(f"  Recall:    {metrics['sections']['recall']}%")
    print(f"  F1-Score:  {metrics['sections']['f1']}%")
    print("-" * 60)
    print("Skill Extraction Taxonomy Matching (Macro Average):")
    print(f"  Precision: {metrics['skills']['precision']}%")
    print(f"  Recall:    {metrics['skills']['recall']}%")
    print(f"  F1-Score:  {metrics['skills']['f1']}%")
    print("="*60)
