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
