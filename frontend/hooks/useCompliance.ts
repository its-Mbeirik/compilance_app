/**
 * React hook for compliance verification workflow
 */

import { useState, useCallback } from "react";
import {
  uploadContract,
  verifyCompliance,
  getComplianceReport,
  queryCompliance,
  ContractUploadResponse,
  ComplianceReport,
  QueryResponse,
} from "@/lib/api";

export interface ComplianceState {
  // Upload state
  isUploading: boolean;
  uploadProgress: number;
  uploadError?: string;
  uploadedContract?: ContractUploadResponse;

  // Verification state
  isVerifying: boolean;
  verificationProgress: string;
  verificationError?: string;
  complianceReport?: ComplianceReport;

  // Query state
  isQuerying: boolean;
  queryError?: string;
  queryResponse?: QueryResponse;
}

const initialState: ComplianceState = {
  isUploading: false,
  uploadProgress: 0,
  isVerifying: false,
  verificationProgress: "",
  isQuerying: false,
};

export function useCompliance() {
  const [state, setState] = useState<ComplianceState>(initialState);

  /**
   * Upload a contract file
   */
  const upload = useCallback(async (file: File) => {
    setState((prev) => ({
      ...prev,
      isUploading: true,
      uploadError: undefined,
      uploadProgress: 0,
    }));

    try {
      // Simulate upload progress
      setState((prev) => ({ ...prev, uploadProgress: 30 }));

      const result = await uploadContract(file);

      setState((prev) => ({
        ...prev,
        uploadProgress: 100,
        uploadedContract: result,
        isUploading: false,
      }));

      return result;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Upload failed";
      setState((prev) => ({
        ...prev,
        isUploading: false,
        uploadError: message,
        uploadProgress: 0,
      }));
      throw error;
    }
  }, []);

  /**
   * Verify contract compliance
   */
  const verify = useCallback(async (contractId: string) => {
    setState((prev) => ({
      ...prev,
      isVerifying: true,
      verificationError: undefined,
      verificationProgress: "Starting compliance verification...",
    }));

    try {
      setState((prev) => ({
        ...prev,
        verificationProgress: "Extracting contract clauses...",
      }));
      await new Promise((r) => setTimeout(r, 500));

      setState((prev) => ({
        ...prev,
        verificationProgress: "Matching clauses against legal corpus...",
      }));
      await new Promise((r) => setTimeout(r, 500));

      setState((prev) => ({
        ...prev,
        verificationProgress: "Analyzing compliance issues...",
      }));
      await new Promise((r) => setTimeout(r, 500));

      setState((prev) => ({
        ...prev,
        verificationProgress: "Generating report...",
      }));

      const report = await verifyCompliance(contractId);

      setState((prev) => ({
        ...prev,
        isVerifying: false,
        verificationProgress: "Compliance verification complete!",
        complianceReport: report,
      }));

      return report;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Verification failed";
      setState((prev) => ({
        ...prev,
        isVerifying: false,
        verificationError: message,
        verificationProgress: "",
      }));
      throw error;
    }
  }, []);

  /**
   * Query compliance findings
   */
  const query = useCallback(async (contractId: string, question: string) => {
    setState((prev) => ({
      ...prev,
      isQuerying: true,
      queryError: undefined,
    }));

    try {
      const response = await queryCompliance(contractId, question);

      setState((prev) => ({
        ...prev,
        isQuerying: false,
        queryResponse: response,
      }));

      return response;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Query failed";
      setState((prev) => ({
        ...prev,
        isQuerying: false,
        queryError: message,
      }));
      throw error;
    }
  }, []);

  /**
   * Get cached report
   */
  const getReport = useCallback(async (contractId: string) => {
    try {
      const report = await getComplianceReport(contractId);
      setState((prev) => ({
        ...prev,
        complianceReport: report,
      }));
      return report;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to fetch report";
      setState((prev) => ({
        ...prev,
        verificationError: message,
      }));
      throw error;
    }
  }, []);

  /**
   * Reset state
   */
  const reset = useCallback(() => {
    setState(initialState);
  }, []);

  return {
    ...state,
    upload,
    verify,
    query,
    getReport,
    reset,
  };
}
