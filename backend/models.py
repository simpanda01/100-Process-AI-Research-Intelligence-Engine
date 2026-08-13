from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Process(Base):
    __tablename__ = "processes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    industry = Column(String(120), nullable=False, index=True)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    analysis = relationship(
        "ProcessAnalysis",
        back_populates="process",
        uselist=False,
        cascade="all, delete-orphan",
    )

    evidence = relationship(
        "Evidence",
        back_populates="process",
        cascade="all, delete-orphan",
    )


class ProcessAnalysis(Base):
    __tablename__ = "process_analyses"

    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(
        Integer,
        ForeignKey("processes.id"),
        unique=True,
        nullable=False,
    )

    business_purpose = Column(Text, default="")
    key_activities = Column(Text, default="")
    current_challenges = Column(Text, default="")
    ai_opportunity = Column(Text, default="")
    automation_potential = Column(String(20), default="Medium")
    human_involvement = Column(Text, default="")
    technologies = Column(Text, default="")
    business_benefit = Column(Text, default="")
    risks = Column(Text, default="")

    ai_score = Column(Float, default=0)
    automation_score = Column(Float, default=0)
    benefit_score = Column(Float, default=0)
    human_criticality_score = Column(Float, default=0)

    reasoning = Column(Text, default="")
    analyzed_at = Column(DateTime, default=datetime.utcnow)

    process = relationship(
        "Process",
        back_populates="analysis",
    )


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(
        Integer,
        ForeignKey("processes.id"),
        nullable=False,
    )

    title = Column(String(500), default="")
    source = Column(String(500), default="")
    url = Column(String(1000), default="")
    snippet = Column(Text, default="")
    source_type = Column(String(80), default="General Web Content")
    created_at = Column(DateTime, default=datetime.utcnow)

    process = relationship(
        "Process",
        back_populates="evidence",
    )