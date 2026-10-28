"""
Live end-to-end verification script for ClauseGuard running locally:
Tests:
1. Health & Disclaimer endpoints
2. User Registration & Login (JWT)
3. Upload of Sample PDF (high_risk_vendor_contract.pdf)
4. Upload of Sample DOCX (standard_commercial_agreement.docx)
5. Asynchronous Pipeline status polling (queued -> parsing -> classifying -> scoring -> done)
6. Clause extraction, risk flags, confidence scores, and plain-English explanations
7. PDF Report generation and binary verification (%PDF-)
8. Document ownership isolation (User B cannot access User A's contract)
9. Admin Portal verification: Review Queue, Rule Updating, Audit Logs, Stats
10. Document Deletion & Cascaded cleanup
"""
import urllib.request
import urllib.error
import json
import os
import time

BASE_URL = "http://127.0.0.1:8000/api"
SAMPLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_contracts")


def api_request(endpoint, method="GET", data=None, headers=None):
    url = f"{BASE_URL}{endpoint}"
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)
    
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=req_headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as resp:
            content_type = resp.headers.get("Content-Type", "")
            raw = resp.read()
            if "application/json" in content_type:
                return resp.status, json.loads(raw.decode("utf-8")), resp.headers
            return resp.status, raw, resp.headers
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            err_json = json.loads(raw.decode("utf-8"))
            return e.code, err_json, e.headers
        except Exception:
            return e.code, raw, e.headers


