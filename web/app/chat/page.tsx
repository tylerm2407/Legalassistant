"use client";

import React, { Suspense, useEffect, useState } from "react";
import ChatInterface from "@/components/ChatInterface";
import type { LegalProfile } from "@/lib/types";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

/**
 * Chat page that loads the user's legal profile and renders the main chat interface.
 *
 * Wraps ChatPageInner in Suspense for loading states. The inner component
 * fetches the authenticated user's profile from the backend and passes it
 * to ChatInterface, which handles the conversation UI, profile sidebar,
 * and action generator.
 */
export default function ChatPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-[#050505] flex items-center justify-center">
          <div className="text-center">
            <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p className="text-sm text-gray-400">Loading...</p>
          </div>
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
 * Fetches the authenticated user's legal profile on mount and renders either
 * a loading spinner, an error state with onboarding redirect, or the full
 * ChatInterface with the loaded profile.
 */
function ChatPageInner() {
  const { user, loading: authLoading } = useAuth();
  const [profile, setProfile] = useState<LegalProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (authLoading || !user) return;

    async function loadProfile() {
      setLoading(true);
      setError("");

      try {
        const p = await api.getProfile(user!.id);
        if (p) {
          setProfile(p);
        } else {
          setError(
            "Profile not found. Please complete onboarding first."
          );
        }
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load profile. Please try again."
        );
      } finally {
        setLoading(false);
      }
    }

    loadProfile();
  }, [user, authLoading]);

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-sm text-gray-400">Loading your profile...</p>
        </div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center p-4">
        <div className="bg-white/[0.03] backdrop-blur-xl rounded-xl border border-white/10 p-8 max-w-md text-center">
          <div className="text-red-400 text-3xl mb-4">!</div>
          <h2 className="text-lg font-semibold text-white mb-2">
            Unable to Load Profile
          </h2>
          <p className="text-sm text-gray-400 mb-6">
            {error || "Something went wrong."}
          </p>
          <div className="flex items-center justify-center gap-3">
            <a
              href="/onboarding"
              className="inline-flex items-center px-4 py-2 bg-blue-500 text-white text-sm font-medium rounded-lg hover:bg-blue-400 shadow-glow-md transition-all"
            >
              Start Onboarding
            </a>
            <button
              onClick={() => window.location.reload()}
              className="inline-flex items-center px-4 py-2 border border-white/15 text-gray-300 text-sm font-medium rounded-lg hover:bg-white/5 hover:border-white/25 transition-all"
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
