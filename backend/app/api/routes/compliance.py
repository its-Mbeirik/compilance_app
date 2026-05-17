"""Compliance verification endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.main import get_db
from app.models.database import Contract, ComplianceReport as ComplianceReportModel, ComplianceIssue as ComplianceIssueModel
from app.services.document_processor import DocumentProcessor
from app.agents.graph import run_compliance_verification

logger = logging.getLogger(__name__)
router = APIRouter()


class SeverityLevel(str, Enum):
    """Severity levels for compliance issues."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ComplianceIssue(BaseModel):
    """A single compliance issue detected."""

    issue_id: str
    severity: SeverityLevel
    clause_reference: str
    issue_type: str  # "missing_clause", "non_compliant", "contradiction", etc.
    description: str
    legal_reference: Optional[str] = None
    recommendation: str


class ComplianceReport(BaseModel):
    """Full compliance report for a contract."""

    contract_id: str
    document_type: str
    analysis_date: str
    overall_status: str  # "compliant", "non_compliant", "partially_compliant"
    compliance_score: float  # 0-100
    total_issues: int
    critical_issues: int
    high_issues: int
    issues: List[ComplianceIssue]
    summary: str
    recommendations: List[str]


@router.post("/compliance/verify/{contract_id}", response_model=ComplianceReport)
async def verify_compliance(contract_id: str, db: Session = Depends(get_db)):
    """
    Trigger compliance verification for a contract.

    Executes the multi-agent workflow:
    1. Extraction Agent: Parse contract and extract clauses
    2. Legal Matching Agent: Match clauses against legal corpus
    3. Compliance Agent: Detect violations and anomalies
    4. Report Agent: Generate compliance report with recommendations

    Returns:
        ComplianceReport: Detailed compliance analysis report
    """
    logger.info(f"Starting compliance verification for contract: {contract_id}")

    # Retrieve contract from database
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    if not contract.file_path:
        raise HTTPException(status_code=400, detail="Contract has no file path")

    try:
        # Extract contract text
        processor = DocumentProcessor()
        contract_text, doc_metadata = processor.process_document(contract.file_path)

        if not contract_text:
            raise ValueError("Failed to extract text from contract")

        logger.info(f"Extracted {len(contract_text)} characters from contract ({doc_metadata.get('file_type')})")

        # Run compliance verification workflow
        logger.info("Running compliance verification workflow...")
        result = await run_compliance_verification(
            db=db,
            contract_id=contract_id,
            contract_text=contract_text,
            document_type=contract.document_type,
        )

        logger.info(f"Workflow completed with status: {result.get('overall_status')}")

        # Extract results from workflow
        overall_status = result.get("overall_status", "unknown")
        compliance_score = result.get("compliance_score", 0.0)
        summary = result.get("summary", "Analysis completed")
        recommendations = result.get("recommendations", [])
        issues_data = result.get("compliance_issues", [])

        # Count issues by severity
        issue_summary = result.get("issue_summary", {})
        total_issues = issue_summary.get("total_issues", 0)
        critical_issues = issue_summary.get("critical", 0)
        high_issues = issue_summary.get("high", 0)

        # Format compliance issues
        formatted_issues = []
        for issue in issues_data:
            formatted_issues.append(
                ComplianceIssue(
                    issue_id=issue.get("id", "ISSUE_UNKNOWN"),
                    severity=SeverityLevel(issue.get("severity", "low")),
                    clause_reference=issue.get("clause_id", ""),
                    issue_type=issue.get("type", ""),
                    description=issue.get("description", ""),
                    legal_reference=issue.get("legal_reference"),
                    recommendation=issue.get("recommendation", ""),
                )
            )

        # Update contract status
        contract.status = "completed"
        contract.processed_at = datetime.utcnow()
        db.commit()

        # Save report to database
        report_model = ComplianceReportModel(
            contract_id=contract_id,
            overall_status=overall_status,
            compliance_score=compliance_score,
            total_issues=total_issues,
            critical_issues=critical_issues,
            high_issues=high_issues,
            summary=summary,
            extracted_clauses=len(result.get("extracted_clauses", [])),
            report_json=result,
        )
        db.add(report_model)
        db.commit()
        db.refresh(report_model)

        # Save individual issues
        for issue in formatted_issues:
            issue_model = ComplianceIssueModel(
                report_id=report_model.id,
                severity=issue.severity.value,
                issue_type=issue.issue_type,
                clause_reference=issue.clause_reference,
                description=issue.description,
                legal_reference=issue.legal_reference or "",
                recommendation=issue.recommendation,
            )
            db.add(issue_model)
        db.commit()

        return ComplianceReport(
            contract_id=contract_id,
            document_type=contract.document_type,
            analysis_date=datetime.utcnow().isoformat(),
            overall_status=overall_status,
            compliance_score=float(compliance_score),
            total_issues=total_issues,
            critical_issues=critical_issues,
            high_issues=high_issues,
            issues=formatted_issues,
            summary=summary,
            recommendations=recommendations,
        )

    except Exception as e:
        logger.error(f"Compliance verification failed: {str(e)}", exc_info=True)
        contract.status = "failed"
        contract.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Compliance verification failed: {str(e)}")


