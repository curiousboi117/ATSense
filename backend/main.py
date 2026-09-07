import os
import tempfile
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import models
import schemas
from database import engine, get_db, SessionLocal
from config import settings
from parser import parse_file
from preprocessing import normalize_text
from nlp_engine import extract_personal_info, detect_sections
from skill_extractor import extract_skills, get_flat_skills
from ats_engine import run_ats_checks
from similarity_engine import calculate_similarity_metrics, load_semantic_model
from scoring_engine import calculate_ats_score
from recommendation_engine import generate_recommendations
from report_generator import generate_pdf_report
from utils import logger
from contextlib import asynccontextmanager

# Initialize database tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    # database initialization...

    db = SessionLocal()
    try:
        # ...
        if not default_user:
            # ...
            db.commit()
    finally:
        db.close()

    # Load NLP and semantic models during application startup
    try:
        load_semantic_model()
    except Exception as e:
        logger.error(f"Semantic model loading failed: {e}")

    try:
        from preprocessing import get_nlp
        get_nlp()
    except Exception as e:
        logger.error(f"spaCy model loading failed: {e}")

    yield


app = FastAPI(
    title="ATSense API",
    description="Explainable NLP & Machine Learning Resume Parser and ATS Analyzer API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
origins = settings.cors_list

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health", response_model=schemas.HealthResponse)
def health_check():
    """
    Checks systems state and whether model dependencies are loaded.
    """
    from preprocessing import nlp
    from similarity_engine import model_loaded, model_name
    return {
        "status": "healthy",
        "nlp_loaded": nlp is not None,
        "model_loaded": model_loaded,
        "model_name": model_name
    }

@app.post("/api/upload", response_model=schemas.AnalysisResponse)
async def upload_resume(
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(None),
    job_title: Optional[str] = Form("Target Role"),
    db: Session = Depends(get_db)
):
    """
    Uploads a resume file (PDF/DOCX), processes parsing, text preprocessing, NLP tagging, 
    skill taxonomy extraction, ATS auditing, scoring, and returns detailed results.
    """
    try:
        content = await file.read()
        filename = file.filename
        file_size = len(content)
        
        # 1. Parsing
        parsed_doc = parse_file(content, filename)
        raw_text = parsed_doc["text"]
        
        # 2. Text preprocessing
        normalized = normalize_text(raw_text)
        
        # 3. Versioning control: check existing resumes for this default user
        user = db.query(models.User).filter_by(id=1).first()
        existing_resumes = db.query(models.Resume).filter_by(user_id=user.id).all()
        next_version = len(existing_resumes) + 1
        
        # Save Resume to DB
        db_resume = models.Resume(
            user_id=user.id,
            filename=filename,
            file_size=file_size,
            version=next_version,
            extracted_text=normalized
        )
        db.add(db_resume)
        db.commit()
        db.refresh(db_resume)
        
        # 4. Extract personal and section info
        personal_info = extract_personal_info(normalized)
        sections = detect_sections(normalized)
        
        # 5. Extract skills
        skills = extract_skills(normalized)
        flat_skills = list(get_flat_skills(skills))
        
        # 6. Check Job Matching (if pasted)
        db_jd = None
        similarity_metrics = None
        if job_description and job_description.strip():
            db_jd = models.JobDescription(
                user_id=user.id,
                title=job_title or "Target Role",
                text=job_description.strip()
            )
            db.add(db_jd)
            db.commit()
            db.refresh(db_jd)
            
            similarity_metrics = calculate_similarity_metrics(normalized, job_description, flat_skills)
            
        # 7. Run ATS checks
        findings = run_ats_checks(normalized, sections, personal_info)
        
        # 8. Compute weighted score
        score, breakdown = calculate_ats_score(sections, skills, findings, similarity_metrics)
        
        # 9. Recommendations
        recommendations = generate_recommendations(normalized, sections, personal_info, findings, job_description or "")
        
        # Save analysis
        db_analysis = models.Analysis(
            resume_id=db_resume.id,
            job_description_id=db_jd.id if db_jd else None,
            ats_score=score,
            score_breakdown=breakdown,
            personal_info=personal_info,
            skills=skills,
            ats_checks=findings,
            recommendations=recommendations,
            similarity_metrics=similarity_metrics
        )
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        
        return {
            "id": db_analysis.id,
            "resume_id": db_resume.id,
            "resume_filename": db_resume.filename,
            "resume_version": db_resume.version,
            "job_description_id": db_analysis.job_description_id,
            "job_title": db_jd.title if db_jd else None,
            "ats_score": db_analysis.ats_score,
            "score_breakdown": db_analysis.score_breakdown,
            "personal_info": db_analysis.personal_info,
            "skills": db_analysis.skills,
            "ats_checks": db_analysis.ats_checks,
            "recommendations": db_analysis.recommendations,
            "similarity_metrics": db_analysis.similarity_metrics,
            "created_at": db_analysis.created_at
        }
        
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"System analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal processing error occurred.")

