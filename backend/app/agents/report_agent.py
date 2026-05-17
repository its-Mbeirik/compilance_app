"""Report Agent - Generate compliance reports and recommendations."""

from typing import Dict, Any, List
from datetime import datetime


class ReportAgent:
    """Agent for generating formatted compliance reports."""

    def __init__(self):
        pass

    def generate_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations based on issues."""

        recommendations = set()

        for issue in issues:
            issue_type = issue.get("type", "")
            severity = issue.get("severity", "")

            if issue_type == "missing_legal_reference":
                recommendations.add(
                    "Verify all clauses against current Mauritanian legislation"
                )

            elif issue_type == "weak_legal_reference":
                recommendations.add(
                    "Review and strengthen clause wording to align with legal requirements"
                )

            elif issue_type == "missing_clause":
                clause_type = issue.get("clause_type", "")
                recommendations.add(
                    f"Add missing {clause_type} clause to ensure legal compliance"
                )

            elif issue_type == "non_compliant":
                recommendations.add(
                    "Modify non-compliant clause to meet legal standards"
                )

            if severity == "critical":
                recommendations.add(
                    "⚠️ Critical issues require immediate legal review and correction"
                )

        return sorted(list(recommendations))

    def generate_summary(self, state: Dict[str, Any]) -> str:
        """Generate executive summary."""

        overall_status = state.get("overall_status", "unknown")
        compliance_score = state.get("compliance_score", 0)
        document_type = state.get("document_type", "contract")
        issues_count = state.get("issue_summary", {}).get("total_issues", 0)
        mandatory_status = state.get("mandatory_clause_status", {})

        if overall_status == "compliant":
            summary = (
                f"✓ This {document_type} is largely compliant with Mauritanian law. "
                f"Compliance score: {compliance_score:.1f}%. "
            )
        elif overall_status == "partially_compliant":
            summary = (
                f"⚠ This {document_type} is partially compliant. "
                f"Compliance score: {compliance_score:.1f}%. "
                f"Found {issues_count} issues requiring attention. "
            )
        else:
            summary = (
                f"✗ This {document_type} has significant compliance issues. "
                f"Compliance score: {compliance_score:.1f}%. "
                f"Found {issues_count} issues. Legal review recommended. "
            )

        missing_mandatory = len(mandatory_status.get("missing", []))
        if missing_mandatory > 0:
            summary += (
                f"Missing {missing_mandatory} mandatory clauses. "
            )

        return summary

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute report generation agent.

        Input state should have all previous agent outputs

        Output adds:
        - final_report: Dict with complete report
        - report_status: str
        """

        try:
            # Prepare report data
            report = {
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "contract_id": state.get("contract_id", "UNKNOWN"),
                    "document_type": state.get("document_type", "contract"),
                },
                "compliance": {
                    "overall_status": state.get("overall_status", "unknown"),
                    "compliance_score": state.get("compliance_score", 0),
                    "score_breakdown": {
                        "critical_issues": state.get("issue_summary", {}).get("critical", 0),
                        "high_issues": state.get("issue_summary", {}).get("high", 0),
                        "medium_issues": state.get("issue_summary", {}).get("medium", 0),
                        "low_issues": state.get("issue_summary", {}).get("low", 0),
                    },
                },
                "mandatory_clauses": state.get("mandatory_clause_status", {}),
                "issues": state.get("compliance_issues", []),
                "summary": self.generate_summary(state),
                "recommendations": self.generate_recommendations(state.get("compliance_issues", [])),
                "extraction_metadata": state.get("extraction_metadata", {}),
                "matching_metadata": state.get("matching_metadata", {}),
            }

            return {
                "report_status": "success",
                "final_report": report,
            }

        except Exception as e:
            return {
                "report_status": "failed",
                "report_errors": [str(e)],
                "final_report": {},
            }
