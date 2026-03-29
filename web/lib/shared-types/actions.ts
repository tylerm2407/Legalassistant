/**
 * AI-generated demand letter with legal citations from the user's profile context.
 *
 * @property letter_text - The full text of the demand letter, ready to send
 * @property legal_citations - Array of legal statute citations referenced in the letter
 */
export interface DemandLetter {
  letter_text: string;
  legal_citations: string[];
}

/**
 * AI-generated summary of the user's legal rights for their specific situation and state.
 *
 * @property summary_text - Narrative summary of the user's rights
 * @property key_rights - Enumerated list of specific rights the user is entitled to
 */
export interface RightsSummary {
  summary_text: string;
  key_rights: string[];
}

/**
 * AI-generated legal action checklist with associated deadlines.
 *
 * @property items - Ordered list of action items the user should complete
 * @property deadlines - Parallel array of deadline strings (null if no deadline for that item)
 */
export interface Checklist {
  items: string[];
  deadlines: (string | null)[];
}
