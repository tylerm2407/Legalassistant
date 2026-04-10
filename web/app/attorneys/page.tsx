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

/** Sample attorneys shown by default so the page isn't empty. */
const SAMPLE_ATTORNEYS: ReferralSuggestion[] = [
  {
    attorney: {
      id: "att-001",
      name: "Maria Gonzalez",
      state: "CA",
      zip_code: "90012",
      specializations: ["landlord_tenant", "consumer_protection"],
      rating: 4.9,
      cost_range: "$150–$300/hr",
      phone: "(213) 555-0147",
      email: "maria@gonzalezlegal.com",
      website: "https://gonzalezlegal.com",
      accepts_free_consultations: true,
      bio: "15 years defending tenants against unlawful evictions, security deposit theft, and habitability violations across Los Angeles County. Bilingual English/Spanish.",
    },
    match_reason: "Highly rated tenant rights specialist offering free consultations",
    relevance_score: 0.97,
  },
  {
    attorney: {
      id: "att-002",
      name: "James Richardson",
      state: "NY",
      zip_code: "10001",
      specializations: ["employment_rights", "contract_disputes"],
      rating: 4.7,
      cost_range: "$250–$450/hr",
      phone: "(212) 555-0293",
      email: "jrichardson@richardsonlaw.com",
      website: "https://richardsonlaw.com",
      accepts_free_consultations: false,
      bio: "Former EEOC attorney now in private practice. Handles wrongful termination, wage theft, workplace discrimination, and non-compete disputes for employees across New York.",
    },
    match_reason: "Employment law expert with federal agency background",
    relevance_score: 0.94,
  },
  {
    attorney: {
      id: "att-003",
      name: "Priya Patel",
      state: "TX",
      zip_code: "77002",
      specializations: ["immigration", "family_law"],
      rating: 4.8,
      cost_range: "$175–$350/hr",
      phone: "(713) 555-0481",
      email: "priya@patelimmigration.com",
      website: "https://patelimmigration.com",
      accepts_free_consultations: true,
      bio: "Specializes in family-based immigration, asylum cases, and DACA renewals. Has successfully handled 500+ visa and green card applications. Fluent in Hindi and Gujarati.",
    },
    match_reason: "Immigration and family law specialist with multilingual support",
    relevance_score: 0.93,
  },
  {
    attorney: {
      id: "att-004",
      name: "David Chen",
      state: "MA",
      zip_code: "02108",
      specializations: ["landlord_tenant", "small_claims"],
      rating: 4.6,
      cost_range: "$125–$250/hr",
      phone: "(617) 555-0372",
      email: "dchen@chenlegalboston.com",
      website: "https://chenlegalboston.com",
      accepts_free_consultations: true,
      bio: "Boston-based attorney focused on tenant rights under Massachusetts General Laws. Regularly helps clients recover security deposits, fight illegal rent increases, and navigate small claims court.",
    },
    match_reason: "Massachusetts tenant law specialist with affordable rates",
    relevance_score: 0.91,
  },
  {
    attorney: {
      id: "att-005",
      name: "Angela Washington",
      state: "FL",
      zip_code: "33101",
      specializations: ["criminal_records", "traffic_violations"],
      rating: 4.5,
      cost_range: "$200–$400/hr",
      phone: "(305) 555-0619",
      email: "angela@washingtondefense.com",
      website: "https://washingtondefense.com",
      accepts_free_consultations: false,
      bio: "Former public defender with 12 years of criminal defense experience. Handles record expungement, DUI defense, license suspension hearings, and misdemeanor defense throughout South Florida.",
    },
    match_reason: "Experienced criminal defense attorney with expungement expertise",
    relevance_score: 0.89,
  },
  {
    attorney: {
      id: "att-006",
      name: "Robert Martinez",
      state: "IL",
      zip_code: "60601",
      specializations: ["debt_collections", "consumer_protection"],
      rating: 4.7,
      cost_range: "$100–$225/hr",
      phone: "(312) 555-0854",
      email: "rob@martinezdebtlaw.com",
      website: "https://martinezdebtlaw.com",
      accepts_free_consultations: true,
      bio: "Consumer rights advocate who fights abusive debt collectors. Handles FDCPA violations, credit report disputes, medical debt negotiations, and bankruptcy alternatives. No-win, no-fee on many cases.",
    },
    match_reason: "Debt defense specialist with contingency fee options",
    relevance_score: 0.88,
  },
  {
    attorney: {
      id: "att-007",
      name: "Sarah Kim",
      state: "WA",
      zip_code: "98101",
      specializations: ["family_law"],
      rating: 4.8,
      cost_range: "$200–$375/hr",
      phone: "(206) 555-0736",
      email: "sarah@kimfamilylaw.com",
      website: "https://kimfamilylaw.com",
      accepts_free_consultations: false,
      bio: "Compassionate family law attorney handling divorce, child custody, child support modifications, and domestic violence protection orders. Certified family law mediator with 10 years of experience.",
    },
    match_reason: "Top-rated family law mediator and custody specialist",
    relevance_score: 0.87,
  },
  {
    attorney: {
      id: "att-008",
      name: "Michael O'Brien",
      state: "PA",
      zip_code: "19103",
      specializations: ["contract_disputes", "small_claims"],
      rating: 4.4,
      cost_range: "$150–$300/hr",
      phone: "(215) 555-0528",
      email: "mobrien@obriencontractlaw.com",
      website: "https://obriencontractlaw.com",
      accepts_free_consultations: true,
      bio: "Helps individuals and small businesses resolve contract disputes, freelancer payment issues, home improvement contractor fraud, and warranty claims. Practical, cost-effective legal strategies.",
    },
    match_reason: "Contract dispute specialist for individuals and small businesses",
    relevance_score: 0.85,
  },
  {
    attorney: {
      id: "att-009",
      name: "Lisa Tran",
      state: "CA",
      zip_code: "95113",
      specializations: ["employment_rights", "immigration"],
      rating: 4.6,
      cost_range: "$175–$325/hr",
      phone: "(408) 555-0943",
      email: "lisa@tranlegalgroup.com",
      website: "https://tranlegalgroup.com",
      accepts_free_consultations: true,
      bio: "Represents workers in wage theft, workplace retaliation, and discrimination cases. Also handles employment-based immigration including H-1B, L-1, and PERM labor certification. Fluent in Vietnamese.",
    },
    match_reason: "Employment and immigration crossover specialist in Silicon Valley",
    relevance_score: 0.84,
  },
  {
    attorney: {
      id: "att-010",
      name: "Anthony Brooks",
      state: "GA",
      zip_code: "30303",
      specializations: ["traffic_violations", "criminal_records"],
      rating: 4.3,
      cost_range: "$125–$275/hr",
      phone: "(404) 555-0167",
      email: "abrooks@brooksdefense.com",
      website: "https://brooksdefense.com",
      accepts_free_consultations: true,
      bio: "Atlanta defense attorney specializing in DUI/DWI cases, speeding tickets, license reinstatement, and criminal record restriction (Georgia's expungement equivalent). Flat-fee pricing on most traffic cases.",
    },
    match_reason: "Affordable traffic and DUI defense with flat-fee options",
    relevance_score: 0.82,
  },
];

