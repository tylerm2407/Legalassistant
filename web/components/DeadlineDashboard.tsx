"use client";

import React, { useEffect, useState } from "react";
import Card from "./ui/Card";
import Button from "./ui/Button";
import Badge from "./ui/Badge";
import { api } from "@/lib/api";
import { useTranslation } from "@/lib/i18n";
import translations from "@/lib/i18n/translations";

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
 * Displays active deadlines with urgency color coding (red for overdue,
 * yellow for within 7 days, blue for within 30 days), allows manual deadline
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
    } catch (err) {
      setError(err instanceof Error ? err.message : t("failedToLoadDeadlines"));
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
      setError(err instanceof Error ? err.message : t("failedToSaveDeadline"));
    }
  }

  async function dismissDeadline(id: string) {
    try {
      await api.updateDeadline(id, { status: "dismissed" });
      loadDeadlines();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("failedToUpdateDeadline"));
    }
  }

  async function completeDeadline(id: string) {
    try {
      await api.updateDeadline(id, { status: "completed" });
      loadDeadlines();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("failedToUpdateDeadline"));
    }
  }

  function getDaysUntil(dateStr: string): number {
    const target = new Date(dateStr);
    const now = new Date();
    return Math.ceil((target.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
  }

  function getUrgencyColor(days: number): string {
    if (days < 0) return "text-red-400";
    if (days <= 7) return "text-yellow-400";
    if (days <= 30) return "text-blue-400";
    return "text-gray-400";
  }

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const activeDeadlines = deadlines.filter((d) => d.status === "active");
  const pastDeadlines = deadlines.filter((d) => d.status !== "active");

  return (
    <div className="space-y-6">
      {error && (
        <p className="text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg p-2">{error}</p>
      )}
      {/* Add button */}
      <div className="flex justify-end">
        <Button size="sm" onClick={() => setShowForm(!showForm)}>
          {showForm ? t("cancel") : t("addDeadline")}
        </Button>
      </div>

      {/* Add form */}
      {showForm && (
        <Card>
          <Card.Body>
            <div className="space-y-3">
              <input
                type="text"
                placeholder={t("deadlineTitlePlaceholder")}
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                className="w-full px-3 py-2 bg-white/[0.03] text-white border border-white/10 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500/50 placeholder:text-gray-600"
              />
              <input
                type="date"
                value={newDate}
                onChange={(e) => setNewDate(e.target.value)}
                className="w-full px-3 py-2 bg-white/[0.03] text-white border border-white/10 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500/50 [color-scheme:dark]"
              />
              <textarea
                placeholder={t("notesOptional")}
                value={newNotes}
                onChange={(e) => setNewNotes(e.target.value)}
                rows={2}
                className="w-full px-3 py-2 bg-white/[0.03] text-white border border-white/10 rounded-lg text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500/50 placeholder:text-gray-600"
              />
              <Button size="sm" onClick={addDeadline} disabled={!newTitle || !newDate}>
                {t("saveDeadline")}
              </Button>
            </div>
          </Card.Body>
        </Card>
      )}

      {/* Active deadlines */}
      {activeDeadlines.length === 0 && !showForm ? (
        <div className="text-center py-12">
          <p className="text-gray-500 mb-2">{t("noActiveDeadlines")}</p>
          <p className="text-xs text-gray-600">{t("deadlinesAutoDetect")}</p>
        </div>
      ) : (
        <div className="space-y-3">
          {activeDeadlines.map((d: Deadline) => {
            const days = getDaysUntil(d.date);
            const urgencyColor = getUrgencyColor(days);
            return (
              <div
                key={d.id}
                className="p-4 bg-white/[0.03] backdrop-blur-xl rounded-xl border border-white/10 flex items-start justify-between gap-4"
              >
                <div className="flex-1">
                  <h3 className="text-sm font-semibold text-white">{d.title}</h3>
                  <div className="flex items-center gap-3 mt-1">
                    <span className={`text-xs font-medium ${urgencyColor}`}>
                      {days < 0
                        ? (translations.daysOverdue[locale] as (n: number) => string)(Math.abs(days))
                        : days === 0
                        ? t("dueToday")
                        : (translations.daysRemaining[locale] as (n: number) => string)(days)}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(d.date).toLocaleDateString()}
                    </span>
                    {d.legal_area && (
                      <Badge variant="default" size="sm">
                        {d.legal_area.replace(/_/g, " ")}
                      </Badge>
                    )}
                  </div>
                  {d.notes && <p className="text-xs text-gray-400 mt-1">{d.notes}</p>}
                </div>
                <div className="flex gap-1 shrink-0">
                  <button
                    onClick={() => completeDeadline(d.id)}
                    className="p-1.5 text-green-400 hover:bg-green-500/10 rounded-lg transition-colors"
                    title={t("markComplete")}
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                    </svg>
                  </button>
                  <button
                    onClick={() => dismissDeadline(d.id)}
                    className="p-1.5 text-gray-500 hover:bg-white/5 rounded-lg transition-colors"
                    title={t("dismiss")}
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
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
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">{t("pastDeadlines")}</h3>
          <div className="space-y-2 opacity-60">
            {pastDeadlines.map((d: Deadline) => (
              <div key={d.id} className="p-3 bg-white/[0.02] rounded-lg border border-white/[0.05] flex items-center justify-between">
                <div>
                  <span className="text-sm text-gray-400 line-through">{d.title}</span>
                  <span className="text-xs text-gray-600 ml-2">{d.status}</span>
                </div>
                <span className="text-xs text-gray-600">{new Date(d.date).toLocaleDateString()}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
