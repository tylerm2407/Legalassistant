/**
 * A comprehensive legal rights guide from the CaseMate knowledge base.
 *
 * @property id - Unique guide identifier
 * @property domain - Legal domain category (e.g., "landlord_tenant")
 * @property title - Display title for the guide
 * @property description - Brief summary for guide listings
 * @property explanation - Detailed plain-language legal explanation
 * @property your_rights - Enumerated rights the user has under this area of law
 * @property action_steps - Ordered concrete steps the user should take
 * @property deadlines - Relevant statutes of limitations and filing deadlines
 * @property common_mistakes - Pitfalls to avoid that could harm the user's case
 * @property when_to_get_a_lawyer - Guidance on when professional counsel is needed
 */
export interface RightsGuide {
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

/**
 * A legal domain category in the rights library with its guide count.
 *
 * @property domain - Machine-readable domain identifier (e.g., "landlord_tenant")
 * @property label - Human-readable display label (e.g., "Housing & Tenant Rights")
 * @property guide_count - Number of guides available in this domain
 */
export interface RightsDomain {
  domain: string;
  label: string;
  guide_count: number;
}
