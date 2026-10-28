import os
import traceback
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import Document, Clause, RiskFlag
from app.services.parser import DocumentParser
from app.services.segmenter import ClauseSegmenter
from app.services.classifier import classifier_service
from app.services.extractor import extractor_service
from app.services.risk_engine import risk_engine
from app.core.logging import logger


from typing import Optional

def process_document_pipeline(document_id: str, db: Optional[Session] = None):
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            logger.error(f"Document {document_id} not found for processing.")
            return

        # 1. Parsing Stage (Progress: 20%)
        doc.status = "parsing"
        doc.progress = 20
        db.commit()

        logger.info(f"Parsing document {doc.filename} ({doc.id})...")
        pages = DocumentParser.parse_file(doc.file_path, doc.filename)
        doc.page_count = len(pages)
        db.commit()

        # 2. Segmentation Stage (Progress: 40%)
        logger.info(f"Segmenting document {doc.filename} into clauses...")
        segmented_clauses = ClauseSegmenter.segment_pages(pages)

        if not segmented_clauses:
            # Fallback if document is empty or non-segmented
            doc.status = "done"
            doc.progress = 100
            db.commit()
            return

        # 3. Classification Stage (Progress: 60%)
        doc.status = "classifying"
        doc.progress = 60
        db.commit()

        # 4. Extraction & Risk Scoring (Progress: 80%)
        doc.status = "scoring"
        doc.progress = 80
        db.commit()

        for seg in segmented_clauses:
            # Classify clause
            cls_res = classifier_service.classify_clause(text=seg.text, heading=seg.heading or "")

            # Extract category-targeted CUAD details and entities
            extracted_data = extractor_service.extract_clause_details(text=seg.text, category=cls_res.primary_category)

            # Evaluate Risk Engine
            risk_res = risk_engine.evaluate_clause(
                text=seg.text,
                category=cls_res.primary_category,
                confidence=cls_res.confidence,
                extracted_data=extracted_data,
                db=db
            )

            # Persist Clause record
            clause_record = Clause(
                document_id=doc.id,
                clause_number=seg.clause_number,
                heading=seg.heading,
                text=seg.text,
                page_number=seg.page_number,
                start_pos=seg.start_pos,
                end_pos=seg.end_pos,
                primary_category=cls_res.primary_category,
                secondary_categories=cls_res.secondary_categories,
                top_3_labels=cls_res.top_3_labels,
                confidence=cls_res.confidence,
                is_reviewed=False
            )
            db.add(clause_record)
            db.flush()

            # Persist RiskFlag record
            risk_flag = RiskFlag(
                clause_id=clause_record.id,
                risk_level=risk_res.risk_level,
                risk_score=risk_res.risk_score,
                triggered_rules=risk_res.triggered_rules,
                extracted_data=extracted_data,
                explanation=risk_res.explanation,
                suggestion=risk_res.suggestion,
                needs_review=risk_res.needs_review
            )
            db.add(risk_flag)

        # 5. Completed! (Progress: 100%)
        doc.status = "done"
        doc.progress = 100
        db.commit()
        logger.info(f"Successfully processed document {doc.filename} ({len(segmented_clauses)} clauses).")

    except Exception as e:
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        logger.error(f"Pipeline failure on document {document_id}: {error_msg}")
        try:
            doc = db.query(Document).filter(Document.id == document_id).first()
            if doc:
                doc.status = "failed"
                doc.error_message = str(e)
                db.commit()
        except Exception:
            pass
    finally:
        if should_close:
            db.close()
