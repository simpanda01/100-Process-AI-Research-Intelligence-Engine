from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Process, ProcessAnalysis, Evidence
from schemas import ProcessCreate, ProcessOut, AnalysisOut, DashboardStats
from seed_data import PROCESSES
from research_service import research_process
from ai_service import analyze_with_ai

load_dotenv()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Enterprise AI Process Intelligence Engine", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173","http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def seed_database(db):
    if db.query(Process).count() > 0:
        return
    db.add_all([Process(industry=i, name=n, description=d) for i,n,d in PROCESSES])
    db.commit()

@app.on_event("startup")
def startup():
    db = next(get_db())
    try: seed_database(db)
    finally: db.close()

@app.get("/api/health")
def health():
    return {"status":"ok"}

@app.get("/api/stats", response_model=DashboardStats)
def stats(db: Session = Depends(get_db)):
    processes = db.query(Process).all()
    analyzed = [p for p in processes if p.analysis]
    scores = [p.analysis.ai_score for p in analyzed]
    return DashboardStats(
        total_processes=len(processes),
        analyzed_processes=len(analyzed),
        high_ai_potential=sum(1 for p in analyzed if p.analysis.automation_potential=="High"),
        medium_ai_potential=sum(1 for p in analyzed if p.analysis.automation_potential=="Medium"),
        low_ai_potential=sum(1 for p in analyzed if p.analysis.automation_potential=="Low"),
        average_ai_score=round(sum(scores)/len(scores),2) if scores else 0
    )

@app.get("/api/processes", response_model=list[ProcessOut])
def list_processes(db: Session=Depends(get_db), search: str=Query("",max_length=200), industry: str=Query("",max_length=100)):
    q = db.query(Process)
    if search: q = q.filter(Process.name.ilike(f"%{search}%"))
    if industry: q = q.filter(Process.industry==industry)
    return q.order_by(Process.id).all()

@app.get("/api/processes/{process_id}", response_model=ProcessOut)
def get_process(process_id:int, db:Session=Depends(get_db)):
    p=db.query(Process).filter(Process.id==process_id).first()
    if not p: raise HTTPException(404,"Process not found")
    return p

@app.get("/api/processes/{process_id}/evidence")
def get_evidence(process_id:int, db:Session=Depends(get_db)):
    p=db.query(Process).filter(Process.id==process_id).first()
    if not p: raise HTTPException(404,"Process not found")
    return p.evidence

async def analyze_record(process_id, db):
    p=db.query(Process).filter(Process.id==process_id).first()
    if not p: raise HTTPException(404,"Process not found")

    evidence=await research_process(p.name,p.industry,p.description)
    db.query(Evidence).filter(Evidence.process_id==p.id).delete()
    for e in evidence:
        db.add(Evidence(process_id=p.id,title=e["title"],source=e["source"],url=e["url"],snippet=e["snippet"],source_type=e["source_type"]))
    db.commit()

    result=await analyze_with_ai(p.name,p.industry,p.description,evidence)
    analysis=db.query(ProcessAnalysis).filter(ProcessAnalysis.process_id==p.id).first()
    if not analysis:
        analysis=ProcessAnalysis(process_id=p.id)
        db.add(analysis)
    for k, v in result.items():
        if hasattr(analysis, k):
            if isinstance(v, list):
                v = ", ".join(str(item) for item in v)
        elif v is None:
            v = ""
        setattr(analysis, k, v)
    analysis.analyzed_at=datetime.utcnow()
    db.commit(); db.refresh(analysis)
    return analysis

@app.post("/api/processes", response_model=ProcessOut)
def create_process(payload:ProcessCreate, db:Session=Depends(get_db)):
    if not payload.name.strip() or not payload.description.strip():
        raise HTTPException(400,"Name and description are required")
    p=Process(name=payload.name.strip(),industry=payload.industry.strip(),description=payload.description.strip())
    db.add(p); db.commit(); db.refresh(p)
    return p

@app.post("/api/processes/{process_id}/analyze", response_model=AnalysisOut)
async def analyze_process(process_id:int, db:Session=Depends(get_db)):
    return await analyze_record(process_id,db)

@app.post("/api/analyze-all")
async def analyze_all(db:Session=Depends(get_db)):
    processes=db.query(Process).order_by(Process.id).all()
    for p in processes:
        await analyze_record(p.id,db)
    return {"message":"All processes analyzed","completed":len(processes)}

@app.get("/api/rankings/top")
def top_processes(db:Session=Depends(get_db), limit:int=Query(10,ge=1,le=50)):
    rows=db.query(Process).join(ProcessAnalysis).order_by(ProcessAnalysis.ai_score.desc()).limit(limit).all()
    return [{"id":p.id,"name":p.name,"industry":p.industry,"ai_score":p.analysis.ai_score,"automation_potential":p.analysis.automation_potential,"ai_opportunity":p.analysis.ai_opportunity} for p in rows]

@app.get("/api/rankings/human-led")
def human_led(db:Session=Depends(get_db), limit:int=Query(10,ge=1,le=50)):
    rows=db.query(Process).join(ProcessAnalysis).order_by(ProcessAnalysis.human_criticality_score.desc()).limit(limit).all()
    return [{"id":p.id,"name":p.name,"industry":p.industry,"human_criticality_score":p.analysis.human_criticality_score,"automation_potential":p.analysis.automation_potential,"human_involvement":p.analysis.human_involvement} for p in rows]
