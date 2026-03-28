export interface Message {
  role: "user" | "assistant" | "error";
  content: string;
  timestamp: Date;
  legalArea?: string;
}

export interface ChatResponse {
  conversation_id: string;
  answer: string;
  legal_area: string;
  suggested_actions: string[];
}

export interface ConversationSummary {
  id: string;
  legal_area: string | null;
  updated_at: string;
  preview: string;
  message_count: number;
}

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