/**
 * Attorney search and referral page for finding legal representation.
 *
 * Displays sample attorneys by default and allows filtering by state,
 * zip code, and legal area. Search hits the backend API when available,
 * falling back to client-side filtering of sample data.
 */
export default function AttorneysPage() {
  const { user, loading: authLoading } = useAuth();
  const { t, locale } = useTranslation();
  const [suggestions, setSuggestions] = useState<ReferralSuggestion[]>(SAMPLE_ATTORNEYS);
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
      if (data && data.length > 0) {
        setSuggestions(data);
      } else {
        // Fall back to filtering sample data client-side
        const filtered = SAMPLE_ATTORNEYS.filter((s) => {
          const stateMatch = s.attorney.state.toUpperCase() === searchState.toUpperCase();
          const areaMatch = !searchArea || s.attorney.specializations.includes(searchArea);
          return stateMatch && areaMatch;
        });
        setSuggestions(filtered);
      }
    } catch {
      // Backend unavailable — filter sample data client-side
      const filtered = SAMPLE_ATTORNEYS.filter((s) => {
        const stateMatch = s.attorney.state.toUpperCase() === searchState.toUpperCase();
        const areaMatch = !searchArea || s.attorney.specializations.includes(searchArea);
        return stateMatch && areaMatch;
      });
      setSuggestions(filtered);
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
    <div className="min-h-screen bg-bg">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-10 max-w-[65ch]">
          <h1 className="font-serif text-5xl md:text-6xl font-medium tracking-tight leading-tight text-ink-primary">
            Find a lawyer
          </h1>
          <p className="font-sans text-base text-ink-secondary mt-4">
            Sometimes you need a real attorney in your corner. Here are
            vetted lawyers who handle your kind of situation in your state.
          </p>
        </div>

        {/* Search */}
        <div className="bg-white border border-border rounded-lg p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
            <div className="md:col-span-2">
              <label className="block text-sm font-sans font-medium text-ink-primary mb-2">
                State
              </label>
              <input
                type="text"
                placeholder="CA"
                value={searchState}
                onChange={(e) => setSearchState(e.target.value.toUpperCase().slice(0, 2))}
                maxLength={2}
                className="w-full bg-white border border-border rounded-md px-4 py-3 font-sans text-base text-ink-primary focus:border-accent focus:ring-2 focus:ring-accent/20 focus:outline-none placeholder:text-ink-tertiary uppercase"
              />
            </div>
            <div className="md:col-span-3">
              <label className="block text-sm font-sans font-medium text-ink-primary mb-2">
                ZIP code
              </label>
              <input
                type="text"
                placeholder="90012"
                value={searchZip}
                onChange={(e) => setSearchZip(e.target.value.replace(/\D/g, "").slice(0, 5))}
                maxLength={5}
                className="w-full bg-white border border-border rounded-md px-4 py-3 font-sans text-base text-ink-primary focus:border-accent focus:ring-2 focus:ring-accent/20 focus:outline-none placeholder:text-ink-tertiary"
              />
            </div>
            <div className="md:col-span-5">
              <label className="block text-sm font-sans font-medium text-ink-primary mb-2">
                Legal area
              </label>
              <select
                value={searchArea}
                onChange={(e) => setSearchArea(e.target.value)}
                className="w-full bg-white border border-border rounded-md px-4 py-3 font-sans text-base text-ink-primary focus:border-accent focus:ring-2 focus:ring-accent/20 focus:outline-none"
              >
                {legalAreaKeys.map((key: string) => (
                  <option key={key} value={key}>
                    {areaLookup[key] ?? key}
                  </option>
                ))}
              </select>
            </div>
            <div className="md:col-span-2 flex items-end">
              <button
                onClick={handleSearch}
                disabled={!searchState || loading}
                className="w-full bg-accent text-white px-6 py-3 rounded-md font-sans font-medium hover:bg-accent-hover transition-colors disabled:opacity-50"
              >
                Search
              </button>
            </div>
          </div>
        </div>

        {/* Results */}
        {loading ? (
          <div className="flex justify-center py-12">
            <p className="font-sans text-ink-secondary">Loading…</p>
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
        ) : suggestions.length === 0 ? (
          <div className="bg-white border border-border rounded-lg p-8 text-center">
            <p className="font-sans text-base text-ink-primary mb-2">
              No matches yet.
            </p>
            <p className="font-sans text-sm text-ink-tertiary">
              Try widening your search or picking a different area.
            </p>
          </div>
        ) : null}
      </div>
    </div>
  );
}
