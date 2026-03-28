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

export interface DeadlineCreateRequest {
  title: string;
  date: string;
  legal_area?: string;
  notes?: string;
}

export interface DeadlineUpdateRequest {
  title?: string;
  date?: string;
  status?: "active" | "completed" | "dismissed" | "expired";
  notes?: string;
}
