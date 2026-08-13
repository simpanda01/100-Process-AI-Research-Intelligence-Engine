from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class ProcessCreate(BaseModel):
    name: str
    industry: str
    description: str

class EvidenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    source: str
    url: str
    snippet: str
    source_type: str

class AnalysisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    process_id: int
    business_purpose: str
    key_activities: str
    current_challenges: str
    ai_opportunity: str
    automation_potential: str
    human_involvement: str
    technologies: str
    business_benefit: str
    risks: str
    ai_score: float
    automation_score: float
    benefit_score: float
    human_criticality_score: float
    reasoning: str
    analyzed_at: datetime

class ProcessOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    industry: str
    description: str
    created_at: datetime
    analysis: Optional[AnalysisOut] = None

class DashboardStats(BaseModel):
    total_processes: int
    analyzed_processes: int
    high_ai_potential: int
    medium_ai_potential: int
    low_ai_potential: int
    average_ai_score: float
