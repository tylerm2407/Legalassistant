export interface Attorney {
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

export interface ReferralSuggestion {
  attorney: Attorney;
  match_reason: string;
  relevance_score: number;
}
