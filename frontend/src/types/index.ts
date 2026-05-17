export type SeverityLevel = 'critical' | 'high' | 'medium' | 'low' | 'info';

export interface ComplianceIssue {
  issue_id: string;
  severity: SeverityLevel;
  clause_reference: string;
  issue_type: string;
  description: string;
  legal_reference: string;
  recommendation: string;
}

export interface ComplianceReport {
  contract_id: string;
  document_type: string;
  analysis_date: string;
  overall_status: 'compliant' | 'non_compliant' | 'partially_compliant';
  compliance_score: number;
  total_issues: number;
  critical_issues: number;
  high_issues: number;
  issues: ComplianceIssue[];
  summary: string;
  recommendations: string[];
}

export interface ContractUploadResponse {
  contract_id: string;
  filename: string;
  document_type: string;
  status: string;
  message: string;
}

export interface ProcessingStatus {
  contract_id: string;
  stage: 'uploaded' | 'extracting' | 'analyzing' | 'complete' | 'failed';
  progress: number;
  message: string;
  timestamp: string;
  errors?: string[];
}
