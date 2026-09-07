from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, default="ats_user")
    email = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    job_descriptions = relationship("JobDescription", back_populates="user", cascade="all, delete-orphan")

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    version = Column(Integer, default=1)
    extracted_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="resumes")
    analyses = relationship("Analysis", back_populates="resume", cascade="all, delete-orphan")

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=True, default="Target Role")
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="job_descriptions")
    analyses = relationship("Analysis", back_populates="job_description", cascade="all, delete-orphan")

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    job_description_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=True)
    ats_score = Column(Float, nullable=False)
    
    # Store structured results as JSON
    score_breakdown = Column(JSON, nullable=False)  # dict of weights/scores
    personal_info = Column(JSON, nullable=False)    # dict of name, email, phone, etc.
    skills = Column(JSON, nullable=False)           # dict of detected skills by category
    ats_checks = Column(JSON, nullable=False)       # list of dictionaries (checks/violations)
    recommendations = Column(JSON, nullable=False)  # list of strings
    similarity_metrics = Column(JSON, nullable=True) # JD matching details (keyword, tfidf, semantic)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    resume = relationship("Resume", back_populates="analyses")
    job_description = relationship("JobDescription", back_populates="analyses")
