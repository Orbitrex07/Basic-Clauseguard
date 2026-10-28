import re
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from sqlalchemy.orm import Session
from app.db.models import RiskRule
from app.core.config import settings
from app.core.logging import logger


@dataclass
class RiskEvaluationResult:
    risk_level: str  # Low, Medium, High
    risk_score: int  # 0 to 100
    triggered_rules: List[Dict[str, Any]]
    explanation: str
    suggestion: str
    needs_review: bool


class RiskEngine:
    def __init__(self):
        self.cached_rules: List[Dict[str, Any]] = []

    def load_rules_from_db(self, db: Optional[Session] = None) -> List[Dict[str, Any]]:
        if db:
            try:
                db_rules = db.query(RiskRule).filter(RiskRule.is_enabled == True).all()
                if db_rules:
                    return [
                        {
                            "rule_code": r.rule_code,
                            "category": r.category,
                            "severity": r.severity,
                            "points": r.points,
                            "pattern_type": r.pattern_type,
                            "pattern_value": r.pattern_value,
                            "reason": r.reason,
                            "suggestion": r.suggestion or ""
                        }
                        for r in db_rules
                    ]
            except Exception as e:
                logger.error(f"Error querying risk_rules table: {e}. Falling back to cached rules.")

        # Fallback to rules.yaml
        if not self.cached_rules:
            import os
            import yaml
            yaml_path = os.path.join(os.path.dirname(__file__), "..", "config", "rules.yaml")
            if os.path.exists(yaml_path):
                with open(yaml_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    self.cached_rules = [r for r in data.get("rules", []) if r.get("is_enabled", True)]
        return self.cached_rules

    @staticmethod
    def evaluate_numeric_threshold(condition_str: str, extracted_data: Dict[str, Any]) -> bool:
        try:
            cond = json.loads(condition_str) if isinstance(condition_str, str) else condition_str
            field = cond.get("field")
            op = cond.get("operator")
            threshold = cond.get("threshold")

            if field not in extracted_data:
                return False

            val = extracted_data[field]
            if op == "<":
                return val < threshold
            elif op == "<=":
                return val <= threshold
            elif op == ">":
                return val > threshold
            elif op == ">=":
                return val >= threshold
            elif op == "==":
                return val == threshold
            return False
        except Exception:
            return False

    def evaluate_clause(
        self,
        text: str,
        category: str,
        confidence: float,
        extracted_data: Dict[str, Any],
        db: Optional[Session] = None
    ) -> RiskEvaluationResult:
        rules = self.load_rules_from_db(db)

        # Filter rules by matching category
        cat_rules = [r for r in rules if r["category"].lower() == category.lower()]

        triggered_rules: List[Dict[str, Any]] = []
        max_high_found = False
        highest_points = 0

        for r in cat_rules:
            is_triggered = False
            ptype = r["pattern_type"]
            pvalue = r["pattern_value"]

            if ptype == "regex_any":
                try:
                    if re.search(pvalue, text, re.IGNORECASE):
                        is_triggered = True
                except Exception as e:
                    logger.error(f"Regex error in rule {r['rule_code']}: {e}")

            elif ptype == "numeric_threshold":
                if self.evaluate_numeric_threshold(pvalue, extracted_data):
                    is_triggered = True

            elif ptype == "extractor_flag":
                # Check if extractor found an answer to a related flagged question
                spans = extracted_data.get("extracted_spans", {})
                for q, ans in spans.items():
                    if pvalue.lower() in q.lower() and ans.strip():
                        is_triggered = True
                        break

            elif ptype == "composite":
                # Composite condition (both regex and threshold or multiple checks)
                try:
                    comp = json.loads(pvalue) if isinstance(pvalue, str) else pvalue
                    regex_part = comp.get("regex")
                    thresh_part = comp.get("threshold")
                    match_regex = bool(re.search(regex_part, text, re.IGNORECASE)) if regex_part else True
                    match_thresh = self.evaluate_numeric_threshold(thresh_part, extracted_data) if thresh_part else True
                    is_triggered = match_regex and match_thresh
                except Exception:
                    is_triggered = False

            if is_triggered:
                triggered_rules.append(r)
                if r["severity"] == "High":
                    max_high_found = True
                if r["points"] > highest_points:
                    highest_points = r["points"]

        # If no rules matched in non-Other category, assign baseline score
        if not triggered_rules:
            if category == "Other":
                final_score = 10
            else:
                final_score = 20  # Neutral baseline
        else:
            # Aggregate score: highest rule points + fraction of secondary triggered rules
            secondary_sum = sum(tr["points"] for tr in triggered_rules) - highest_points
            final_score = min(100, highest_points + int(secondary_sum * 0.2))

        # Determine Risk Level
        # Spec: High-severity rule forces High.
        if max_high_found or final_score >= 60:
            risk_level = "High"
            final_score = max(60, final_score)
        elif final_score >= 30:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        # Needs review if confidence < 0.50
        needs_review = confidence < settings.CONFIDENCE_THRESHOLD

        # Generate Plain-English Explanation & Suggestion (template-based, strictly no LLM)
        explanation, suggestion = self.generate_explanation(
            category=category,
            risk_level=risk_level,
            triggered_rules=triggered_rules,
            extracted_data=extracted_data
        )

        return RiskEvaluationResult(
            risk_level=risk_level,
            risk_score=final_score,
            triggered_rules=triggered_rules,
            explanation=explanation,
            suggestion=suggestion,
            needs_review=needs_review
        )

    def generate_explanation(
        self,
        category: str,
        risk_level: str,
        triggered_rules: List[Dict[str, Any]],
        extracted_data: Dict[str, Any]
    ) -> Tuple[str, str]:
        # Structure:
        # 1. What the clause does.
        # 2. What triggered the risk.
        # 3. Plain-English explanation.
        # 4. Informational suggestion.

        if not triggered_rules:
            if risk_level == "Low":
                expl = (
                    f"Low risk — {category}: This clause sets out standard contractual provisions for {category.lower()}. "
                    f"No non-standard or unilateral exposure terms were detected."
                )
                sugg = "Terms appear standard and commercially balanced."
            else:
                expl = (
                    f"{risk_level} risk — {category}: Standard provisions were detected for {category.lower()}, "
                    f"but standard verification is advised."
                )
                sugg = "Review terms against standard commercial terms."
            return expl, sugg

        primary_rule = triggered_rules[0]
        rule_reason = primary_rule["reason"]
        rule_sugg = primary_rule["suggestion"] or "Request commercially reasonable terms."

        expl = (
            f"{risk_level} risk — {category}: This clause governs {category.lower()} terms. "
            f"It triggered rule [{primary_rule['rule_code']}]: {rule_reason} "
            f"This may create disproportionate legal or financial exposure for one party."
        )

        if len(triggered_rules) > 1:
            additional_reasons = "; ".join([r["reason"] for r in triggered_rules[1:]])
            expl += f" Additional risk factors: {additional_reasons}."

        sugg = f"Informational suggestion: {rule_sugg}"

        return expl, sugg


risk_engine = RiskEngine()
