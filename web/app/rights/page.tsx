"use client";

import React, { useState } from "react";
import RightsGuide from "@/components/RightsGuide";
import { useTranslation } from "@/lib/i18n";
import { RIGHTS_DOMAINS, RIGHTS_GUIDES } from "@/lib/rights-data";
import type { RightsGuide as GuideType, RightsDomain } from "@/lib/rights-data";
import { ArrowLeft, ArrowRight } from "@phosphor-icons/react";

/**
 * "Know Your Rights" library page with domain browsing and guide detail views.
 *
 * Uses static data embedded in the frontend — no backend required.
 * Two-level navigation: first shows legal domain categories (e.g., Housing,
 * Employment), then guides within the selected domain. Selecting a guide
 * renders the full RightsGuide component with rights, action steps, deadlines,
 * and common mistakes.
 */
export default function RightsPage() {
  const { t } = useTranslation();
  const [selectedDomain, setSelectedDomain] = useState<string | null>(null);
  const [selectedGuide, setSelectedGuide] = useState<GuideType | null>(null);

  const domains: RightsDomain[] = RIGHTS_DOMAINS;
  const guides: GuideType[] = selectedDomain
    ? RIGHTS_GUIDES.filter((g) => g.domain === selectedDomain)
    : [];

  function handleDomainSelect(domain: string) {
    setSelectedDomain(domain);
    setSelectedGuide(null);
  }

  if (selectedGuide) {
    return (
      <div className="min-h-screen bg-bg">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <button
            onClick={() => setSelectedGuide(null)}
            className="font-sans text-sm text-ink-secondary hover:text-ink-primary mb-8 flex items-center gap-2 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" weight="regular" />
            {t("backToGuides")}
          </button>
          <RightsGuide guide={selectedGuide} />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-bg">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="mb-12 max-w-[65ch]">
          {selectedDomain && (
            <button
              onClick={() => { setSelectedDomain(null); }}
              className="font-sans text-sm text-ink-secondary hover:text-ink-primary mb-6 flex items-center gap-2 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" weight="regular" />
              {t("allCategories")}
            </button>
          )}
          <h1 className="font-serif text-5xl md:text-6xl font-medium tracking-tight leading-tight text-ink-primary">
            Know your rights
          </h1>
          <p className="font-sans text-base text-ink-secondary mt-4">
            {selectedDomain
              ? "Pick a guide to read what you're entitled to and what to do next."
              : "Plain-language guides for the situations people actually find themselves in."}
          </p>
        </div>

        {/* Domain grid or Guide list */}
        {!selectedDomain ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {domains.map((d: RightsDomain) => (
              <button
                key={d.domain}
                onClick={() => handleDomainSelect(d.domain)}
                className="text-left bg-white border border-border rounded-lg p-6 hover:border-border-strong hover:bg-bg-hover transition-colors group"
              >
                <h3 className="font-serif text-2xl font-medium tracking-tight text-ink-primary mb-2 group-hover:text-accent transition-colors">
                  {d.label}
                </h3>
                <p className="font-sans text-sm text-ink-tertiary">
                  {d.guide_count} {d.guide_count === 1 ? t("guide") : t("guides")}
                </p>
              </button>
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {guides.map((guide: GuideType) => (
              <button
                key={guide.id}
                onClick={() => setSelectedGuide(guide)}
                className="w-full text-left bg-white border border-border rounded-lg p-6 hover:border-border-strong hover:bg-bg-hover transition-colors group"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <h3 className="font-serif text-2xl font-medium tracking-tight text-ink-primary mb-2 group-hover:text-accent transition-colors">
                      {guide.title}
                    </h3>
                    <p className="font-sans text-base text-ink-secondary max-w-[65ch]">
                      {guide.description}
                    </p>
                  </div>
                  <ArrowRight className="w-5 h-5 text-ink-tertiary shrink-0 mt-1 group-hover:text-accent transition-colors" weight="regular" />
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
