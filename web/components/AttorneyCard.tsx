"use client";

import React from "react";
import Card from "./ui/Card";
import Badge from "./ui/Badge";

/**
 * Attorney profile data for referral display.
 *
 * @property id - Unique attorney identifier
 * @property name - Attorney's full name
 * @property state - Two-letter state code where the attorney is licensed
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
  return (
    <Card>
      <Card.Body>
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="text-base font-semibold text-white">{attorney.name}</h3>
              {attorney.accepts_free_consultations && (
                <Badge variant="success" size="sm">Free consult</Badge>
              )}
            </div>
            <p className="text-xs text-blue-400 mb-2">{matchReason}</p>
            {attorney.bio && (
              <p className="text-sm text-gray-400 mb-3">{attorney.bio}</p>
            )}
            <div className="flex flex-wrap gap-1.5 mb-3">
              {attorney.specializations.map((spec: string) => (
                <Badge key={spec} variant="default" size="sm">
                  {spec.replace(/_/g, " ")}
                </Badge>
              ))}
            </div>
            <div className="flex items-center gap-4 text-xs text-gray-500">
              {attorney.cost_range && <span>{attorney.cost_range}</span>}
              {attorney.rating > 0 && (
                <span className="flex items-center gap-1">
                  <svg className="w-3.5 h-3.5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                  {attorney.rating.toFixed(1)}
                </span>
              )}
              <span>{attorney.state}</span>
            </div>
          </div>
          <div className="flex flex-col gap-2 shrink-0">
            {attorney.phone && (
              <a
                href={`tel:${attorney.phone}`}
                className="text-xs text-blue-400 hover:text-blue-300 transition-colors"
              >
                Call
              </a>
            )}
            {attorney.email && (
              <a
                href={`mailto:${attorney.email}`}
                className="text-xs text-blue-400 hover:text-blue-300 transition-colors"
              >
                Email
              </a>
            )}
            {attorney.website && (
              <a
                href={attorney.website}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-blue-400 hover:text-blue-300 transition-colors"
              >
                Website
              </a>
            )}
          </div>
        </div>
      </Card.Body>
    </Card>
  );
}
