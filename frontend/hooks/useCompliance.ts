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
} from "@/lib/api";

export interface ComplianceState {
  loading: boolean;
  error?: string;
  report?: ComplianceReport;
}

const initialState: ComplianceState = {
  loading: false,
};

export function useCompliance() {
  const [state, setState] = useState<ComplianceState>(initialState);

  /**
   * Upload a contract file
   */
  const uploadContract_ = useCallback(async (file: File) => {
    setState((prev) => ({
      ...prev,
      loading: true,
      error: undefined,
    }));

    try {
      const result = await uploadContract(file);
      setState((prev) => ({
        ...prev,
        loading: false,
      }));
      return result;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Upload failed";
      setState((prev) => ({
        ...prev,
        loading: false,
        error: message,
      }));
      throw error;
    }
  }, []);

  /**
   * Verify contract compliance
   */
  const verifyCompliance_ = useCallback(async (contractId: string) => {
    setState((prev) => ({
      ...prev,
      loading: true,
      error: undefined,
    }));

    try {
      const report = await verifyCompliance(contractId);

      setState((prev) => ({
        ...prev,
        loading: false,
        report: report,
      }));

      return report;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Verification failed";
      setState((prev) => ({
        ...prev,
        loading: false,
        error: message,
      }));
      throw error;
    }
  }, []);

  /**
   * Query compliance findings - returns just the answer text
   */
  const queryCompliance_ = useCallback(async (contractId: string, question: string) => {
    setState((prev) => ({
      ...prev,
      loading: true,
      error: undefined,
    }));

    try {
      const response = await queryCompliance(contractId, question);

      setState((prev) => ({
        ...prev,
        loading: false,
      }));

      // Return just the answer text
      return response.answer;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Query failed";
      setState((prev) => ({
        ...prev,
        loading: false,
        error: message,
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
        report: report,
      }));
      return report;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to fetch report";
      setState((prev) => ({
        ...prev,
        error: message,
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
    loading: state.loading,
    error: state.error,
    report: state.report,
    uploadContract: uploadContract_,
    verifyCompliance: verifyCompliance_,
    queryCompliance: queryCompliance_,
    getReport,
    reset,
  };
}
