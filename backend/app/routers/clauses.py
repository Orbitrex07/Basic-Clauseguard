from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import User, Clause, Document
from app.core.security import get_current_user
from app.schemas.clause import ClauseOut

router = APIRouter(prefix="/clauses", tags=["Clauses"])


@router.get("/{clause_id}", response_model=ClauseOut)
def get_clause_by_id(
    clause_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    clause = db.query(Clause).filter(Clause.id == clause_id).first()
    if not clause:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clause not found")

    doc = db.query(Document).filter(Document.id == clause.document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated document not found")

    if current_user.role != "admin" and doc.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this clause")

    return ClauseOut.model_validate(clause)
