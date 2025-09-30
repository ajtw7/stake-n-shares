from datetime import datetime
from sqlalchemy import Column, DateTime, JSON, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class ComparisonHistory(Base):
    __tablename__ = "comparison_history"

    # If using Postgres UUID:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    payload = Column(JSON, nullable=False)
    result = Column(JSON, nullable=False)
    params = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)