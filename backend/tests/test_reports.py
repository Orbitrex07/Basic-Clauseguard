import io
import pytest
import fitz
from app.db.models import User, Document, Clause, RiskFlag
from app.core.security import create_access_token, get_password_hash


@pytest.fixture
def auth_user(db):
    user = User(
        email="report_user@example.com",
        hashed_password=get_password_hash("Password123!"),
        full_name="Report User",
        role="user",
        is_active=True
    )
    db.add(user)
    db.commit()
    token = create_access_token(subject=user.id, role="user")
    return user, token


def test_generate_and_download_report(client, db, auth_user):
    user, token = auth_user
    headers = {"Authorization": f"Bearer {token}"}

    # Create completed document with a clause and risk flag
    doc = Document(
        user_id=user.id,
        filename="Reportable_Agreement.pdf",
        file_path="/tmp/fake.pdf",
        file_size=1000,
        page_count=1,
        mime_type="application/pdf",
        status="done",
        progress=100
    )
    db.add(doc)
    db.commit()

    clause = Clause(
        document_id=doc.id,
        clause_number=1,
        heading="Termination Clause",
        text="Either party may terminate upon 30 days prior written notice.",
        page_number=1,
        primary_category="Termination",
        confidence=0.92,
        is_reviewed=False
    )
    db.add(clause)
    db.commit()

    rf = RiskFlag(
        clause_id=clause.id,
        risk_level="Low",
        risk_score=10,
        triggered_rules=[{"rule_code": "TERM_FAIR", "reason": "Mutual termination with standard notice."}],
        extracted_data={"notice_days": 30},
        explanation="Standard mutual termination provision.",
        suggestion="Terms are balanced.",
        needs_review=False
    )
    db.add(rf)
    db.commit()

    # Generate Report
    gen_resp = client.post(f"/api/documents/{doc.id}/report", headers=headers)
    assert gen_resp.status_code == 200
    data = gen_resp.json()
    assert "report_id" in data
    assert "download_url" in data

    report_id = data["report_id"]

    # Download Report
    down_resp = client.get(f"/api/reports/{report_id}/download", headers=headers)
    assert down_resp.status_code == 200
    assert down_resp.headers["content-type"] == "application/pdf"
    # Ensure PDF starts with %PDF
    assert down_resp.content.startswith(b"%PDF-")
