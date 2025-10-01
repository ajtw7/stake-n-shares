import uuid
from sqlalchemy import Column, DateTime, JSON, Text, func
from sqlalchemy.dialects.postgresql import UUID
from backend.app.db.base import Base

class ComparisonHistory(Base):
    __tablename__ = "comparison_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    payload = Column(JSON, nullable=False)
    result = Column(JSON, nullable=False)
    params = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)