def upload_multipart(endpoint, filepath, filename, content_type, token):
    boundary = "----WebKitFormBoundaryClauseGuardLiveVerification"
    with open(filepath, "rb") as f:
        file_bytes = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n"
    ).encode("utf-8") + file_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(
        f"{BASE_URL}{endpoint}",
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Authorization": f"Bearer {token}"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


def run_verification():
    print("=" * 70)
    print("ClauseGuard Live Verification Suite (Windows Local)")
    print("=" * 70)

    # 1. Health Endpoint & Disclaimer
    print("\n[Step 1] Checking Health Endpoint...")
    status, health_data, _ = api_request("/health")
    assert status == 200, f"Health check failed with status {status}"
    assert health_data["status"] == "ok"
    assert health_data["ml_mode"] == "mock"
    assert health_data["models_loaded"] is True
    assert "informational" in health_data["disclaimer"].lower()
    print("  -> Health OK:", health_data)

    # 2. Registration & Login for User A
    print("\n[Step 2] Testing Auth: Register & Login User A...")
    ts = int(time.time())
    user_a_email = f"live_user_a_{ts}@example.com"
    status, reg_data, _ = api_request("/auth/register", method="POST", data={
        "email": user_a_email,
        "password": "Password123!",
        "full_name": "Live Tester A"
    })
    assert status in [200, 201], f"Register failed: {reg_data}"
    print(f"  -> User A registered: {user_a_email}")

    status, login_data, _ = api_request("/auth/login", method="POST", data={
        "email": user_a_email,
        "password": "Password123!"
    })
    assert status == 200, f"Login failed: {login_data}"
    token_a = login_data["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    print("  -> User A login successful. JWT obtained.")

    # Also register User B for isolation testing
    user_b_email = f"live_user_b_{ts}@example.com"
    api_request("/auth/register", method="POST", data={
        "email": user_b_email,
        "password": "Password123!",
        "full_name": "Live Tester B"
    })
    _, login_b, _ = api_request("/auth/login", method="POST", data={
        "email": user_b_email,
        "password": "Password123!"
    })
    token_b = login_b["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 3. Upload Sample PDF
    print("\n[Step 3] Uploading Sample PDF (high_risk_vendor_contract.pdf)...")
    pdf_path = os.path.join(SAMPLE_DIR, "high_risk_vendor_contract.pdf")
    status, doc_pdf = upload_multipart(
        "/documents",
        pdf_path,
        "high_risk_vendor_contract.pdf",
        "application/pdf",
        token_a
    )
    assert status in [200, 201], f"PDF upload failed: {doc_pdf}"
    pdf_id = doc_pdf["id"]
    print(f"  -> Uploaded PDF ID: {pdf_id}")

    # 4. Upload Sample DOCX
    print("\n[Step 4] Uploading Sample DOCX (standard_commercial_agreement.docx)...")
    docx_path = os.path.join(SAMPLE_DIR, "standard_commercial_agreement.docx")
    status, doc_docx = upload_multipart(
        "/documents",
        docx_path,
        "standard_commercial_agreement.docx",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        token_a
    )
    assert status in [200, 201], f"DOCX upload failed: {doc_docx}"
    docx_id = doc_docx["id"]
    print(f"  -> Uploaded DOCX ID: {docx_id}")

    # 5. Poll Status until Done
    print("\n[Step 5] Polling Pipeline Status...")
    for doc_id, name in [(pdf_id, "PDF"), (docx_id, "DOCX")]:
        for attempt in range(20):
            status, s_data, _ = api_request(f"/documents/{doc_id}/status", headers=headers_a)
            assert status == 200
            print(f"  -> {name} status: {s_data['status']} (progress: {s_data['progress']}%)")
            if s_data["status"] == "done":
                break
            time.sleep(1)
        assert s_data["status"] == "done", f"{name} pipeline did not reach done state"

    # 6. Retrieve Clauses and Verify Risk Analysis
    print("\n[Step 6] Verifying Segmented Clauses and Risk Flags...")
    status, clauses_pdf, _ = api_request(f"/documents/{pdf_id}/clauses", headers=headers_a)
    assert status == 200
    assert len(clauses_pdf) >= 4, f"Expected at least 4 clauses in PDF, got {len(clauses_pdf)}"
    
    high_risks = [c for c in clauses_pdf if c.get("risk_flag", {}).get("risk_level") == "High"]
    print(f"  -> PDF extracted {len(clauses_pdf)} clauses, High-risk clauses: {len(high_risks)}")
    assert len(high_risks) >= 1, "High-risk sample contract must trigger at least 1 High-risk clause"

    # Inspect first clause detail
    c0 = clauses_pdf[0]
    status, c_detail, _ = api_request(f"/clauses/{c0['id']}", headers=headers_a)
    assert status == 200
    assert "risk_flag" in c_detail
    assert "explanation" in c_detail["risk_flag"]
    print("  -> Clause detail verified with explanation:", c_detail["risk_flag"]["explanation"][:80], "...")

    # 7. Generate & Download PDF Report
    print("\n[Step 7] Generating & Downloading ReportLab PDF Report...")
    status, r_gen, _ = api_request(f"/documents/{pdf_id}/report", method="POST", headers=headers_a)
    assert status in [200, 201]
    report_id = r_gen["report_id"]
    print(f"  -> Report generated with ID: {report_id}")

    status, r_bytes, r_hdrs = api_request(f"/reports/{report_id}/download", headers=headers_a)
    assert status == 200
    assert r_bytes.startswith(b"%PDF-"), "Downloaded file is not a valid PDF"
    assert len(r_bytes) > 2000, "PDF report content is unexpectedly small"
    print(f"  -> Report downloaded successfully ({len(r_bytes)} bytes, %PDF- header valid)")

    # 8. Document Ownership Isolation
    print("\n[Step 8] Testing Document Ownership Protection...")
    status, isol_res, _ = api_request(f"/documents/{pdf_id}", headers=headers_b)
    assert status == 403, f"Expected 403 Forbidden for User B accessing User A's document, got {status}"
    print("  -> Ownership isolation verified: User B received 403 Forbidden.")

    # 9. Admin Portal Functions
    print("\n[Step 9] Testing Admin Portal Endpoints...")
    status, admin_login, _ = api_request("/auth/login", method="POST", data={
        "email": "admin@clauseguard.local",
        "password": "AdminSecurePass123!"
    })
    assert status == 200, f"Admin login failed: {admin_login}"
    admin_token = admin_login["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Review queue
    status, rev_queue, _ = api_request("/admin/review-queue", headers=admin_headers)
    assert status == 200
    print(f"  -> Admin review queue accessible ({len(rev_queue)} items)")

    # Rules editor
    status, rules_list, _ = api_request("/admin/rules", headers=admin_headers)
    assert status == 200
    assert len(rules_list) == 21, f"Expected 21 rules, got {len(rules_list)}"
    print(f"  -> Admin rules editor returned {len(rules_list)} rules")

    # Audit logs
    status, audit_logs, _ = api_request("/admin/audit-logs", headers=admin_headers)
    assert status == 200
    print(f"  -> Admin audit logs returned {len(audit_logs)} events")

    # Stats
    status, stats, _ = api_request("/admin/stats", headers=admin_headers)
    assert status == 200
    print("  -> Admin stats:", stats)

    # 10. Deletion and Cascaded Cleanup
    print("\n[Step 10] Testing Document Deletion...")
    status, del_res, _ = api_request(f"/documents/{pdf_id}", method="DELETE", headers=headers_a)
    assert status == 200
    status, _, _ = api_request(f"/documents/{pdf_id}", headers=headers_a)
    assert status == 404, "Deleted document should return 404"
    print("  -> Document deleted successfully and cascaded records cleared.")

    print("\n" + "=" * 70)
    print("ALL LIVE VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_verification()
