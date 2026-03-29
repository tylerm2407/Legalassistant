/**
 * Attorney profile data for the referral system.
 *
 * @property id - Unique attorney identifier
 * @property name - Attorney's full name
 * @property state - Two-letter state code where licensed
 * @property specializations - Legal practice area identifiers
 * @property rating - Average client rating (0-5)
 * @property cost_range - Display string for fee range
 * @property phone - Contact phone number
 * @property email - Contact email address
 * @property website - Attorney's website URL
 * @property accepts_free_consultations - Whether free initial consultations are offered
 * @property bio - Professional biography
 */
export interface Attorney {
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
 * An attorney referral suggestion with match context from the AI matching system.
 *
 * @property attorney - The matched attorney's full profile
 * @property match_reason - AI-generated explanation of why this attorney fits the user's needs
 * @property relevance_score - Numeric score (0-1) indicating match quality
 */
export interface ReferralSuggestion {
  attorney: Attorney;
  match_reason: string;
  relevance_score: number;
}
