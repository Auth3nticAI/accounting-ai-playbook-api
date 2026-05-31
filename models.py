from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database import Base


class PainPoint(Base):
    __tablename__ = "pain_points"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    firm_size_fit = Column(String, nullable=False, default="all")
    severity = Column(String, nullable=False, default="medium")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    solutions = relationship(
        "AISolution",
        back_populates="pain_point",
        cascade="all, delete-orphan",
        order_by="AISolution.id",
    )


class AISolution(Base):
    __tablename__ = "ai_solutions"

    id = Column(Integer, primary_key=True, index=True)
    pain_point_id = Column(
        Integer,
        ForeignKey("pain_points.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    tech_stack = Column(String, nullable=False, default="")
    maturity = Column(String, nullable=False, default="concept")
    setup_days = Column(Integer, nullable=True)
    pricing_model = Column(String, nullable=False, default="fixed")
    estimated_price_usd = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    pain_point = relationship("PainPoint", back_populates="solutions")
