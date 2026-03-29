"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";
import RightsGuide from "@/components/RightsGuide";

interface Domain {
  domain: string;
  label: string;
  guide_count: number;
}

interface Guide {
  id: string;
  domain: string;
  title: string;
  description: string;
  explanation: string;
  your_rights: string[];
  action_steps: string[];
  deadlines: string[];
  common_mistakes: string[];
  when_to_get_a_lawyer: string;
}

export default function RightsPage() {
  const { user, loading: authLoading } = useAuth();
  const [domains, setDomains] = useState<Domain[]>([]);
  const [guides, setGuides] = useState<Guide[]>([]);
  const [selectedDomain, setSelectedDomain] = useState<string | null>(null);
  const [selectedGuide, setSelectedGuide] = useState<Guide | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading || !user) return;
    async function loadDomains() {
      try {
        const data = await api.getRightsDomains();
        setDomains(data);
      } catch {
        // silent
      } finally {
        setLoading(false);
      }
    }
    loadDomains();
  }, [user, authLoading]);

  async function handleDomainSelect(domain: string) {
    setSelectedDomain(domain);
    setSelectedGuide(null);
    setLoading(true);
    try {
      const data = await api.getRightsGuides(domain);
      setGuides(data);
    } catch {
      // silent
    } finally {
      setLoading(false);
    }
  }

  if (authLoading || (loading && !selectedDomain)) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
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
            Back to guides
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
              onClick={() => { setSelectedDomain(null); setGuides([]); }}
              className="text-sm text-gray-400 hover:text-white mb-4 flex items-center gap-1.5 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
              </svg>
              All categories
            </button>
          )}
          <h1 className="text-2xl font-bold text-white mb-2">Know Your Rights</h1>
          <p className="text-gray-400">
            {selectedDomain
              ? "Select a guide to learn about your rights"
              : "Browse legal rights guides by category"}
          </p>
        </div>

        {/* Domain grid or Guide list */}
        {!selectedDomain ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {domains.map((d: Domain) => (
              <button
                key={d.domain}
                onClick={() => handleDomainSelect(d.domain)}
                className="text-left p-5 bg-white/[0.03] backdrop-blur-xl rounded-xl border border-white/10 hover:border-blue-500/30 hover:shadow-glow-sm transition-all group"
              >
                <h3 className="text-base font-semibold text-white mb-1 group-hover:text-blue-400 transition-colors">
                  {d.label}
                </h3>
                <p className="text-xs text-gray-500">
                  {d.guide_count} {d.guide_count === 1 ? "guide" : "guides"}
                </p>
              </button>
            ))}
          </div>
        ) : loading ? (
          <div className="flex justify-center py-12">
            <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <div className="space-y-3">
            {guides.map((guide: Guide) => (
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
