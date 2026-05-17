/**
 * API client for Compliance Verification System
 */

// Construct API URL based on environment
// In browser: use relative /api/v1 path (proxied by Next.js)
// In Node (SSR): use direct backend URL
const API_BASE_URL = typeof window !== 'undefined'
  ? '/api/v1' // Browser: use Next.js proxy (relative path)
  : (process.env.NEXT_PUBLIC_API_URL || 'http://backend:8000/api/v1'); // Server: direct URL

export interface ContractUploadResponse {
  contract_id: string;
  filename: string;
  document_type: string;
  status: string;
  message: string;
}

export interface ContractMetadata {
  contract_id: string;
  filename: string;
  document_type: string;
  upload_date: string;
  size_mb: number;
  status: string;
}

export interface ComplianceIssue {
  issue_id: string;
  severity: "critical" | "high" | "medium" | "low" | "info";
  clause_reference: string;
  issue_type: string;
  description: string;
  legal_reference?: string;
  recommendation: string;
}

export interface ComplianceReport {
  contract_id: string;
  document_type: string;
  analysis_date: string;
  overall_status: "compliant" | "partially_compliant" | "non_compliant";
  compliance_score: number;
  total_issues: number;
  critical_issues: number;
  high_issues: number;
  issues: ComplianceIssue[];
  summary: string;
  recommendations: string[];
}

export interface QueryResponse {
  contract_id: string;
  question: string;
  answer: string;
}

/**
 * Upload a contract for compliance verification
 */
export async function uploadContract(file: File): Promise<ContractUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/contracts/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to upload contract");
  }

  return response.json();
}

/**
 * Get list of contracts
 */
export async function listContracts(skip: number = 0, limit: number = 10) {
  const response = await fetch(
    `${API_BASE_URL}/contracts?skip=${skip}&limit=${limit}`
  );

  if (!response.ok) {
    throw new Error("Failed to list contracts");
  }

  return response.json();
}

/**
 * Get contract metadata
 */
export async function getContract(contractId: string): Promise<ContractMetadata> {
  const response = await fetch(`${API_BASE_URL}/contracts/${contractId}`);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error("Contract not found");
    }
    throw new Error("Failed to get contract");
  }

  return response.json();
}

/**
 * Trigger compliance verification for a contract
 */
export async function verifyCompliance(
  contractId: string
): Promise<ComplianceReport> {
  const response = await fetch(
    `${API_BASE_URL}/compliance/verify/${contractId}`,
    {
      method: "POST",
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Compliance verification failed");
  }

  return response.json();
}

/**
 * Get cached compliance report
 */
export async function getComplianceReport(
  contractId: string
): Promise<ComplianceReport> {
  const response = await fetch(`${API_BASE_URL}/compliance/${contractId}`);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error("Compliance report not found");
    }
    throw new Error("Failed to get compliance report");
  }

  return response.json();
}

/**
 * Query compliance findings
 */
export async function queryCompliance(
  contractId: string,
  question: string
): Promise<QueryResponse> {
  const response = await fetch(
    `${API_BASE_URL}/compliance/${contractId}/query`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question }),
    }
  );

  if (!response.ok) {
    throw new Error("Failed to query compliance");
  }

  return response.json();
}

/**
 * Export compliance report
 */
export async function exportReport(contractId: string, format: string = "json") {
  const response = await fetch(
    `${API_BASE_URL}/compliance/${contractId}/export?format=${format}`
  );

  if (!response.ok) {
    throw new Error("Failed to export report");
  }

  if (format === "json") {
    return response.json();
  } else if (format === "pdf" || format === "docx") {
    // Download binary file
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `report.${format}`;
    a.click();
  }
}

/**
 * Check health of backend
 */
export async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
}
