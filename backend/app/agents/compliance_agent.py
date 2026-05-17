"""Compliance Verification Agent - Detect violations and issues."""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.services.vector_store import VectorStore


class ComplianceAgent:
    """Agent for verifying contract compliance and detecting violations."""

    def __init__(self, db: Session):
        self.db = db
        self.vector_store = VectorStore(db)

    def check_mandatory_clauses(self, extracted_clauses: List[Dict], document_type: str) -> Dict[str, Any]:
        """Check for missing mandatory clauses."""

        mandatory_clauses = self.vector_store.get_mandatory_clauses(document_type)
        extracted_articles = [c["id"] for c in extracted_clauses]

        missing_clauses = []
        found_clauses = []

        for mandatory in mandatory_clauses:
            found = any(mandatory.lower() in str(c).lower() for c in extracted_articles)
            if found:
                found_clauses.append(mandatory)
            else:
                missing_clauses.append(mandatory)

        return {
            "found": found_clauses,
            "missing": missing_clauses,
            "coverage": len(found_clauses) / len(mandatory_clauses) * 100 if mandatory_clauses else 0,
        }

    def detect_issues(self, legal_matches: List[Dict]) -> List[Dict[str, Any]]:
        """Detect compliance issues based on legal matches."""

        issues = []
        issue_id = 0

        for match in legal_matches:
            articles = match.get("matched_articles", [])

            # Issue 1: No matching legal articles found
            if not articles:
                issue_id += 1
                issues.append({
                    "id": f"ISSUE_{issue_id:03d}",
                    "clause_id": match["clause_id"],
                    "severity": "high",
                    "type": "missing_legal_reference",
                    "description": f"Clause {match['clause_id']} has no matching legal articles in the database",
                    "recommendation": "Review this clause against current legislation",
                })
                continue

            # Issue 2: Low relevance match
            best_match = articles[0] if articles else None
            if best_match and best_match["similarity_score"] < 0.5:
                issue_id += 1
                issues.append({
                    "id": f"ISSUE_{issue_id:03d}",
                    "clause_id": match["clause_id"],
                    "severity": "medium",
                    "type": "weak_legal_reference",
                    "description": f"Clause may not align well with applicable law (similarity: {best_match['similarity_score']:.1%})",
                    "legal_reference": f"{best_match['law_code']} {best_match['article']}",
                    "recommendation": "Review clause wording to improve alignment with legal requirements",
                })

        return issues

    def calculate_compliance_score(
        self,
        total_clauses: int,
        clauses_with_matches: int,
        mandatory_coverage: float,
        issue_count: int
    ) -> float:
        """Calculate overall compliance score (0-100)."""

        if total_clauses == 0:
            return 0.0

        # Base score from clause matching
        matching_score = (clauses_with_matches / total_clauses) * 60

        # Score from mandatory clauses
        mandatory_score = (mandatory_coverage / 100) * 30

        # Penalty for issues
        issue_penalty = min(issue_count * 2, 10)

        # Final score
        score = matching_score + mandatory_score - issue_penalty
        return max(0.0, min(100.0, score))

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute compliance verification agent.

        Input state should have:
        - extracted_clauses: List[Dict]
        - legal_matches: List[Dict]
        - document_type: str
        - matching_metadata: Dict

        Output adds:
        - compliance_issues: List[Dict]
        - compliance_score: float
        - overall_status: str
        """

        try:
            extracted_clauses = state.get("extracted_clauses", [])
            legal_matches = state.get("legal_matches", [])
            document_type = state.get("document_type", "contrat_travail")
            matching_metadata = state.get("matching_metadata", {})

            # Check mandatory clauses
            mandatory_check = self.check_mandatory_clauses(extracted_clauses, document_type)

            # Detect compliance issues
            issues = self.detect_issues(legal_matches)

            # Categorize issues by severity
            critical_issues = len([i for i in issues if i["severity"] == "critical"])
            high_issues = len([i for i in issues if i["severity"] == "high"])
            medium_issues = len([i for i in issues if i["severity"] == "medium"])
            low_issues = len([i for i in issues if i["severity"] in ("low", "info")])

            # Calculate compliance score
            compliance_score = self.calculate_compliance_score(
                total_clauses=len(extracted_clauses),
                clauses_with_matches=matching_metadata.get("clauses_with_matches", 0),
                mandatory_coverage=mandatory_check["coverage"],
                issue_count=len(issues)
            )

            # Determine overall status
            if compliance_score >= 90:
                overall_status = "compliant"
            elif compliance_score >= 70:
                overall_status = "partially_compliant"
            else:
                overall_status = "non_compliant"

            return {
                "verification_status": "success",
                "compliance_issues": issues,
                "compliance_score": float(compliance_score),
                "overall_status": overall_status,
                "mandatory_clause_status": mandatory_check,
                "issue_summary": {
                    "total_issues": len(issues),
                    "critical": critical_issues,
                    "high": high_issues,
                    "medium": medium_issues,
                    "low": low_issues,
                },
            }

        except Exception as e:
            return {
                "verification_status": "failed",
                "verification_errors": [str(e)],
                "compliance_issues": [],
                "compliance_score": 0.0,
                "overall_status": "failed",
            }
