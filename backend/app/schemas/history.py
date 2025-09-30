from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime
from uuid import UUID

class HistoryOut(BaseModel):
    id: UUID
    created_at: datetime
    payload: Any
    result: Any
    params: Optional[Any]
    notes: Optional[str]

    class Config:
        orm_mode = True