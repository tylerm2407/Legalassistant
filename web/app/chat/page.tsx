"use client";

import React, { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import ChatInterface from "@/components/ChatInterface";
import type { LegalProfile } from "@/lib/types";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

/**
 * Load the user's legal profile, trying localStorage first then the backend API.
 *
 * This ensures the chat works even when the Python backend is unavailable.
 * The profile is saved to localStorage during onboarding.
 *
 * @param userId - The authenticated user's ID
 * @returns The user's LegalProfile, or null if not found
 */
async function loadProfile(userId: string): Promise<LegalProfile | null> {
  try {
    const raw = localStorage.getItem("casemate_profile");
    if (raw) {
      const profile = JSON.parse(raw) as LegalProfile;
      if (profile.user_id === userId || profile.display_name) {
        return profile;
      }
    }
  } catch {
    // localStorage parse failed — fall through
  }

  try {
    const profile = await api.getProfile(userId);
    if (profile) {
      try {
        localStorage.setItem("casemate_profile", JSON.stringify(profile));
      } catch {
        // ignore
      }
      return profile;
    }
  } catch {
    // Backend unavailable — fall through
  }

  return null;
}

/**
 * Chat page that loads the user's legal profile and renders the main chat interface.
 *
 * Wraps ChatPageInner in Suspense for loading states. The inner component
 * fetches the authenticated user's profile from localStorage (with backend fallback)
 * and passes it to ChatInterface.
 */
export default function ChatPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-bg flex items-center justify-center">
          <p className="font-sans text-base text-ink-secondary">Loading…</p>
        </div>
      }
    >
      <ChatPageInner />
    </Suspense>
  );
}

/**
 * Inner chat page component that handles profile loading and error states.
 *
 * Loads the user's legal profile from localStorage first (for offline-first UX),
 * then falls back to the backend API. If no profile exists anywhere, shows
 * an onboarding redirect.
 */
function ChatPageInner() {
  const { user, loading: authLoading } = useAuth();
  const [profile, setProfile] = useState<LegalProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (authLoading) return;

    async function load() {
      setLoading(true);
      setError("");

      const userId = user?.id || "local";

      try {
        const p = await loadProfile(userId);
        if (p) {
          setProfile(p);
        } else {
          setError(
            "We don't have your profile yet. Let's set it up."
          );
        }
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "We couldn't load your profile. Please try again."
        );
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [user, authLoading]);

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-bg flex items-center justify-center">
        <p className="font-sans text-base text-ink-secondary">
          Loading your profile…
        </p>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="min-h-screen bg-bg flex items-center justify-center p-6">
        <div className="bg-white border border-border rounded-lg p-10 max-w-md text-center">
          <h2 className="font-serif text-2xl font-medium text-ink-primary mb-3">
            Let's set up your profile
          </h2>
          <p className="font-sans text-base text-ink-secondary mb-8 max-w-[45ch]">
            {error || "We need a few details about your situation so CaseMate can help."}
          </p>
          <div className="flex items-center justify-center gap-3">
            <Link
              href="/onboarding"
              className="inline-flex items-center px-6 py-3 bg-accent text-white text-base font-sans font-medium rounded-md hover:bg-accent-hover transition-colors"
            >
              Start onboarding
            </Link>
            <button
              onClick={() => window.location.reload()}
              className="inline-flex items-center px-6 py-3 border border-border-strong text-ink-primary text-base font-sans font-medium rounded-md hover:bg-bg-hover transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return <ChatInterface profile={profile} />;
}
