"""Database models and initialization."""

from sqlalchemy import Column, String, Text, Float, Integer, DateTime, Index, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from pgvector.sqlalchemy import Vector
from datetime import datetime
import uuid

Base = declarative_base()


class LegalDocument(Base):
    """Legal document (law articles) with vector embeddings."""

    __tablename__ = "legal_documents"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    law_code = Column(String(100), index=True)  # "Code du Travail", "Code des Sociétés"
    article = Column(String(50), index=True)  # "Article 25"
    article_title = Column(String(255), nullable=True)
    content = Column(Text)  # Full article text
    embedding = Column(Vector(1024))  # pgvector embedding
    jurisdiction = Column(String(50), default="Mauritanie")
    category = Column(String(100), nullable=True)  # "labor", "corporate", etc.
    effective_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_law_code", "law_code"),
        Index("idx_embedding", "embedding", postgresql_using="ivfflat", postgresql_ops={"embedding": "vector_cosine_ops"}),
    )


class Contract(Base):
    """Uploaded contract document."""

    __tablename__ = "contracts"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255))
    document_type = Column(String(50))  # "statuts_entreprise" or "contrat_travail"
    file_path = Column(String(255))
    file_size_bytes = Column(Integer)
    status = Column(String(50), default="uploaded")  # uploaded, processing, completed, failed
    error_message = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_status", "status"),
        Index("idx_document_type", "document_type"),
    )


class ComplianceReport(Base):
    """Compliance analysis report."""

    __tablename__ = "compliance_reports"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id = Column(PG_UUID(as_uuid=True), index=True)
    overall_status = Column(String(50))  # compliant, non_compliant, partially_compliant
    compliance_score = Column(Float)  # 0-100
    total_issues = Column(Integer)
    critical_issues = Column(Integer)
    high_issues = Column(Integer)
    summary = Column(Text)
    extracted_clauses = Column(Integer)  # Number of clauses found
    report_json = Column(JSONB)  # Full report data
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_contract_id", "contract_id"),
        Index("idx_overall_status", "overall_status"),
    )


class ComplianceIssue(Base):
    """Individual compliance issue found."""

    __tablename__ = "compliance_issues"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(PG_UUID(as_uuid=True), index=True)
    severity = Column(String(20))  # critical, high, medium, low, info
    issue_type = Column(String(100))  # missing_clause, non_compliant, contradiction, etc.
    clause_reference = Column(String(255))
    description = Column(Text)
    legal_reference = Column(String(255))  # "Code du Travail Article 25"
    recommendation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_report_id", "report_id"),
        Index("idx_severity", "severity"),
        Index("idx_issue_type", "issue_type"),
    )


def init_db(engine):
    """Initialize database with all tables."""
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    Base.metadata.create_all(engine)


def enable_pgvector(session: Session):
    """Enable pgvector extension if not already enabled."""
    try:
        session.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        session.commit()
    except Exception as e:
        print(f"Note: pgvector extension might already exist: {e}")
