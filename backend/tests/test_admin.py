import pytest
from app.db.models import User, Document, Clause, RiskFlag, RiskRule
from app.core.security import create_access_token, get_password_hash


@pytest.fixture
def admin_token(db):
    admin = db.query(User).filter(User.role == "admin").first()
    if not admin:
        admin = User(
            email="admin_test@clauseguard.local",
            hashed_password=get_password_hash("AdminPass123!"),
            full_name="Admin",
            role="admin",
            is_active=True
        )
        db.add(admin)
        db.commit()
    return create_access_token(subject=admin.id, role="admin")


@pytest.fixture
def regular_user_token(db):
    user = User(
        email="regular_user@example.com",
        hashed_password=get_password_hash("UserPass123!"),
        full_name="Regular",
        role="user",
        is_active=True
    )
    db.add(user)
    db.commit()
    return create_access_token(subject=user.id, role="user")


def test_admin_access_control(client, regular_user_token):
    # Non-admin user receives 403 Forbidden
    resp = client.get("/api/admin/rules", headers={"Authorization": f"Bearer {regular_user_token}"})
    assert resp.status_code == 403


def test_admin_get_and_update_rules(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.get("/api/admin/rules", headers=headers)
    assert resp.status_code == 200
    rules = resp.json()
    assert len(rules) >= 1

    first_rule = rules[0]
    rule_id = first_rule["id"]

    # Update points
    update_resp = client.put(
        f"/api/admin/rules/{rule_id}",
        headers=headers,
        json={"points": 90, "severity": "High"}
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["points"] == 90
    assert update_resp.json()["severity"] == "High"


def test_admin_review_queue_and_correction(client, admin_token, db):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create dummy user, document, clause needing review
    user = db.query(User).first()
    doc = Document(
        user_id=user.id,
        filename="review_sample.pdf",
        file_path="/tmp/fake.pdf",
        file_size=1000,
        page_count=1,
        mime_type="application/pdf",
        status="done"
    )
    db.add(doc)
    db.commit()

    clause = Clause(
        document_id=doc.id,
        clause_number=1,
        heading="Uncertain Clause",
        text="The client shall pay all expenses upon demand.",
        page_number=1,
        primary_category="Other",
        confidence=0.40,
        is_reviewed=False
    )
    db.add(clause)
    db.commit()

    rf = RiskFlag(
        clause_id=clause.id,
        risk_level="Low",
        risk_score=20,
        triggered_rules=[],
        extracted_data={},
        explanation="Baseline",
        suggestion="Review",
        needs_review=True
    )
    db.add(rf)
    db.commit()

    # Check review queue
    rq_resp = client.get("/api/admin/review-queue", headers=headers)
    assert rq_resp.status_code == 200
    items = rq_resp.json()
    assert any(c["id"] == clause.id for c in items)

    # Correct category to Payment
    correct_resp = client.patch(
        f"/api/admin/clauses/{clause.id}",
        headers=headers,
        json={"corrected_category": "Payment", "note": "Classified as payment clause"}
    )
    assert correct_resp.status_code == 200
    updated_clause = correct_resp.json()
    assert updated_clause["primary_category"] == "Payment"
    assert updated_clause["is_reviewed"] is True


def test_admin_stats(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.get("/api/admin/stats", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "total_documents" in data
    assert "risk_breakdown" in data
    assert "category_distribution" in data
