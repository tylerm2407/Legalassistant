"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Button from "./ui/Button";
import Input from "./ui/Input";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

/** All 50 US states used in the state selection dropdown during onboarding. */
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

/** Total number of steps in the onboarding intake wizard. */
const TOTAL_STEPS = 5;

/**
 * Form state for the onboarding intake wizard.
 *
 * Captures all information needed to build the user's initial LegalProfile
 * in Supabase. Each field maps to a step in the 5-question wizard.
 *
 * @property displayName - User's preferred display name shown in the sidebar
 * @property state - US state of residence, determines which laws apply
 * @property housingSituation - Renter, homeowner, or other housing status
 * @property housingDetails - Optional free-text housing details (e.g., lease type)
 * @property employmentType - Employment classification (W-2, 1099, etc.)
 * @property employmentDetails - Optional free-text employment details
 * @property familyStatus - Marital/relationship status
 * @property dependents - Number of dependents (affects family law rights)
 * @property currentIssue - Optional description of an active legal issue
 */
interface FormData {
  displayName: string;
  state: string;
  housingSituation: string;
  housingDetails: string;
  employmentType: string;
  employmentDetails: string;
  familyStatus: string;
  dependents: string;
  currentIssue: string;
}

/**
 * Five-step onboarding intake wizard that builds the user's initial legal profile.
 *
 * Collects name, state, housing situation, employment type, family status,
 * and an optional current legal issue. On completion, creates a LegalProfile
 * in Supabase and redirects to the subscription page.
 *
 * Steps:
 * 1. Name and state of residence
 * 2. Housing situation (renter/homeowner/other)
 * 3. Employment type (W-2, 1099, etc.)
 * 4. Family status and dependents
 * 5. Current legal issue (optional)
 */