@app.post("/api/match-job", response_model=schemas.AnalysisResponse)
def match_job(
    resume_id: int,
    job_description: str = Form(...),
    job_title: Optional[str] = Form("Target Role"),
    db: Session = Depends(get_db)
):
    """
    Reruns analysis for an existing resume matched against a new Job Description.
    """
    resume = db.query(models.Resume).filter_by(id=resume_id).first()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")
        
    try:
        user = db.query(models.User).filter_by(id=1).first()
        db_jd = models.JobDescription(
            user_id=user.id,
            title=job_title or "Target Role",
            text=job_description.strip()
        )
        db.add(db_jd)
        db.commit()
        db.refresh(db_jd)
        
        # Redetect structures from saved resume text
        normalized = resume.extracted_text
        personal_info = extract_personal_info(normalized)
        sections = detect_sections(normalized)
        skills = extract_skills(normalized)
        flat_skills = list(get_flat_skills(skills))
        
        # Calculate new matching
        similarity_metrics = calculate_similarity_metrics(normalized, job_description, flat_skills)
        findings = run_ats_checks(normalized, sections, personal_info)
        
        # Score changes because JD is now active (different weights)
        score, breakdown = calculate_ats_score(sections, skills, findings, similarity_metrics)
        recommendations = generate_recommendations(normalized, sections, personal_info, findings, job_description)
        
        # Save new analysis
        db_analysis = models.Analysis(
            resume_id=resume.id,
            job_description_id=db_jd.id,
            ats_score=score,
            score_breakdown=breakdown,
            personal_info=personal_info,
            skills=skills,
            ats_checks=findings,
            recommendations=recommendations,
            similarity_metrics=similarity_metrics
        )
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        
        return {
            "id": db_analysis.id,
            "resume_id": resume.id,
            "resume_filename": resume.filename,
            "resume_version": resume.version,
            "job_description_id": db_analysis.job_description_id,
            "job_title": db_jd.title,
            "ats_score": db_analysis.ats_score,
            "score_breakdown": db_analysis.score_breakdown,
            "personal_info": db_analysis.personal_info,
            "skills": db_analysis.skills,
            "ats_checks": db_analysis.ats_checks,
            "recommendations": db_analysis.recommendations,
            "similarity_metrics": db_analysis.similarity_metrics,
            "created_at": db_analysis.created_at
        }
    except Exception as e:
        logger.error(f"Job matching failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to run job match.")

@app.get("/api/history", response_model=List[schemas.HistoryResponseItem])
def get_history(db: Session = Depends(get_db)):
    """
    Returns lists of all stored resume analyses.
    """
    analyses = db.query(models.Analysis).join(models.Resume).order_by(models.Analysis.created_at.desc()).all()
    history = []
    for a in analyses:
        history.append({
            "id": a.id,
            "resume_id": a.resume_id,
            "filename": a.resume.filename,
            "version": a.resume.version,
            "ats_score": a.ats_score,
            "job_title": a.job_description.title if a.job_description else None,
            "created_at": a.created_at
        })
    return history

