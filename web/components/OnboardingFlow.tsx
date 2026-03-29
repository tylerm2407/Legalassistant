"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Button from "./ui/Button";
import Input from "./ui/Input";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { useTranslation } from "@/lib/i18n";
import translations from "@/lib/i18n/translations";

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
const TOTAL_STEPS = 6;

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
 * @property languagePreference - Preferred response language ("en" or "es")
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
  languagePreference: string;
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
 * 6. Language preference (optional — defaults to English)
 */
export default function OnboardingFlow() {
  const router = useRouter();
  const { user } = useAuth();
  const { t, locale } = useTranslation();
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
    languagePreference: "en",
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
      case 6:
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
      setError(t("mustBeSignedIn"));
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
        language_preference: form.languagePreference as "en" | "es",
      });
    } catch {
      // Profile creation failed — continue to subscription regardless
    }

    setSubmitting(false);
    router.push(`/subscription?userId=${userId}`);
  }

  const stepOfLabel = translations.stepOf[locale];

  function renderStep() {
    switch (step) {
      case 1:
        return (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-white">
              {t("letsGetToKnowYou")}
            </h2>
            <p className="text-sm text-gray-400">
              {t("onboardingPersonalizeNote")}
            </p>
            <Input
              label={t("yourName")}
              placeholder={t("namePlaceholder")}
              value={form.displayName}
              onChange={(e) => update("displayName", e.target.value)}
            />
            <div>
              <label htmlFor="onboarding-state" className="block text-sm font-medium text-gray-300 mb-1">
                {t("state")}
              </label>
              <select
                id="onboarding-state"
                value={form.state}
                onChange={(e) => update("state", e.target.value)}
                className="w-full px-3 py-2 bg-white/[0.03] text-white border border-white/10 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500/50"
              >
                <option value="" className="text-black bg-white">{t("selectYourState")}</option>
                {US_STATES.map((s: string) => (
                  <option key={s} value={s} className="text-black bg-white">
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
              {t("housingSituationTitle")}
            </h2>
            <p className="text-sm text-gray-400">
              {t("housingNote")}
            </p>
            <div className="space-y-2">
              {[
                { value: "renter", label: t("renter") },
                { value: "homeowner", label: t("homeowner") },
                { value: "other", label: t("other") },
              ].map((opt) => (
                <label
                  key={opt.value}
                  className={`flex items-center gap-3 p-3 border rounded-lg cursor-pointer transition-all ${
                    form.housingSituation === opt.value
                      ? "border-blue-500 bg-blue-500/10 shadow-glow-sm"
                      : "border-white/10 hover:border-white/20 hover:bg-white/[0.03]"
                  }`}
                >
                  <input
                    type="radio"
                    name="housing"
                    value={opt.value}
                    checked={form.housingSituation === opt.value}
                    onChange={(e) => update("housingSituation", e.target.value)}
                    className="text-blue-500"
                  />
                  <span className="text-sm text-gray-200">{opt.label}</span>
                </label>
              ))}
            </div>
            <Input
              label={t("detailsOptional")}
              placeholder={t("housingDetailPlaceholder")}
              value={form.housingDetails}
              onChange={(e) => update("housingDetails", e.target.value)}
            />
          </div>
        );

      case 3:
        return (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-white">
              {t("employmentTypeTitle")}
            </h2>
            <p className="text-sm text-gray-400">
              {t("employmentNote")}
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
              label={t("detailsOptional")}
              placeholder={t("employmentDetailPlaceholder")}
              value={form.employmentDetails}
              onChange={(e) => update("employmentDetails", e.target.value)}
            />
          </div>
        );

      case 4:
        return (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-white">
              {t("familyStatusTitle")}
            </h2>
            <p className="text-sm text-gray-400">
              {t("familyNote")}
            </p>
            <div className="space-y-2">
              {[
                { value: "single", label: t("single") },
                { value: "married", label: t("married") },
                { value: "divorced", label: t("divorced") },
                { value: "widowed", label: t("widowed") },
                { value: "domestic partnership", label: t("domesticPartnership") },
              ].map(
                (opt) => (
                  <label
                    key={opt.value}
                    className={`flex items-center gap-3 p-3 border rounded-lg cursor-pointer transition-all ${
                      form.familyStatus === opt.value
                        ? "border-blue-500 bg-blue-500/10 shadow-glow-sm"
                        : "border-white/10 hover:border-white/20 hover:bg-white/[0.03]"
                    }`}
                  >
                    <input
                      type="radio"
                      name="family"
                      value={opt.value}
                      checked={form.familyStatus === opt.value}
                      onChange={(e) => update("familyStatus", e.target.value)}
                      className="text-blue-500"
                    />
                    <span className="text-sm text-gray-200">{opt.label}</span>
                  </label>
                )
              )}
            </div>
            <Input
              label={t("numberOfDependents")}
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
              {t("currentLegalIssue")}
            </h2>
            <p className="text-sm text-gray-400">
              {t("legalIssueNote")}
            </p>
            <textarea
              value={form.currentIssue}
              onChange={(e) => update("currentIssue", e.target.value)}
              rows={5}
              placeholder={t("legalIssuePlaceholder")}
              className="w-full px-3 py-2 bg-white/[0.03] text-white border border-white/10 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500/50 resize-none placeholder:text-gray-600"
            />
          </div>
        );

      case 6:
        return (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-white">
              {t("preferredLanguage")}
            </h2>
            <p className="text-sm text-gray-400">
              {t("languageNote")}
            </p>
            <div className="flex gap-3">
              {(
                [
                  { code: "en", label: t("english") },
                  { code: "es", label: t("spanish") },
                ] as const
              ).map((lang) => (
                <button
                  key={lang.code}
                  type="button"
                  onClick={() => update("languagePreference", lang.code)}
                  className={`flex-1 py-3 px-4 rounded-lg border text-sm font-medium transition-all ${
                    form.languagePreference === lang.code
                      ? "border-blue-500 bg-blue-500/10 text-white shadow-glow-sm"
                      : "border-white/10 text-gray-400 hover:border-white/20 hover:bg-white/[0.03]"
                  }`}
                >
                  {lang.label}
                </button>
              ))}
            </div>
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
              {typeof stepOfLabel === "function" ? stepOfLabel(step, TOTAL_STEPS) : `${t("step")} ${step} ${t("of")} ${TOTAL_STEPS}`}
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
            {t("onboardingSecureNotice")}
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
              {t("back")}
            </Button>

            {step < TOTAL_STEPS ? (
              <Button onClick={() => setStep((s) => s + 1)} disabled={!canAdvance()}>
                {t("next")}
              </Button>
            ) : (
              <Button onClick={handleSubmit} disabled={submitting}>
                {submitting ? t("settingUp") : t("continue_")}
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
