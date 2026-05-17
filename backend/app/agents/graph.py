"""LangGraph state machine for multi-agent compliance verification workflow."""

from typing import TypedDict, List, Optional, Any, Dict
from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session

from app.agents.extraction_agent import ExtractionAgent
from app.agents.legal_matching_agent import LegalMatchingAgent
from app.agents.compliance_agent import ComplianceAgent
from app.agents.report_agent import ReportAgent


class ComplianceState(TypedDict):
    """Shared state for the compliance verification workflow."""

    # Input
    contract_id: str
    contract_text: str
    document_type: str  # "statuts_entreprise" or "contrat_travail"

    # Extraction phase
    extracted_clauses: Optional[List[dict]]
    extraction_status: Optional[str]
    extraction_metadata: Optional[Dict[str, Any]]

    # Legal matching phase
    legal_matches: Optional[List[dict]]
    matching_status: Optional[str]
    matching_metadata: Optional[Dict[str, Any]]

    # Compliance verification phase
    compliance_issues: Optional[List[dict]]
    compliance_score: Optional[float]
    overall_status: Optional[str]
    mandatory_clause_status: Optional[Dict[str, Any]]
    issue_summary: Optional[Dict[str, Any]]
    verification_status: Optional[str]

    # Report generation phase
    final_report: Optional[dict]
    report_status: Optional[str]


def build_compliance_graph(db: Session) -> StateGraph:
    """
    Build the LangGraph state machine for compliance verification.

    Workflow:
    1. Extraction Agent: Parse contract and extract clauses
    2. Legal Matching Agent: Match clauses against legal corpus
    3. Compliance Agent: Detect violations and anomalies
    4. Report Agent: Generate compliance report with recommendations

    Args:
        db: Database session

    Returns:
        Compiled LangGraph graph
    """

    # Initialize agents
    extraction_agent = ExtractionAgent(db)
    legal_matching_agent = LegalMatchingAgent(db)
    compliance_agent = ComplianceAgent(db)
    report_agent = ReportAgent()

    # Create graph
    graph = StateGraph(ComplianceState)

    # Add nodes for each agent
    graph.add_node("extract", lambda state: extraction_agent.run(state))
    graph.add_node("match_legal", lambda state: legal_matching_agent.run(state))
    graph.add_node("check_compliance", lambda state: compliance_agent.run(state))
    graph.add_node("generate_report", lambda state: report_agent.run(state))

    # Define workflow edges
    graph.add_edge("extract", "match_legal")
    graph.add_edge("match_legal", "check_compliance")
    graph.add_edge("check_compliance", "generate_report")
    graph.add_edge("generate_report", END)

    # Set entry point
    graph.set_entry_point("extract")

    # Compile the graph
    return graph.compile()


def create_compliance_workflow(db: Session):
    """Create and return a compiled compliance verification workflow."""
    return build_compliance_graph(db)


# Helper function to run the workflow
async def run_compliance_verification(
    db: Session,
    contract_id: str,
    contract_text: str,
    document_type: str = "contrat_travail"
) -> Dict[str, Any]:
    """
    Run the full compliance verification workflow.

    Args:
        db: Database session
        contract_id: Unique identifier for the contract
        contract_text: Full contract document text
        document_type: Type of contract ("statuts_entreprise" or "contrat_travail")

    Returns:
        Complete compliance analysis report with all agent outputs
    """

    # Create workflow
    workflow = create_compliance_workflow(db)

    # Prepare initial state
    initial_state: ComplianceState = {
        "contract_id": contract_id,
        "contract_text": contract_text,
        "document_type": document_type,
        "extracted_clauses": None,
        "extraction_status": None,
        "extraction_metadata": None,
        "legal_matches": None,
        "matching_status": None,
        "matching_metadata": None,
        "compliance_issues": None,
        "compliance_score": None,
        "overall_status": None,
        "mandatory_clause_status": None,
        "issue_summary": None,
        "verification_status": None,
        "final_report": None,
        "report_status": None,
    }

    # Run workflow (invoke is synchronous, runs in-process)
    result = workflow.invoke(initial_state)

    # Extract and return all relevant data from workflow result
    final_report = result.get("final_report", {})

    # Ensure all necessary fields are present in the response
    return {
        "overall_status": result.get("overall_status", "unknown"),
        "compliance_score": result.get("compliance_score", 0.0),
        "summary": final_report.get("summary", ""),
        "recommendations": final_report.get("recommendations", []),
        "compliance_issues": result.get("compliance_issues", []),
        "extracted_clauses": result.get("extracted_clauses", []),
        "issue_summary": result.get("issue_summary", {}),
        "mandatory_clause_status": result.get("mandatory_clause_status", {}),
        "final_report": final_report,
    }