@app.get("/api/analysis/{id}", response_model=schemas.AnalysisResponse)
def get_analysis(id: int, db: Session = Depends(get_db)):
    """
    Returns details of a specific analysis execution.
    """
    a = db.query(models.Analysis).filter_by(id=id).first()
    if not a:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis details not found.")
        
    return {
        "id": a.id,
        "resume_id": a.resume_id,
        "resume_filename": a.resume.filename,
        "resume_version": a.resume.version,
        "job_description_id": a.job_description_id,
        "job_title": a.job_description.title if a.job_description else None,
        "ats_score": a.ats_score,
        "score_breakdown": a.score_breakdown,
        "personal_info": a.personal_info,
        "skills": a.skills,
        "ats_checks": a.ats_checks,
        "recommendations": a.recommendations,
        "similarity_metrics": a.similarity_metrics,
        "created_at": a.created_at
    }

@app.get("/api/report/{id}/pdf")
def download_pdf_report(id: int, db: Session = Depends(get_db)):
    """
    Renders and serves a PDF download of the analysis results.
    """
    a = db.query(models.Analysis).filter_by(id=id).first()
    if not a:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis details not found.")
        
    report_data = {
        "filename": a.resume.filename,
        "version": a.resume.version,
        "ats_score": a.ats_score,
        "score_breakdown": a.score_breakdown,
        "personal_info": a.personal_info,
        "skills": a.skills,
        "ats_checks": a.ats_checks,
        "recommendations": a.recommendations,
        "similarity_metrics": a.similarity_metrics
    }
    
    # Save PDF report to temporary file and stream it
    temp_dir = tempfile.gettempdir()
    pdf_filename = f"ATSense_Report_v{a.resume.version}_{a.id}.pdf"
    output_path = os.path.join(temp_dir, pdf_filename)
    
    try:
        generate_pdf_report(report_data, output_path)
        return FileResponse(
            path=output_path, 
            media_type="application/pdf", 
            filename=pdf_filename
        )
    except Exception as e:
        logger.error(f"PDF compilation failed: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to compile PDF report.")

@app.get("/api/report/{id}/json")
def download_json_report(id: int, db: Session = Depends(get_db)):
    """
    Exports structured resume analysis as JSON.
    """
    a = db.query(models.Analysis).filter_by(id=id).first()
    if not a:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis details not found.")
        
    export = {
        "atsense_version": "1.0.0",
        "ats_score": a.ats_score,
        "score_breakdown": a.score_breakdown,
        "personal_info": a.personal_info,
        "skills": a.skills,
        "ats_checks": a.ats_checks,
        "recommendations": a.recommendations,
        "similarity_metrics": a.similarity_metrics,
        "analysis_metadata": {
            "resume_filename": a.resume.filename,
            "resume_version": a.resume.version,
            "created_at": str(a.created_at),
            "job_title": a.job_description.title if a.job_description else "None"
        }
    }
    return JSONResponse(content=export, headers={"Content-Disposition": f"attachment; filename=ATSense_Report_v{a.resume.version}.json"})

@app.delete("/api/resume/{id}")
def delete_resume_data(id: int, db: Session = Depends(get_db)):
    """
    Deletes resume records and cascade deletes its analyses.
    """
    resume = db.query(models.Resume).filter_by(id=id).first()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")
    try:
        db.delete(resume)
        db.commit()
        return {"status": "success", "message": "Resume and analysis data deleted."}
    except Exception as e:
        logger.error(f"Deletion failed: {e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Deletion failed.")

@app.post("/api/reset-all")
def reset_database(db: Session = Depends(get_db)):
    """
    Wipes all resumes, analyses, and JDs for demonstration resets.
    """
    try:
        db.query(models.Analysis).delete()
        db.query(models.Resume).delete()
        db.query(models.JobDescription).delete()
        db.commit()
        return {"status": "success", "message": "All database histories reset successfully."}
    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Reset failed.")
