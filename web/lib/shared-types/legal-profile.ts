/** Possible statuses for a tracked legal issue. */
export type IssueStatus = "open" | "resolved" | "watching" | "escalated";

/**
 * A tracked legal issue or dispute in the user's profile.
 *
 * @property issue_type - Category of the issue (e.g., "landlord_tenant", "employment")
 * @property summary - Brief description of the issue
 * @property status - Current resolution status
 * @property started_at - ISO timestamp when the issue was first recorded
 * @property updated_at - ISO timestamp of the last update
 * @property notes - Chronological notes added over time by CaseMate or the user
 */
export interface LegalIssue {
  issue_type: string;
  summary: string;
  status: IssueStatus;
  started_at: string;
  updated_at: string;
  notes: string[];
}

/**
 * The user's persistent legal context stored in Supabase.
 *
 * This is the single most important data model in CaseMate. It is injected
 * into every Claude API call via the memory injector to provide personalized,
 * state-specific legal guidance. Fields come from onboarding intake or are
 * automatically extracted from conversations by the profile auto-updater.
 *
 * @property user_id - Supabase auth user ID (primary key)
 * @property display_name - User's preferred name shown in the UI
 * @property state - US state of residence, determines which laws apply
 * @property housing_situation - Housing arrangement (renter, homeowner, etc.)
 * @property employment_type - Employment classification affecting legal rights
 * @property family_status - Marital/family status for family law context
 * @property language_preference - ISO language code for response language ("en" or "es")
 * @property active_issues - Ongoing legal disputes being tracked
 * @property legal_facts - Specific facts extracted from conversations over time
 * @property documents - References to uploaded legal documents in Supabase Storage
 * @property member_since - ISO timestamp of account creation
 * @property conversation_count - Total number of conversations for engagement tracking
 */
export interface LegalProfile {
  user_id: string;
  display_name: string;
  state: string;
  housing_situation: string;
  employment_type: string;
  family_status: string;
  language_preference: "en" | "es";
  active_issues: LegalIssue[];
  legal_facts: string[];
  documents: string[];
  member_since: string;
  conversation_count: number;
}
