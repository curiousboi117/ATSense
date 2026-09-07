from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ResumeBase(BaseModel):
    filename: str
    file_size: int
    version: int

class ResumeResponse(ResumeBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class JobDescriptionCreate(BaseModel):
    text: str
    title: Optional[str] = "Target Role"

class JobDescriptionResponse(BaseModel):
    id: int
    title: str
    text: str
    created_at: datetime

    class Config:
        from_attributes = True

class AnalysisResponse(BaseModel):
    id: int
    resume_id: int
    resume_filename: str
    resume_version: int
    job_description_id: Optional[int] = None
    job_title: Optional[str] = None
    ats_score: float
    score_breakdown: Dict[str, float]
    personal_info: Dict[str, Any]
    skills: Dict[str, List[str]]
    ats_checks: List[Dict[str, Any]]
    recommendations: List[str]
    similarity_metrics: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class HistoryResponseItem(BaseModel):
    id: int
    resume_id: int
    filename: str
    version: int
    ats_score: float
    job_title: Optional[str] = None
    created_at: datetime

class CompareItem(BaseModel):
    version: int
    ats_score: float
    job_title: Optional[str] = None
    skills_count: int
    issues_count: int
    created_at: datetime

class CompareResponse(BaseModel):
    history: List[CompareItem]
    improvement: float
    issues_resolved: int
    issues_remaining: int

class HealthResponse(BaseModel):
    status: str
    nlp_loaded: bool
    model_loaded: bool
    model_name: str
