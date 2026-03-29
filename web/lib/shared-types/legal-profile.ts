export type IssueStatus = "open" | "resolved" | "watching" | "escalated";

export interface LegalIssue {
  issue_type: string;
  summary: string;
  status: IssueStatus;
  started_at: string;
  updated_at: string;
  notes: string[];
}

export interface LegalProfile {
  user_id: string;
  display_name: string;
  state: string;
  housing_situation: string;
  employment_type: string;
  family_status: string;
  active_issues: LegalIssue[];
  legal_facts: string[];
  documents: string[];
  member_since: string;
  conversation_count: number;
}
