"use client";

import React, { useEffect, useState } from "react";
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

export default function ProfilePage() {
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
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-8 max-w-md text-center">
          <h2 className="text-lg font-semibold text-gray-900 mb-2">
            Profile Not Found
          </h2>
          <p className="text-sm text-gray-600 mb-4">{error}</p>
          <a
            href="/onboarding"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
          >
            Start Onboarding
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="container-wide py-4 flex items-center justify-between">
          <div>
            <a href="/" className="text-xl font-bold text-blue-600">
              Lex
            </a>
            <span className="text-gray-400 mx-2">/</span>
            <span className="text-sm text-gray-600">Profile</span>
          </div>
          <a
            href={`/chat?userId=${userId}`}
            className="text-sm text-blue-600 hover:text-blue-700 transition-colors"
          >
            Back to Chat
          </a>
        </div>
      </header>

      <main className="container-narrow py-8 space-y-8">
        {/* Profile Form */}
        <Card>
          <Card.Header>
            <h2 className="text-lg font-semibold text-gray-900">
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
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  State
                </label>
                <select
                  value={state}
                  onChange={(e) => setState(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select state</option>
                  {US_STATES.map((s) => (
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
                  <p className="text-sm text-red-600">{error}</p>
                )}
                {success && (
                  <p className="text-sm text-green-600">{success}</p>
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
            <h2 className="text-lg font-semibold text-gray-900">
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
            <h2 className="text-lg font-semibold text-gray-900">
              Documents
            </h2>
          </Card.Header>
          <Card.Body>
            {profile.documents.length > 0 && (
              <ul className="space-y-2 mb-6">
                {profile.documents.map((doc, i) => (
                  <li
                    key={i}
                    className="flex items-center gap-2 text-sm text-gray-700 p-2 bg-gray-50 rounded-lg"
                  >
                    <svg
                      className="w-4 h-4 text-gray-400 shrink-0"
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
              <h2 className="text-lg font-semibold text-gray-900">
                Known Legal Facts
              </h2>
            </Card.Header>
            <Card.Body>
              <ul className="space-y-1.5">
                {profile.legal_facts.map((fact, i) => (
                  <li key={i} className="text-sm text-gray-700 flex gap-2">
                    <span className="text-blue-500 shrink-0">&#8226;</span>
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
