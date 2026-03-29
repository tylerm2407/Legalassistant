"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";
import AttorneyCard from "@/components/AttorneyCard";
import { useTranslation } from "@/lib/i18n";
import translations from "@/lib/i18n/translations";

interface Attorney {
  id: string;
  name: string;
  state: string;
  zip_code: string;
  specializations: string[];
  rating: number;
  cost_range: string;
  phone: string;
  email: string;
  website: string;
  accepts_free_consultations: boolean;
  bio: string;
}

interface ReferralSuggestion {
  attorney: Attorney;
  match_reason: string;
  relevance_score: number;
}

/**
 * Attorney search and referral page for finding legal representation.
 *
 * Allows users to search for attorneys by state and legal area, displaying
 * AI-matched results with relevance scores, specializations, ratings, and
 * contact information via AttorneyCard components.
 */
export default function AttorneysPage() {
  const { user, loading: authLoading } = useAuth();
  const { t, locale } = useTranslation();
  const [suggestions, setSuggestions] = useState<ReferralSuggestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchState, setSearchState] = useState("");
  const [searchArea, setSearchArea] = useState("");
  const [searchZip, setSearchZip] = useState("");

  useEffect(() => {
    if (authLoading || !user) return;
    setLoading(false);
  }, [user, authLoading]);

  async function handleSearch() {
    if (!searchState) return;
    setLoading(true);
    try {
      const data = await api.findAttorneys(searchState, searchArea || undefined, searchZip || undefined);
      setSuggestions(data);
    } catch {
      // silent
    } finally {
      setLoading(false);
    }
  }

  const areaLookup = translations.attorneyAreas[locale] as Record<string, string>;
  const legalAreaKeys = [
    "",
    "landlord_tenant",
    "employment_rights",
    "consumer_protection",
    "family_law",
    "criminal_records",
    "immigration",
    "debt_collections",
    "traffic_violations",
    "small_claims",
    "contract_disputes",
  ];

  return (
    <div className="min-h-screen bg-[#050505] p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold text-white mb-2">{t("findAttorney")}</h1>
        <p className="text-gray-400 mb-8">{t("findAttorneyDescription")}</p>

        {/* Search */}
        <div className="flex gap-3 mb-8">
          <input
            type="text"
            placeholder={t("statePlaceholder")}
            value={searchState}
            onChange={(e) => setSearchState(e.target.value.toUpperCase().slice(0, 2))}
            maxLength={2}
            className="w-24 px-3 py-2 bg-white/[0.03] text-white border border-white/10 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500/50 placeholder:text-gray-600 uppercase"
          />
          <input
            type="text"
            placeholder={t("zipPlaceholder")}
            value={searchZip}
            onChange={(e) => setSearchZip(e.target.value.replace(/\D/g, "").slice(0, 5))}
            maxLength={5}
            className="w-28 px-3 py-2 bg-white/[0.03] text-white border border-white/10 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500/50 placeholder:text-gray-600"
          />
          <select
            value={searchArea}
            onChange={(e) => setSearchArea(e.target.value)}
            className="flex-1 px-3 py-2 bg-white/[0.03] text-white border border-white/10 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500/50 [color-scheme:dark]"
          >
            {legalAreaKeys.map((key: string) => (
              <option key={key} value={key} className="bg-[#1a1a1a]">
                {areaLookup[key] ?? key}
              </option>
            ))}
          </select>
          <button
            onClick={handleSearch}
            disabled={!searchState || loading}
            className="px-4 py-2 bg-blue-500 text-white text-sm font-medium rounded-lg hover:bg-blue-400 disabled:opacity-50 disabled:hover:bg-blue-500 shadow-glow-sm transition-all"
          >
            {t("search")}
          </button>
        </div>

        {/* Results */}
        {loading ? (
          <div className="flex justify-center py-12">
            <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : suggestions.length > 0 ? (
          <div className="space-y-4">
            {suggestions.map((s: ReferralSuggestion) => (
              <AttorneyCard
                key={s.attorney.id}
                attorney={s.attorney}
                matchReason={s.match_reason}
                relevanceScore={s.relevance_score}
              />
            ))}
          </div>
        ) : searchState ? (
          <div className="text-center py-12">
            <p className="text-gray-500 mb-2">{t("noAttorneysFound")}</p>
            <p className="text-xs text-gray-600">{t("tryBroadening")}</p>
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-500">{t("enterStateToSearch")}</p>
          </div>
        )}
      </div>
    </div>
  );
}
