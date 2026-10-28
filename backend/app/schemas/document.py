from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


class DocumentStatus(BaseModel):
    id: str
    status: str
    progress: int
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentSummary(BaseModel):
    total_clauses: int = 0
    high_risk_count: int = 0
    medium_risk_count: int = 0
    low_risk_count: int = 0
    needs_review_count: int = 0
    category_distribution: Dict[str, int] = {}


class DocumentOut(BaseModel):
    id: str
    user_id: str
    filename: str
    file_size: int
    page_count: int
    mime_type: str
    status: str
    progress: int
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    summary: Optional[DocumentSummary] = None

    model_config = ConfigDict(from_attributes=True)
