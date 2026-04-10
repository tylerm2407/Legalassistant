"use client";

import React, { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import CaseHistory from "@/components/CaseHistory";
import DocumentUpload from "@/components/DocumentUpload";
import { api } from "@/lib/api";
import type { LegalProfile } from "@/lib/types";
import { File, ArrowRight } from "@phosphor-icons/react";

const DEMO_USER_ID = "demo-sarah-chen-uuid";

const US_STATES = [
  "Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut",
  "Delaware","Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa",
  "Kansas","Kentucky","Louisiana","Maine","Maryland","Massachusetts","Michigan",
  "Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada",
  "New Hampshire","New Jersey","New Mexico","New York","North Carolina",
  "North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania","Rhode Island",
  "South Carolina","South Dakota","Tennessee","Texas","Utah","Vermont",
  "Virginia","Washington","West Virginia","Wisconsin","Wyoming",
];

/**
 * Profile management page with editable fields, case history, and document upload.
 *
 * Displays the user's legal profile in editable form fields, shows active issues
 * on a timeline, lists uploaded documents, and provides a document upload zone.
 * Changes are persisted to Supabase via the backend API.
 */
export default function ProfilePage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-bg flex items-center justify-center">
          <p className="font-sans text-ink-secondary">Loading…</p>
        </div>
      }
    >
      <ProfilePageInner />
    </Suspense>
  );
}

/**
 * Inner profile page component handling profile fetch, edit form, and save logic.
 *
 * Loads the user's profile on mount, populates editable form fields, and saves
 * changes back to Supabase. Includes sections for active issues (CaseHistory),
 * document upload (DocumentUpload), and extracted legal facts.
 */
