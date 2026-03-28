export interface DemandLetter {
  letter_text: string;
  legal_citations: string[];
}

export interface RightsSummary {
  summary_text: string;
  key_rights: string[];
}

export interface Checklist {
  items: string[];
  deadlines: (string | null)[];
}
