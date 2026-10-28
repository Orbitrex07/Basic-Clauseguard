import pytest
from app.services.risk_engine import risk_engine


def evaluate(text: str, category: str, extracted_data: dict = None, confidence: float = 0.9):
    return risk_engine.evaluate_clause(
        text=text,
        category=category,
        confidence=confidence,
        extracted_data=extracted_data or {}
    )


# --- 1. Termination Rules ---

def test_term_unilateral_positive():
    text = "Company shall have the sole discretion to terminate this agreement at any time without cause."
    res = evaluate(text, "Termination")
    assert res.risk_level == "High"
    assert any(r["rule_code"] == "TERM_UNILATERAL" for r in res.triggered_rules)


def test_term_unilateral_negative():
    text = "Either party may terminate this agreement upon mutual written consent."
    res = evaluate(text, "Termination")
    assert not any(r["rule_code"] == "TERM_UNILATERAL" for r in res.triggered_rules)


def test_term_no_notice_positive():
    text = "Provider may terminate immediately without notice in the event of any inconvenience."
    res = evaluate(text, "Termination")
    assert res.risk_level == "High"
    assert any(r["rule_code"] == "TERM_NO_NOTICE" for r in res.triggered_rules)


def test_term_no_notice_negative():
    text = "Termination requires at least thirty days advance written notice."
    res = evaluate(text, "Termination")
    assert not any(r["rule_code"] == "TERM_NO_NOTICE" for r in res.triggered_rules)


def test_term_short_notice_positive():
    text = "Customer may terminate upon 5 days notice."
    res = evaluate(text, "Termination", extracted_data={"notice_days": 5})
    assert any(r["rule_code"] == "TERM_SHORT_NOTICE" for r in res.triggered_rules)


def test_term_short_notice_negative():
    text = "Customer may terminate upon 30 days notice."
    res = evaluate(text, "Termination", extracted_data={"notice_days": 30})
    assert not any(r["rule_code"] == "TERM_SHORT_NOTICE" for r in res.triggered_rules)


def test_term_fair_positive():
    text = "Either party may terminate upon at least 30 days prior written notice."
    res = evaluate(text, "Termination", extracted_data={"notice_days": 30})
    assert any(r["rule_code"] == "TERM_FAIR" for r in res.triggered_rules)
    assert res.risk_level == "Low"


# --- 2. Limitation of Liability Rules ---

def test_liab_unlimited_positive():
    text = "Customer's liability under this agreement shall not be limited and disclaims all liability whatsoever for provider."
    res = evaluate(text, "Limitation of Liability")
    assert res.risk_level == "High"
    assert any(r["rule_code"] == "LIAB_UNLIMITED" for r in res.triggered_rules)


def test_liab_unlimited_negative():
    text = "Each party's aggregate liability shall be capped at the fees paid in the prior 12 months."
    res = evaluate(text, "Limitation of Liability")
    assert not any(r["rule_code"] == "LIAB_UNLIMITED" for r in res.triggered_rules)


def test_liab_low_cap_positive():
    text = "Total liability shall not exceed $100 under any circumstances."
    res = evaluate(text, "Limitation of Liability")
    assert any(r["rule_code"] == "LIAB_LOW_CAP" for r in res.triggered_rules)


def test_liab_low_cap_negative():
    text = "Total liability shall be capped at $1,000,000."
    res = evaluate(text, "Limitation of Liability")
    assert not any(r["rule_code"] == "LIAB_LOW_CAP" for r in res.triggered_rules)


def test_liab_cap_ok_positive():
    text = "Each party's aggregate liability is mutually capped at the total fees paid or payable in the preceding 12 months."
    res = evaluate(text, "Limitation of Liability")
    assert any(r["rule_code"] == "LIAB_CAP_OK" for r in res.triggered_rules)
    assert res.risk_level == "Low"


# --- 3. Confidentiality Rules ---

def test_conf_indefinite_positive():
    text = "The receiving party shall maintain all disclosures strictly confidential in perpetuity."
    res = evaluate(text, "Confidentiality")
    assert any(r["rule_code"] == "CONF_INDEFINITE" for r in res.triggered_rules)


def test_conf_indefinite_negative():
    text = "Confidentiality obligations shall survive for a period of three years."
    res = evaluate(text, "Confidentiality")
    assert not any(r["rule_code"] == "CONF_INDEFINITE" for r in res.triggered_rules)


def test_conf_long_term_positive():
    text = "Confidentiality obligations survive for 10 years."
    res = evaluate(text, "Confidentiality", extracted_data={"confidentiality_years": 10})
    assert any(r["rule_code"] == "CONF_LONG_TERM" for r in res.triggered_rules)


def test_conf_long_term_negative():
    text = "Confidentiality obligations survive for 3 years."
    res = evaluate(text, "Confidentiality", extracted_data={"confidentiality_years": 3})
    assert not any(r["rule_code"] == "CONF_LONG_TERM" for r in res.triggered_rules)


