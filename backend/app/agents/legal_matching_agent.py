"""Legal Matching Agent - Match clauses against legal corpus."""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.services.vector_store import VectorStore


class LegalMatchingAgent:
    """Agent for matching contract clauses against legal requirements."""

    def __init__(self, db: Session):
        self.db = db
        self.vector_store = VectorStore(db)

    def match_clause_to_laws(self, clause: Dict[str, Any], document_type: str) -> Dict[str, Any]:
        """
        Find legal articles relevant to a specific clause.

        Args:
            clause: Single extracted clause
            document_type: Type of contract

        Returns:
            Clause with matched legal articles
        """

        clause_text = clause.get("full_content", clause.get("content", ""))

        # Find similar articles using vector search
        matches = self.vector_store.find_similar_articles(
            clause_content=clause_text,
            document_type=document_type,
            top_k=5
        )

        matched_articles = []
        for article, similarity_score in matches:
            matched_articles.append({
                "law_code": article.law_code,
                "article": article.article,
                "article_title": article.article_title,
                "content_summary": article.content[:200],
                "similarity_score": float(similarity_score),
                "relevance": "high" if similarity_score > 0.7 else "medium" if similarity_score > 0.5 else "low",
            })

        return {
            "clause_id": clause["id"],
            "clause_type": clause["type"],
            "matched_articles": matched_articles,
            "best_match_score": matched_articles[0]["similarity_score"] if matched_articles else 0,
        }

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute legal matching agent.

        Input state should have:
        - extracted_clauses: List[Dict]
        - document_type: str

        Output adds:
        - legal_matches: List[Dict]
        - matching_status: str
        """

        try:
            clauses = state.get("extracted_clauses", [])
            document_type = state.get("document_type", "contrat_travail")

            if not clauses:
                return {
                    "matching_status": "failed",
                    "matching_errors": ["No clauses to match"],
                    "legal_matches": [],
                }

            # Match each clause against legal corpus
            matches = []
            for clause in clauses:
                match_result = self.match_clause_to_laws(clause, document_type)
                matches.append(match_result)

            # Calculate matching statistics
            matched_clauses = len([m for m in matches if m["matched_articles"]])
            avg_similarity = sum(m["best_match_score"] for m in matches) / len(matches) if matches else 0

            return {
                "matching_status": "success",
                "legal_matches": matches,
                "matching_metadata": {
                    "total_clauses_matched": len(clauses),
                    "clauses_with_matches": matched_clauses,
                    "average_similarity": float(avg_similarity),
                },
            }

        except Exception as e:
            return {
                "matching_status": "failed",
                "matching_errors": [str(e)],
                "legal_matches": [],
            }
