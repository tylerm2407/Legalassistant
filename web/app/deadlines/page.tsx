"use client";

import React from "react";
import { useAuth } from "@/lib/auth";
import DeadlineDashboard from "@/components/DeadlineDashboard";
import { useTranslation } from "@/lib/i18n";

/**
 * Deadlines page for tracking legal deadlines and statutes of limitations.
 *
 * Requires authentication. Renders the DeadlineDashboard component which
 * displays active deadlines with urgency indicators and allows creating,
 * completing, and dismissing deadlines.
 */
export default function DeadlinesPage() {
  const { user, loading: authLoading } = useAuth();
  const { t } = useTranslation();

  if (authLoading || !user) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#050505] p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold text-white mb-2">{t("deadlinesTitle")}</h1>
        <p className="text-gray-400 mb-8">{t("deadlinesDescription")}</p>
        <DeadlineDashboard />
      </div>
    </div>
  );
}