@router.get("/compliance/{contract_id}", response_model=ComplianceReport)
async def get_compliance_report(contract_id: str, db: Session = Depends(get_db)):
    """Retrieve cached compliance report for a contract."""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    report = db.query(ComplianceReportModel).filter(
        ComplianceReportModel.contract_id == contract_id
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="Compliance report not found")

    # Retrieve issues for this report
    issues = db.query(ComplianceIssueModel).filter(
        ComplianceIssueModel.report_id == report.id
    ).all()

    formatted_issues = [
        ComplianceIssue(
            issue_id=f"ISSUE_{i:03d}",
            severity=SeverityLevel(issue.severity),
            clause_reference=issue.clause_reference,
            issue_type=issue.issue_type,
            description=issue.description,
            legal_reference=issue.legal_reference,
            recommendation=issue.recommendation,
        )
        for i, issue in enumerate(issues, 1)
    ]

    # Extract recommendations from report JSON
    recommendations = report.report_json.get("recommendations", []) if report.report_json else []

    return ComplianceReport(
        contract_id=contract_id,
        document_type=contract.document_type,
        analysis_date=report.created_at.isoformat(),
        overall_status=report.overall_status,
        compliance_score=report.compliance_score,
        total_issues=report.total_issues,
        critical_issues=report.critical_issues,
        high_issues=report.high_issues,
        issues=formatted_issues,
        summary=report.summary,
        recommendations=recommendations,
    )


@router.post("/compliance/{contract_id}/query")
async def query_compliance(contract_id: str, question: str, db: Session = Depends(get_db)):
    """
    Interactive Q&A mode for compliance-related questions.

    Example: "What are the missing clauses in this contract?"
    """
    report = db.query(ComplianceReportModel).filter(
        ComplianceReportModel.contract_id == contract_id
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="Compliance report not found")

    # Basic question answering based on report data
    question_lower = question.lower()
    answer = ""

    if "missing" in question_lower or "clause" in question_lower:
        issues = db.query(ComplianceIssueModel).filter(
            ComplianceIssueModel.report_id == report.id,
            ComplianceIssueModel.issue_type.like("%missing%"),
        ).all()
        if issues:
            answer = f"Found {len(issues)} missing clauses: " + ", ".join(
                [i.description for i in issues]
            )
        else:
            answer = "No missing clauses detected."

    elif "score" in question_lower or "compliance" in question_lower:
        answer = (
            f"Overall compliance status: {report.overall_status}. "
            f"Compliance score: {report.compliance_score}%. "
            f"Total issues found: {report.total_issues}"
        )

    elif "recommendation" in question_lower or "fix" in question_lower:
        answer = " ".join(report.report_json.get("recommendations", []))
        if not answer:
            answer = "No specific recommendations available."

    else:
        answer = report.summary

    return {
        "contract_id": contract_id,
        "question": question,
        "answer": answer,
    }


@router.get("/compliance/{contract_id}/export")
async def export_report(contract_id: str, format: str = "json", db: Session = Depends(get_db)):
    """
    Export compliance report in specified format.

    Supported formats: json, pdf, docx
    """
    report = db.query(ComplianceReportModel).filter(
        ComplianceReportModel.contract_id == contract_id
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="Compliance report not found")

    if format == "json":
        return {
            "format": "json",
            "data": report.report_json,
        }
    elif format in ["pdf", "docx"]:
        return {
            "contract_id": contract_id,
            "format": format,
            "status": "pending",
            "message": f"Export to {format.upper()} is not yet implemented",
        }
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
