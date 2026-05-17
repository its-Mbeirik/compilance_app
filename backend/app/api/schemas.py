"""Pydantic schemas for API request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ClauseExtraction(BaseModel):
    """Extracted clause from a contract."""

    clause_id: str
    clause_type: str  # Article, Section, Clause, etc.
    title: Optional[str] = None
    content: str
    location: str  # Page number or section reference
    confidence: float  # 0-1 confidence score


class LegalReference(BaseModel):
    """Reference to a law or regulation."""

    law_code: str  # e.g., "Code du Travail", "Code des Sociétés"
    article: str
    article_title: Optional[str] = None
    content: str
    applicable_jurisdiction: str  # "Mauritanie"


class ComplianceMatch(BaseModel):
    """Result of matching a clause against legal requirements."""

    clause_id: str
    matched_articles: List[LegalReference]
    match_score: float  # 0-1
    is_compliant: bool
    notes: Optional[str] = None


class ProcessingStatus(BaseModel):
    """Status of document processing."""

    contract_id: str
    stage: str  # "uploaded", "extracting", "analyzing", "complete", "failed"
    progress: int  # 0-100
    message: str
    timestamp: datetime
    errors: Optional[List[str]] = None
