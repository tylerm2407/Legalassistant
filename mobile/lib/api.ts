import type {
  ChatResponse,
  LegalProfile,
  DemandLetter,
  RightsSummary,
  Checklist,
  ConversationSummary,
  ConversationDetail,
  Deadline,
  DeadlineCreateRequest,
  RightsDomain,
  RightsGuide,
  WorkflowTemplate,
  WorkflowInstance,
  WorkflowSummary,
  ReferralSuggestion,
} from "./types";
import { supabase } from "./supabase";

const API_BASE = process.env.EXPO_PUBLIC_API_URL || "http://localhost:8000/api";

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
      const response = await fetch(url, options);
      if (response.ok || (response.status >= 400 && response.status < 500)) {
        return response;
      }
      if (attempt < retries - 1) {
        await new Promise((r) => setTimeout(r, 1000 * Math.pow(2, attempt)));
        continue;
      }
      return response;
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

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${path}`;
  const authHeaders = await getAuthHeaders();
  const headers: Record<string, string> = {
    ...authHeaders,
    ...(options.headers as Record<string, string>),
  };

  const response = await fetchWithRetry(url, { ...options, headers });

  if (!response.ok) {
    const errorBody = await response.text().catch(() => "Unknown error");
    throw new Error(`API error ${response.status}: ${errorBody}`);
  }

  return response.json() as Promise<T>;
}

export async function chat(
  userId: string,
  message: string,
  conversationId?: string
): Promise<ChatResponse> {
  return request<ChatResponse>("/chat", {
    method: "POST",
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
    }),
  });
}

export async function getProfile(userId: string): Promise<LegalProfile> {
  return request<LegalProfile>(`/profile/${userId}`);
}

export async function createProfile(
  profile: Partial<LegalProfile> & { user_id: string }
): Promise<LegalProfile> {
  return request<LegalProfile>("/profile", {
    method: "POST",
    body: JSON.stringify({
      display_name: profile.display_name,
      state: profile.state,
      housing_situation: profile.housing_situation,
      employment_type: profile.employment_type,
      family_status: profile.family_status,
    }),
  });
}

export async function generateLetter(
  userId: string,
  issueType: string,
  details: string
): Promise<DemandLetter> {
  return request<DemandLetter>("/actions/letter", {
    method: "POST",
    body: JSON.stringify({
      context: `${issueType}: ${details}`,
    }),
  });
}

export async function generateRights(
  userId: string,
  issueType: string
): Promise<RightsSummary> {
  return request<RightsSummary>("/actions/rights", {
    method: "POST",
    body: JSON.stringify({
      context: issueType,
    }),
  });
}

export async function generateChecklist(
  userId: string,
  issueType: string
): Promise<Checklist> {
  return request<Checklist>("/actions/checklist", {
    method: "POST",
    body: JSON.stringify({
      context: issueType,
    }),
  });
}

export async function uploadDocument(
  userId: string,
  fileUri: string,
  fileName: string,
  mimeType: string
): Promise<{ document_id: string; extracted_facts: string[] }> {
  const { data: { session } } = await supabase.auth.getSession();
  const headers: Record<string, string> = {};
  if (session?.access_token) {
    headers["Authorization"] = `Bearer ${session.access_token}`;
  }

  const formData = new FormData();
  formData.append("file", {
    uri: fileUri,
    name: fileName,
    type: mimeType,
  } as unknown as Blob);

  const url = `${API_BASE}/documents`;
  const response = await fetchWithRetry(url, {
    method: "POST",
    body: formData,
    headers,
  });

  if (!response.ok) {
    const errorBody = await response.text().catch(() => "Unknown error");
    throw new Error(`Upload error ${response.status}: ${errorBody}`);
  }

  return response.json();
}

// --- Conversations ---
export async function getConversations(
  userId: string
): Promise<{ conversations: ConversationSummary[] }> {
  return request<{ conversations: ConversationSummary[] }>("/conversations");
}

export async function getConversation(
  conversationId: string
): Promise<{ conversation: ConversationDetail }> {
  return request<{ conversation: ConversationDetail }>(`/conversations/${conversationId}`);
}

export async function deleteConversation(
  conversationId: string
): Promise<{ status: string }> {
  return request<{ status: string }>(`/conversations/${conversationId}`, {
    method: "DELETE",
  });
}

// --- Deadlines ---
export async function getDeadlines(
  userId: string
): Promise<{ deadlines: Deadline[] }> {
  return request<{ deadlines: Deadline[] }>("/deadlines");
}

export async function createDeadline(
  deadline: DeadlineCreateRequest
): Promise<{ deadline: Deadline }> {
  return request<{ deadline: Deadline }>("/deadlines", {
    method: "POST",
    body: JSON.stringify(deadline),
  });
}

export async function updateDeadline(
  deadlineId: string,
  update: Partial<Deadline>
): Promise<{ deadline: Deadline }> {
  return request<{ deadline: Deadline }>(`/deadlines/${deadlineId}`, {
    method: "PATCH",
    body: JSON.stringify(update),
  });
}

export async function deleteDeadline(
  deadlineId: string
): Promise<{ status: string }> {
  return request<{ status: string }>(`/deadlines/${deadlineId}`, {
    method: "DELETE",
  });
}

// --- Rights Library ---
export async function getRightsDomains(): Promise<{ domains: RightsDomain[] }> {
  return request<{ domains: RightsDomain[] }>("/rights/domains");
}

export async function getRightsGuides(
  domain?: string
): Promise<{ guides: RightsGuide[] }> {
  const query = domain ? `?domain=${domain}` : "";
  return request<{ guides: RightsGuide[] }>(`/rights/guides${query}`);
}

export async function getRightsGuide(
  guideId: string
): Promise<{ guide: RightsGuide }> {
  return request<{ guide: RightsGuide }>(`/rights/guides/${guideId}`);
}

// --- Workflows ---
export async function getWorkflowTemplates(
  domain?: string
): Promise<{ templates: WorkflowTemplate[] }> {
  const query = domain ? `?domain=${domain}` : "";
  return request<{ templates: WorkflowTemplate[] }>(`/workflows/templates${query}`);
}

export async function startWorkflow(
  templateId: string
): Promise<{ workflow: WorkflowInstance }> {
  return request<{ workflow: WorkflowInstance }>("/workflows", {
    method: "POST",
    body: JSON.stringify({ template_id: templateId }),
  });
}

export async function getActiveWorkflows(): Promise<{ workflows: WorkflowSummary[] }> {
  return request<{ workflows: WorkflowSummary[] }>("/workflows");
}

export async function getWorkflow(
  workflowId: string
): Promise<{ workflow: WorkflowInstance }> {
  return request<{ workflow: WorkflowInstance }>(`/workflows/${workflowId}`);
}

export async function updateWorkflowStep(
  workflowId: string,
  stepIndex: number,
  status: string
): Promise<{ workflow: WorkflowInstance }> {
  return request<{ workflow: WorkflowInstance }>(`/workflows/${workflowId}/steps`, {
    method: "PATCH",
    body: JSON.stringify({ step_index: stepIndex, status }),
  });
}

// --- Attorneys ---
export async function findAttorneys(
  state: string,
  legalArea?: string
): Promise<{ suggestions: ReferralSuggestion[] }> {
  const params = new URLSearchParams({ state });
  if (legalArea) params.append("legal_area", legalArea);
  return request<{ suggestions: ReferralSuggestion[] }>(`/attorneys/search?${params}`);
}

// --- Export ---
export async function exportPdf(
  type: string,
  content: Record<string, unknown>
): Promise<Blob> {
  const url = `${API_BASE}/export/document`;
  const headers = await getAuthHeaders();
  const response = await fetchWithRetry(url, {
    method: "POST",
    headers,
    body: JSON.stringify({ type, content }),
  });
  if (!response.ok) {
    throw new Error(`Export error ${response.status}`);
  }
  return response.blob();
}
