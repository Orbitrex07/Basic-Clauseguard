from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.schemas.risk import RiskFlagOut


class ClauseOut(BaseModel):
    id: str
    document_id: str
    clause_number: int
    heading: Optional[str] = None
    text: str
    page_number: int
    start_pos: int
    end_pos: int
    primary_category: str
    secondary_categories: List[str] = []
    top_3_labels: List[Dict[str, Any]] = []
    confidence: float
    is_reviewed: bool
    created_at: datetime
    risk_flag: Optional[RiskFlagOut] = None

    model_config = ConfigDict(from_attributes=True)


class ClauseCorrectionCreate(BaseModel):
    corrected_category: str
    note: Optional[str] = None


class ClauseCorrectionOut(BaseModel):
    id: str
    clause_id: str
    user_id: str
    original_category: str
    corrected_category: str
    note: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
