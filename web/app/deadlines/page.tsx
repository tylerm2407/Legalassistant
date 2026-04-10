"use client";

import React from "react";
import { useAuth } from "@/lib/auth";
import DeadlineDashboard from "@/components/DeadlineDashboard";

/**
 * Deadlines page for tracking legal deadlines and statutes of limitations.
 *
 * Requires authentication. Renders the DeadlineDashboard component which
 * displays active deadlines with urgency indicators and allows creating,
 * completing, and dismissing deadlines.
 */
export default function DeadlinesPage() {
  const { user, loading: authLoading } = useAuth();

  if (authLoading || !user) {
    return (
      <div className="min-h-screen bg-bg flex items-center justify-center">
        <p className="font-sans text-ink-secondary">Loading…</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-bg">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-10">
          <h1 className="font-serif text-5xl md:text-6xl font-medium tracking-tight leading-tight text-ink-primary">
            Deadlines
          </h1>
          <p className="font-sans text-base text-ink-secondary mt-4 max-w-[65ch]">
            Legal matters have clocks on them. We'll keep track of the ones
            that matter to you so nothing important slips past.
          </p>
        </div>
        <DeadlineDashboard />
      </div>
    </div>
  );
}
