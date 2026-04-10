"use client";

import React from "react";
import type { LegalIssue, IssueStatus } from "@/lib/types";

/** Maps issue status values to dot color classes for the timeline. */
const statusDot: Record<IssueStatus, string> = {
  open: "bg-accent",
  resolved: "bg-accent",
  watching: "bg-ink-tertiary",
  escalated: "bg-warning",
};

/** Maps issue status values to pill label classes. */
const statusPill: Record<IssueStatus, string> = {
  open: "text-accent bg-accent-subtle border-accent/20",
  resolved: "text-accent bg-accent-subtle border-accent/20",
  watching: "text-ink-secondary bg-bg border-border",
  escalated: "text-warning bg-warning-subtle border-warning/30",
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
 * Each issue is shown as a card on a vertical timeline with status
 * pills, issue type, summary, dates, and associated notes. Empty state shows
 * a friendly message when there are no active cases.
 *
 * @param props - Component props
 * @param props.issues - Array of legal issues from the user's profile
 */
export default function CaseHistory({ issues }: CaseHistoryProps) {
  if (issues.length === 0) {
    return (
      <div className="text-center py-10">
        <p className="text-sm font-sans text-ink-tertiary">
          You don't have any active cases yet.
        </p>
      </div>
    );
  }

  return (
    <div className="relative">
      {/* Timeline line */}
      <div className="absolute left-[7px] top-2 bottom-2 w-px bg-border" />

      <ul className="space-y-4">
        {issues.map((issue: LegalIssue, i: number) => (
          <li key={i} className="relative pl-8">
            {/* Timeline dot */}
            <div
              className={`absolute left-0 top-2 w-[15px] h-[15px] rounded-full border-2 border-bg ${statusDot[issue.status]}`}
            />

            <div className="bg-white border border-border rounded-lg p-6 hover:border-border-strong transition-colors">
              <div className="flex items-center justify-between gap-3 mb-3">
                <span className="font-serif font-medium tracking-tight text-ink-primary text-base capitalize">
                  {issue.issue_type.replace(/_/g, " ")}
                </span>
                <span
                  className={`inline-flex items-center text-xs font-sans font-medium border rounded-md px-2 py-0.5 capitalize ${statusPill[issue.status]}`}
                >
                  {issue.status}
                </span>
              </div>

              <p className="text-sm font-sans text-ink-secondary leading-relaxed mb-3">
                {issue.summary}
              </p>

              <div className="flex items-center gap-4 text-xs font-sans text-ink-tertiary flex-wrap">
                <span>
                  Started {new Date(issue.started_at).toLocaleDateString()}
                </span>
                <span>
                  Updated {new Date(issue.updated_at).toLocaleDateString()}
                </span>
              </div>

              {issue.notes.length > 0 && (
                <div className="mt-4 pt-4 border-t border-border">
                  <p className="text-xs font-sans font-medium text-ink-tertiary uppercase tracking-wider mb-2">
                    Notes
                  </p>
                  <ul className="space-y-1.5">
                    {issue.notes.map((note: string, j: number) => (
                      <li key={j} className="text-sm font-sans text-ink-secondary">
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
