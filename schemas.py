from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# Categories used for both filtering and validation hints in the UI.
PAIN_CATEGORIES = {
    "AP/AR",
    "Audit",
    "Close cycle",
    "Tax",
    "Client management",
    "Reporting",
    "Advisory",
}

FIRM_SIZES = {"small", "mid", "enterprise", "all"}
SEVERITIES = {"low", "medium", "high"}
MATURITIES = {"concept", "prototype", "proven"}
PRICING_MODELS = {"fixed", "monthly", "per-seat", "usage", "custom"}


# ---------- AI Solution ----------


class AISolutionBase(BaseModel):
    title: str
    description: str
    tech_stack: str = ""
    maturity: str = "concept"
    setup_days: Optional[int] = None
    pricing_model: str = "fixed"
    estimated_price_usd: Optional[int] = None


class AISolutionCreate(AISolutionBase):
    pass


class AISolutionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tech_stack: Optional[str] = None
    maturity: Optional[str] = None
    setup_days: Optional[int] = None
    pricing_model: Optional[str] = None
    estimated_price_usd: Optional[int] = None


class AISolutionResponse(AISolutionBase):
    id: int
    pain_point_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------- Pain Point ----------


class PainPointBase(BaseModel):
    title: str
    description: str
    category: str
    firm_size_fit: str = "all"
    severity: str = "medium"


class PainPointCreate(PainPointBase):
    pass


class PainPointUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    firm_size_fit: Optional[str] = None
    severity: Optional[str] = None


class PainPointResponse(PainPointBase):
    id: int
    created_at: datetime
    solution_count: int = 0

    model_config = {"from_attributes": True}


class PainPointDetailResponse(PainPointResponse):
    solutions: list[AISolutionResponse] = []
