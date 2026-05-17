import React from 'react';
import { ComplianceReport, SeverityLevel } from '@/types';
import clsx from 'clsx';

interface ResultsDisplayProps {
  report: ComplianceReport | null;
  loading?: boolean;
}

const getSeverityColor = (severity: SeverityLevel) => {
  const colors: Record<SeverityLevel, string> = {
    critical: 'bg-red-100 text-red-800 border-red-300',
    high: 'bg-orange-100 text-orange-800 border-orange-300',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    low: 'bg-blue-100 text-blue-800 border-blue-300',
    info: 'bg-gray-100 text-gray-800 border-gray-300',
  };
  return colors[severity];
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'compliant':
      return 'text-green-700 bg-green-50';
    case 'non_compliant':
      return 'text-red-700 bg-red-50';
    case 'partially_compliant':
      return 'text-yellow-700 bg-yellow-50';
    default:
      return 'text-gray-700 bg-gray-50';
  }
};

export const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ report, loading }) => {
  if (loading) {
    return (
      <div className="space-y-4">
        <div className="animate-pulse space-y-4">
          <div className="h-32 bg-gray-200 rounded-lg"></div>
          <div className="h-64 bg-gray-200 rounded-lg"></div>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p>No compliance report available. Upload and verify a contract to see results.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <div className={clsx('rounded-lg p-6 border', getStatusColor(report.overall_status))}>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <p className="text-sm font-medium opacity-75 mb-1">Overall Status</p>
            <p className="text-2xl font-bold capitalize">{report.overall_status.replace('_', ' ')}</p>
          </div>
          <div>
            <p className="text-sm font-medium opacity-75 mb-1">Compliance Score</p>
            <p className="text-2xl font-bold">{report.compliance_score.toFixed(1)}%</p>
          </div>
          <div>
            <p className="text-sm font-medium opacity-75 mb-1">Total Issues</p>
            <p className="text-2xl font-bold">{report.total_issues}</p>
          </div>
        </div>
      </div>

      {/* Issues Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-700 font-medium mb-1">Critical Issues</p>
          <p className="text-3xl font-bold text-red-700">{report.critical_issues}</p>
        </div>
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <p className="text-sm text-orange-700 font-medium mb-1">High Issues</p>
          <p className="text-3xl font-bold text-orange-700">{report.high_issues}</p>
        </div>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-700 font-medium mb-1">Other Issues</p>
          <p className="text-3xl font-bold text-blue-700">
            {report.total_issues - report.critical_issues - report.high_issues}
          </p>
        </div>
      </div>

      {/* Summary Text */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
        <h3 className="font-semibold text-gray-900 mb-2">Summary</h3>
        <p className="text-gray-700">{report.summary}</p>
      </div>

      {/* Issues List */}
      {report.issues.length > 0 && (
        <div className="space-y-4">
          <h3 className="font-semibold text-gray-900">Detected Issues</h3>
          <div className="space-y-3">
            {report.issues.map((issue) => (
              <div
                key={issue.issue_id}
                className={clsx('border rounded-lg p-4', getSeverityColor(issue.severity))}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="inline-block px-2 py-1 rounded text-xs font-semibold bg-opacity-30">
                        {issue.severity.toUpperCase()}
                      </span>
                      <span className="text-sm font-medium">{issue.clause_reference}</span>
                    </div>
                    <p className="font-medium text-base mb-1">{issue.issue_type.replace(/_/g, ' ')}</p>
                  </div>
                </div>
                <p className="text-sm mb-2">{issue.description}</p>
                <div className="bg-white bg-opacity-50 rounded p-2 mb-2 text-sm">
                  <p className="font-medium">Legal Reference:</p>
                  <p className="text-xs opacity-75">{issue.legal_reference}</p>
                </div>
                <div className="text-sm">
                  <p className="font-medium mb-1">Recommendation:</p>
                  <p>{issue.recommendation}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {report.recommendations.length > 0 && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Key Recommendations</h3>
          <ul className="space-y-2">
            {report.recommendations.map((rec, idx) => (
              <li key={idx} className="flex items-start gap-2 text-gray-700">
                <svg
                  className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
