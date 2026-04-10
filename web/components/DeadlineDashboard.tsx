"use client";

import React, { useEffect, useState } from "react";
import Button from "./ui/Button";
import { api } from "@/lib/api";
import { useTranslation } from "@/lib/i18n";
import translations from "@/lib/i18n/translations";
import { Plus, Check, X, CircleNotch, Warning, Clock } from "@phosphor-icons/react";

/**
 * Local representation of a legal deadline for the dashboard UI.
 *
 * @property id - Unique deadline identifier from Supabase
 * @property title - Short description of the deadline (e.g., "File small claims motion")
 * @property date - ISO date string for the deadline date
 * @property legal_area - Optional legal domain category (e.g., "landlord_tenant")
 * @property status - Current status: "active", "completed", or "dismissed"
 * @property notes - Optional user or AI-generated notes about the deadline
 */
interface Deadline {
  id: string;
  title: string;
  date: string;
  legal_area: string | null;
  status: string;
  notes: string;
}

/**
 * Dashboard for tracking legal deadlines and statutes of limitations.
 *
 * Displays active deadlines with urgency indicators, allows manual deadline
 * creation, and supports marking deadlines as completed or dismissed.
 * Deadlines can also be auto-detected from chat conversations by the backend.
 */
export default function DeadlineDashboard() {
  const [deadlines, setDeadlines] = useState<Deadline[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newDate, setNewDate] = useState("");
  const [newNotes, setNewNotes] = useState("");
  const { t, locale } = useTranslation();

  useEffect(() => {
    loadDeadlines();
  }, []);

  async function loadDeadlines() {
    try {
      const data = await api.getDeadlines();
      setDeadlines(data);
    } catch {
      // Silently handle — table may not be available yet
    } finally {
      setLoading(false);
    }
  }

  async function addDeadline() {
    if (!newTitle || !newDate) return;
    try {
      await api.createDeadline({ title: newTitle, date: newDate, notes: newNotes });
      setNewTitle("");
      setNewDate("");
      setNewNotes("");
      setShowForm(false);
      loadDeadlines();
    } catch (err) {
      setError(err instanceof Error ? err.message : "We couldn't save that. Let's try again.");
    }
  }

  async function dismissDeadline(id: string) {
    try {
      await api.updateDeadline(id, { status: "dismissed" });
      loadDeadlines();
    } catch (err) {
      setError(err instanceof Error ? err.message : "We couldn't save that. Let's try again.");
    }
  }

  async function completeDeadline(id: string) {
    try {
      await api.updateDeadline(id, { status: "completed" });
      loadDeadlines();
    } catch (err) {
      setError(err instanceof Error ? err.message : "We couldn't save that. Let's try again.");
    }
  }

  function getDaysUntil(dateStr: string): number {
    const target = new Date(dateStr);
    const now = new Date();
    return Math.ceil((target.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
  }

  function getUrgencyClass(days: number): string {
    if (days < 0) return "text-warning";
    if (days <= 7) return "text-warning";
    if (days <= 30) return "text-accent";
    return "text-ink-secondary";
  }

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <CircleNotch className="w-8 h-8 text-ink-tertiary animate-spin" weight="regular" />
      </div>
    );
  }

  const activeDeadlines = deadlines.filter((d) => d.status === "active");
  const pastDeadlines = deadlines.filter((d) => d.status !== "active");

  return (
    <div className="space-y-6">
      {error && (
        <div className="flex items-start gap-2 bg-warning-subtle border border-warning/30 rounded-md p-3">
          <Warning className="w-4 h-4 text-warning shrink-0 mt-0.5" weight="regular" />
          <p className="text-sm font-sans text-warning">{error}</p>
        </div>
      )}

      {/* Add button */}
      <div className="flex justify-end">
        <Button size="sm" onClick={() => setShowForm(!showForm)}>
          {showForm ? t("cancel") : t("addDeadline")}
        </Button>
      </div>

      {/* Add form */}
      {showForm && (
        <div className="bg-white border border-border rounded-lg p-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-sans font-medium text-ink-primary mb-2">
                Title
              </label>
              <input
                type="text"
                placeholder={t("deadlineTitlePlaceholder")}
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                className="w-full bg-white border border-border rounded-md px-4 py-3 text-sm font-sans text-ink-primary focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/20 placeholder:text-ink-tertiary"
              />
            </div>
            <div>
              <label className="block text-sm font-sans font-medium text-ink-primary mb-2">
                Date
              </label>
              <input
                type="date"
                value={newDate}
                onChange={(e) => setNewDate(e.target.value)}
                className="w-full bg-white border border-border rounded-md px-4 py-3 text-sm font-sans text-ink-primary focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
              />
            </div>
            <div>
              <label className="block text-sm font-sans font-medium text-ink-primary mb-2">
                Notes
              </label>
              <textarea
                placeholder={t("notesOptional")}
                value={newNotes}
                onChange={(e) => setNewNotes(e.target.value)}
                rows={3}
                className="w-full bg-white border border-border rounded-md px-4 py-3 text-sm font-sans text-ink-primary resize-none focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/20 placeholder:text-ink-tertiary"
              />
            </div>
            <Button size="sm" onClick={addDeadline} disabled={!newTitle || !newDate}>
              {t("saveDeadline")}
            </Button>
          </div>
        </div>
      )}

      {/* Active deadlines */}
      {activeDeadlines.length === 0 && !showForm ? (
        <div className="text-center py-12">
          <Clock className="w-10 h-10 text-ink-tertiary mx-auto mb-3" weight="regular" />
          <p className="text-base font-sans text-ink-secondary mb-1">{t("noActiveDeadlines")}</p>
          <p className="text-sm font-sans text-ink-tertiary">{t("deadlinesAutoDetect")}</p>
        </div>
      ) : (
        <div className="space-y-3">
          {activeDeadlines.map((d: Deadline) => {
            const days = getDaysUntil(d.date);
            const urgencyClass = getUrgencyClass(days);
            return (
              <div
                key={d.id}
                className="bg-white border border-border rounded-lg p-6 flex items-start justify-between gap-4 hover:border-border-strong transition-colors"
              >
                <div className="flex-1 min-w-0">
                  <h3 className="font-serif font-medium tracking-tight text-ink-primary text-lg leading-tight">
                    {d.title}
                  </h3>
                  <div className="flex items-center gap-3 mt-2 flex-wrap">
                    <span className={`text-sm font-sans font-medium ${urgencyClass}`}>
                      {days < 0
                        ? (translations.daysOverdue[locale] as (n: number) => string)(Math.abs(days))
                        : days === 0
                        ? t("dueToday")
                        : (translations.daysRemaining[locale] as (n: number) => string)(days)}
                    </span>
                    <span className="text-sm font-sans text-ink-tertiary">
                      {new Date(d.date).toLocaleDateString()}
                    </span>
                    {d.legal_area && (
                      <span className="inline-flex items-center text-xs font-sans font-medium text-ink-secondary bg-bg border border-border rounded-md px-2 py-0.5 capitalize">
                        {d.legal_area.replace(/_/g, " ")}
                      </span>
                    )}
                  </div>
                  {d.notes && (
                    <p className="text-sm font-sans text-ink-secondary mt-3 leading-relaxed">
                      {d.notes}
                    </p>
                  )}
                </div>
                <div className="flex gap-1 shrink-0">
                  <button
                    onClick={() => completeDeadline(d.id)}
                    className="p-2 text-ink-secondary hover:text-accent hover:bg-accent-subtle rounded-md transition-colors"
                    title={t("markComplete")}
                  >
                    <Check className="w-4 h-4" weight="regular" />
                  </button>
                  <button
                    onClick={() => dismissDeadline(d.id)}
                    className="p-2 text-ink-secondary hover:text-ink-primary hover:bg-bg-hover rounded-md transition-colors"
                    title={t("dismiss")}
                  >
                    <X className="w-4 h-4" weight="regular" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Past deadlines */}
      {pastDeadlines.length > 0 && (
        <div>
          <h3 className="text-xs font-sans font-medium text-ink-tertiary uppercase tracking-wider mb-3">
            {t("pastDeadlines")}
          </h3>
          <div className="space-y-2">
            {pastDeadlines.map((d: Deadline) => (
              <div
                key={d.id}
                className="bg-bg border border-border rounded-lg px-4 py-3 flex items-center justify-between"
              >
                <div>
                  <span className="text-sm font-sans text-ink-tertiary line-through">
                    {d.title}
                  </span>
                  <span className="text-xs font-sans text-ink-tertiary ml-2 capitalize">
                    {d.status}
                  </span>
                </div>
                <span className="text-xs font-sans text-ink-tertiary">
                  {new Date(d.date).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
