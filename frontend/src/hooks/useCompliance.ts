import { useState, useCallback } from 'react';
import axios from 'axios';
import { ComplianceReport, ContractUploadResponse, ProcessingStatus } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface UseComplianceReturn {
  loading: boolean;
  error: string | null;
  report: ComplianceReport | null;
  status: ProcessingStatus | null;
  uploadContract: (file: File, documentType: string) => Promise<ContractUploadResponse>;
  verifyCompliance: (contractId: string) => Promise<ComplianceReport>;
  getComplianceReport: (contractId: string) => Promise<ComplianceReport>;
  queryCompliance: (contractId: string, question: string) => Promise<string>;
}

export const useCompliance = (): UseComplianceReturn => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<ComplianceReport | null>(null);
  const [status, setStatus] = useState<ProcessingStatus | null>(null);

  const uploadContract = useCallback(
    async (file: File, documentType: string): Promise<ContractUploadResponse> => {
      setLoading(true);
      setError(null);

      try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await axios.post<ContractUploadResponse>(
          `${API_URL}/api/v1/contracts/upload`,
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          }
        );

        return response.data;
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Upload failed';
        setError(errorMsg);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const verifyCompliance = useCallback(
    async (contractId: string): Promise<ComplianceReport> => {
      setLoading(true);
      setError(null);

      try {
        const response = await axios.post<ComplianceReport>(
          `${API_URL}/api/v1/compliance/verify/${contractId}`
        );

        setReport(response.data);
        return response.data;
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Verification failed';
        setError(errorMsg);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const getComplianceReport = useCallback(
    async (contractId: string): Promise<ComplianceReport> => {
      setLoading(true);
      setError(null);

      try {
        const response = await axios.get<ComplianceReport>(
          `${API_URL}/api/v1/compliance/${contractId}`
        );

        setReport(response.data);
        return response.data;
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Failed to fetch report';
        setError(errorMsg);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const queryCompliance = useCallback(
    async (contractId: string, question: string): Promise<string> => {
      setLoading(true);
      setError(null);

      try {
        const response = await axios.post(
          `${API_URL}/api/v1/compliance/${contractId}/query`,
          { question }
        );

        return response.data.answer;
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Query failed';
        setError(errorMsg);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return {
    loading,
    error,
    report,
    status,
    uploadContract,
    verifyCompliance,
    getComplianceReport,
    queryCompliance,
  };
};
