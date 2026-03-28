import type {
  LegalProfile,
  ChatResponse,
  DemandLetter,
  RightsSummary,
  Checklist,
  ConversationSummary,
  ConversationDetail,
  Deadline,
  DeadlineCreateRequest,
  DeadlineUpdateRequest,
  RightsDomain,
  RightsGuide,
  WorkflowTemplate,
  WorkflowInstance,
  WorkflowSummary,
  ReferralSuggestion,
} from "./types";
import { supabase } from "./supabase";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api";

async function getAuthHeaders(): Promise<Record<string, string>> {
  const { data: { session } } = await supabase.auth.getSession();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (session?.access_token) {
    headers["Authorization"] = `Bearer ${session.access_token}`;
  }
  return headers;
}

async function fetchWithRetry(
  url: string,
  options: RequestInit,
  retries = 3,
): Promise<Response> {
  for (let attempt = 0; attempt < retries; attempt++) {
    try {
      const res = await fetch(url, options);
      if (res.ok || (res.status >= 400 && res.status < 500)) {
        return res;
      }
      // 5xx — retry
      if (attempt < retries - 1) {
        await new Promise((r) => setTimeout(r, 1000 * Math.pow(2, attempt)));
        continue;
      }
      return res;
    } catch (err) {
      if (attempt < retries - 1) {
        await new Promise((r) => setTimeout(r, 1000 * Math.pow(2, attempt)));
        continue;
      }
      throw err;
    }
  }
  throw new Error("Request failed after retries");
}

