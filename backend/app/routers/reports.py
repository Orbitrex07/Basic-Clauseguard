import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_current_user
from app.db.session import get_db
from app.db.models import User, Document, Clause, Report
from app.services.report_generator import ReportGenerator
from app.services.audit import log_audit_event

router = APIRouter(tags=["Reports"])


@router.post("/documents/{document_id}/report")
def create_document_report(
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

    if doc.status != "done":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot generate report while document status is '{doc.status}'")

    clauses = db.query(Clause).filter(Clause.document_id == doc.id).order_by(Clause.clause_number.asc()).all()

    report_id = str(uuid.uuid4())
    safe_name = f"ClauseGuard_Report_{doc.id[:8]}.pdf"
    output_path = os.path.join(settings.REPORT_DIR, f"{report_id}_{safe_name}")

    # Generate PDF
    ReportGenerator.generate_pdf_report(doc=doc, clauses=clauses, output_path=output_path)
    file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0

    report_record = Report(
        id=report_id,
        document_id=doc.id,
        user_id=current_user.id,
        file_path=output_path,
        file_size=file_size
    )
    db.add(report_record)
    db.commit()
    db.refresh(report_record)

    log_audit_event(
        db=db,
        action="generate_report",
        user_id=current_user.id,
        entity_type="report",
        entity_id=report_id,
        details={"document_id": doc.id, "filename": doc.filename},
        ip_address=request.client.host if request.client else None
    )

    return {
        "report_id": report_record.id,
        "document_id": doc.id,
        "download_url": f"/api/reports/{report_record.id}/download",
        "file_size": file_size,
        "generated_at": report_record.generated_at
    }


@router.get("/reports/{report_id}/download")
def download_report(
    report_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    doc = db.query(Document).filter(Document.id == report.document_id).first()
    if current_user.role != "admin" and report.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this report")

    if not os.path.exists(report.file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report file not found on disk")

    log_audit_event(
        db=db,
        action="download",
        user_id=current_user.id,
        entity_type="report",
        entity_id=report.id,
        details={"document_id": report.document_id},
        ip_address=request.client.host if request.client else None
    )

    download_filename = f"ClauseGuard_Report_{doc.filename if doc else 'Contract'}.pdf"
    return FileResponse(
        path=report.file_path,
        media_type="application/pdf",
        filename=download_filename
    )
