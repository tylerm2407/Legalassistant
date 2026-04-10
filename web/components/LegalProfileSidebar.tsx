"use client";

import React, { useState, useEffect, useCallback } from "react";
import { File } from "@phosphor-icons/react";
import Badge from "./ui/Badge";
import type { LegalProfile, LegalIssue, IssueStatus } from "@/lib/types";
import { supabase } from "@/lib/supabase";
import { api } from "@/lib/api";
import { useTranslation } from "@/lib/i18n";
import type { Locale } from "@/lib/i18n";

/** Maps issue status values to Badge variant styles for visual differentiation. */
const statusVariant: Record<IssueStatus, "default" | "success" | "warning"> = {
  open: "default",
  resolved: "success",
  watching: "warning",
  escalated: "warning",
};

interface LegalProfileSidebarProps {
  profile: LegalProfile;
}

/**
 * Persistent sidebar displaying the user's legal profile during chat.
 *
 * This sidebar is the visible proof that CaseMate has memory. It shows the user's
 * jurisdiction, housing/employment/family situation, active legal issues with
 * status badges, known legal facts extracted from conversations, and uploaded
 * documents. The "Memory active" indicator confirms the profile is being injected
 * into every Claude API call.
 */
export default function LegalProfileSidebar({ profile }: LegalProfileSidebarProps) {
  const [liveProfile, setLiveProfile] = useState<LegalProfile>(profile);
  const [memoryPulse, setMemoryPulse] = useState(false);
  const { t, setLocale } = useTranslation();

  const toggleLanguage = useCallback(async () => {
    const newLang: Locale = liveProfile.language_preference === "es" ? "en" : "es";
    setLiveProfile((prev) => ({ ...prev, language_preference: newLang }));
    setLocale(newLang);
    try {
      await api.updateProfile({ language_preference: newLang });
    } catch {
      const reverted: Locale = newLang === "es" ? "en" : "es";
      setLiveProfile((prev) => ({
        ...prev,
        language_preference: reverted,
      }));
      setLocale(reverted);
    }
  }, [liveProfile.language_preference, setLocale]);

  useEffect(() => {
    setLiveProfile(profile);
  }, [profile]);

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
    <aside className="w-[300px] shrink-0 border-r border-border bg-bg h-full overflow-y-auto scrollbar-thin">
      <div className="p-6 space-y-8">
        {/* Header */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span
              className={`w-1.5 h-1.5 bg-accent rounded-full ${
                memoryPulse ? "animate-ping" : ""
              }`}
            />
            <span className="text-xs font-sans font-medium text-accent uppercase tracking-wider">
              {memoryPulse ? t("memoryUpdated") : t("memoryActive")}
            </span>
          </div>
          <h2 className="font-serif text-2xl font-medium text-ink-primary leading-tight">
            {liveProfile.display_name}
          </h2>
          <p className="mt-1 text-sm font-mono text-ink-secondary">
            {liveProfile.state}
          </p>
          {/* Language toggle */}
          <div className="flex items-center mt-3">
            <button
              type="button"
              onClick={toggleLanguage}
              className={`px-3 py-1 text-xs font-sans font-medium rounded-l-md border transition-colors ${
                liveProfile.language_preference === "en"
                  ? "bg-accent-subtle border-accent/30 text-accent"
                  : "bg-white border-border text-ink-tertiary hover:text-ink-secondary"
              }`}
            >
              EN
            </button>
            <button
              type="button"
              onClick={toggleLanguage}
              className={`px-3 py-1 text-xs font-sans font-medium rounded-r-md border-y border-r transition-colors ${
                liveProfile.language_preference === "es"
                  ? "bg-accent-subtle border-accent/30 text-accent"
                  : "bg-white border-border text-ink-tertiary hover:text-ink-secondary"
              }`}
            >
              ES
            </button>
          </div>
        </div>

        {/* Your Situation */}
        <section>
          <h3 className="text-xs font-sans font-medium text-ink-tertiary uppercase tracking-wider mb-3">
            {t("yourSituation")}
          </h3>
          <dl className="space-y-3 text-sm font-sans">
            <div>
              <dt className="text-ink-tertiary text-xs uppercase tracking-wider mb-0.5">{t("housing")}</dt>
              <dd className="text-ink-primary">{liveProfile.housing_situation}</dd>
            </div>
            <div>
              <dt className="text-ink-tertiary text-xs uppercase tracking-wider mb-0.5">{t("employment")}</dt>
              <dd className="text-ink-primary">{liveProfile.employment_type}</dd>
            </div>
            <div>
              <dt className="text-ink-tertiary text-xs uppercase tracking-wider mb-0.5">{t("family")}</dt>
              <dd className="text-ink-primary">{liveProfile.family_status}</dd>
            </div>
          </dl>
        </section>

        {/* Active Issues */}
        <section>
          <h3 className="text-xs font-sans font-medium text-ink-tertiary uppercase tracking-wider mb-3">
            {t("activeIssues")}
          </h3>
          {liveProfile.active_issues.length === 0 ? (
            <p className="text-sm font-sans text-ink-tertiary">{t("noActiveIssues")}</p>
          ) : (
            <ul className="space-y-3">
              {liveProfile.active_issues.map((issue: LegalIssue, i: number) => (
                <li
                  key={i}
                  className="p-3 bg-white border border-border rounded-md"
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-sm font-sans font-medium text-ink-primary capitalize">
                      {issue.issue_type.replace(/_/g, " ")}
                    </span>
                    <Badge variant={statusVariant[issue.status]} size="sm">
                      {issue.status}
                    </Badge>
                  </div>
                  <p className="text-sm font-sans text-ink-secondary leading-snug">
                    {issue.summary}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* Known Facts */}
        <section>
          <h3 className="text-xs font-sans font-medium text-ink-tertiary uppercase tracking-wider mb-3">
            {t("knownFacts")}
          </h3>
          {liveProfile.legal_facts.length === 0 ? (
            <p className="text-sm font-sans text-ink-tertiary leading-snug">
              {t("factsWillAppear")}
            </p>
          ) : (
            <ul className="space-y-2">
              {liveProfile.legal_facts.map((fact: string, i: number) => (
                <li
                  key={i}
                  className="text-sm font-sans text-ink-secondary flex gap-2 leading-snug"
                >
                  <span className="text-ink-tertiary shrink-0">—</span>
                  <span>{fact}</span>
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* Documents */}
        <section>
          <h3 className="text-xs font-sans font-medium text-ink-tertiary uppercase tracking-wider mb-3">
            {t("documents")}
          </h3>
          {liveProfile.documents.length === 0 ? (
            <p className="text-sm font-sans text-ink-tertiary">{t("noDocumentsUploaded")}</p>
          ) : (
            <ul className="space-y-2">
              {liveProfile.documents.map((doc: string, i: number) => (
                <li
                  key={i}
                  className="text-sm font-sans text-ink-secondary flex items-center gap-2"
                >
                  <File className="w-4 h-4 text-ink-tertiary shrink-0" weight="regular" />
                  <span>{doc}</span>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </aside>
  );
}
