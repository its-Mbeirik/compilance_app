"""Extraction Agent - Parse contracts and extract clauses."""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.services.document_processor import DocumentProcessor


class ExtractionAgent:
    """Agent for extracting clauses from contract documents."""

    def __init__(self, db: Session):
        self.db = db
        self.processor = DocumentProcessor()

    def extract_clauses(self, contract_text: str, document_type: str) -> Dict[str, Any]:
        """
        Extract clauses from contract text.

        Args:
            contract_text: Full contract document text
            document_type: Type of contract ("statuts_entreprise" or "contrat_travail")

        Returns:
            Dict with extracted clauses and metadata
        """

        # Normalize text
        normalized_text = self.processor.normalize_text(contract_text)

        # Extract clauses
        clauses = self.processor.extract_clauses(normalized_text)

        # Enrich clauses with metadata
        enriched_clauses = []
        for clause in clauses:
            enriched_clauses.append({
                "id": clause["id"],
                "type": clause["type"],
                "title": clause.get("title", ""),
                "content": clause["content"],
                "full_content": clause["full_content"],
                "word_count": len(clause["full_content"].split()),
                "character_count": len(clause["full_content"]),
            })

        return {
            "status": "success",
            "document_type": document_type,
            "total_clauses": len(enriched_clauses),
            "clauses": enriched_clauses,
            "text_length": len(normalized_text),
            "text_preview": normalized_text[:500],
        }

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute extraction agent.

        Input state should have:
        - contract_text: str
        - document_type: str

        Output adds:
        - extracted_clauses: List[Dict]
        - extraction_status: str
        """

        try:
            contract_text = state.get("contract_text", "")
            document_type = state.get("document_type", "contrat_travail")

            if not contract_text:
                return {
                    "extraction_status": "failed",
                    "extraction_errors": ["No contract text provided"],
                    "extracted_clauses": [],
                }

            result = self.extract_clauses(contract_text, document_type)

            return {
                "extraction_status": "success",
                "extracted_clauses": result["clauses"],
                "extraction_metadata": {
                    "total_clauses": result["total_clauses"],
                    "text_length": result["text_length"],
                },
            }

        except Exception as e:
            return {
                "extraction_status": "failed",
                "extraction_errors": [str(e)],
                "extracted_clauses": [],
            }
