"use client";

import React, { useState } from "react";
import RightsGuide from "@/components/RightsGuide";
import { useTranslation } from "@/lib/i18n";
import { RIGHTS_DOMAINS, RIGHTS_GUIDES } from "@/lib/rights-data";
import type { RightsGuide as GuideType, RightsDomain } from "@/lib/rights-data";

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
      <div className="min-h-screen bg-[#050505] p-6">
        <div className="max-w-4xl mx-auto">
          <button
            onClick={() => setSelectedGuide(null)}
            className="text-sm text-gray-400 hover:text-white mb-6 flex items-center gap-1.5 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
            {t("backToGuides")}
          </button>
          <RightsGuide guide={selectedGuide} />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#050505] p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          {selectedDomain && (
            <button
              onClick={() => { setSelectedDomain(null); }}
              className="text-sm text-gray-400 hover:text-white mb-4 flex items-center gap-1.5 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
              </svg>
              {t("allCategories")}
            </button>
          )}
          <h1 className="text-2xl font-bold text-white mb-2">{t("knowYourRights")}</h1>
          <p className="text-gray-400">
            {selectedDomain
              ? t("selectGuidePrompt")
              : t("browseByCategory")}
          </p>
        </div>

        {/* Domain grid or Guide list */}
        {!selectedDomain ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {domains.map((d: RightsDomain) => (
              <button
                key={d.domain}
                onClick={() => handleDomainSelect(d.domain)}
                className="text-left p-5 bg-white/[0.03] backdrop-blur-xl rounded-xl border border-white/10 hover:border-blue-500/30 hover:shadow-glow-sm transition-all group"
              >
                <h3 className="text-base font-semibold text-white mb-1 group-hover:text-blue-400 transition-colors">
                  {d.label}
                </h3>
                <p className="text-xs text-gray-500">
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
                className="w-full text-left p-5 bg-white/[0.03] backdrop-blur-xl rounded-xl border border-white/10 hover:border-blue-500/30 hover:shadow-glow-sm transition-all"
              >
                <h3 className="text-base font-semibold text-white mb-1">{guide.title}</h3>
                <p className="text-sm text-gray-400">{guide.description}</p>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
