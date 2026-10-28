import os
import json
import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from app.core.config import settings
from app.core.logging import logger

CANONICAL_CATEGORIES = [
    "Termination",
    "Payment",
    "Limitation of Liability",
    "Confidentiality",
    "Indemnification",
    "Auto-Renewal",
    "Dispute Resolution",
    "Other"
]

CATEGORY_KEYWORDS = {
    "Termination": [
        "terminate", "termination", "cancellation", "end of agreement", "expiry", "survive termination", "cure period"
    ],
    "Payment": [
        "payment", "fee", "invoice", "payable", "billing", "charges", "expenses", "taxes", "compensation", "net 30"
    ],
    "Limitation of Liability": [
        "limitation of liability", "liability", "consequential damages", "indirect damages", "cap", "aggregate liability", "disclaimer of warranties"
    ],
    "Confidentiality": [
        "confidential", "confidentiality", "proprietary information", "non-disclosure", "trade secrets", "disclose"
    ],
    "Indemnification": [
        "indemnify", "indemnification", "hold harmless", "defend", "indemnity", "third party claims", "losses"
    ],
    "Auto-Renewal": [
        "automatic renewal", "auto-renew", "successive periods", "renewal term", "opt-out", "cancel renewal"
    ],
    "Dispute Resolution": [
        "governing law", "jurisdiction", "arbitration", "dispute", "venue", "court", "mediation", "laws of the state"
    ]
}


@dataclass
class ClassificationResult:
    primary_category: str
    secondary_categories: List[str]
    top_3_labels: List[Dict[str, Any]]
    confidence: float


class ClassifierService:
    def __init__(self):
        self.mode = settings.ML_MODE
        self.model = None
        self.tokenizer = None
        self.device = None
        self.label2id = {}
        self.id2label = {}
        self.taxonomy_mapping = {}
        self.model_loaded = False

        if self.mode == "real":
            self.load_real_model()

    def is_loaded(self) -> bool:
        if self.mode == "mock":
            return True
        return self.model_loaded

    def load_real_model(self):
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForSequenceClassification

            classifier_dir = os.path.join(settings.MODEL_DIR, "classifier")
            mapping_dir = os.path.join(os.path.dirname(__file__), "..", "..", "ml", "mappings")
            tax_path = os.path.join(mapping_dir, "taxonomy_mapping.json")

            if os.path.exists(tax_path):
                with open(tax_path, "r", encoding="utf-8") as f:
                    self.taxonomy_mapping = json.load(f)

            if os.path.exists(os.path.join(classifier_dir, "config.json")):
                logger.info(f"Loading real classifier from {classifier_dir}...")
                self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                self.tokenizer = AutoTokenizer.from_pretrained(classifier_dir)
                self.model = AutoModelForSequenceClassification.from_pretrained(classifier_dir)
                self.model.to(self.device)
                self.model.eval()
                self.model_loaded = True
                logger.info(f"Real classifier loaded successfully on {self.device}!")
            else:
                logger.warning(f"No trained classifier found in {classifier_dir}. Running mock fallback for real mode.")
                self.model_loaded = False
        except Exception as e:
            logger.error(f"Failed to load real classifier: {e}. Falling back to mock logic.")
            self.model_loaded = False

    def classify_clause_mock(self, text: str, heading: str = "") -> ClassificationResult:
        full_text = f"{heading or ''} {text}".lower()

        scores: Dict[str, float] = {cat: 0.05 for cat in CANONICAL_CATEGORIES}

        # Check signature blocks and preamble
        if re.search(r"(in\s+witness\s+whereof|signature\s+page|by:\s*_{3,})", full_text):
            return ClassificationResult(
                primary_category="Other",
                secondary_categories=[],
                top_3_labels=[{"label": "Other", "probability": 0.95}],
                confidence=0.95
            )

        for cat, keywords in CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if kw in full_text:
                    scores[cat] += 0.35

        # Cap scores to probability range
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_cat, top_score = sorted_scores[0]

        if top_score < 0.20:
            top_cat = "Other"
            top_score = 0.45  # Low confidence triggers needs_review

        confidence = min(0.96, max(0.42, round(top_score / (top_score + 0.5), 2)))

        secondary = [c for c, s in sorted_scores[1:3] if s > 0.30 and c != "Other"]

        top_3 = [
            {"label": c, "probability": round(min(0.98, s / 1.5), 2)}
            for c, s in sorted_scores[:3]
        ]

        return ClassificationResult(
            primary_category=top_cat,
            secondary_categories=secondary,
            top_3_labels=top_3,
            confidence=confidence
        )

    def classify_clause(self, text: str, heading: str = "") -> ClassificationResult:
        if self.mode == "real" and self.model_loaded and self.tokenizer and self.model:
            try:
                import torch
                inputs = self.tokenizer(
                    text,
                    truncation=True,
                    max_length=256,
                    padding="max_length",
                    return_tensors="pt"
                )
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    probs = torch.softmax(outputs.logits, dim=-1)[0].cpu().numpy()

                top_indices = probs.argsort()[-3:][::-1]
                top_3 = []
                for idx in top_indices:
                    raw_label = self.model.config.id2label.get(idx, str(idx))
                    canon_label = self.taxonomy_mapping.get(raw_label, "Other")
                    top_3.append({
                        "label": canon_label,
                        "source_label": raw_label,
                        "probability": round(float(probs[idx]), 3)
                    })

                primary = top_3[0]["label"]
                conf = float(top_3[0]["probability"])
                secondary = [item["label"] for item in top_3[1:] if item["label"] != primary and item["label"] != "Other"]

                return ClassificationResult(
                    primary_category=primary,
                    secondary_categories=list(set(secondary)),
                    top_3_labels=top_3,
                    confidence=round(conf, 2)
                )
            except Exception as e:
                logger.error(f"Error during real classification inference: {e}. Using fallback.")
                return self.classify_clause_mock(text, heading)

        return self.classify_clause_mock(text, heading)


classifier_service = ClassifierService()