def test_conf_fair_positive():
    text = "Confidentiality obligations shall survive for a period of three years with standard exceptions."
    res = evaluate(text, "Confidentiality")
    assert any(r["rule_code"] == "CONF_FAIR" for r in res.triggered_rules)
    assert res.risk_level == "Low"


# --- 4. Indemnification Rules ---

def test_indem_negligence_positive():
    text = "Customer agrees to indemnify company regardless of sole negligence or misconduct."
    res = evaluate(text, "Indemnification")
    assert res.risk_level == "High"
    assert any(r["rule_code"] == "INDEM_NEGLIGENCE" for r in res.triggered_rules)


def test_indem_negligence_negative():
    text = "Each party shall defend, indemnify and hold harmless against third-party claims excluding gross negligence."
    res = evaluate(text, "Indemnification")
    assert not any(r["rule_code"] == "INDEM_NEGLIGENCE" for r in res.triggered_rules)


def test_indem_broad_positive():
    text = "Client shall indemnify, defend and hold harmless against any and all claims, all losses, damages, consequential damages."
    res = evaluate(text, "Indemnification")
    assert res.risk_level == "High"
    assert any(r["rule_code"] == "INDEM_BROAD" for r in res.triggered_rules)


def test_indem_broad_negative():
    text = "Each party shall indemnify the other limited to third-party intellectual property claims."
    res = evaluate(text, "Indemnification")
    assert not any(r["rule_code"] == "INDEM_BROAD" for r in res.triggered_rules)


def test_indem_mutual_positive():
    text = "Each party shall defend, indemnify and hold harmless the other, limited to third-party intellectual property claims."
    res = evaluate(text, "Indemnification")
    assert any(r["rule_code"] == "INDEM_MUTUAL" for r in res.triggered_rules)
    assert res.risk_level == "Low"


# --- 5. Auto-Renewal Rules ---

def test_renew_auto_short_positive():
    text = "Agreement shall automatically renew unless notice is given at least 90 days prior to term expiration."
    res = evaluate(text, "Auto-Renewal")
    assert any(r["rule_code"] == "RENEW_AUTO_SHORT" for r in res.triggered_rules)


def test_renew_auto_long_positive():
    text = "Agreement shall automatically renew for successive three years terms."
    res = evaluate(text, "Auto-Renewal")
    assert any(r["rule_code"] == "RENEW_AUTO_LONG" for r in res.triggered_rules)


def test_renew_manual_positive():
    text = "This contract shall not automatically renew and shall extend only upon mutual written agreement."
    res = evaluate(text, "Auto-Renewal")
    assert any(r["rule_code"] == "RENEW_MANUAL" for r in res.triggered_rules)
    assert res.risk_level == "Low"


# --- 6. Payment Rules ---

def test_pay_discretion_positive():
    text = "Provider retains sole discretion to increase fees at any time without right to terminate."
    res = evaluate(text, "Payment")
    assert res.risk_level == "High"
    assert any(r["rule_code"] == "PAY_DISCRETION" for r in res.triggered_rules)


def test_pay_vague_positive():
    text = "Customer shall pay undetermined fees and arbitrary penalties payable on demand without invoice."
    res = evaluate(text, "Payment")
    assert any(r["rule_code"] == "PAY_VAGUE" for r in res.triggered_rules)


def test_pay_clear_positive():
    text = "All amounts payable within 30 days of receipt of invoice Net 30 days."
    res = evaluate(text, "Payment")
    assert any(r["rule_code"] == "PAY_CLEAR" for r in res.triggered_rules)
    assert res.risk_level == "Low"


# --- 7. Dispute Resolution Rules ---

def test_disp_arb_far_positive():
    text = "Exclusive jurisdiction in remote foreign court; customer waives all rights to jury trial and class actions."
    res = evaluate(text, "Dispute Resolution")
    assert any(r["rule_code"] == "DISP_ARB_FAR" for r in res.triggered_rules)


def test_disp_mutual_positive():
    text = "Parties agree to good faith negotiation prior to arbitration with mutually agreed arbitrator."
    res = evaluate(text, "Dispute Resolution")
    assert any(r["rule_code"] == "DISP_MUTUAL" for r in res.triggered_rules)
    assert res.risk_level == "Low"


# --- 8. Boundary & Needs Review Tests ---

def test_low_confidence_forces_needs_review():
    text = "General operational provisions and standard terms."
    res = evaluate(text, "Other", confidence=0.45)
    assert res.needs_review is True


def test_high_confidence_no_needs_review():
    text = "General operational provisions and standard terms."
    res = evaluate(text, "Other", confidence=0.85)
    assert res.needs_review is False


def test_score_bounded_to_100():
    # Trigger multiple high risk rules
    text = (
        "Provider has sole discretion to terminate at any time without notice. "
        "Customer agrees to unlimited liability and broad indemnity."
    )
    res = evaluate(text, "Termination")
    assert 0 <= res.risk_score <= 100
