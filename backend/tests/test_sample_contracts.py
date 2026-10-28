"""
Tests for parsing, segmenting, analyzing, and risk-scoring the 3 sample contracts:
1. Standard Commercial Agreement (balanced)
2. High-Risk Vendor Contract (severe terms)
3. Mutual Non-Disclosure Agreement (clean low-risk)
"""
import os
from app.services.parser import DocumentParser
from app.services.segmenter import ClauseSegmenter
from app.services.classifier import classifier_service
from app.services.extractor import extractor_service
from app.services.risk_engine import risk_engine

SAMPLE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "sample_contracts")
document_parser = DocumentParser()
clause_segmenter = ClauseSegmenter()


def test_standard_commercial_agreement_docx():
    file_path = os.path.join(SAMPLE_DIR, "standard_commercial_agreement.docx")
    assert os.path.exists(file_path), "Sample contract must exist"

    # 1. Parse
    pages = DocumentParser.parse_docx(file_path)
    assert len(pages) >= 1
    assert any("Master Services Agreement" in p.text or "Scope of Services" in p.text for p in pages)

    # 2. Segment
    clauses = ClauseSegmenter.segment_pages(pages)
    assert len(clauses) >= 4

    # 3. Classify & evaluate risk
    results = []
    for c in clauses:
        clf_res = classifier_service.classify_clause(c.text, c.heading)
        extracted = extractor_service.extract_clause_details(c.text, clf_res.primary_category)
        risk = risk_engine.evaluate_clause(
            text=c.text,
            category=clf_res.primary_category,
            confidence=clf_res.confidence,
            extracted_data=extracted
        )
        results.append((c, clf_res, risk))

    categories = [clf.primary_category for _, clf, _ in results]
    assert any(cat in categories for cat in ["Termination", "Limitation of Liability", "Payment", "Confidentiality"])

    scores = [r.risk_score for _, _, r in results]
    avg_score = sum(scores) / len(scores)
    assert avg_score < 60, f"Standard contract average risk score should be reasonable (<60), got {avg_score}"


def test_high_risk_vendor_contract_pdf():
    file_path = os.path.join(SAMPLE_DIR, "high_risk_vendor_contract.pdf")
    assert os.path.exists(file_path), "Sample contract must exist"

    # 1. Parse
    pages = DocumentParser.parse_pdf(file_path)
    assert len(pages) >= 1

    # 2. Segment
    clauses = ClauseSegmenter.segment_pages(pages)
    assert len(clauses) >= 4

    # 3. Analyze
    high_risk_count = 0
    triggered_all_rules = set()

    for c in clauses:
        clf_res = classifier_service.classify_clause(c.text, c.heading)
        extracted = extractor_service.extract_clause_details(c.text, clf_res.primary_category)
        risk = risk_engine.evaluate_clause(
            text=c.text,
            category=clf_res.primary_category,
            confidence=clf_res.confidence,
            extracted_data=extracted
        )
        if risk.risk_level == "High":
            high_risk_count += 1
        for rule in risk.triggered_rules:
            triggered_all_rules.add(rule["rule_code"])

    # High-risk contract must trigger High-risk flags
    assert high_risk_count >= 1, "High-risk contract must trigger at least one High-risk clause"
    severe_rules = {"TERM_UNILATERAL", "TERM_NO_NOTICE", "LIAB_UNLIMITED", "INDEM_NEGLIGENCE", "CONF_INDEFINITE", "PAY_DISCRETION"}
    assert len(triggered_all_rules.intersection(severe_rules)) > 0, f"Expected trigger of severe rules, got {triggered_all_rules}"


def test_mutual_nda_pdf_and_docx():
    pdf_path = os.path.join(SAMPLE_DIR, "mutual_nda.pdf")
    docx_path = os.path.join(SAMPLE_DIR, "mutual_nda.docx")
    assert os.path.exists(pdf_path)
    assert os.path.exists(docx_path)

    pages_pdf = DocumentParser.parse_pdf(pdf_path)
    pages_docx = DocumentParser.parse_docx(docx_path)

    clauses_pdf = ClauseSegmenter.segment_pages(pages_pdf)
    clauses_docx = ClauseSegmenter.segment_pages(pages_docx)

    assert len(clauses_pdf) >= 3
    assert len(clauses_docx) >= 3

    # Analyze NDA clauses
    nda_categories = []
    for c in clauses_pdf:
        clf = classifier_service.classify_clause(c.text, c.heading)
        nda_categories.append(clf.primary_category)

    assert "Confidentiality" in nda_categories or "Termination" in nda_categories
