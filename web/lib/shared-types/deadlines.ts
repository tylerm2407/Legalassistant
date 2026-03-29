/**
 * A tracked legal deadline or statute of limitations.
 *
 * @property id - Unique deadline identifier
 * @property user_id - The user who owns this deadline
 * @property title - Short description of the deadline
 * @property date - ISO date string for when the deadline expires
 * @property legal_area - Optional legal domain category
 * @property source_conversation_id - Conversation ID if auto-detected from chat
 * @property status - Current status: active, completed, dismissed, or expired
 * @property notes - Additional notes about the deadline
 * @property created_at - ISO timestamp of creation
 */
export interface Deadline {
  id: string;
  user_id: string;
  title: string;
  date: string;
  legal_area: string | null;
  source_conversation_id: string | null;
  status: "active" | "completed" | "dismissed" | "expired";
  notes: string;
  created_at: string;
}

/**
 * Request body for creating a new legal deadline.
 *
 * @property title - Short description of the deadline
 * @property date - ISO date string for the deadline date
 * @property legal_area - Optional legal domain for categorization
 * @property notes - Optional notes about the deadline
 */
export interface DeadlineCreateRequest {
  title: string;
  date: string;
  legal_area?: string;
  notes?: string;
}

/**
 * Partial update fields for modifying an existing deadline.
 *
 * @property title - Updated title
 * @property date - Updated date
 * @property status - New status (active, completed, dismissed, expired)
 * @property notes - Updated notes
 */
export interface DeadlineUpdateRequest {
  title?: string;
  date?: string;
  status?: "active" | "completed" | "dismissed" | "expired";
  notes?: string;
}
