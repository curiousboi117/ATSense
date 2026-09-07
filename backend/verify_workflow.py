import os
import requests
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def create_test_pdf(filepath):
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph("Jane Test Doe", styles['Heading1']))
    story.append(Paragraph("Email: jane.test@email.com | Phone: 9876543210 | Location: Mumbai, India", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Summary", styles['Heading2']))
    story.append(Paragraph("Experienced AI Engineer specializing in Natural Language Processing and deep learning frameworks.", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Education", styles['Heading2']))
    story.append(Paragraph("Bachelor of Technology in Artificial Intelligence and Data Science, Mumbai University (2020-2024)", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Experience", styles['Heading2']))
    story.append(Paragraph("Machine Learning Engineer at AI Labs (Jan 2023 - Present)\n- Led development of NLP models using PyTorch and FastAPI, improving latency by 35%.\n- Maintained AWS cloud deployments using Docker.", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Projects", styles['Heading2']))
    story.append(Paragraph("ATSense Resume Optimizer (Fall 2023)\n- Developed explainable scoring algorithms and job matching similarities in Python.", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Skills", styles['Heading2']))
    story.append(Paragraph("Python, PyTorch, FastAPI, AWS, Docker, Git, SQL, Teamwork, Communication", styles['Normal']))
    
    doc.build(story)

def run_verification():
    print("=" * 60)
    print("ATSense End-to-End Workflow Verification")
    print("=" * 60)
    
    # 1. Create a temporary PDF
    temp_dir = tempfile.gettempdir()
    filepath = os.path.join(temp_dir, "test_verify_resume.pdf")
    create_test_pdf(filepath)
    print(f"[+] Synthetic test resume PDF created at: {filepath}")
    
    # 2. Define API endpoint & payload
    url = "http://localhost:8000/api/upload"
    files = {'file': ('test_verify_resume.pdf', open(filepath, 'rb'), 'application/pdf')}
    data = {
        'job_title': 'Senior NLP Engineer',
        'job_description': 'We are looking for a Senior NLP Engineer with experience in Python, PyTorch, AWS, Docker, Git, and FastAPI. Soft skills like communication and teamwork are highly preferred.'
    }
    
    # 3. Post to API
    print("[+] Submitting upload request to FastAPI backend...")
    try:
        response = requests.post(url, files=files, data=data, timeout=30)
        if response.status_code != 200:
            print(f"[!] Error: API returned status code {response.status_code}")
            print(response.text)
            return False
            
        res_data = response.json()
        print("[+] API Response received successfully. Validating schema properties:")
        
        # 4. Validations
        print(f"  - ATS Score: {res_data.get('ats_score')} (Expected Float)")
        assert isinstance(res_data.get('ats_score'), (int, float)), "ATS Score must be numeric"
        
        print(f"  - Name: '{res_data.get('personal_info', {}).get('name')}' (Expected: Jane Test Doe)")
        assert "Jane Test Doe" in res_data.get('personal_info', {}).get('name'), "Candidate name mismatch"
        
        print(f"  - Email: '{res_data.get('personal_info', {}).get('email')}' (Expected: jane.test@email.com)")
        assert res_data.get('personal_info', {}).get('email') == "jane.test@email.com", "Email mismatch"
        
        print(f"  - Phone: '{res_data.get('personal_info', {}).get('phone')}' (Expected: 9876543210)")
        assert "9876543210" in res_data.get('personal_info', {}).get('phone'), "Phone mismatch"
        
        sim = res_data.get('similarity_metrics', {})
        print(f"  - Similarity overall match: {sim.get('overall_match')}% (Method: {sim.get('method_used')})")
        assert sim.get('overall_match') is not None, "Missing similarity metrics"
        
        print(f"  - Matched Skills: {sim.get('matched_skills')}")
        print(f"  - Missing Skills: {sim.get('missing_skills')}")
        
        print(f"  - ATS Checks Count: {len(res_data.get('ats_checks', []))}")
        print(f"  - Recommendations Count: {len(res_data.get('recommendations', []))}")
        
        print("=" * 60)
        print("[+] SUCCESS: ATSense E2E pipeline verified successfully!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"[!] Exception encountered: {e}")
        return False
    finally:
        # Clean up file
        try:
            os.remove(filepath)
        except Exception:
            pass

if __name__ == "__main__":
    run_verification()
