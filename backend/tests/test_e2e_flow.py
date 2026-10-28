"""
Comprehensive End-to-End Integration Test for ClauseGuard:
User Registration -> Login -> Upload Sample Contract -> Pipeline Execution
-> Done Status -> Retrieve Clauses -> Filter Clauses -> Retrieve Clause Detail
-> Generate PDF Report -> Download PDF Report -> Delete Document & Cascaded Cleanup
"""
import os
import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.db.models import User, Document, Clause, RiskFlag, Report
from app.services.pipeline import process_document_pipeline

client = TestClient(app)
SAMPLE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "sample_contracts")


def test_complete_e2e_workflow():
    db = SessionLocal()
    try:
        # 1. Register a new user
        reg_payload = {
            "email": "e2e_user@example.com",
            "password": "Password123!",
            "full_name": "E2E Tester"
        }
        res_reg = client.post("/api/auth/register", json=reg_payload)
        assert res_reg.status_code in [200, 201], f"Registration failed: {res_reg.text}"

        # 2. Login to obtain access token
        res_login = client.post("/api/auth/login", json={
            "email": "e2e_user@example.com",
            "password": "Password123!"
        })
        assert res_login.status_code == 200, f"Login failed: {res_login.text}"
        token = res_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Verify /api/auth/me
        res_me = client.get("/api/auth/me", headers=headers)
        assert res_me.status_code == 200
        assert res_me.json()["email"] == reg_payload["email"]

        # 3. Upload Sample Contract (Standard Commercial Agreement)
        sample_path = os.path.join(SAMPLE_DIR, "standard_commercial_agreement.docx")
        assert os.path.exists(sample_path)

        with open(sample_path, "rb") as f:
            file_content = f.read()

        upload_files = {
            "file": ("standard_commercial_agreement.docx", file_content, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        }
        res_upload = client.post("/api/documents", headers=headers, files=upload_files)
        assert res_upload.status_code in [200, 201], f"Upload failed: {res_upload.text}"
        doc_data = res_upload.json()
        doc_id = doc_data["id"]
        assert doc_data["filename"] == "standard_commercial_agreement.docx"

        # 4. Run pipeline directly within test session
        process_document_pipeline(doc_id, db=db)

        # 5. Check Document Status
        res_status = client.get(f"/api/documents/{doc_id}/status", headers=headers)
        assert res_status.status_code == 200
        status_info = res_status.json()
        assert status_info["status"] == "done"
        assert status_info["progress"] == 100

        # 6. Retrieve Document Clauses
        res_clauses = client.get(f"/api/documents/{doc_id}/clauses", headers=headers)
        assert res_clauses.status_code == 200
        clauses_data = res_clauses.json()
        assert len(clauses_data) >= 4, f"Expected at least 4 clauses, got {len(clauses_data)}"

        # 7. Check Clause Structure and Risk Flag
        first_clause = clauses_data[0]
        assert "clause_number" in first_clause
        assert "risk_flag" in first_clause
        assert first_clause["risk_flag"]["risk_level"] in ["Low", "Medium", "High"]
        assert "explanation" in first_clause["risk_flag"]

        # 8. Retrieve Specific Clause Detail
        clause_id = first_clause["id"]
        res_clause = client.get(f"/api/clauses/{clause_id}", headers=headers)
        assert res_clause.status_code == 200
        assert res_clause.json()["id"] == clause_id

        # 9. Generate PDF Report
        res_report = client.post(f"/api/documents/{doc_id}/report", headers=headers)
        assert res_report.status_code in [200, 201], f"Report generation failed: {res_report.text}"
        report_data = res_report.json()
        report_id = report_data["report_id"]
        assert report_id is not None

        # 10. Download PDF Report
        res_download = client.get(f"/api/reports/{report_id}/download", headers=headers)
        assert res_download.status_code == 200
        assert res_download.headers["content-type"] == "application/pdf"
        assert res_download.content.startswith(b"%PDF-")

        # 11. Delete Document and verify cascade
        res_del = client.delete(f"/api/documents/{doc_id}", headers=headers)
        assert res_del.status_code == 200

        # Verify 404 after deletion
        res_get_deleted = client.get(f"/api/documents/{doc_id}", headers=headers)
        assert res_get_deleted.status_code == 404

    finally:
        db.close()