function ProfilePageInner() {
  const searchParams = useSearchParams();
  const [profile, setProfile] = useState<LegalProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [displayName, setDisplayName] = useState("");
  const [state, setState] = useState("");
  const [housing, setHousing] = useState("");
  const [employment, setEmployment] = useState("");
  const [family, setFamily] = useState("");

  const userId = searchParams.get("userId") || DEMO_USER_ID;

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError("");
      try {
        const p = await api.getProfile(userId);
        if (p) {
          setProfile(p);
          setDisplayName(p.display_name);
          setState(p.state);
          setHousing(p.housing_situation);
          setEmployment(p.employment_type);
          setFamily(p.family_status);
        } else {
          setError("We couldn't find your profile. Let's get you set up.");
        }
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "We couldn't load your profile. Let's try again."
        );
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [userId]);

  async function handleSave() {
    setSaving(true);
    setError("");
    setSuccess("");
    try {
      const updated = await api.createProfile({
        user_id: userId,
        display_name: displayName.trim(),
        state,
        housing_situation: housing,
        employment_type: employment,
        family_status: family,
      });
      setProfile(updated);
      setSuccess("Saved.");
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "We couldn't save your changes. Let's try again."
      );
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-bg flex items-center justify-center">
        <p className="font-sans text-ink-secondary">Loading…</p>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="min-h-screen bg-bg flex items-center justify-center p-4">
        <div className="bg-white border border-border rounded-lg p-8 max-w-md text-center">
          <h2 className="font-serif text-2xl font-medium tracking-tight text-ink-primary mb-3">
            We couldn't find your profile
          </h2>
          <p className="font-sans text-base text-ink-secondary mb-6">{error}</p>
          <a
            href="/onboarding"
            className="inline-flex items-center gap-2 bg-accent text-white px-6 py-3 rounded-md font-sans font-medium hover:bg-accent-hover transition-colors"
          >
            Start onboarding
            <ArrowRight className="w-4 h-4" weight="regular" />
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-bg">
      {/* Header */}
      <header className="bg-bg border-b border-border">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <a href="/" className="font-serif text-xl font-medium tracking-tight text-accent">
              CaseMate
            </a>
            <span className="text-ink-tertiary">/</span>
            <span className="font-sans text-sm text-ink-secondary">Your profile</span>
          </div>
          <a
            href={`/chat?userId=${userId}`}
            className="font-sans text-sm text-accent hover:text-accent-hover transition-colors"
          >
            Back to chat
          </a>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-8">
        {/* Page intro */}
        <div>
          <h1 className="font-serif text-5xl md:text-6xl font-medium tracking-tight leading-tight text-ink-primary">
            Your profile
          </h1>
          <p className="font-sans text-base text-ink-secondary mt-4 max-w-[65ch]">
            The more we know about you, the more specific we can be. Everything
            here stays with you and shapes every answer CaseMate gives.
          </p>
        </div>

        {/* Profile Form */}
        <section className="bg-white border border-border rounded-lg p-8">
          <div className="mb-6">
            <h2 className="font-serif text-2xl font-medium tracking-tight text-ink-primary">
              About you
            </h2>
            <p className="font-sans text-sm text-ink-tertiary mt-1">
              Member since {new Date(profile.member_since).toLocaleDateString()} ·{" "}
              {profile.conversation_count} conversations
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label className="block text-sm font-sans font-medium text-ink-primary mb-2">
                Display name
              </label>
              <input
                type="text"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                className="w-full bg-white border border-border rounded-md px-4 py-3 font-sans text-base text-ink-primary focus:border-accent focus:ring-2 focus:ring-accent/20 focus:outline-none placeholder:text-ink-tertiary"
              />
            </div>
            <div>
              <label className="block text-sm font-sans font-medium text-ink-primary mb-2">
                State
              </label>
              <select
                value={state}
                onChange={(e) => setState(e.target.value)}
                className="w-full bg-white border border-border rounded-md px-4 py-3 font-sans text-base text-ink-primary focus:border-accent focus:ring-2 focus:ring-accent/20 focus:outline-none"
              >
                <option value="">Select state</option>
                {US_STATES.map((s: string) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-sans font-medium text-ink-primary mb-2">
                Housing situation
              </label>
              <input
                type="text"
                value={housing}
                onChange={(e) => setHousing(e.target.value)}
                className="w-full bg-white border border-border rounded-md px-4 py-3 font-sans text-base text-ink-primary focus:border-accent focus:ring-2 focus:ring-accent/20 focus:outline-none placeholder:text-ink-tertiary"
              />
            </div>
            <div>
              <label className="block text-sm font-sans font-medium text-ink-primary mb-2">
                Employment type
              </label>
              <input
                type="text"
                value={employment}
                onChange={(e) => setEmployment(e.target.value)}
                className="w-full bg-white border border-border rounded-md px-4 py-3 font-sans text-base text-ink-primary focus:border-accent focus:ring-2 focus:ring-accent/20 focus:outline-none placeholder:text-ink-tertiary"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-sans font-medium text-ink-primary mb-2">
                Family status
              </label>
              <input
                type="text"
                value={family}
                onChange={(e) => setFamily(e.target.value)}
                className="w-full bg-white border border-border rounded-md px-4 py-3 font-sans text-base text-ink-primary focus:border-accent focus:ring-2 focus:ring-accent/20 focus:outline-none placeholder:text-ink-tertiary"
              />
            </div>
          </div>

          <div className="mt-8 pt-6 border-t border-border flex items-center justify-between gap-4">
            <div className="min-h-[1.25rem]">
              {error && (
                <p className="font-sans text-sm text-warning">{error}</p>
              )}
              {success && (
                <p className="font-sans text-sm text-accent">{success}</p>
              )}
            </div>
            <button
              onClick={handleSave}
              disabled={saving}
              className="bg-accent text-white px-6 py-3 rounded-md font-sans font-medium hover:bg-accent-hover transition-colors disabled:opacity-50"
            >
              {saving ? "Saving…" : "Save changes"}
            </button>
          </div>
        </section>

        {/* Active Issues */}
        <section className="bg-white border border-border rounded-lg p-8">
          <h2 className="font-serif text-2xl font-medium tracking-tight text-ink-primary mb-6">
            What you're dealing with
          </h2>
          <CaseHistory issues={profile.active_issues} />
        </section>

        {/* Documents */}
        <section className="bg-white border border-border rounded-lg p-8">
          <h2 className="font-serif text-2xl font-medium tracking-tight text-ink-primary mb-6">
            Your documents
          </h2>
          {profile.documents.length > 0 && (
            <ul className="space-y-2 mb-6">
              {profile.documents.map((doc: string, i: number) => (
                <li
                  key={i}
                  className="flex items-center gap-3 font-sans text-sm text-ink-primary p-3 bg-bg rounded-md border border-border"
                >
                  <File className="w-5 h-5 text-ink-secondary shrink-0" weight="regular" />
                  {doc}
                </li>
              ))}
            </ul>
          )}
          <DocumentUpload userId={userId} />
        </section>

        {/* Legal Facts */}
        {profile.legal_facts.length > 0 && (
          <section className="bg-white border border-border rounded-lg p-8">
            <h2 className="font-serif text-2xl font-medium tracking-tight text-ink-primary mb-2">
              What we remember
            </h2>
            <p className="font-sans text-sm text-ink-tertiary mb-6">
              Facts CaseMate has picked up from your conversations over time.
            </p>
            <ul className="space-y-3">
              {profile.legal_facts.map((fact: string, i: number) => (
                <li key={i} className="font-sans text-base text-ink-primary flex gap-3 max-w-[65ch]">
                  <span className="text-accent shrink-0 leading-relaxed">•</span>
                  <span className="leading-relaxed">{fact}</span>
                </li>
              ))}
            </ul>
          </section>
        )}
      </main>
    </div>
  );
}
