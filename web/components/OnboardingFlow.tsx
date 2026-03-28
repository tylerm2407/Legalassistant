"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Button from "./ui/Button";
import Input from "./ui/Input";
import { api } from "@/lib/api";

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

const TOTAL_STEPS = 5;

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

export default function OnboardingFlow() {
  const router = useRouter();
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
    try {
      const userId = crypto.randomUUID();
      const housing = form.housingDetails
        ? `${form.housingSituation} — ${form.housingDetails}`
        : form.housingSituation;
      const employment = form.employmentDetails
        ? `${form.employmentType} — ${form.employmentDetails}`
        : form.employmentType;
      const family = form.dependents
        ? `${form.familyStatus}, ${form.dependents} dependents`
        : form.familyStatus;

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

      router.push(`/chat?userId=${userId}`);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Something went wrong. Try again."
      );
    } finally {
      setSubmitting(false);
    }
  }

  function renderStep() {
    switch (step) {
      case 1:
        return (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-gray-900">
              Let&apos;s get to know you
            </h2>
            <p className="text-sm text-gray-600">
              Lex uses this information to give you personalized guidance.
            </p>
            <Input
              label="Your Name"
              placeholder="e.g. Sarah Chen"
              value={form.displayName}
              onChange={(e) => update("displayName", e.target.value)}
            />
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                State
              </label>
              <select
                value={form.state}
                onChange={(e) => update("state", e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Select your state</option>
                {US_STATES.map((s) => (
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
            <h2 className="text-xl font-semibold text-gray-900">
              Housing Situation
            </h2>
            <p className="text-sm text-gray-600">
              This helps Lex understand tenant/homeowner rights that apply to
              you.
            </p>
            <div className="space-y-2">
              {["Renter", "Homeowner", "Other"].map((opt) => (
                <label
                  key={opt}
                  className={`flex items-center gap-3 p-3 border rounded-lg cursor-pointer transition-colors ${
                    form.housingSituation === opt.toLowerCase()
                      ? "border-blue-500 bg-blue-50"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                >
                  <input
                    type="radio"
                    name="housing"
                    value={opt.toLowerCase()}
                    checked={form.housingSituation === opt.toLowerCase()}
                    onChange={(e) => update("housingSituation", e.target.value)}
                    className="text-blue-600"
                  />
                  <span className="text-sm text-gray-800">{opt}</span>
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
            <h2 className="text-xl font-semibold text-gray-900">
              Employment Type
            </h2>
            <p className="text-sm text-gray-600">
              Employment status affects your rights in many legal areas.
            </p>
            <div className="space-y-2">
              {["W-2 Employee", "1099 Contractor", "Unemployed", "Student", "Retired"].map(
                (opt) => (
                  <label
                    key={opt}
                    className={`flex items-center gap-3 p-3 border rounded-lg cursor-pointer transition-colors ${
                      form.employmentType === opt.toLowerCase()
                        ? "border-blue-500 bg-blue-50"
                        : "border-gray-200 hover:border-gray-300"
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
                      className="text-blue-600"
                    />
                    <span className="text-sm text-gray-800">{opt}</span>
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
            <h2 className="text-xl font-semibold text-gray-900">
              Family Status
            </h2>
            <p className="text-sm text-gray-600">
              Family situation can affect custody, benefits, and housing rights.
            </p>
            <div className="space-y-2">
              {["Single", "Married", "Divorced", "Widowed", "Domestic Partnership"].map(
                (opt) => (
                  <label
                    key={opt}
                    className={`flex items-center gap-3 p-3 border rounded-lg cursor-pointer transition-colors ${
                      form.familyStatus === opt.toLowerCase()
                        ? "border-blue-500 bg-blue-50"
                        : "border-gray-200 hover:border-gray-300"
                    }`}
                  >
                    <input
                      type="radio"
                      name="family"
                      value={opt.toLowerCase()}
                      checked={form.familyStatus === opt.toLowerCase()}
                      onChange={(e) => update("familyStatus", e.target.value)}
                      className="text-blue-600"
                    />
                    <span className="text-sm text-gray-800">{opt}</span>
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
            <h2 className="text-xl font-semibold text-gray-900">
              Current Legal Issue
            </h2>
            <p className="text-sm text-gray-600">
              Optionally describe a legal issue you&apos;re dealing with. You can
              always add this later.
            </p>
            <textarea
              value={form.currentIssue}
              onChange={(e) => update("currentIssue", e.target.value)}
              rows={5}
              placeholder="e.g. My landlord hasn't returned my security deposit after 45 days..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
            />
          </div>
        );

      default:
        return null;
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-lg">
        {/* Progress bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">
              Step {step} of {TOTAL_STEPS}
            </span>
            <span className="text-sm text-gray-500">
              {Math.round((step / TOTAL_STEPS) * 100)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(step / TOTAL_STEPS) * 100}%` }}
            />
          </div>
        </div>

        {/* Card */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
          {renderStep()}

          {error && (
            <p className="mt-4 text-sm text-red-600 bg-red-50 rounded-lg p-3">
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
                {submitting ? "Creating profile..." : "Start Chatting"}
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
