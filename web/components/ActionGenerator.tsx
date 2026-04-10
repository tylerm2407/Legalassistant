"use client";

import React, { useState } from "react";
import Button from "./ui/Button";
import { api } from "@/lib/api";
import type { DemandLetter, RightsSummary, Checklist } from "@/lib/types";
import { useTranslation } from "@/lib/i18n";
import { FileText, Scales, ListChecks, Copy, Check, CircleNotch, Warning } from "@phosphor-icons/react";

/** The three types of legal actions CaseMate can generate from the user's profile context. */
type ActionType = "letter" | "rights" | "checklist";

/** Union type for all possible action generation results. */
type ActionResult = DemandLetter | RightsSummary | Checklist;

/**
 * Props for the ActionGenerator component.
 *
 * @property userId - The authenticated user's Supabase ID, used to fetch their
 *   profile context when generating actions
 */
interface ActionGeneratorProps {
  userId: string;
}

/**
 * Action generator toolbar for creating demand letters, rights summaries, and checklists.
 *
 * This is the demo-critical feature. It uses the user's legal profile and conversation
 * context to generate three types of actionable legal documents via the backend API:
 * - Demand letters with legal citations and pre-filled recipient details
 * - Rights summaries listing the user's specific entitlements under their state law
 * - Legal checklists with deadlines and concrete next steps
 *
 * Each generated result includes a copy-to-clipboard button and appropriate disclaimers.
 *
 * @param props - Component props
 * @param props.userId - The authenticated user's Supabase ID
 */
