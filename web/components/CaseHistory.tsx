"use client";

import React from "react";
import Badge from "./ui/Badge";
import type { LegalIssue, IssueStatus } from "@/lib/types";

/** Maps issue status values to CSS color classes with glow effects for timeline dots. */
const statusColor: Record<IssueStatus, string> = {
  open: "bg-blue-500 shadow-[0_0_6px_rgba(59,130,246,0.4)]",
  resolved: "bg-green-500 shadow-[0_0_6px_rgba(34,197,94,0.4)]",
  watching: "bg-yellow-500 shadow-[0_0_6px_rgba(234,179,8,0.4)]",
  escalated: "bg-red-500 shadow-[0_0_6px_rgba(239,68,68,0.4)]",
};

/** Maps issue status values to Badge variant styles for the case history timeline. */
const statusVariant: Record<IssueStatus, "default" | "success" | "warning" | "error"> = {
  open: "default",
  resolved: "success",
  watching: "warning",
  escalated: "error",
};

/**
 * Props for the CaseHistory component.
 *
 * @property issues - Array of the user's active and past legal issues to display on the timeline
 */
interface CaseHistoryProps {
  issues: LegalIssue[];
}

/**
 * Vertical timeline displaying the user's active legal issues and case history.
 *
 * Each issue is shown as a card on a vertical timeline with color-coded status
 * dots (blue=open, green=resolved, yellow=watching, red=escalated), issue type,
 * summary, dates, and associated notes. Empty state shows "No active cases".
 *
 * @param props - Component props
 * @param props.issues - Array of legal issues from the user's profile
 */
export default function CaseHistory({ issues }: CaseHistoryProps) {
  if (issues.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-sm text-gray-500">No active cases</p>
      </div>
    );
  }

  return (
    <div className="relative">
      {/* Timeline line */}
      <div className="absolute left-3 top-0 bottom-0 w-px bg-white/10" />

      <ul className="space-y-4">
        {issues.map((issue: LegalIssue, i: number) => (
          <li key={i} className="relative pl-8">
            {/* Timeline dot */}
            <div
              className={`absolute left-1.5 top-1.5 w-3 h-3 rounded-full border-2 border-[#050505] ${statusColor[issue.status]}`}
            />

            <div className="bg-white/[0.03] backdrop-blur rounded-lg border border-white/10 p-4 hover:border-white/20 transition-colors">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-white capitalize">
                  {issue.issue_type.replace(/_/g, " ")}
                </span>
                <Badge variant={statusVariant[issue.status]} size="sm">
                  {issue.status}
                </Badge>
              </div>

              <p className="text-sm text-gray-400 mb-2">{issue.summary}</p>

              <div className="flex items-center gap-4 text-xs text-gray-500">
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
                <div className="mt-3 pt-3 border-t border-white/[0.06]">
                  <p className="text-xs font-medium text-gray-500 mb-1">
                    Notes
                  </p>
                  <ul className="space-y-1">
                    {issue.notes.map((note: string, j: number) => (
                      <li key={j} className="text-xs text-gray-400">
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
