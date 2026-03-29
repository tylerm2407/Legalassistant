"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";
import AttorneyCard from "@/components/AttorneyCard";

interface Attorney {
  id: string;
  name: string;
  state: string;
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

export default function AttorneysPage() {
  const { user, loading: authLoading } = useAuth();
  const [suggestions, setSuggestions] = useState<ReferralSuggestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchState, setSearchState] = useState("");
  const [searchArea, setSearchArea] = useState("");

  useEffect(() => {
    if (authLoading || !user) return;
    setLoading(false);
  }, [user, authLoading]);

  async function handleSearch() {
    if (!searchState) return;
    setLoading(true);
    try {
      const data = await api.findAttorneys(searchState, searchArea || undefined);
      setSuggestions(data);
    } catch {
      // silent
    } finally {
      setLoading(false);
    }
  }

  const legalAreas = [
    { value: "", label: "All areas" },
    { value: "landlord_tenant", label: "Housing & Tenant" },
    { value: "employment_rights", label: "Employment" },
    { value: "consumer_protection", label: "Consumer Protection" },
    { value: "family_law", label: "Family Law" },
    { value: "criminal_records", label: "Criminal Defense" },
    { value: "immigration", label: "Immigration" },
    { value: "debt_collections", label: "Debt & Collections" },
    { value: "traffic_violations", label: "Traffic & DUI" },
    { value: "small_claims", label: "Small Claims" },
    { value: "contract_disputes", label: "Contracts" },
  ];

  return (
    <div className="min-h-screen bg-[#050505] p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold text-white mb-2">Find an Attorney</h1>
        <p className="text-gray-400 mb-8">Find attorneys in your area who specialize in your legal issue</p>

        {/* Search */}
        <div className="flex gap-3 mb-8">
          <input
            type="text"
            placeholder="State (e.g., CA)"
            value={searchState}
            onChange={(e) => setSearchState(e.target.value.toUpperCase().slice(0, 2))}
            maxLength={2}
            className="w-24 px-3 py-2 bg-white/[0.03] text-white border border-white/10 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500/50 placeholder:text-gray-600 uppercase"
          />
          <select
            value={searchArea}
            onChange={(e) => setSearchArea(e.target.value)}
            className="flex-1 px-3 py-2 bg-white/[0.03] text-white border border-white/10 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500/50 [color-scheme:dark]"
          >
            {legalAreas.map((area: { value: string; label: string }) => (
              <option key={area.value} value={area.value} className="bg-[#1a1a1a]">
                {area.label}
              </option>
            ))}
          </select>
          <button
            onClick={handleSearch}
            disabled={!searchState || loading}
            className="px-4 py-2 bg-blue-500 text-white text-sm font-medium rounded-lg hover:bg-blue-400 disabled:opacity-50 disabled:hover:bg-blue-500 shadow-glow-sm transition-all"
          >
            Search
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
            <p className="text-gray-500 mb-2">No attorneys found</p>
            <p className="text-xs text-gray-600">Try broadening your search criteria</p>
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-500">Enter a state to search for attorneys</p>
          </div>
        )}
      </div>
    </div>
  );
}
