import os
import re
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.core.logging import logger

# Relevant CUAD questions targeted strictly by predicted category
CATEGORY_CUAD_QUESTIONS = {
    "Termination": [
        "What is the notice period required to terminate?",
        "Does a party have the right to terminate for convenience?"
    ],
    "Payment": [
        "What are the payment terms, due dates, or invoicing intervals?",
        "Are there price increase caps or late payment fees?"
    ],
    "Limitation of Liability": [
        "What is the cap or limitation on liability?",
        "Is there an uncapped liability provision?"
    ],
    "Confidentiality": [
        "How long do confidentiality obligations survive post-termination?",
        "What are the standard exceptions to confidentiality?"
    ],
    "Indemnification": [
        "What is the scope of indemnification obligations?",
        "Does indemnification include third-party intellectual property infringement?"
    ],
    "Auto-Renewal": [
        "Does the agreement automatically renew?",
        "What is the renewal notice window?"
    ],
    "Dispute Resolution": [
        "What is the governing law and jurisdiction?",
        "Is mandatory arbitration or mediation required?"
    ]
}


class ExtractorService:
    def __init__(self):
        self.mode = settings.ML_MODE
        self.model = None
        self.tokenizer = None
        self.device = None
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
            from transformers import AutoTokenizer, AutoModelForQuestionAnswering

            extractor_dir = os.path.join(settings.MODEL_DIR, "extractor")
            if os.path.exists(os.path.join(extractor_dir, "config.json")):
                logger.info(f"Loading real extractor from {extractor_dir}...")
                self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                self.tokenizer = AutoTokenizer.from_pretrained(extractor_dir)
                self.model = AutoModelForQuestionAnswering.from_pretrained(extractor_dir)
                self.model.to(self.device)
                self.model.eval()
                self.model_loaded = True
                logger.info(f"Real extractor loaded successfully on {self.device}!")
            else:
                logger.warning(f"No trained extractor found in {extractor_dir}. Running mock fallback.")
                self.model_loaded = False
        except Exception as e:
            logger.error(f"Failed to load real extractor: {e}. Falling back to mock logic.")
            self.model_loaded = False

    @staticmethod
    def extract_numeric_entities(text: str) -> Dict[str, Any]:
        entities: Dict[str, Any] = {}

        # 1. Days (e.g., 30 days, 15 days, 0 days)
        day_match = re.search(r"(\b\d{1,3}\b)\s*(-|\s)?(calendar|business|working)?\s*days?", text, re.IGNORECASE)
        if day_match:
            entities["days"] = int(day_match.group(1))

        # Check specifically for notice days
        notice_match = re.search(r"(?:notice|prior\s+to|within)\s+(?:of\s+)?(?:at\s+least\s+)?(\d{1,3})\s*days?", text, re.IGNORECASE)
        if notice_match:
            entities["notice_days"] = int(notice_match.group(1))
        elif "days" in entities:
            entities["notice_days"] = entities["days"]

        # 2. Months
        month_match = re.search(r"(\b\d{1,2}\b)\s*(-|\s)?months?", text, re.IGNORECASE)
        if month_match:
            entities["months"] = int(month_match.group(1))

        # 3. Years (e.g., 2 years, 3 years, 5 years)
        year_match = re.search(r"(\b\d{1,2}\b)\s*(-|\s)?years?", text, re.IGNORECASE)
        if year_match:
            entities["years"] = int(year_match.group(1))
            entities["confidentiality_years"] = int(year_match.group(1))

        # 4. Percentages
        pct_match = re.search(r"(\d+(?:\.\d+)?)\s*%", text)
        if pct_match:
            entities["percentages"] = float(pct_match.group(1))

        # 5. Currencies (e.g., $100, $5,000, USD 1,000)
        curr_match = re.search(r"(?:\$|USD\s*|EUR\s*|GBP\s*)(\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+)", text, re.IGNORECASE)
        if curr_match:
            raw_num = curr_match.group(1).replace(",", "")
            entities["currency_amount"] = float(raw_num)

        return entities

    def extract_clause_details(self, text: str, category: str) -> Dict[str, Any]:
        data = self.extract_numeric_entities(text)
        spans: Dict[str, str] = {}

        questions = CATEGORY_CUAD_QUESTIONS.get(category, [])

        if self.mode == "real" and self.model_loaded and self.tokenizer and self.model:
            try:
                import torch
                for q in questions:
                    inputs = self.tokenizer(
                        q,
                        text,
                        truncation=True,
                        max_length=512,
                        doc_stride=128,
                        return_tensors="pt"
                    )
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}
                    with torch.no_grad():
                        outputs = self.model(**inputs)
                        start_idx = torch.argmax(outputs.start_logits, dim=-1).item()
                        end_idx = torch.argmax(outputs.end_logits, dim=-1).item()

                    if end_idx >= start_idx:
                        tokens = inputs["input_ids"][0][start_idx:end_idx + 1]
                        ans = self.tokenizer.decode(tokens, skip_special_tokens=True).strip()
                        if ans:
                            spans[q] = ans
            except Exception as e:
                logger.error(f"Error in real extractor: {e}")

        # If spans empty or mock mode, extract key heuristic spans
        if not spans:
            for q in questions:
                q_low = q.lower()
                if "notice period" in q_low or "convenience" in q_low:
                    m = re.search(r"(?:upon|with|within)?\s*(?:at\s+least\s+)?(?:\w+\s*)?\(?\d+\)?\s*(?:calendar|business|working)?\s*days?(?:\s+prior\s+written\s+notice)?|without\s+cause|without\s+notice|effective\s+immediately|for\s+convenience", text, re.IGNORECASE)
                    if m:
                        spans[q] = m.group(0).strip()
                elif "cap" in q_low or "liability" in q_low:
                    m = re.search(r"capped\s+at\s+[^.;]+|total\s+(?:aggregate\s+)?liability\s+shall\s+(?:not\s+exceed|be\s+limited\s+to)\s+[^.;]+|disclaims?\s+all\s+liability|in\s+no\s+event\s+shall[^.;]+liability\s+exceed\s+[^.;]+", text, re.IGNORECASE)
                    if m:
                        spans[q] = m.group(0).strip()
                elif "confidentiality" in q_low or "survive" in q_low:
                    m = re.search(r"survive\s+(?:for\s+)?(?:a\s+period\s+of\s+)?(?:(?:\w+\s*)?\(?\d+\)?\s*years?|in\s+perpetuity|indefinitely)|for\s+(?:a\s+period\s+of\s+)?(?:\w+\s*)?\(?\d+\)?\s*years?", text, re.IGNORECASE)
                    if m:
                        spans[q] = m.group(0).strip()
                elif "indemnif" in q_low:
                    m = re.search(r"indemnify,\s*defend\s*(?:and|&)\s*hold\s*harmless[^.;]+|sole\s+negligence|gross\s+negligence\s+or\s+willful\s+misconduct|third[- ]party[^.;]+claims?", text, re.IGNORECASE)
                    if m:
                        spans[q] = m.group(0).strip()
                elif "renew" in q_low:
                    m = re.search(r"automatically\s+renew[^.;]+|successive\s+(?:terms|periods)[^.;]*|at\s+least\s+(?:\w+\s*)?\(?\d+\)?\s*days\s+prior", text, re.IGNORECASE)
                    if m:
                        spans[q] = m.group(0).strip()
                elif "payment" in q_low or "fee" in q_low:
                    m = re.search(r"within\s+(?:\w+\s*)?\(?\d+\)?\s*days[^.;]*|net\s+\d+|interest\s+at\s+[^.;]+|all\s+undisputed\s+invoices\s+within[^.;]+", text, re.IGNORECASE)
                    if m:
                        spans[q] = m.group(0).strip()
                elif "governing law" in q_low or "jurisdiction" in q_low or "arbitration" in q_low:
                    m = re.search(r"governed\s+by\s+the\s+laws\s+of\s+[^.;]+|arbitration\s+(?:administered\s+by|in)\s+[^.;]+|jurisdiction\s+of\s+[^.;]+", text, re.IGNORECASE)
                    if m:
                        spans[q] = m.group(0).strip()

        data["extracted_spans"] = spans
        return data


extractor_service = ExtractorService()
