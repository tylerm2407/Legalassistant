"use client";

import React from "react";
import Badge from "./ui/Badge";
import type { LegalProfile, IssueStatus } from "@/lib/types";

const statusVariant: Record<IssueStatus, "default" | "success" | "warning" | "error"> = {
  open: "default",
  resolved: "success",
  watching: "warning",
  escalated: "error",
};

interface LegalProfileSidebarProps {
  profile: LegalProfile;
}

export default function LegalProfileSidebar({ profile }: LegalProfileSidebarProps) {
  return (
    <aside className="w-[300px] shrink-0 border-r border-gray-200 bg-white h-full overflow-y-auto scrollbar-thin">
      <div className="p-4 space-y-6">
        {/* Header */}
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2 h-2 bg-green-500 rounded-full" />
            <span className="text-xs text-green-600 font-medium">
              Memory Active
            </span>
          </div>
          <h2 className="text-lg font-semibold text-gray-900">
            {profile.display_name}
          </h2>
          <Badge variant="default" size="sm">
            {profile.state}
          </Badge>
        </div>

        {/* Your Situation */}
        <section>
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
            Your Situation
          </h3>
          <dl className="space-y-2 text-sm">
            <div>
              <dt className="text-gray-500">Housing</dt>
              <dd className="text-gray-800">{profile.housing_situation}</dd>
            </div>
            <div>
              <dt className="text-gray-500">Employment</dt>
              <dd className="text-gray-800">{profile.employment_type}</dd>
            </div>
            <div>
              <dt className="text-gray-500">Family</dt>
              <dd className="text-gray-800">{profile.family_status}</dd>
            </div>
          </dl>
        </section>

        {/* Active Issues */}
        <section>
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
            Active Issues
          </h3>
          {profile.active_issues.length === 0 ? (
            <p className="text-sm text-gray-400">No active issues</p>
          ) : (
            <ul className="space-y-2">
              {profile.active_issues.map((issue, i) => (
                <li
                  key={i}
                  className="p-2 bg-gray-50 rounded-lg border border-gray-100"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-medium text-gray-700 capitalize">
                      {issue.issue_type.replace(/_/g, " ")}
                    </span>
                    <Badge variant={statusVariant[issue.status]} size="sm">
                      {issue.status}
                    </Badge>
                  </div>
                  <p className="text-xs text-gray-600 line-clamp-2">
                    {issue.summary}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* Known Facts */}
        <section>
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
            Known Facts
          </h3>
          {profile.legal_facts.length === 0 ? (
            <p className="text-sm text-gray-400">
              Facts will appear as you chat
            </p>
          ) : (
            <ul className="space-y-1">
              {profile.legal_facts.map((fact, i) => (
                <li key={i} className="text-xs text-gray-600 flex gap-1.5">
                  <span className="text-gray-400 shrink-0">&#8226;</span>
                  {fact}
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* Documents */}
        <section>
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
            Documents
          </h3>
          {profile.documents.length === 0 ? (
            <p className="text-sm text-gray-400">No documents uploaded</p>
          ) : (
            <ul className="space-y-1">
              {profile.documents.map((doc, i) => (
                <li
                  key={i}
                  className="text-xs text-gray-600 flex items-center gap-1.5"
                >
                  <svg
                    className="w-3.5 h-3.5 text-gray-400 shrink-0"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={2}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                    />
                  </svg>
                  {doc}
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </aside>
  );
}