export const api = {
  async chat(params: {
    userId: string;
    question: string;
    conversationId?: string;
  }): Promise<ChatResponse> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/chat`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        message: params.question,
        conversation_id: params.conversationId,
      }),
    });
    if (!res.ok) throw new Error(`Chat failed: ${res.status}`);
    return res.json();
  },

  async getProfile(userId: string): Promise<LegalProfile | null> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/profile/${userId}`, {
      headers,
    });
    if (res.status === 404) return null;
    if (!res.ok) throw new Error(`Profile fetch failed: ${res.status}`);
    const data = await res.json();
    return data.profile || data;
  },

  async createProfile(profile: Partial<LegalProfile>): Promise<LegalProfile> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/profile`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        display_name: profile.display_name,
        state: profile.state,
        housing_situation: profile.housing_situation,
        employment_type: profile.employment_type,
        family_status: profile.family_status,
      }),
    });
    if (!res.ok) throw new Error(`Profile create failed: ${res.status}`);
    const data = await res.json();
    return data.profile || data;
  },

  async generateLetter(
    userId: string,
    context?: string
  ): Promise<DemandLetter> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/actions/letter`, {
      method: "POST",
      headers,
      body: JSON.stringify({ context: context || "" }),
    });
    if (!res.ok) throw new Error(`Letter generation failed: ${res.status}`);
    return res.json();
  },

  async generateRights(
    userId: string,
    context?: string
  ): Promise<RightsSummary> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/actions/rights`, {
      method: "POST",
      headers,
      body: JSON.stringify({ context: context || "" }),
    });
    if (!res.ok) throw new Error(`Rights summary failed: ${res.status}`);
    return res.json();
  },

  async generateChecklist(
    userId: string,
    context?: string
  ): Promise<Checklist> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/actions/checklist`, {
      method: "POST",
      headers,
      body: JSON.stringify({ context: context || "" }),
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
    const { data: { session } } = await supabase.auth.getSession();
    const headers: Record<string, string> = {};
    if (session?.access_token) {
      headers["Authorization"] = `Bearer ${session.access_token}`;
    }

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetchWithRetry(`${API_BASE}/documents`, {
      method: "POST",
      headers,
      body: formData,
    });
    if (!res.ok) throw new Error(`Document upload failed: ${res.status}`);
    return res.json();
  },

  // Conversations
  async getConversations(): Promise<ConversationSummary[]> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/conversations`, { headers });
    if (!res.ok) throw new Error(`Failed to load conversations: ${res.status}`);
    const data = await res.json();
    return data.conversations || [];
  },

  async getConversation(conversationId: string): Promise<ConversationDetail> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/conversations/${conversationId}`, { headers });
    if (!res.ok) throw new Error(`Failed to load conversation: ${res.status}`);
    const data = await res.json();
    return data.conversation;
  },

  async deleteConversation(conversationId: string): Promise<void> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/conversations/${conversationId}`, {
      method: "DELETE",
      headers,
    });
    if (!res.ok) throw new Error(`Failed to delete conversation: ${res.status}`);
  },

  // Deadlines
  async getDeadlines(): Promise<Deadline[]> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/deadlines`, { headers });
    if (!res.ok) throw new Error(`Failed to load deadlines: ${res.status}`);
    const data = await res.json();
    return data.deadlines || [];
  },

  async createDeadline(deadline: DeadlineCreateRequest): Promise<Deadline> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/deadlines`, {
      method: "POST",
      headers,
      body: JSON.stringify(deadline),
    });
    if (!res.ok) throw new Error(`Failed to create deadline: ${res.status}`);
    const data = await res.json();
    return data.deadline;
  },

  async updateDeadline(deadlineId: string, updates: DeadlineUpdateRequest): Promise<Deadline> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/deadlines/${deadlineId}`, {
      method: "PATCH",
      headers,
      body: JSON.stringify(updates),
    });
    if (!res.ok) throw new Error(`Failed to update deadline: ${res.status}`);
    const data = await res.json();
    return data.deadline;
  },

  // Rights Library
  async getRightsDomains(): Promise<RightsDomain[]> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/rights/domains`, { headers });
    if (!res.ok) throw new Error(`Failed to load rights domains: ${res.status}`);
    const data = await res.json();
    return data.domains || [];
  },

  async getRightsGuides(domain: string): Promise<RightsGuide[]> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/rights/guides?domain=${domain}`, { headers });
    if (!res.ok) throw new Error(`Failed to load rights guides: ${res.status}`);
    const data = await res.json();
    return data.guides || [];
  },

  async getRightsGuide(guideId: string): Promise<RightsGuide> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/rights/guides/${guideId}`, { headers });
    if (!res.ok) throw new Error(`Failed to load rights guide: ${res.status}`);
    const data = await res.json();
    return data.guide;
  },

  // Workflows
  async getWorkflowTemplates(): Promise<WorkflowTemplate[]> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/workflows/templates`, { headers });
    if (!res.ok) throw new Error(`Failed to load workflow templates: ${res.status}`);
    const data = await res.json();
    return data.templates || [];
  },

  async startWorkflow(templateId: string): Promise<WorkflowInstance> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/workflows`, {
      method: "POST",
      headers,
      body: JSON.stringify({ template_id: templateId }),
    });
    if (!res.ok) throw new Error(`Failed to start workflow: ${res.status}`);
    const data = await res.json();
    return data.workflow;
  },

  async getActiveWorkflows(): Promise<WorkflowSummary[]> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/workflows`, { headers });
    if (!res.ok) throw new Error(`Failed to load workflows: ${res.status}`);
    const data = await res.json();
    return data.workflows || [];
  },

  async getWorkflow(workflowId: string): Promise<WorkflowInstance> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/workflows/${workflowId}`, { headers });
    if (!res.ok) throw new Error(`Failed to load workflow: ${res.status}`);
    const data = await res.json();
    return data.workflow;
  },

  async updateWorkflowStep(workflowId: string, stepIndex: number, status: string): Promise<WorkflowInstance> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/workflows/${workflowId}/steps`, {
      method: "PATCH",
      headers,
      body: JSON.stringify({ step_index: stepIndex, status }),
    });
    if (!res.ok) throw new Error(`Failed to update workflow step: ${res.status}`);
    const data = await res.json();
    return data.workflow;
  },

  // Attorney Referrals
  async findAttorneys(state: string, legalArea?: string): Promise<ReferralSuggestion[]> {
    const headers = await getAuthHeaders();
    let url = `${API_BASE}/attorneys/search?state=${state}`;
    if (legalArea) url += `&legal_area=${legalArea}`;
    const res = await fetchWithRetry(url, { headers });
    if (!res.ok) throw new Error(`Failed to search attorneys: ${res.status}`);
    const data = await res.json();
    return data.suggestions || [];
  },

  // Export
  async exportPdf(params: { type: string; content: Record<string, unknown> }): Promise<Blob> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/export/document`, {
      method: "POST",
      headers,
      body: JSON.stringify(params),
    });
    if (!res.ok) throw new Error(`Export failed: ${res.status}`);
    return res.blob();
  },

  async exportEmail(params: { type: string; content: Record<string, unknown>; email: string }): Promise<void> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/export/email`, {
      method: "POST",
      headers,
      body: JSON.stringify(params),
    });
    if (!res.ok) throw new Error(`Email export failed: ${res.status}`);
  },
};
