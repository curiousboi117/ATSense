import os
import tempfile
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from starlette.background import BackgroundTask

import models
import schemas
from auth import create_access_token, decode_access_token, verify_password
from ats_engine import run_ats_checks
from config import settings
from database import get_db
from nlp_engine import detect_sections, extract_personal_info
from parser import parse_file
from preprocessing import normalize_text
from recommendation_engine import generate_recommendations
from report_generator import generate_pdf_report
from scoring_engine import calculate_ats_score
from similarity_engine import calculate_similarity_metrics, load_semantic_model
from skill_extractor import extract_skills, get_flat_skills
from utils import logger


# Upload safety limits
MAX_RESUME_SIZE = 5 * 1024 * 1024  # 5 MiB
ALLOWED_RESUME_EXTENSIONS = {".pdf", ".docx"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize application resources during startup."""
    # Initialize database tables.
    models.Base.metadata.create_all(bind=engine)

    # Load NLP and semantic models during application startup.
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

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Return the authenticated user from a valid JWT access token."""
    token = credentials.credentials
    user_id = decode_access_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

@app.post("/api/auth/login", response_model=schemas.TokenResponse)
def login(
    login_data: schemas.LoginRequest,
    db: Session = Depends(get_db),
):
    """Authenticate a user and return a JWT access token."""
    user = (
        db.query(models.User)
        .filter(models.User.username == login_data.username)
        .first()
    )

    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(str(user.id))

    return schemas.TokenResponse(access_token=access_token)

def get_owned_analysis(
    analysis_id: int,
    user: models.User,
    db: Session,
):
    """Fetch an analysis only when it belongs to the current user."""
    analysis = (
        db.query(models.Analysis)
        .join(models.Resume)
        .filter(
            models.Analysis.id == analysis_id,
            models.Resume.user_id == user.id,
        )
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis details not found.",
        )

    return analysis


@app.get("/api/health", response_model=schemas.HealthResponse)
def health_check():
    from preprocessing import nlp
    from similarity_engine import model_loaded, model_name

    return {
        "status": "healthy",
        "nlp_loaded": nlp is not None,
        "model_loaded": model_loaded,
        "model_name": model_name,
    }


@app.post("/api/upload", response_model=schemas.AnalysisResponse)
async def upload_resume(
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(None),
    job_title: Optional[str] = Form("Target Role"),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """
    Upload a resume, process it, optionally match it against a job description,
    and return the complete analysis.
    """
    try:
        content = await file.read()
        filename = file.filename

        if not filename:
            raise ValueError("A filename is required.")

        file_size = len(content)

        if file_size == 0:
            raise ValueError("The uploaded file is empty.")

        if file_size > MAX_RESUME_SIZE:
            raise ValueError("Resume file size must not exceed 5 MB.")

        extension = os.path.splitext(filename)[1].lower()
        if extension not in ALLOWED_RESUME_EXTENSIONS:
            raise ValueError("Only PDF and DOCX resume files are supported.")

        # 1. Parsing
        parsed_doc = parse_file(content, filename)
        raw_text = parsed_doc["text"]

        # 2. Text preprocessing
        normalized = normalize_text(raw_text)

        # 3. Versioning for the current user
        existing_resumes = (
            db.query(models.Resume)
            .filter_by(user_id=user.id)
            .all()
        )
        next_version = len(existing_resumes) + 1

        # 4. Save resume
        db_resume = models.Resume(
            user_id=user.id,
            filename=filename,
            file_size=file_size,
            version=next_version,
            extracted_text=normalized,
        )
        db.add(db_resume)
        db.flush()

        # 5. Extract personal and section information
        personal_info = extract_personal_info(normalized)
        sections = detect_sections(normalized)

        # 6. Extract skills
        skills = extract_skills(normalized)
        flat_skills = list(get_flat_skills(skills))

        # 7. Optional job matching
        db_jd = None
        similarity_metrics = None

        if job_description and job_description.strip():
            cleaned_job_description = job_description.strip()
            db_jd = models.JobDescription(
                user_id=user.id,
                title=job_title or "Target Role",
                text=cleaned_job_description,
            )
            db.add(db_jd)
            db.flush()

            similarity_metrics = calculate_similarity_metrics(
                normalized,
                cleaned_job_description,
                flat_skills,
            )

        # 8. ATS checks
        findings = run_ats_checks(normalized, sections, personal_info)

        # 9. Score
        score, breakdown = calculate_ats_score(
            sections,
            skills,
            findings,
            similarity_metrics,
        )

        # 10. Recommendations
        recommendations = generate_recommendations(
            normalized,
            sections,
            personal_info,
            findings,
            job_description or "",
        )

        # 11. Save analysis
        db_analysis = models.Analysis(
            resume_id=db_resume.id,
            job_description_id=db_jd.id if db_jd else None,
            ats_score=score,
            score_breakdown=breakdown,
            personal_info=personal_info,
            skills=skills,
            ats_checks=findings,
            recommendations=recommendations,
            similarity_metrics=similarity_metrics,
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
            "created_at": db_analysis.created_at,
        }

    except HTTPException:
        db.rollback()
        raise
    except ValueError as ve:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
    except Exception:
        db.rollback()
        logger.error("System analysis failed.", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal processing error occurred.",
        )


@app.post("/api/match-job", response_model=schemas.AnalysisResponse)
def match_job(
    resume_id: int,
    job_description: str = Form(...),
    job_title: Optional[str] = Form("Target Role"),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """
    Re-run analysis for an existing resume against a new job description.
    """
    resume = (
        db.query(models.Resume)
        .filter_by(id=resume_id, user_id=user.id)
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found.",
        )

    if not job_description or not job_description.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job description cannot be empty.",
        )

    try:
        cleaned_job_description = job_description.strip()

        db_jd = models.JobDescription(
            user_id=user.id,
            title=job_title or "Target Role",
            text=cleaned_job_description,
        )
        db.add(db_jd)
        db.flush()

        normalized = resume.extracted_text
        personal_info = extract_personal_info(normalized)
        sections = detect_sections(normalized)
        skills = extract_skills(normalized)
        flat_skills = list(get_flat_skills(skills))

        similarity_metrics = calculate_similarity_metrics(
            normalized,
            cleaned_job_description,
            flat_skills,
        )
        findings = run_ats_checks(normalized, sections, personal_info)

        score, breakdown = calculate_ats_score(
            sections,
            skills,
            findings,
            similarity_metrics,
        )
        recommendations = generate_recommendations(
            normalized,
            sections,
            personal_info,
            findings,
            cleaned_job_description,
        )

        db_analysis = models.Analysis(
            resume_id=resume.id,
            job_description_id=db_jd.id,
            ats_score=score,
            score_breakdown=breakdown,
            personal_info=personal_info,
            skills=skills,
            ats_checks=findings,
            recommendations=recommendations,
            similarity_metrics=similarity_metrics,
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
            "created_at": db_analysis.created_at,
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        logger.error("Job matching failed.", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to run job match.",
        )


@app.get("/api/history", response_model=List[schemas.HistoryResponseItem])
def get_history(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """
    Return analyses belonging only to the current user.
    """
    analyses = (
        db.query(models.Analysis)
        .join(models.Resume)
        .filter(models.Resume.user_id == user.id)
        .order_by(models.Analysis.created_at.desc())
        .all()
    )

    return [
        {
            "id": a.id,
            "resume_id": a.resume_id,
            "filename": a.resume.filename,
            "version": a.resume.version,
            "ats_score": a.ats_score,
            "job_title": a.job_description.title if a.job_description else None,
            "created_at": a.created_at,
        }
        for a in analyses
    ]


@app.get("/api/analysis/{id}", response_model=schemas.AnalysisResponse)
def get_analysis(
    id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """
    Return a specific analysis only when it belongs to the current user.
    """
    a = get_owned_analysis(id, user, db)

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
        "created_at": a.created_at,
    }


def _delete_temp_file(path: str) -> None:
    """Remove a generated report after the response has been sent."""
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError as e:
        logger.warning(f"Failed to remove temporary report {path}: {e}")


@app.get("/api/report/{id}/pdf")
def download_pdf_report(
    id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """
    Generate and serve a PDF report for an owned analysis.
    """
    a = get_owned_analysis(id, user, db)

    report_data = {
        "filename": a.resume.filename,
        "version": a.resume.version,
        "ats_score": a.ats_score,
        "score_breakdown": a.score_breakdown,
        "personal_info": a.personal_info,
        "skills": a.skills,
        "ats_checks": a.ats_checks,
        "recommendations": a.recommendations,
        "similarity_metrics": a.similarity_metrics,
    }

    temp_dir = tempfile.gettempdir()
    pdf_filename = f"ATSense_Report_v{a.resume.version}_{a.id}.pdf"
    output_path = os.path.join(temp_dir, pdf_filename)

    try:
        generate_pdf_report(report_data, output_path)

        return FileResponse(
            path=output_path,
            media_type="application/pdf",
            filename=pdf_filename,
            background=BackgroundTask(_delete_temp_file, output_path),
        )
    except Exception:
        _delete_temp_file(output_path)
        logger.error("PDF compilation failed.", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compile PDF report.",
        )


@app.get("/api/report/{id}/json")
def download_json_report(
    id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """
    Export structured analysis JSON for an owned analysis.
    """
    a = get_owned_analysis(id, user, db)

    export = {
        "atsense_version": app.version,
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
            "job_title": a.job_description.title if a.job_description else None,
        },
    }

    return JSONResponse(
        content=export,
        headers={
            "Content-Disposition": (
                f"attachment; filename=ATSense_Report_v{a.resume.version}.json"
            )
        },
    )


@app.delete("/api/resume/{id}")
def delete_resume_data(
    id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """
    Delete a resume and its associated analyses only when owned by the user.
    """
    resume = (
        db.query(models.Resume)
        .filter_by(id=id, user_id=user.id)
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found.",
        )

    try:
        db.delete(resume)
        db.commit()
        return {
            "status": "success",
            "message": "Resume and analysis data deleted.",
        }
    except Exception:
        logger.error("Deletion failed.", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Deletion failed.",
        )


@app.post("/api/reset-all")
def reset_database(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """
    Reset the current user's resumes, analyses, and job descriptions.

    This keeps the existing demo endpoint behavior for the current single-user
    application without deleting data belonging to other users.
    """
    try:
        resume_ids = [
            row[0]
            for row in (
                db.query(models.Resume.id)
                .filter(models.Resume.user_id == user.id)
                .all()
            )
        ]

        if resume_ids:
            db.query(models.Analysis).filter(
                models.Analysis.resume_id.in_(resume_ids)
            ).delete(synchronize_session=False)

            db.query(models.Resume).filter(
                models.Resume.id.in_(resume_ids)
            ).delete(synchronize_session=False)

        db.query(models.JobDescription).filter(
            models.JobDescription.user_id == user.id
        ).delete(synchronize_session=False)

        db.commit()

        return {
            "status": "success",
            "message": "All database histories reset successfully.",
        }
    except Exception:
        logger.error("Database reset failed.", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Reset failed.",
        )
