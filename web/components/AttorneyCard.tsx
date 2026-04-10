"use client";

import React from "react";
import { useTranslation } from "@/lib/i18n";
import { Star, Phone, Envelope, Globe, MapPin } from "@phosphor-icons/react";

/**
 * Attorney profile data for referral display.
 *
 * @property id - Unique attorney identifier
 * @property name - Attorney's full name
 * @property state - Two-letter state code where the attorney is licensed
 * @property zip_code - Attorney's office zip code (5 digits)
 * @property specializations - Legal practice areas (e.g., ["landlord_tenant", "consumer_protection"])
 * @property rating - Average rating from 0 to 5
 * @property cost_range - Display string for typical fee range (e.g., "$200-$400/hr")
 * @property phone - Attorney's contact phone number
 * @property email - Attorney's contact email address
 * @property website - Attorney's website URL
 * @property accepts_free_consultations - Whether the attorney offers free initial consultations
 * @property bio - Brief professional biography
 */
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

/**
 * Props for the AttorneyCard component.
 *
 * @property attorney - Complete attorney profile data to display
 * @property matchReason - AI-generated explanation of why this attorney matches the user's needs
 * @property relevanceScore - Numeric relevance score (0-1) for ranking match quality
 */
interface AttorneyCardProps {
  attorney: Attorney;
  matchReason: string;
  relevanceScore: number;
}

/**
 * Display card for an attorney referral with contact links and match details.
 *
 * Shows the attorney's name, specializations, rating, cost range, bio, and
 * an AI-generated explanation of why they match the user's legal needs.
 * Includes direct call, email, and website links for easy contact.
 *
 * @param props - Component props
 * @param props.attorney - Attorney profile data
 * @param props.matchReason - Why this attorney is a good match for the user
 * @param props.relevanceScore - Numeric relevance ranking
 */
export default function AttorneyCard({ attorney, matchReason, relevanceScore }: AttorneyCardProps) {
  const { t } = useTranslation();
  return (
    <div className="bg-white border border-border rounded-lg p-6 hover:border-border-strong transition-colors">
      <div className="flex items-start justify-between gap-6">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 mb-2 flex-wrap">
            <h3 className="font-serif font-medium tracking-tight text-ink-primary text-xl leading-tight">
              {attorney.name}
            </h3>
            {attorney.accepts_free_consultations && (
              <span className="inline-flex items-center text-xs font-sans font-medium text-accent bg-accent-subtle border border-accent/20 rounded-md px-2 py-0.5">
                {t("freeConsult")}
              </span>
            )}
          </div>

          {matchReason && (
            <p className="text-sm font-sans text-accent mb-3">{matchReason}</p>
          )}

          {attorney.bio && (
            <p className="text-sm font-sans text-ink-secondary leading-relaxed mb-4">
              {attorney.bio}
            </p>
          )}

          <div className="flex flex-wrap gap-1.5 mb-4">
            {attorney.specializations.map((spec: string) => (
              <span
                key={spec}
                className="inline-flex items-center text-xs font-sans font-medium text-ink-secondary bg-bg border border-border rounded-md px-2 py-0.5 capitalize"
              >
                {spec.replace(/_/g, " ")}
              </span>
            ))}
          </div>

          <div className="flex items-center gap-5 text-sm font-sans text-ink-tertiary flex-wrap">
            {attorney.cost_range && <span>{attorney.cost_range}</span>}
            {attorney.rating > 0 && (
              <span className="flex items-center gap-1">
                <Star className="w-4 h-4 text-ink-secondary" weight="regular" />
                {attorney.rating.toFixed(1)}
              </span>
            )}
            <span className="flex items-center gap-1">
              <MapPin className="w-4 h-4" weight="regular" />
              {attorney.state}
              {attorney.zip_code ? ` ${attorney.zip_code}` : ""}
            </span>
          </div>
        </div>

        <div className="flex flex-col gap-2 shrink-0">
          {attorney.phone && (
            <a
              href={`tel:${attorney.phone}`}
              className="flex items-center gap-2 text-sm font-sans text-accent hover:text-accent-hover transition-colors"
            >
              <Phone className="w-4 h-4" weight="regular" />
              {t("call")}
            </a>
          )}
          {attorney.email && (
            <a
              href={`mailto:${attorney.email}`}
              className="flex items-center gap-2 text-sm font-sans text-accent hover:text-accent-hover transition-colors"
            >
              <Envelope className="w-4 h-4" weight="regular" />
              {t("email")}
            </a>
          )}
          {attorney.website && (
            <a
              href={attorney.website}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-sm font-sans text-accent hover:text-accent-hover transition-colors"
            >
              <Globe className="w-4 h-4" weight="regular" />
              {t("website")}
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
