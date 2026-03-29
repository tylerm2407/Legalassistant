/**
 * A single message in a CaseMate chat conversation.
 *
 * @property role - Who sent the message: "user", "assistant" (CaseMate), or "error"
 * @property content - The message text content
 * @property timestamp - When the message was sent
 * @property legalArea - Optional classified legal domain (e.g., "landlord_tenant")
 */
export interface Message {
  role: "user" | "assistant" | "error";
  content: string;
  timestamp: Date;
  legalArea?: string;
}

/**
 * Response from the CaseMate chat API after processing a legal question.
 *
 * @property conversation_id - ID of the conversation this message belongs to
 * @property answer - CaseMate's personalized legal guidance response
 * @property legal_area - Classified legal domain of the question
 * @property suggested_actions - Actions CaseMate suggests (e.g., "Generate demand letter")
 */
export interface ChatResponse {
  conversation_id: string;
  answer: string;
  legal_area: string;
  suggested_actions: string[];
}

/**
 * Abbreviated conversation data for display in the conversation history sidebar.
 *
 * @property id - Unique conversation identifier
 * @property legal_area - Classified legal domain, or null if not yet classified
 * @property updated_at - ISO timestamp of the most recent message
 * @property preview - Truncated text of the first user message
 * @property message_count - Total messages in the conversation
 */
export interface ConversationSummary {
  id: string;
  legal_area: string | null;
  updated_at: string;
  preview: string;
  message_count: number;
}

/**
 * Full conversation data including all messages, used when loading a conversation.
 *
 * @property id - Unique conversation identifier
 * @property user_id - The user who owns this conversation
 * @property messages - Complete array of messages in chronological order
 * @property legal_area - Overall classified legal domain of the conversation
 * @property created_at - ISO timestamp of conversation creation
 * @property updated_at - ISO timestamp of last activity
 */
export interface ConversationDetail {
  id: string;
  user_id: string;
  messages: {
    role: "user" | "assistant" | "error";
    content: string;
    timestamp: string;
    legal_area: string | null;
  }[];
  legal_area: string | null;
  created_at: string;
  updated_at: string;
}
