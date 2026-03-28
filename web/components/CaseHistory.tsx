"use client";

import React from "react";
import Badge from "./ui/Badge";
import type { LegalIssue, IssueStatus } from "@/lib/types";

const statusColor: Record<IssueStatus, string> = {
  open: "bg-blue-500",
  resolved: "bg-green-500",
  watching: "bg-yellow-500",
  escalated: "bg-red-500",
};

const statusVariant: Record<IssueStatus, "default" | "success" | "warning" | "error"> = {
  open: "default",
  resolved: "success",
  watching: "warning",
  escalated: "error",
};

interface CaseHistoryProps {
  issues: LegalIssue[];
}

export default function CaseHistory({ issues }: CaseHistoryProps) {
  if (issues.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-sm text-gray-400">No active cases</p>
      </div>
    );
  }

  return (
    <div className="relative">
      {/* Timeline line */}
      <div className="absolute left-3 top-0 bottom-0 w-px bg-gray-200" />

      <ul className="space-y-4">
        {issues.map((issue, i) => (
          <li key={i} className="relative pl-8">
            {/* Timeline dot */}
            <div
              className={`absolute left-1.5 top-1.5 w-3 h-3 rounded-full border-2 border-white ${statusColor[issue.status]}`}
            />

            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-900 capitalize">
                  {issue.issue_type.replace(/_/g, " ")}
                </span>
                <Badge variant={statusVariant[issue.status]} size="sm">
                  {issue.status}
                </Badge>
              </div>

              <p className="text-sm text-gray-600 mb-2">{issue.summary}</p>

              <div className="flex items-center gap-4 text-xs text-gray-400">
                <span>
                  Started:{" "}
                  {new Date(issue.started_at).toLocaleDateString()}
                </span>
                <span>
                  Updated:{" "}
                  {new Date(issue.updated_at).toLocaleDateString()}
                </span>
              </div>

              {issue.notes.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-100">
                  <p className="text-xs font-medium text-gray-500 mb-1">
                    Notes
                  </p>
                  <ul className="space-y-1">
                    {issue.notes.map((note, j) => (
                      <li key={j} className="text-xs text-gray-600">
                        {note}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
