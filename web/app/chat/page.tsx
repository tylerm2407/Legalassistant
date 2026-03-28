"use client";

import React, { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import ChatInterface from "@/components/ChatInterface";
import type { LegalProfile } from "@/lib/types";
import { api } from "@/lib/api";

const DEMO_USER_ID = "demo-sarah-chen-uuid";

export default function ChatPage() {
  const searchParams = useSearchParams();
  const [profile, setProfile] = useState<LegalProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadProfile() {
      setLoading(true);
      setError("");

      const userId = searchParams.get("userId") || DEMO_USER_ID;

      try {
        const p = await api.getProfile(userId);
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
  }, [searchParams]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-sm text-gray-600">Loading your profile...</p>
        </div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-8 max-w-md text-center">
          <div className="text-red-500 text-3xl mb-4">!</div>
          <h2 className="text-lg font-semibold text-gray-900 mb-2">
            Unable to Load Profile
          </h2>
          <p className="text-sm text-gray-600 mb-6">
            {error || "Something went wrong."}
          </p>
          <div className="flex items-center justify-center gap-3">
            <a
              href="/onboarding"
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
            >
              Start Onboarding
            </a>
            <button
              onClick={() => window.location.reload()}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors"
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
