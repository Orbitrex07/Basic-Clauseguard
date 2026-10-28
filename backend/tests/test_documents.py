import io
import pytest
import fitz
from app.services.pipeline import process_document_pipeline


def get_auth_token(client, email, password, full_name="Test"):
    client.post("/api/auth/register", json={"email": email, "password": password, "full_name": full_name})
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    return res.json()["access_token"]


def create_dummy_pdf_bytes():
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "1. Termination: Either party may terminate with 30 days notice.\n2. Payment: Net 30 days.")
    stream = io.BytesIO()
    doc.save(stream)
    doc.close()
    return stream.getvalue()


def test_upload_valid_pdf_and_pipeline(client, db):
    token = get_auth_token(client, "uploader@example.com", "SecretPass123!")
    headers = {"Authorization": f"Bearer {token}"}

    pdf_bytes = create_dummy_pdf_bytes()
    files = {"file": ("test_contract.pdf", pdf_bytes, "application/pdf")}

    response = client.post("/api/documents", headers=headers, files=files)
    assert response.status_code == 201
    doc_data = response.json()
    assert doc_data["filename"] == "test_contract.pdf"
    assert doc_data["status"] == "queued"
    doc_id = doc_data["id"]

    # Process pipeline directly for testing
    process_document_pipeline(doc_id, db=db)

    # Poll status
    status_resp = client.get(f"/api/documents/{doc_id}/status", headers=headers)
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] == "done"
    assert status_resp.json()["progress"] == 100

    # Get clauses
    clauses_resp = client.get(f"/api/documents/{doc_id}/clauses", headers=headers)
    assert clauses_resp.status_code == 200
    clauses = clauses_resp.json()
    assert len(clauses) >= 1
    assert "risk_flag" in clauses[0]


def test_upload_invalid_extension(client):
    token = get_auth_token(client, "badext@example.com", "SecretPass123!")
    headers = {"Authorization": f"Bearer {token}"}

    files = {"file": ("malicious.exe", b"fake binary executable", "application/octet-stream")}
    response = client.post("/api/documents", headers=headers, files=files)
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]


def test_upload_disguised_file_magic_bytes(client):
    token = get_auth_token(client, "fakeheader@example.com", "SecretPass123!")
    headers = {"Authorization": f"Bearer {token}"}

    # Named .pdf but content does not start with %PDF-
    files = {"file": ("fake.pdf", b"This is plain text pretending to be a PDF", "application/pdf")}
    response = client.post("/api/documents", headers=headers, files=files)
    assert response.status_code == 400
    assert "magic bytes" in response.json()["detail"]


def test_ownership_isolation(client):
    token_user_a = get_auth_token(client, "usera@example.com", "SecretPass123!", "User A")
    token_user_b = get_auth_token(client, "userb@example.com", "SecretPass123!", "User B")

    # User A uploads a document
    pdf_bytes = create_dummy_pdf_bytes()
    files = {"file": ("user_a_contract.pdf", pdf_bytes, "application/pdf")}
    res_a = client.post("/api/documents", headers={"Authorization": f"Bearer {token_user_a}"}, files=files)
    doc_id_a = res_a.json()["id"]

    # User B tries to access User A's document -> 403 Forbidden
    res_b_get = client.get(f"/api/documents/{doc_id_a}", headers={"Authorization": f"Bearer {token_user_b}"})
    assert res_b_get.status_code == 403

    # User B tries to delete User A's document -> 403 Forbidden
    res_b_del = client.delete(f"/api/documents/{doc_id_a}", headers={"Authorization": f"Bearer {token_user_b}"})
    assert res_b_del.status_code == 403


def test_cascade_delete_document(client, db):
    token = get_auth_token(client, "deleter@example.com", "SecretPass123!")
    headers = {"Authorization": f"Bearer {token}"}

    pdf_bytes = create_dummy_pdf_bytes()
    files = {"file": ("to_delete.pdf", pdf_bytes, "application/pdf")}
    res = client.post("/api/documents", headers=headers, files=files)
    doc_id = res.json()["id"]

    process_document_pipeline(doc_id, db=db)

    # Delete
    del_resp = client.delete(f"/api/documents/{doc_id}", headers=headers)
    assert del_resp.status_code == 200

    # Ensure document is gone
    get_resp = client.get(f"/api/documents/{doc_id}", headers=headers)
    assert get_resp.status_code == 404
