"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Button from "./ui/Button";
import Input from "./ui/Input";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { useTranslation } from "@/lib/i18n";
import translations from "@/lib/i18n/translations";
import { Warning } from "@phosphor-icons/react";

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

    const profileData = {
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
              status: "open" as const,
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
    };

    // Save to localStorage so chat works without backend
    try {
      localStorage.setItem("casemate_profile", JSON.stringify(profileData));
    } catch {
      // localStorage unavailable — continue
    }

    try {
      await api.createProfile(profileData);
    } catch {
      // Profile creation failed — continue to subscription regardless
    }

    setSubmitting(false);
    router.push(`/subscription?userId=${userId}`);
  }

  const stepOfLabel = translations.stepOf[locale];

  // Shared radio option styling: selected vs unselected
  const radioClass = (selected: boolean) =>
    `flex items-center gap-3 p-4 border rounded-md cursor-pointer transition-colors ${
      selected
        ? "border-accent bg-accent-subtle"
        : "border-border hover:border-border-strong hover:bg-bg-hover"
    }`;

  function renderStep() {
    switch (step) {
      case 1:
        return (
          <div className="space-y-6">
            <div className="space-y-3">
              <h2 className="font-serif font-medium tracking-tight leading-tight text-3xl text-ink-primary">
                {t("letsGetToKnowYou")}
              </h2>
              <p className="font-sans text-ink-secondary max-w-[65ch]">
                {t("onboardingPersonalizeNote")}
              </p>
            </div>
            <Input
              label={t("yourName")}
              placeholder={t("namePlaceholder")}
              value={form.displayName}
              onChange={(e) => update("displayName", e.target.value)}
            />
            <div>
              <label htmlFor="onboarding-state" className="block text-sm font-sans font-medium text-ink-primary mb-2">
                {t("state")}
              </label>
              <select
                id="onboarding-state"
                value={form.state}
                onChange={(e) => update("state", e.target.value)}
                className="w-full bg-white border border-border rounded-md px-4 py-3 font-sans text-sm text-ink-primary focus:border-accent focus:ring-2 focus:ring-accent/20"
              >
                <option value="">{t("selectYourState")}</option>
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
          <div className="space-y-6">
            <div className="space-y-3">
              <h2 className="font-serif font-medium tracking-tight leading-tight text-3xl text-ink-primary">
                {t("housingSituationTitle")}
              </h2>
              <p className="font-sans text-ink-secondary max-w-[65ch]">
                {t("housingNote")}
              </p>
            </div>
            <div className="space-y-3">
              {[
                { value: "renter", label: t("renter") },
                { value: "homeowner", label: t("homeowner") },
                { value: "other", label: t("other") },
              ].map((opt) => (
                <label
                  key={opt.value}
                  className={radioClass(form.housingSituation === opt.value)}
                >
                  <input
                    type="radio"
                    name="housing"
                    value={opt.value}
                    checked={form.housingSituation === opt.value}
                    onChange={(e) => update("housingSituation", e.target.value)}
                    className="accent-accent"
                  />
                  <span className="font-sans text-sm text-ink-primary">{opt.label}</span>
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
          <div className="space-y-6">
            <div className="space-y-3">
              <h2 className="font-serif font-medium tracking-tight leading-tight text-3xl text-ink-primary">
                {t("employmentTypeTitle")}
              </h2>
              <p className="font-sans text-ink-secondary max-w-[65ch]">
                {t("employmentNote")}
              </p>
            </div>
            <div className="space-y-3">
              {["W-2 Employee", "1099 Contractor", "Unemployed", "Student", "Retired"].map(
                (opt: string) => (
                  <label
                    key={opt}
                    className={radioClass(form.employmentType === opt.toLowerCase())}
                  >
                    <input
                      type="radio"
                      name="employment"
                      value={opt.toLowerCase()}
                      checked={form.employmentType === opt.toLowerCase()}
                      onChange={(e) =>
                        update("employmentType", e.target.value)
                      }
                      className="accent-accent"
                    />
                    <span className="font-sans text-sm text-ink-primary">{opt}</span>
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
          <div className="space-y-6">
            <div className="space-y-3">
              <h2 className="font-serif font-medium tracking-tight leading-tight text-3xl text-ink-primary">
                {t("familyStatusTitle")}
              </h2>
              <p className="font-sans text-ink-secondary max-w-[65ch]">
                {t("familyNote")}
              </p>
            </div>
            <div className="space-y-3">
              {[
                { value: "single", label: t("single") },
                { value: "married", label: t("married") },
                { value: "divorced", label: t("divorced") },
                { value: "widowed", label: t("widowed") },
                { value: "domestic partnership", label: t("domesticPartnership") },
              ].map((opt) => (
                <label
                  key={opt.value}
                  className={radioClass(form.familyStatus === opt.value)}
                >
                  <input
                    type="radio"
                    name="family"
                    value={opt.value}
                    checked={form.familyStatus === opt.value}
                    onChange={(e) => update("familyStatus", e.target.value)}
                    className="accent-accent"
                  />
                  <span className="font-sans text-sm text-ink-primary">{opt.label}</span>
                </label>
              ))}
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
          <div className="space-y-6">
            <div className="space-y-3">
              <h2 className="font-serif font-medium tracking-tight leading-tight text-3xl text-ink-primary">
                {t("currentLegalIssue")}
              </h2>
              <p className="font-sans text-ink-secondary max-w-[65ch]">
                {t("legalIssueNote")}
              </p>
            </div>
            <div>
              <label htmlFor="onboarding-issue" className="block text-sm font-sans font-medium text-ink-primary mb-2">
                {t("currentLegalIssue")}
              </label>
              <textarea
                id="onboarding-issue"
                value={form.currentIssue}
                onChange={(e) => update("currentIssue", e.target.value)}
                rows={5}
                placeholder={t("legalIssuePlaceholder")}
                className="w-full bg-white border border-border rounded-md px-4 py-3 font-sans text-sm text-ink-primary focus:border-accent focus:ring-2 focus:ring-accent/20 placeholder:text-ink-tertiary resize-none"
              />
            </div>
          </div>
        );

      case 6:
        return (
          <div className="space-y-6">
            <div className="space-y-3">
              <h2 className="font-serif font-medium tracking-tight leading-tight text-3xl text-ink-primary">
                {t("preferredLanguage")}
              </h2>
              <p className="font-sans text-ink-secondary max-w-[65ch]">
                {t("languageNote")}
              </p>
            </div>
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
                  className={`flex-1 py-3 px-4 rounded-md border font-sans font-medium text-sm transition-colors ${
                    form.languagePreference === lang.code
                      ? "border-accent bg-accent-subtle text-ink-primary"
                      : "border-border text-ink-secondary hover:border-border-strong hover:bg-bg-hover"
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
    <div className="min-h-screen bg-bg flex items-center justify-center p-6">
      <div className="w-full max-w-xl">
        {/* Step indicator */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-sans font-medium text-accent">
              {typeof stepOfLabel === "function"
                ? stepOfLabel(step, TOTAL_STEPS)
                : `${t("step")} ${step} ${t("of")} ${TOTAL_STEPS}`}
            </span>
            <span className="text-sm font-sans text-ink-tertiary">
              {Math.round((step / TOTAL_STEPS) * 100)}%
            </span>
          </div>
          <div className="flex items-center gap-2">
            {Array.from({ length: TOTAL_STEPS }).map((_, i) => {
              const isActive = i + 1 <= step;
              return (
                <div
                  key={i}
                  className={`h-1 flex-1 rounded-sm transition-colors ${
                    isActive ? "bg-accent" : "bg-border"
                  }`}
                />
              );
            })}
          </div>
          <p className="text-xs font-sans text-ink-tertiary mt-3">
            {t("onboardingSecureNotice")}
          </p>
        </div>

        {/* Card */}
        <div className="bg-white border border-border rounded-lg p-8">
          {renderStep()}

          {error && (
            <div className="mt-6 flex items-start gap-2 text-sm font-sans text-warning bg-warning-subtle border border-warning/30 rounded-md p-3">
              <Warning className="w-4 h-4 shrink-0 mt-0.5" weight="regular" />
              <span>{error}</span>
            </div>
          )}

          {/* Navigation */}
          <div className="flex items-center justify-between mt-8 pt-6 border-t border-border">
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
