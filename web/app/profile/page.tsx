"use client";

import React, { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Card from "@/components/ui/Card";
import CaseHistory from "@/components/CaseHistory";
import DocumentUpload from "@/components/DocumentUpload";
import { api } from "@/lib/api";
import type { LegalProfile } from "@/lib/types";

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
        <div className="min-h-screen bg-[#050505] flex items-center justify-center">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
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
          setError("Profile not found.");
        }
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to load profile."
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
      setSuccess("Profile saved successfully.");
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to save profile."
      );
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center p-4">
        <div className="bg-white/[0.03] backdrop-blur-xl rounded-xl border border-white/10 p-8 max-w-md text-center">
          <h2 className="text-lg font-semibold text-white mb-2">
            Profile Not Found
          </h2>
          <p className="text-sm text-gray-400 mb-4">{error}</p>
          <a
            href="/onboarding"
            className="inline-flex items-center px-4 py-2 bg-blue-500 text-white text-sm font-medium rounded-lg hover:bg-blue-400 shadow-glow-md transition-all"
          >
            Start Onboarding
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#050505]">
      {/* Header */}
      <header className="bg-white/[0.03] backdrop-blur-xl border-b border-white/10">
        <div className="container-wide py-4 flex items-center justify-between">
          <div>
            <a href="/" className="text-xl font-bold text-blue-400">
              CaseMate
            </a>
            <span className="text-gray-600 mx-2">/</span>
            <span className="text-sm text-gray-400">Profile</span>
          </div>
          <a
            href={`/chat?userId=${userId}`}
            className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
          >
            Back to Chat
          </a>
        </div>
      </header>

      <main className="container-narrow py-8 space-y-8">
        {/* Profile Form */}
        <Card>
          <Card.Header>
            <h2 className="text-lg font-semibold text-white">
              Your Profile
            </h2>
            <p className="text-sm text-gray-500">
              Member since{" "}
              {new Date(profile.member_since).toLocaleDateString()} |{" "}
              {profile.conversation_count} conversations
            </p>
          </Card.Header>
          <Card.Body>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Display Name"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
              />
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  State
                </label>
                <select
                  value={state}
                  onChange={(e) => setState(e.target.value)}
                  className="w-full px-3 py-2 bg-white/[0.03] text-white border border-white/10 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500/50"
                >
                  <option value="">Select state</option>
                  {US_STATES.map((s: string) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </div>
              <Input
                label="Housing Situation"
                value={housing}
                onChange={(e) => setHousing(e.target.value)}
              />
              <Input
                label="Employment Type"
                value={employment}
                onChange={(e) => setEmployment(e.target.value)}
              />
              <Input
                label="Family Status"
                value={family}
                onChange={(e) => setFamily(e.target.value)}
              />
            </div>
          </Card.Body>
          <Card.Footer>
            <div className="flex items-center justify-between">
              <div>
                {error && (
                  <p className="text-sm text-red-400">{error}</p>
                )}
                {success && (
                  <p className="text-sm text-green-400">{success}</p>
                )}
              </div>
              <Button onClick={handleSave} disabled={saving}>
                {saving ? "Saving..." : "Save Changes"}
              </Button>
            </div>
          </Card.Footer>
        </Card>

        {/* Active Issues */}
        <Card>
          <Card.Header>
            <h2 className="text-lg font-semibold text-white">
              Active Issues
            </h2>
          </Card.Header>
          <Card.Body>
            <CaseHistory issues={profile.active_issues} />
          </Card.Body>
        </Card>

        {/* Documents */}
        <Card>
          <Card.Header>
            <h2 className="text-lg font-semibold text-white">
              Documents
            </h2>
          </Card.Header>
          <Card.Body>
            {profile.documents.length > 0 && (
              <ul className="space-y-2 mb-6">
                {profile.documents.map((doc: string, i: number) => (
                  <li
                    key={i}
                    className="flex items-center gap-2 text-sm text-gray-300 p-2 bg-white/[0.03] rounded-lg border border-white/[0.06]"
                  >
                    <svg
                      className="w-4 h-4 text-gray-500 shrink-0"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      strokeWidth={2}
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                      />
                    </svg>
                    {doc}
                  </li>
                ))}
              </ul>
            )}
            <DocumentUpload userId={userId} />
          </Card.Body>
        </Card>

        {/* Legal Facts */}
        {profile.legal_facts.length > 0 && (
          <Card>
            <Card.Header>
              <h2 className="text-lg font-semibold text-white">
                Known Legal Facts
              </h2>
            </Card.Header>
            <Card.Body>
              <ul className="space-y-1.5">
                {profile.legal_facts.map((fact: string, i: number) => (
                  <li key={i} className="text-sm text-gray-300 flex gap-2">
                    <span className="text-blue-400 shrink-0">&#8226;</span>
                    {fact}
                  </li>
                ))}
              </ul>
            </Card.Body>
          </Card>
        )}
      </main>
    </div>
  );
}