export default function ActionGenerator({ userId }: ActionGeneratorProps) {
  const [activeAction, setActiveAction] = useState<ActionType | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ActionResult | null>(null);
  const [resultType, setResultType] = useState<ActionType | null>(null);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);
  const { t } = useTranslation();

  async function handleGenerate(action: ActionType) {
    setLoading(true);
    setActiveAction(action);
    setResult(null);
    setResultType(null);
    setError("");

    try {
      let data: ActionResult;
      switch (action) {
        case "letter":
          data = await api.generateLetter(userId);
          break;
        case "rights":
          data = await api.generateRights(userId);
          break;
        case "checklist":
          data = await api.generateChecklist(userId);
          break;
      }
      setResult(data);
      setResultType(action);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "We couldn't generate that right now. Let's try again."
      );
    } finally {
      setLoading(false);
      setActiveAction(null);
    }
  }

  function getTextContent(): string {
    if (!result || !resultType) return "";
    switch (resultType) {
      case "letter":
        return (result as DemandLetter).letter_text;
      case "rights":
        return (result as RightsSummary).summary_text;
      case "checklist":
        return (result as Checklist).items.join("\n");
    }
  }

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(getTextContent());
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback: ignored
    }
  }

  function renderResult() {
    if (!result || !resultType) return null;

    switch (resultType) {
      case "letter": {
        const letter = result as DemandLetter;
        return (
          <div className="bg-white border border-border rounded-lg p-6 mt-3">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-serif font-medium tracking-tight text-ink-primary text-lg">
                {t("demandLetter")}
              </h3>
              <button
                onClick={handleCopy}
                className="flex items-center gap-1.5 text-sm text-ink-secondary hover:text-ink-primary transition-colors"
              >
                {copied ? (
                  <>
                    <Check className="w-4 h-4" weight="regular" />
                    {t("copied")}
                  </>
                ) : (
                  <>
                    <Copy className="w-4 h-4" weight="regular" />
                    {t("copy")}
                  </>
                )}
              </button>
            </div>
            <pre className="text-sm text-ink-primary whitespace-pre-wrap font-sans leading-relaxed">
              {letter.letter_text}
            </pre>
            {letter.legal_citations.length > 0 && (
              <div className="mt-5 pt-4 border-t border-border">
                <p className="text-xs font-sans font-medium text-ink-tertiary uppercase tracking-wider mb-2">
                  {t("legalCitations")}
                </p>
                <ul className="space-y-1">
                  {letter.legal_citations.map((cite: string, i: number) => (
                    <li key={i} className="font-mono text-sm text-ink-secondary">
                      {cite}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            <p className="mt-4 text-xs text-ink-tertiary leading-relaxed">
              {t("aiDisclaimer")}
            </p>
          </div>
        );
      }

      case "rights": {
        const rights = result as RightsSummary;
        return (
          <div className="bg-white border border-border rounded-lg p-6 mt-3">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-serif font-medium tracking-tight text-ink-primary text-lg">
                {t("rightsSummary")}
              </h3>
              <button
                onClick={handleCopy}
                className="flex items-center gap-1.5 text-sm text-ink-secondary hover:text-ink-primary transition-colors"
              >
                {copied ? (
                  <>
                    <Check className="w-4 h-4" weight="regular" />
                    {t("copied")}
                  </>
                ) : (
                  <>
                    <Copy className="w-4 h-4" weight="regular" />
                    {t("copy")}
                  </>
                )}
              </button>
            </div>
            <p className="text-sm text-ink-primary leading-relaxed mb-4">
              {rights.summary_text}
            </p>
            {rights.key_rights.length > 0 && (
              <div>
                <p className="text-xs font-sans font-medium text-ink-tertiary uppercase tracking-wider mb-2">
                  {t("keyRights")}
                </p>
                <ul className="space-y-2">
                  {rights.key_rights.map((right: string, i: number) => (
                    <li
                      key={i}
                      className="text-sm text-ink-primary flex gap-2"
                    >
                      <Check className="w-4 h-4 text-accent shrink-0 mt-0.5" weight="regular" />
                      <span>{right}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            <p className="mt-4 text-xs text-ink-tertiary leading-relaxed">
              {t("aiDisclaimer")}
            </p>
          </div>
        );
      }

      case "checklist": {
        const checklist = result as Checklist;
        return (
          <div className="bg-white border border-border rounded-lg p-6 mt-3">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-serif font-medium tracking-tight text-ink-primary text-lg">
                {t("legalChecklist")}
              </h3>
              <button
                onClick={handleCopy}
                className="flex items-center gap-1.5 text-sm text-ink-secondary hover:text-ink-primary transition-colors"
              >
                {copied ? (
                  <>
                    <Check className="w-4 h-4" weight="regular" />
                    {t("copied")}
                  </>
                ) : (
                  <>
                    <Copy className="w-4 h-4" weight="regular" />
                    {t("copy")}
                  </>
                )}
              </button>
            </div>
            <ul className="space-y-3">
              {checklist.items.map((item: string, i: number) => (
                <li key={i} className="flex items-start gap-3 text-sm">
                  <input
                    type="checkbox"
                    className="mt-0.5 rounded border-border bg-white text-accent focus:ring-accent/20 accent-accent"
                  />
                  <div>
                    <span className="text-ink-primary">{item}</span>
                    {checklist.deadlines[i] && (
                      <span className="block text-xs text-warning mt-1">
                        {t("deadline")}: {checklist.deadlines[i]}
                      </span>
                    )}
                  </div>
                </li>
              ))}
            </ul>
            <p className="mt-4 text-xs text-ink-tertiary leading-relaxed">
              {t("aiDisclaimer")}
            </p>
          </div>
        );
      }
    }
  }

  const actionButton = (action: ActionType, label: string, Icon: typeof FileText) => {
    const isActive = loading && activeAction === action;
    return (
      <button
        onClick={() => handleGenerate(action)}
        disabled={loading}
        className="flex items-center gap-2 px-4 py-2 text-sm font-sans font-medium text-ink-primary bg-white border border-border-strong rounded-md hover:bg-bg-hover transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isActive ? (
          <>
            <CircleNotch className="w-4 h-4 animate-spin" weight="regular" />
            Working on it
          </>
        ) : (
          <>
            <Icon className="w-4 h-4 text-ink-secondary" weight="regular" />
            {label}
          </>
        )}
      </button>
    );
  };

  return (
    <div className="bg-bg border-t border-border px-6 py-4 shrink-0">
      {/* Action buttons */}
      <div className="flex items-center gap-2 flex-wrap mb-2">
        <span className="text-sm font-sans text-ink-secondary mr-1">{t("actions")}</span>
        {actionButton("letter", t("generateLetter"), FileText)}
        {actionButton("rights", t("rightsSummary"), Scales)}
        {actionButton("checklist", t("checklist"), ListChecks)}
      </div>

      {error && (
        <div className="mt-3 flex items-start gap-2 bg-warning-subtle border border-warning/30 rounded-md p-3">
          <Warning className="w-4 h-4 text-warning shrink-0 mt-0.5" weight="regular" />
          <p className="text-sm text-warning">{error}</p>
        </div>
      )}

      {result && <div className="max-h-72 overflow-y-auto">{renderResult()}</div>}
    </div>
  );
}
