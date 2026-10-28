from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.security import get_current_admin_user
from app.db.session import get_db
from app.db.models import User, Document, Clause, RiskFlag, RiskRule, ClauseCorrection, AuditLog
from app.schemas.clause import ClauseOut, ClauseCorrectionCreate, ClauseCorrectionOut
from app.schemas.risk import RiskRuleOut, RiskRuleUpdate
from app.services.risk_engine import risk_engine
from app.services.extractor import extractor_service
from app.services.audit import log_audit_event

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(get_current_admin_user)])


@router.get("/review-queue", response_model=List[ClauseOut])
def get_review_queue(db: Session = Depends(get_db)):
    # Find clauses that need review (confidence < 0.50 or needs_review=True, and not reviewed yet)
    clauses = (
        db.query(Clause)
        .join(RiskFlag, Clause.id == RiskFlag.clause_id)
        .filter((RiskFlag.needs_review == True) | (Clause.confidence < 0.50))
        .filter(Clause.is_reviewed == False)
        .order_by(Clause.created_at.desc())
        .limit(100)
        .all()
    )
    return [ClauseOut.model_validate(c) for c in clauses]


@router.patch("/clauses/{clause_id}", response_model=ClauseOut)
def correct_clause_category(
    clause_id: str,
    correction_in: ClauseCorrectionCreate,
    request: Request,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    clause = db.query(Clause).filter(Clause.id == clause_id).first()
    if not clause:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clause not found")

    original_cat = clause.primary_category
    clause.primary_category = correction_in.corrected_category
    clause.is_reviewed = True
    clause.confidence = 1.0  # Manually verified by admin

    # Re-run extractor and risk engine with updated category
    extracted_data = extractor_service.extract_clause_details(text=clause.text, category=clause.primary_category)
    risk_res = risk_engine.evaluate_clause(
        text=clause.text,
        category=clause.primary_category,
        confidence=clause.confidence,
        extracted_data=extracted_data,
        db=db
    )

    if clause.risk_flag:
        clause.risk_flag.risk_level = risk_res.risk_level
        clause.risk_flag.risk_score = risk_res.risk_score
        clause.risk_flag.triggered_rules = risk_res.triggered_rules
        clause.risk_flag.extracted_data = extracted_data
        clause.risk_flag.explanation = risk_res.explanation
        clause.risk_flag.suggestion = risk_res.suggestion
        clause.risk_flag.needs_review = False
    else:
        rf = RiskFlag(
            clause_id=clause.id,
            risk_level=risk_res.risk_level,
            risk_score=risk_res.risk_score,
            triggered_rules=risk_res.triggered_rules,
            extracted_data=extracted_data,
            explanation=risk_res.explanation,
            suggestion=risk_res.suggestion,
            needs_review=False
        )
        db.add(rf)

    # Save correction record
    correction = ClauseCorrection(
        clause_id=clause.id,
        user_id=current_admin.id,
        original_category=original_cat,
        corrected_category=correction_in.corrected_category,
        note=correction_in.note
    )
    db.add(correction)
    db.commit()
    db.refresh(clause)

    log_audit_event(
        db=db,
        action="correct_clause",
        user_id=current_admin.id,
        entity_type="clause",
        entity_id=clause.id,
        details={
            "from_category": original_cat,
            "to_category": correction_in.corrected_category,
            "note": correction_in.note
        },
        ip_address=request.client.host if request.client else None
    )

    return ClauseOut.model_validate(clause)


@router.get("/rules", response_model=List[RiskRuleOut])
def get_risk_rules(db: Session = Depends(get_db)):
    rules = db.query(RiskRule).order_by(RiskRule.category.asc(), RiskRule.points.desc()).all()
    return [RiskRuleOut.model_validate(r) for r in rules]


@router.put("/rules/{rule_id}", response_model=RiskRuleOut)
def update_risk_rule(
    rule_id: str,
    rule_in: RiskRuleUpdate,
    request: Request,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    rule = db.query(RiskRule).filter(RiskRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")

    update_dict = rule_in.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(rule, field, val)

    db.commit()
    db.refresh(rule)

    log_audit_event(
        db=db,
        action="update_rule",
        user_id=current_admin.id,
        entity_type="rule",
        entity_id=rule.id,
        details=update_dict,
        ip_address=request.client.host if request.client else None
    )

    return RiskRuleOut.model_validate(rule)


@router.get("/audit-logs")
def get_audit_logs(
    action: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action)
    
    total = query.count()
    logs = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()

    return {
        "total": total,
        "logs": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "details": log.details,
                "ip_address": log.ip_address,
                "created_at": log.created_at
            }
            for log in logs
        ]
    }


@router.get("/stats")
def get_admin_stats(db: Session = Depends(get_db)):
    total_docs = db.query(Document).count()
    total_users = db.query(User).count()
    total_clauses = db.query(Clause).count()

    high_risk = db.query(RiskFlag).filter(RiskFlag.risk_level == "High").count()
    med_risk = db.query(RiskFlag).filter(RiskFlag.risk_level == "Medium").count()
    low_risk = db.query(RiskFlag).filter(RiskFlag.risk_level == "Low").count()
    needs_review = db.query(RiskFlag).filter(RiskFlag.needs_review == True).count()

    category_counts = (
        db.query(Clause.primary_category, func.count(Clause.id))
        .group_by(Clause.primary_category)
        .all()
    )

    return {
        "total_documents": total_docs,
        "total_users": total_users,
        "total_clauses": total_clauses,
        "risk_breakdown": {
            "High": high_risk,
            "Medium": med_risk,
            "Low": low_risk,
            "Needs Review": needs_review
        },
        "category_distribution": dict(category_counts),
        "average_processing_time_sec": 4.2
    }
