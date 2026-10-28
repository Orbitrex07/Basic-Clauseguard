import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.db.base import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(32), default="user", nullable=False)  # "user" or "admin"
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    clause_corrections = relationship("ClauseCorrection", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(1024), nullable=False)
    file_size = Column(Integer, nullable=False)
    page_count = Column(Integer, default=1, nullable=False)
    mime_type = Column(String(128), nullable=False)
    status = Column(String(32), default="queued", index=True, nullable=False)  # queued, parsing, classifying, scoring, done, failed
    progress = Column(Integer, default=0, nullable=False)  # 0 to 100
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="documents")
    clauses = relationship("Clause", back_populates="document", cascade="all, delete-orphan", order_by="Clause.clause_number")
    reports = relationship("Report", back_populates="document", cascade="all, delete-orphan")


class Clause(Base):
    __tablename__ = "clauses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False)
    clause_number = Column(Integer, nullable=False, index=True)
    heading = Column(String(255), nullable=True)
    text = Column(Text, nullable=False)
    page_number = Column(Integer, default=1, nullable=False)
    start_pos = Column(Integer, default=0, nullable=False)
    end_pos = Column(Integer, default=0, nullable=False)
    primary_category = Column(String(64), index=True, nullable=False)
    secondary_categories = Column(JSON, default=list, nullable=False)
    top_3_labels = Column(JSON, default=list, nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)
    is_reviewed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    document = relationship("Document", back_populates="clauses")
    risk_flag = relationship("RiskFlag", back_populates="clause", uselist=False, cascade="all, delete-orphan")
    corrections = relationship("ClauseCorrection", back_populates="clause", cascade="all, delete-orphan")


class RiskFlag(Base):
    __tablename__ = "risk_flags"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    clause_id = Column(String(36), ForeignKey("clauses.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    risk_level = Column(String(32), index=True, nullable=False)  # Low, Medium, High
    risk_score = Column(Integer, nullable=False)  # 0 to 100
    triggered_rules = Column(JSON, default=list, nullable=False)
    extracted_data = Column(JSON, default=dict, nullable=False)
    explanation = Column(Text, nullable=False)
    suggestion = Column(Text, nullable=True)
    needs_review = Column(Boolean, default=False, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    clause = relationship("Clause", back_populates="risk_flag")


class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    file_path = Column(String(1024), nullable=False)
    file_size = Column(Integer, default=0, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    document = relationship("Document", back_populates="reports")


class RiskRule(Base):
    __tablename__ = "risk_rules"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    rule_code = Column(String(64), unique=True, index=True, nullable=False)
    category = Column(String(64), index=True, nullable=False)
    severity = Column(String(32), nullable=False)  # Low, Medium, High
    points = Column(Integer, nullable=False)  # 0 to 100
    pattern_type = Column(String(32), nullable=False)  # regex_any, extractor_flag, numeric_threshold, composite
    pattern_value = Column(Text, nullable=False)
    reason = Column(Text, nullable=False)
    suggestion = Column(Text, nullable=True)
    is_enabled = Column(Boolean, default=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ClauseCorrection(Base):
    __tablename__ = "clause_corrections"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    clause_id = Column(String(36), ForeignKey("clauses.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    original_category = Column(String(64), nullable=False)
    corrected_category = Column(String(64), nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    clause = relationship("Clause", back_populates="corrections")
    user = relationship("User", back_populates="clause_corrections")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(64), index=True, nullable=False)  # login, upload, analysis, download, correction, rule_modification
    entity_type = Column(String(64), nullable=True)  # document, clause, rule, user
    entity_id = Column(String(64), nullable=True)
    details = Column(JSON, default=dict, nullable=False)
    ip_address = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)

    user = relationship("User", back_populates="audit_logs")
