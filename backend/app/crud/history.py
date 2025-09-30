from sqlalchemy.orm import Session
from ..models.comparison_history import ComparisonHistory

def create_history(db: Session, payload: dict, result: dict, params: dict | None = None, notes: str | None = None):
    rec = ComparisonHistory(payload=payload, result=result, params=params, notes=notes)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

def list_history(db: Session, limit: int = 50, offset: int = 0):
    return db.query(ComparisonHistory).order_by(ComparisonHistory.created_at.desc()).limit(limit).offset(offset).all()