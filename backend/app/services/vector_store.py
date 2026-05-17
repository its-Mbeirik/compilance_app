"""Vector database service for semantic search over legal corpus."""

from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from sentence_transformers import SentenceTransformer

from app.models.database import LegalDocument
from app.core.config import get_settings


class VectorStore:
    """Vector store for semantic search over legal documents."""

    def __init__(self, session: Session, embedding_model: Optional[SentenceTransformer] = None):
        self.session = session
        self.settings = get_settings()

        if embedding_model is None:
            self.model = SentenceTransformer(self.settings.embedding_model)
        else:
            self.model = embedding_model

    def semantic_search(
        self,
        query: str,
        law_codes: Optional[List[str]] = None,
        top_k: int = 5,
        similarity_threshold: float = 0.5
    ) -> List[Tuple[LegalDocument, float]]:
        """
        Semantic search over legal corpus.

        Args:
            query: Search query text
            law_codes: Filter by specific law codes (e.g., ["Code du Travail"])
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score (0-1)

        Returns:
            List of (legal_document, similarity_score) tuples, sorted by relevance
        """

        # Embed query
        query_embedding = self.model.encode(query, normalize_embeddings=True)

        # Build query
        q = self.session.query(
            LegalDocument,
            func.max(1 - func.l2_distance(LegalDocument.embedding, query_embedding)).label("similarity")
        )

        # Filter by law codes if provided
        if law_codes:
            q = q.filter(LegalDocument.law_code.in_(law_codes))

        # Order by similarity and limit results
        results = (
            q.group_by(LegalDocument.id)
            .order_by(func.max(1 - func.l2_distance(LegalDocument.embedding, query_embedding)).desc())
            .limit(top_k * 2)  # Get more results to filter by threshold
            .all()
        )

        # Filter by threshold and format results
        filtered_results = [
            (doc, float(similarity))
            for doc, similarity in results
            if similarity >= similarity_threshold
        ][:top_k]

        return filtered_results

    def find_similar_articles(
        self,
        clause_content: str,
        document_type: str,
        top_k: int = 5
    ) -> List[Tuple[LegalDocument, float]]:
        """
        Find legal articles most relevant to a contract clause.

        Args:
            clause_content: The clause text to match
            document_type: Type of contract ("statuts_entreprise" or "contrat_travail")
            top_k: Number of results

        Returns:
            List of (legal_document, similarity_score) tuples
        """

        # Determine applicable laws based on document type
        applicable_laws = []
        if document_type == "contrat_travail":
            applicable_laws = ["Code du Travail", "Convention Collective du Travail"]
        elif document_type == "statuts_entreprise":
            applicable_laws = ["Code des Sociétés", "Code du Commerce", "Code des Obligations et des Contrats"]

        return self.semantic_search(
            query=clause_content,
            law_codes=applicable_laws,
            top_k=top_k,
            similarity_threshold=0.4  # Lower threshold for clause matching
        )

    def get_mandatory_clauses(self, document_type: str) -> List[str]:
        """
        Get mandatory clause requirements for document type.

        Returns: List of expected article references
        """

        if document_type == "contrat_travail":
            # Mandatory labor contract clauses per Code du Travail
            return [
                "Article 5",      # Employer identification
                "Article 11",     # Contract type and duration
                "Article 12",     # Salary and compensation
                "Article 13",     # Working conditions
                "Article 23",     # Leave and vacation
                "Article 25",     # Probation period
                "Article 30",     # Termination conditions
            ]
        elif document_type == "statuts_entreprise":
            # Mandatory corporate statute articles
            return [
                "Article 5",      # Raison sociale (company name)
                "Article 6",      # Siège social (registered office)
                "Article 7",      # Objet social (purpose)
                "Article 10",     # Capital social
                "Article 15",     # Governance structure
                "Article 20",     # Assemblée générale
                "Article 30",     # Modification of statutes
            ]

        return []

    def extract_article_summary(self, article: LegalDocument) -> str:
        """Extract a concise summary of an article."""
        # Return first 150 characters or up to first period
        text = article.content
        period_pos = text.find('.')
        if period_pos > 0 and period_pos < 200:
            return text[:period_pos + 1]
        return text[:150] + "..."

    def get_database_stats(self) -> dict:
        """Get statistics about the legal corpus."""

        total_docs = self.session.query(func.count(LegalDocument.id)).scalar()
        law_codes = self.session.query(
            LegalDocument.law_code,
            func.count(LegalDocument.id).label("count")
        ).group_by(LegalDocument.law_code).all()

        return {
            "total_documents": total_docs,
            "by_law_code": {code: count for code, count in law_codes},
        }
