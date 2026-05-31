from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from database import Base, engine, get_db
from models import AISolution, PainPoint
from schemas import (
    AISolutionCreate,
    AISolutionResponse,
    AISolutionUpdate,
    PainPointCreate,
    PainPointDetailResponse,
    PainPointResponse,
    PainPointUpdate,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Accounting AI Playbook API",
    description="A library of accounting pain points and the AI solutions that address them.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _to_pain_response(pp: PainPoint) -> PainPointResponse:
    return PainPointResponse(
        id=pp.id,
        title=pp.title,
        description=pp.description,
        category=pp.category,
        firm_size_fit=pp.firm_size_fit,
        severity=pp.severity,
        created_at=pp.created_at,
        solution_count=len(pp.solutions),
    )


# ---------- Meta ----------


@app.get("/")
def root():
    return {
        "message": "Accounting AI Playbook API",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/stats")
def stats(db: Session = Depends(get_db)):
    pain_total = db.query(PainPoint).count()
    solution_total = db.query(AISolution).count()

    by_category = dict(
        db.query(PainPoint.category, func.count(PainPoint.id))
        .group_by(PainPoint.category)
        .all()
    )
    by_severity = dict(
        db.query(PainPoint.severity, func.count(PainPoint.id))
        .group_by(PainPoint.severity)
        .all()
    )
    by_maturity = dict(
        db.query(AISolution.maturity, func.count(AISolution.id))
        .group_by(AISolution.maturity)
        .all()
    )

    return {
        "pain_point_total": pain_total,
        "solution_total": solution_total,
        "pain_points_by_category": by_category,
        "pain_points_by_severity": by_severity,
        "solutions_by_maturity": by_maturity,
    }


@app.get("/categories")
def categories(db: Session = Depends(get_db)):
    rows = (
        db.query(PainPoint.category)
        .distinct()
        .order_by(PainPoint.category)
        .all()
    )
    return [r[0] for r in rows]


# ---------- Pain Points ----------


@app.get("/pain-points", response_model=list[PainPointResponse])
def list_pain_points(
    category: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(PainPoint).options(joinedload(PainPoint.solutions))
    if category:
        query = query.filter(PainPoint.category == category)
    if severity:
        query = query.filter(PainPoint.severity == severity)
    pain_points = query.order_by(PainPoint.id).all()
    return [_to_pain_response(pp) for pp in pain_points]


@app.post("/pain-points", response_model=PainPointResponse, status_code=201)
def create_pain_point(data: PainPointCreate, db: Session = Depends(get_db)):
    pp = PainPoint(**data.model_dump())
    db.add(pp)
    db.commit()
    db.refresh(pp)
    return _to_pain_response(pp)


@app.get("/pain-points/{pain_id}", response_model=PainPointDetailResponse)
def get_pain_point(pain_id: int, db: Session = Depends(get_db)):
    pp = (
        db.query(PainPoint)
        .options(joinedload(PainPoint.solutions))
        .filter(PainPoint.id == pain_id)
        .first()
    )
    if pp is None:
        raise HTTPException(status_code=404, detail="Pain point not found")

    return PainPointDetailResponse(
        id=pp.id,
        title=pp.title,
        description=pp.description,
        category=pp.category,
        firm_size_fit=pp.firm_size_fit,
        severity=pp.severity,
        created_at=pp.created_at,
        solution_count=len(pp.solutions),
        solutions=[AISolutionResponse.model_validate(s) for s in pp.solutions],
    )


@app.put("/pain-points/{pain_id}", response_model=PainPointResponse)
def update_pain_point(
    pain_id: int,
    updates: PainPointUpdate,
    db: Session = Depends(get_db),
):
    pp = db.query(PainPoint).filter(PainPoint.id == pain_id).first()
    if pp is None:
        raise HTTPException(status_code=404, detail="Pain point not found")

    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(pp, field, value)

    db.commit()
    db.refresh(pp)
    return _to_pain_response(pp)


@app.delete("/pain-points/{pain_id}")
def delete_pain_point(pain_id: int, db: Session = Depends(get_db)):
    pp = db.query(PainPoint).filter(PainPoint.id == pain_id).first()
    if pp is None:
        raise HTTPException(status_code=404, detail="Pain point not found")

    title = pp.title
    db.delete(pp)
    db.commit()
    return {"message": f"Deleted '{title}'", "id": pain_id}


# ---------- AI Solutions ----------


@app.post(
    "/pain-points/{pain_id}/solutions",
    response_model=AISolutionResponse,
    status_code=201,
)
def create_solution(
    pain_id: int,
    data: AISolutionCreate,
    db: Session = Depends(get_db),
):
    pp = db.query(PainPoint).filter(PainPoint.id == pain_id).first()
    if pp is None:
        raise HTTPException(status_code=404, detail="Pain point not found")

    solution = AISolution(pain_point_id=pain_id, **data.model_dump())
    db.add(solution)
    db.commit()
    db.refresh(solution)
    return solution


@app.put("/solutions/{solution_id}", response_model=AISolutionResponse)
def update_solution(
    solution_id: int,
    updates: AISolutionUpdate,
    db: Session = Depends(get_db),
):
    solution = db.query(AISolution).filter(AISolution.id == solution_id).first()
    if solution is None:
        raise HTTPException(status_code=404, detail="Solution not found")

    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(solution, field, value)

    db.commit()
    db.refresh(solution)
    return solution


@app.delete("/solutions/{solution_id}")
def delete_solution(solution_id: int, db: Session = Depends(get_db)):
    solution = db.query(AISolution).filter(AISolution.id == solution_id).first()
    if solution is None:
        raise HTTPException(status_code=404, detail="Solution not found")

    title = solution.title
    db.delete(solution)
    db.commit()
    return {"message": f"Deleted '{title}'", "id": solution_id}
