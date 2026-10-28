import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks, Request
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.config import settings
from app.core.security import get_current_user
from app.db.session import get_db
from app.db.models import User, Document, Clause, RiskFlag, Report
from app.schemas.document import DocumentOut, DocumentStatus, DocumentSummary
from app.schemas.clause import ClauseOut
from app.services.pipeline import process_document_pipeline
from app.services.audit import log_audit_event
from app.core.logging import logger

router = APIRouter(prefix="/documents", tags=["Documents"])

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/octet-stream"  # Some browsers send octet-stream for docx
}


def validate_file_magic_bytes(header: bytes, filename: str) -> bool:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return header.startswith(b"%PDF-")
    elif lower.endswith(".docx"):
        return header.startswith(b"PK\x03\x04")
    return False


def get_document_summary(db: Session, doc_id: str) -> DocumentSummary:
    clauses = db.query(Clause).filter(Clause.document_id == doc_id).all()
    total = len(clauses)
    high = 0
    med = 0
    low = 0
    needs_rev = 0
    cat_dist: dict = {}

    for c in clauses:
        cat_dist[c.primary_category] = cat_dist.get(c.primary_category, 0) + 1
        if c.risk_flag:
            if c.risk_flag.risk_level == "High":
                high += 1
            elif c.risk_flag.risk_level == "Medium":
                med += 1
            else:
                low += 1
            if c.risk_flag.needs_review:
                needs_rev += 1

    return DocumentSummary(
        total_clauses=total,
        high_risk_count=high,
        medium_risk_count=med,
        low_risk_count=low,
        needs_review_count=needs_rev,
        category_distribution=cat_dist
    )


@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    filename = file.filename or "uploaded_contract"
    _, ext = os.path.splitext(filename)
    ext = ext.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Only .pdf and .docx files are permitted."
        )

    # Read initial bytes to check size and magic bytes
    initial_bytes = await file.read(2048)
    if not initial_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    if not validate_file_magic_bytes(initial_bytes, filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File content does not match expected PDF/DOCX magic bytes. File may be corrupted or disguised."
        )

    # Read remaining file content and check size limit (20 MB)
    remaining_bytes = await file.read()
    full_content = initial_bytes + remaining_bytes
    file_size = len(full_content)

    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    if file_size > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_MB} MB."
        )

    # Generate safe random filename
    unique_prefix = str(uuid.uuid4())
    safe_stored_filename = f"{unique_prefix}_{filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_stored_filename)

    with open(file_path, "wb") as f:
        f.write(full_content)

    # Create document record
    doc = Document(
        user_id=current_user.id,
        filename=filename,
        file_path=file_path,
        file_size=file_size,
        page_count=1,
        mime_type=file.content_type or "application/octet-stream",
        status="queued",
        progress=0
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    log_audit_event(
        db=db,
        action="upload",
        user_id=current_user.id,
        entity_type="document",
        entity_id=doc.id,
        details={"filename": filename, "size": file_size},
        ip_address=request.client.host if request.client else None
    )

    # Enqueue background pipeline processing
    background_tasks.add_task(process_document_pipeline, doc.id)

    doc_out = DocumentOut.model_validate(doc)
    doc_out.summary = DocumentSummary()
    return doc_out


@router.get("", response_model=List[DocumentOut])
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Document)
    if current_user.role != "admin":
        query = query.filter(Document.user_id == current_user.id)
    
    docs = query.order_by(Document.created_at.desc()).all()
    results = []
    for d in docs:
        d_out = DocumentOut.model_validate(d)
        d_out.summary = get_document_summary(db, d.id)
        results.append(d_out)
    return results


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    if current_user.role != "admin" and doc.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this document")

    d_out = DocumentOut.model_validate(doc)
    d_out.summary = get_document_summary(db, doc.id)
    return d_out


@router.get("/{document_id}/status", response_model=DocumentStatus)
def get_document_status(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    if current_user.role != "admin" and doc.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this document")

    return DocumentStatus.model_validate(doc)


@router.get("/{document_id}/text")
def get_document_text(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    if current_user.role != "admin" and doc.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this document")

    clauses = db.query(Clause).filter(Clause.document_id == doc.id).order_by(Clause.clause_number.asc()).all()
    full_text = "\n\n".join([f"[{c.clause_number}] {c.heading or ''}\n{c.text}" for c in clauses])
    return {
        "document_id": doc.id,
        "filename": doc.filename,
        "text": full_text
    }


@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    if current_user.role != "admin" and doc.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this document")

    # Delete physical uploaded file
    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception as e:
            logger.warning(f"Could not remove file {doc.file_path}: {e}")

    # Delete any generated reports from disk
    reports = db.query(Report).filter(Report.document_id == doc.id).all()
    for r in reports:
        if os.path.exists(r.file_path):
            try:
                os.remove(r.file_path)
            except Exception as e:
                logger.warning(f"Could not remove report file {r.file_path}: {e}")

    db.delete(doc)
    db.commit()

    log_audit_event(
        db=db,
        action="delete_document",
        user_id=current_user.id,
        entity_type="document",
        entity_id=document_id,
        details={"filename": doc.filename},
        ip_address=request.client.host if request.client else None
    )

    return {"message": "Document deleted successfully", "document_id": document_id}


@router.get("/{document_id}/clauses", response_model=List[ClauseOut])
def get_document_clauses(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    if current_user.role != "admin" and doc.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this document")

    clauses = db.query(Clause).filter(Clause.document_id == doc.id).order_by(Clause.clause_number.asc()).all()
    return [ClauseOut.model_validate(c) for c in clauses]