export default function OnboardingFlow() {
  const router = useRouter();
  const { user } = useAuth();
  const [step, setStep] = useState(1);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState<FormData>({
    displayName: "",
    state: "",
    housingSituation: "",
    housingDetails: "",
    employmentType: "",
    employmentDetails: "",
    familyStatus: "",
    dependents: "",
    currentIssue: "",
  });

  function update(field: keyof FormData, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function canAdvance(): boolean {
    switch (step) {
      case 1:
        return form.displayName.trim().length > 0 && form.state.length > 0;
      case 2:
        return form.housingSituation.length > 0;
      case 3:
        return form.employmentType.length > 0;
      case 4:
        return form.familyStatus.length > 0;
      case 5:
        return true;
      default:
        return false;
    }
  }

  async function handleSubmit() {
    setSubmitting(true);
    setError("");
    const userId = user?.id;
    if (!userId) {
      setError("You must be signed in. Redirecting...");
      router.push("/auth");
      return;
    }

    const housing = form.housingDetails
      ? `${form.housingSituation} — ${form.housingDetails}`
      : form.housingSituation;
    const employment = form.employmentDetails
      ? `${form.employmentType} — ${form.employmentDetails}`
      : form.employmentType;
    const family = form.dependents
      ? `${form.familyStatus}, ${form.dependents} dependents`
      : form.familyStatus;

    try {
      await api.createProfile({
        user_id: userId,
        display_name: form.displayName.trim(),
        state: form.state,
        housing_situation: housing,
        employment_type: employment,
        family_status: family,
        active_issues: form.currentIssue.trim()
          ? [
              {
                issue_type: "general",
                summary: form.currentIssue.trim(),
                status: "open",
                started_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
                notes: [],
              },
            ]
          : [],
        legal_facts: [],
        documents: [],
        member_since: new Date().toISOString(),
        conversation_count: 0,
      });
    } catch (err) {
      console.warn("Profile creation failed, continuing to subscription:", err);
    }

    setSubmitting(false);
    router.push(`/subscription?userId=${userId}`);
  }

  function renderStep() {
    switch (step) {
      case 1:
        return (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-white">
              Let&apos;s get to know you
            </h2>
            <p className="text-sm text-gray-400">
              CaseMate uses this information to give you personalized guidance.
            </p>
            <Input
              label="Your Name"
              placeholder="e.g. Sarah Chen"
              value={form.displayName}
              onChange={(e) => update("displayName", e.target.value)}
            />
            <div>
              <label htmlFor="onboarding-state" className="block text-sm font-medium text-gray-300 mb-1">
                State
              </label>
              <select
                id="onboarding-state"
                value={form.state}
                onChange={(e) => update("state", e.target.value)}
                className="w-full px-3 py-2 bg-white/[0.03] text-white border border-white/10 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500/50"
              >
                <option value="">Select your state</option>
                {US_STATES.map((s: string) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-white">
              Housing Situation
            </h2>
            <p className="text-sm text-gray-400">
              This helps CaseMate understand tenant/homeowner rights that apply to
              you.
            </p>
            <div className="space-y-2">
              {["Renter", "Homeowner", "Other"].map((opt: string) => (
                <label
                  key={opt}
                  className={`flex items-center gap-3 p-3 border rounded-lg cursor-pointer transition-all ${
                    form.housingSituation === opt.toLowerCase()
                      ? "border-blue-500 bg-blue-500/10 shadow-glow-sm"
                      : "border-white/10 hover:border-white/20 hover:bg-white/[0.03]"
                  }`}
                >
                  <input
                    type="radio"
                    name="housing"
                    value={opt.toLowerCase()}
                    checked={form.housingSituation === opt.toLowerCase()}
                    onChange={(e) => update("housingSituation", e.target.value)}
                    className="text-blue-500"
                  />
                  <span className="text-sm text-gray-200">{opt}</span>
                </label>
              ))}
            </div>
            <Input
              label="Details (optional)"
              placeholder="e.g. apartment, month-to-month lease"
              value={form.housingDetails}
              onChange={(e) => update("housingDetails", e.target.value)}
            />
          </div>
        );

      case 3:
        return (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-white">
              Employment Type
            </h2>
            <p className="text-sm text-gray-400">
              Employment status affects your rights in many legal areas.
            </p>
            <div className="space-y-2">
              {["W-2 Employee", "1099 Contractor", "Unemployed", "Student", "Retired"].map(
                (opt: string) => (
                  <label
                    key={opt}
                    className={`flex items-center gap-3 p-3 border rounded-lg cursor-pointer transition-all ${
                      form.employmentType === opt.toLowerCase()
                        ? "border-blue-500 bg-blue-500/10 shadow-glow-sm"
                        : "border-white/10 hover:border-white/20 hover:bg-white/[0.03]"
                    }`}
                  >
                    <input
                      type="radio"
                      name="employment"
                      value={opt.toLowerCase()}
                      checked={form.employmentType === opt.toLowerCase()}
                      onChange={(e) =>
                        update("employmentType", e.target.value)
                      }
                      className="text-blue-500"
                    />
                    <span className="text-sm text-gray-200">{opt}</span>
                  </label>
                )
              )}
            </div>
            <Input
              label="Details (optional)"
              placeholder="e.g. tech industry, part-time"
              value={form.employmentDetails}
              onChange={(e) => update("employmentDetails", e.target.value)}
            />
          </div>
        );

      case 4:
        return (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-white">
              Family Status
            </h2>
            <p className="text-sm text-gray-400">
              Family situation can affect custody, benefits, and housing rights.
            </p>
            <div className="space-y-2">
              {["Single", "Married", "Divorced", "Widowed", "Domestic Partnership"].map(
                (opt: string) => (
                  <label
                    key={opt}
                    className={`flex items-center gap-3 p-3 border rounded-lg cursor-pointer transition-all ${
                      form.familyStatus === opt.toLowerCase()
                        ? "border-blue-500 bg-blue-500/10 shadow-glow-sm"
                        : "border-white/10 hover:border-white/20 hover:bg-white/[0.03]"
                    }`}
                  >
                    <input
                      type="radio"
                      name="family"
                      value={opt.toLowerCase()}
                      checked={form.familyStatus === opt.toLowerCase()}
                      onChange={(e) => update("familyStatus", e.target.value)}
                      className="text-blue-500"
                    />
                    <span className="text-sm text-gray-200">{opt}</span>
                  </label>
                )
              )}
            </div>
            <Input
              label="Number of Dependents (optional)"
              placeholder="e.g. 2"
              type="number"
              min="0"
              value={form.dependents}
              onChange={(e) => update("dependents", e.target.value)}
            />
          </div>
        );

      case 5:
        return (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-white">
              Current Legal Issue
            </h2>
            <p className="text-sm text-gray-400">
              Optionally describe a legal issue you&apos;re dealing with. You can
              always add this later.
            </p>
            <textarea
              value={form.currentIssue}
              onChange={(e) => update("currentIssue", e.target.value)}
              rows={5}
              placeholder="e.g. My landlord hasn't returned my security deposit after 45 days..."
              className="w-full px-3 py-2 bg-white/[0.03] text-white border border-white/10 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500/50 resize-none placeholder:text-gray-600"
            />
          </div>
        );

      default:
        return null;
    }
  }

  return (
    <div className="min-h-screen bg-[#050505] flex items-center justify-center p-4">
      <div className="w-full max-w-lg">
        {/* Progress bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-400">
              Step {step} of {TOTAL_STEPS}
            </span>
            <span className="text-sm text-gray-500">
              {Math.round((step / TOTAL_STEPS) * 100)}%
            </span>
          </div>
          <div className="w-full bg-white/10 rounded-full h-2">
            <div
              className="bg-gradient-to-r from-blue-600 to-violet-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(step / TOTAL_STEPS) * 100}%` }}
            />
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Your information is stored securely and used only to personalize your legal guidance.
          </p>
        </div>

        {/* Card */}
        <div className="bg-white/[0.03] backdrop-blur-xl rounded-xl border border-white/10 p-6">
          {renderStep()}

          {error && (
            <p className="mt-4 text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg p-3">
              {error}
            </p>
          )}

          {/* Navigation */}
          <div className="flex items-center justify-between mt-8">
            <Button
              variant="ghost"
              onClick={() => setStep((s) => s - 1)}
              disabled={step === 1}
            >
              Back
            </Button>

            {step < TOTAL_STEPS ? (
              <Button onClick={() => setStep((s) => s + 1)} disabled={!canAdvance()}>
                Next
              </Button>
            ) : (
              <Button onClick={handleSubmit} disabled={submitting}>
                {submitting ? "Setting up..." : "Continue"}
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
