import type {
  LegalProfile,
  ChatResponse,
  DemandLetter,
  RightsSummary,
  Checklist,
} from "./types";

const API_BASE = "/api";

export const api = {
  async chat(params: {
    userId: string;
    question: string;
    conversationId?: string;
  }): Promise<ChatResponse> {
    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: params.userId,
        question: params.question,
        conversation_id: params.conversationId,
      }),
    });
    if (!res.ok) throw new Error(`Chat failed: ${res.status}`);
    return res.json();
  },

  async getProfile(userId: string): Promise<LegalProfile | null> {
    const res = await fetch(`${API_BASE}/profile/${userId}`);
    if (res.status === 404) return null;
    if (!res.ok) throw new Error(`Profile fetch failed: ${res.status}`);
    return res.json();
  },

  async createProfile(profile: Partial<LegalProfile>): Promise<LegalProfile> {
    const res = await fetch(`${API_BASE}/profile`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(profile),
    });
    if (!res.ok) throw new Error(`Profile create failed: ${res.status}`);
    return res.json();
  },

  async generateLetter(
    userId: string,
    context?: string
  ): Promise<DemandLetter> {
    const res = await fetch(`${API_BASE}/actions/letter`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, context }),
    });
    if (!res.ok) throw new Error(`Letter generation failed: ${res.status}`);
    return res.json();
  },

  async generateRights(
    userId: string,
    context?: string
  ): Promise<RightsSummary> {
    const res = await fetch(`${API_BASE}/actions/rights`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, context }),
    });
    if (!res.ok) throw new Error(`Rights summary failed: ${res.status}`);
    return res.json();
  },

  async generateChecklist(
    userId: string,
    context?: string
  ): Promise<Checklist> {
    const res = await fetch(`${API_BASE}/actions/checklist`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, context }),
    });
    if (!res.ok) throw new Error(`Checklist generation failed: ${res.status}`);
    return res.json();
  },

  async uploadDocument(
    userId: string,
    file: File
  ): Promise<{
    filename: string;
    key_facts: string[];
    red_flags: string[];
    summary: string;
  }> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("user_id", userId);

    const res = await fetch(`${API_BASE}/documents/upload`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error(`Document upload failed: ${res.status}`);
    return res.json();
  },
};
