"use client";

import React, { useState, useEffect } from "react";
import Badge from "./ui/Badge";
import type { LegalProfile, LegalIssue, IssueStatus } from "@/lib/types";
import { supabase } from "@/lib/supabase";

/** Maps issue status values to Badge variant styles for visual differentiation. */
const statusVariant: Record<IssueStatus, "default" | "success" | "warning" | "error"> = {
  open: "default",
  resolved: "success",
  watching: "warning",
  escalated: "error",
};

/**
 * Props for the LegalProfileSidebar component.
 *
 * @property profile - The user's complete legal profile including state, housing,
 *   employment, active issues, known facts, and uploaded documents
 */
interface LegalProfileSidebarProps {
  profile: LegalProfile;
}

/**
 * Persistent sidebar displaying the user's legal profile during chat.
 *
 * This sidebar is the visible proof that CaseMate has memory. It shows the user's
 * jurisdiction, housing/employment/family situation, active legal issues with
 * status badges, known legal facts extracted from conversations, and uploaded
 * documents. The "Memory Active" indicator confirms the profile is being injected
 * into every Claude API call.
 *
 * @param props - Component props
 * @param props.profile - The user's complete legal profile from Supabase
 */
export default function LegalProfileSidebar({ profile }: LegalProfileSidebarProps) {
  const [liveProfile, setLiveProfile] = useState<LegalProfile>(profile);
  const [memoryPulse, setMemoryPulse] = useState(false);

  // Sync prop changes
  useEffect(() => {
    setLiveProfile(profile);
  }, [profile]);

  // Subscribe to realtime profile updates
  useEffect(() => {
    const channel = supabase
      .channel(`profile:${profile.user_id}`)
      .on(
        "postgres_changes",
        {
          event: "UPDATE",
          schema: "public",
          table: "user_profiles",
          filter: `user_id=eq.${profile.user_id}`,
        },
        (payload) => {
          const newData = payload.new as Record<string, unknown>;
          setLiveProfile((prev) => ({ ...prev, ...newData } as LegalProfile));
          // Flash the memory indicator
          setMemoryPulse(true);
          setTimeout(() => setMemoryPulse(false), 2000);
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [profile.user_id]);

  return (
    <aside className="w-[300px] shrink-0 border-r border-white/10 bg-white/[0.02] h-full overflow-y-auto scrollbar-thin">
      <div className="p-4 space-y-6">
        {/* Header */}
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className={`w-2 h-2 bg-green-500 rounded-full shadow-[0_0_8px_rgba(34,197,94,0.4)] ${memoryPulse ? "animate-ping" : ""}`} />
            <span className={`text-xs font-medium ${memoryPulse ? "text-green-300" : "text-green-400"}`}>
              {memoryPulse ? "Memory Updated" : "Memory Active"}
            </span>
          </div>
          <h2 className="text-lg font-semibold text-white">
            {liveProfile.display_name}
          </h2>
          <span className="jurisdiction-badge">
            {liveProfile.state}
          </span>
        </div>

        {/* Your Situation */}
        <section>
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
            Your Situation
          </h3>
          <dl className="space-y-2 text-sm">
            <div>
              <dt className="text-gray-500">Housing</dt>
              <dd className="text-gray-300">{liveProfile.housing_situation}</dd>
            </div>
            <div>
              <dt className="text-gray-500">Employment</dt>
              <dd className="text-gray-300">{liveProfile.employment_type}</dd>
            </div>
            <div>
              <dt className="text-gray-500">Family</dt>
              <dd className="text-gray-300">{liveProfile.family_status}</dd>
            </div>
          </dl>
        </section>

        {/* Active Issues */}
        <section>
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
            Active Issues
          </h3>
          {liveProfile.active_issues.length === 0 ? (
            <p className="text-sm text-gray-500">No active issues</p>
          ) : (
            <ul className="space-y-2">
              {liveProfile.active_issues.map((issue: LegalIssue, i: number) => (
                <li
                  key={i}
                  className="p-2 bg-white/[0.03] rounded-lg border border-white/[0.06] hover:border-white/15 transition-colors"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-medium text-gray-300 capitalize">
                      {issue.issue_type.replace(/_/g, " ")}
                    </span>
                    <Badge variant={statusVariant[issue.status]} size="sm">
                      {issue.status}
                    </Badge>
                  </div>
                  <p className="text-xs text-gray-400 line-clamp-2">
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
          {liveProfile.legal_facts.length === 0 ? (
            <p className="text-sm text-gray-500">
              Facts will appear as you chat
            </p>
          ) : (
            <ul className="space-y-1">
              {liveProfile.legal_facts.map((fact: string, i: number) => (
                <li key={i} className="text-xs text-gray-400 flex gap-1.5">
                  <span className="text-gray-500 shrink-0">&#8226;</span>
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
          {liveProfile.documents.length === 0 ? (
            <p className="text-sm text-gray-500">No documents uploaded</p>
          ) : (
            <ul className="space-y-1">
              {liveProfile.documents.map((doc: string, i: number) => (
                <li
                  key={i}
                  className="text-xs text-gray-400 flex items-center gap-1.5"
                >
                  <svg
                    className="w-3.5 h-3.5 text-gray-500 shrink-0"
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
