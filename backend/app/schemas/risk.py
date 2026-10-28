from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime


class RiskRuleBase(BaseModel):
    rule_code: str
    category: str
    severity: str  # Low, Medium, High
    points: int
    pattern_type: str
    pattern_value: str
    reason: str
    suggestion: Optional[str] = None
    is_enabled: bool = True


class RiskRuleOut(RiskRuleBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RiskRuleUpdate(BaseModel):
    severity: Optional[str] = None
    points: Optional[int] = None
    pattern_type: Optional[str] = None
    pattern_value: Optional[str] = None
    reason: Optional[str] = None
    suggestion: Optional[str] = None
    is_enabled: Optional[bool] = None


class RiskFlagOut(BaseModel):
    id: str
    clause_id: str
    risk_level: str  # Low, Medium, High
    risk_score: int  # 0 to 100
    triggered_rules: List[Dict[str, Any]] = []
    extracted_data: Dict[str, Any] = {}
    explanation: str
    suggestion: Optional[str] = None
    needs_review: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
