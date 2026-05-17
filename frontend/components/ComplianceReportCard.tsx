/**
 * Component for displaying compliance report
 */

import React from "react";
import { ComplianceReport, ComplianceIssue } from "@/lib/api";
import { CheckCircle, AlertTriangle, AlertCircle, Info, Lightbulb } from "lucide-react";

interface ComplianceReportCardProps {
  report: ComplianceReport;
  onQueryChange?: (question: string) => void;
}

const SeverityBadge: React.FC<{ severity: string }> = ({ severity }) => {
  const colors: Record<string, { bg: string; text: string; border: string }> = {
    critical: { bg: "bg-red-900", text: "text-red-200", border: "border-red-700" },
    high: { bg: "bg-orange-900", text: "text-orange-200", border: "border-orange-700" },
    medium: {
      bg: "bg-yellow-900",
      text: "text-yellow-200",
      border: "border-yellow-700",
    },
    low: { bg: "bg-blue-900", text: "text-blue-200", border: "border-blue-700" },
    info: { bg: "bg-cyan-900", text: "text-cyan-200", border: "border-cyan-700" },
  };

  const style = colors[severity] || colors.info;

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${style.bg} ${style.text} ${style.border}`}
    >
      {severity.charAt(0).toUpperCase() + severity.slice(1)}
    </span>
  );
};

const StatusIcon: React.FC<{ status: string }> = ({ status }) => {
  switch (status) {
    case "compliant":
      return <CheckCircle className="w-5 h-5 text-green-400" />;
    case "partially_compliant":
      return <AlertTriangle className="w-5 h-5 text-yellow-400" />;
    case "non_compliant":
      return <AlertCircle className="w-5 h-5 text-red-400" />;
    default:
      return <Info className="w-5 h-5 text-gray-400" />;
  }
};

const StatusText: React.FC<{ status: string }> = ({ status }) => {
  const texts: Record<string, string> = {
    compliant: "Compliant",
    partially_compliant: "Partially Compliant",
    non_compliant: "Non-Compliant",
  };
  return <>{texts[status] || "Unknown"}</>;
};

export const ComplianceReportCard: React.FC<ComplianceReportCardProps> = ({
  report,
  onQueryChange,
}) => {
  const scorePercentage = Math.round(report.compliance_score);
  const scoreColor =
    scorePercentage >= 90
      ? "text-green-400"
      : scorePercentage >= 70
      ? "text-yellow-400"
      : "text-red-400";

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-6">
      {/* Header with Status */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <StatusIcon status={report.overall_status} />
            <div>
              <h3 className="text-lg font-semibold text-white">
                Compliance Report
              </h3>
              <p className="text-sm text-gray-400">
                {report.document_type} · {new Date(report.analysis_date).toLocaleDateString()}
              </p>
            </div>
          </div>
          <SeverityBadge severity={report.overall_status.split("_")[0]} />
        </div>

        {/* Compliance Score */}
        <div className="bg-gray-800 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400">Overall Score</span>
            <span className={`text-3xl font-bold ${scoreColor}`}>
              {scorePercentage}%
            </span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all ${
                scorePercentage >= 90
                  ? "bg-green-500"
                  : scorePercentage >= 70
                  ? "bg-yellow-500"
                  : "bg-red-500"
              }`}
              style={{ width: `${scorePercentage}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-400 mt-2">
            <StatusText status={report.overall_status} />
          </p>
        </div>
      </div>

      {/* Summary */}
      <div className="bg-gray-800 rounded-lg p-4 border-l-4 border-blue-500">
        <p className="text-gray-200">{report.summary}</p>
      </div>

      {/* Issues Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="bg-gray-800 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-gray-200">
            {report.total_issues}
          </div>
          <div className="text-xs text-gray-400 mt-1">Total Issues</div>
        </div>
        {report.critical_issues > 0 && (
          <div className="bg-red-900 bg-opacity-30 rounded-lg p-3 text-center border border-red-800">
            <div className="text-2xl font-bold text-red-400">
              {report.critical_issues}
            </div>
            <div className="text-xs text-red-300 mt-1">Critical</div>
          </div>
        )}
        {report.high_issues > 0 && (
          <div className="bg-orange-900 bg-opacity-30 rounded-lg p-3 text-center border border-orange-800">
            <div className="text-2xl font-bold text-orange-400">
              {report.high_issues}
            </div>
            <div className="text-xs text-orange-300 mt-1">High</div>
          </div>
        )}
      </div>

      {/* Issues List */}
      {report.issues.length > 0 && (
        <div className="space-y-3">
          <h4 className="font-semibold text-gray-200">Issues Found</h4>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {report.issues.slice(0, 5).map((issue, idx) => (
              <div
                key={idx}
                className="bg-gray-800 rounded-lg p-3 border-l-4 border-gray-700 hover:border-gray-600 transition-colors"
              >
                <div className="flex items-start gap-3">
                  <SeverityBadge severity={issue.severity} />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-200">
                      {issue.issue_type}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      {issue.description}
                    </p>
                    {issue.legal_reference && (
                      <p className="text-xs text-blue-400 mt-2">
                        Reference: {issue.legal_reference}
                      </p>
                    )}
                    <p className="text-xs text-gray-500 mt-2 italic">
                      💡 {issue.recommendation}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
          {report.issues.length > 5 && (
            <p className="text-xs text-gray-500 text-center">
              +{report.issues.length - 5} more issues
            </p>
          )}
        </div>
      )}

      {/* Recommendations */}
      {report.recommendations.length > 0 && (
        <div className="bg-blue-900 bg-opacity-20 rounded-lg p-4 border border-blue-800 space-y-2">
          <div className="flex items-center gap-2">
            <Lightbulb className="w-4 h-4 text-blue-400" />
            <h4 className="font-semibold text-blue-300">Recommendations</h4>
          </div>
          <ul className="space-y-1">
            {report.recommendations.slice(0, 3).map((rec, idx) => (
              <li key={idx} className="text-sm text-blue-200 flex items-start gap-2">
                <span className="text-blue-400 mt-1">•</span>
                <span>{rec}</span>
              </li>
            ))}
          </ul>
          {report.recommendations.length > 3 && (
            <p className="text-xs text-blue-400 mt-2">
              +{report.recommendations.length - 3} more recommendations
            </p>
          )}
        </div>
      )}

      {/* Quick Questions */}
      <div className="bg-gray-800 rounded-lg p-4 space-y-3">
        <h4 className="font-semibold text-gray-200 text-sm">Quick Questions</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {[
            "What are the missing clauses?",
            "What needs to be fixed?",
            "Is this compliant?",
            "What are the critical issues?",
          ].map((question) => (
            <button
              key={question}
              onClick={() => onQueryChange?.(question)}
              className="text-left text-xs px-3 py-2 rounded bg-gray-700 hover:bg-gray-600 text-gray-300 transition-colors"
            >
              {question}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
