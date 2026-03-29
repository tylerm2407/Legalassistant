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

/** Base URL for the CaseMate backend API. Falls back to relative path for same-origin requests. */
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api";

/**
 * Retrieves authentication headers from the current Supabase session.
 *
 * Includes the JWT access token as a Bearer token in the Authorization header
 * when a session exists. Always includes Content-Type: application/json.
 *
 * @returns Headers object with Content-Type and optional Authorization
 */
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

/**
 * Fetch wrapper with exponential backoff retry for transient server errors.
 *
 * Retries up to 3 times on 5xx errors and network failures with exponential
 * backoff (1s, 2s, 4s). Client errors (4xx) are returned immediately without retry.
 *
 * @param url - The URL to fetch
 * @param options - Standard fetch RequestInit options
 * @param retries - Maximum number of retry attempts (default: 3)
 * @returns The fetch Response
 * @throws {Error} If all retry attempts fail
 */
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

/**
 * CaseMate API client.
 *
 * Provides typed methods for all backend endpoints including chat, profile management,
 * action generation, document upload, conversations, deadlines, rights library,
 * workflows, attorney referrals, and export. All methods automatically include
 * Supabase auth headers and use retry logic for resilience.
 */
export const api = {
  /**
   * Sends a legal question to the CaseMate chat API.
   *
   * The backend injects the user's legal profile into Claude's system prompt,
   * classifies the legal area, and returns a personalized response with citations.
   *
   * @param params - Chat request parameters
   * @param params.userId - The authenticated user's Supabase ID
   * @param params.question - The user's legal question
   * @param params.conversationId - Optional conversation ID for continuing an existing thread
   * @returns Chat response with answer, legal area classification, and suggested actions
   * @throws {Error} If the chat API request fails
   */
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

  /**
   * Fetches the user's legal profile from Supabase via the backend.
   *
   * @param userId - The authenticated user's Supabase ID
   * @returns The user's complete legal profile, or null if not found
   * @throws {Error} If the API request fails (non-404 errors)
   */
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

  /**
   * Creates or updates a user's legal profile in Supabase.
   *
   * @param profile - Partial profile data (at minimum: display_name, state, housing, employment, family)
   * @returns The created or updated legal profile
   * @throws {Error} If the profile creation fails
   */
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

  /**
   * Generates a demand letter using the user's legal profile and conversation context.
   *
   * @param userId - The authenticated user's Supabase ID
   * @param context - Optional additional context to guide letter generation
   * @returns Generated demand letter with text and legal citations
   * @throws {Error} If letter generation fails
   */
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

  /**
   * Generates a rights summary tailored to the user's state and legal situation.
   *
   * @param userId - The authenticated user's Supabase ID
   * @param context - Optional additional context to focus the summary
   * @returns Rights summary with narrative text and enumerated key rights
   * @throws {Error} If rights summary generation fails
   */
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

  /**
   * Generates a legal action checklist with deadlines based on the user's profile.
   *
   * @param userId - The authenticated user's Supabase ID
   * @param context - Optional additional context to customize the checklist
   * @returns Checklist with ordered action items and associated deadlines
   * @throws {Error} If checklist generation fails
   */
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

  /**
   * Uploads a legal document for AI-powered analysis and fact extraction.
   *
   * The backend extracts text from the document, sends it to Claude for legal
   * analysis, and returns key facts, red flags, and a summary. Extracted facts
   * are automatically added to the user's legal profile.
   *
   * @param userId - The authenticated user's Supabase ID
   * @param file - The file to upload (PDF, image, or text, max 10MB)
   * @returns Analysis results with filename, key facts, red flags, and summary
   * @throws {Error} If the upload or analysis fails
   */
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

  /**
   * Fetches all conversation summaries for the authenticated user.
   *
   * @returns Array of conversation summaries sorted by most recent
   * @throws {Error} If the request fails
   */
  async getConversations(): Promise<ConversationSummary[]> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/conversations`, { headers });
    if (!res.ok) throw new Error(`Failed to load conversations: ${res.status}`);
    const data = await res.json();
    return data.conversations || [];
  },

  /**
   * Fetches a full conversation with all messages by ID.
   *
   * @param conversationId - The conversation's unique identifier
   * @returns Complete conversation detail including all messages
   * @throws {Error} If the conversation is not found or request fails
   */
  async getConversation(conversationId: string): Promise<ConversationDetail> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/conversations/${conversationId}`, { headers });
    if (!res.ok) throw new Error(`Failed to load conversation: ${res.status}`);
    const data = await res.json();
    return data.conversation;
  },

  /**
   * Deletes a conversation and all its messages.
   *
   * @param conversationId - The conversation's unique identifier
   * @throws {Error} If the deletion fails
   */
  async deleteConversation(conversationId: string): Promise<void> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/conversations/${conversationId}`, {
      method: "DELETE",
      headers,
    });
    if (!res.ok) throw new Error(`Failed to delete conversation: ${res.status}`);
  },

  /**
   * Fetches all deadlines for the authenticated user.
   *
   * @returns Array of deadlines including active, completed, and dismissed
   * @throws {Error} If the request fails
   */
  async getDeadlines(): Promise<Deadline[]> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/deadlines`, { headers });
    if (!res.ok) throw new Error(`Failed to load deadlines: ${res.status}`);
    const data = await res.json();
    return data.deadlines || [];
  },

  /**
   * Creates a new legal deadline for the authenticated user.
   *
   * @param deadline - Deadline creation parameters (title, date, optional notes/legal area)
   * @returns The created deadline with server-generated ID
   * @throws {Error} If creation fails
   */
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

  /**
   * Updates an existing deadline's title, date, status, or notes.
   *
   * @param deadlineId - The deadline's unique identifier
   * @param updates - Partial update fields to apply
   * @returns The updated deadline
   * @throws {Error} If the update fails
   */
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

  /**
   * Fetches all legal rights domains (categories) from the knowledge base.
   *
   * @returns Array of rights domains with labels and guide counts
   * @throws {Error} If the request fails
   */
  async getRightsDomains(): Promise<RightsDomain[]> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/rights/domains`, { headers });
    if (!res.ok) throw new Error(`Failed to load rights domains: ${res.status}`);
    const data = await res.json();
    return data.domains || [];
  },

  /**
   * Fetches rights guides for a specific legal domain.
   *
   * @param domain - The legal domain to fetch guides for (e.g., "landlord_tenant")
   * @returns Array of rights guides within the specified domain
   * @throws {Error} If the request fails
   */
  async getRightsGuides(domain: string): Promise<RightsGuide[]> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/rights/guides?domain=${domain}`, { headers });
    if (!res.ok) throw new Error(`Failed to load rights guides: ${res.status}`);
    const data = await res.json();
    return data.guides || [];
  },

  /**
   * Fetches a single rights guide by ID with full content.
   *
   * @param guideId - The guide's unique identifier
   * @returns Complete rights guide with all sections
   * @throws {Error} If the guide is not found or request fails
   */
  async getRightsGuide(guideId: string): Promise<RightsGuide> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/rights/guides/${guideId}`, { headers });
    if (!res.ok) throw new Error(`Failed to load rights guide: ${res.status}`);
    const data = await res.json();
    return data.guide;
  },

  /**
   * Fetches all available workflow templates.
   *
   * @returns Array of workflow templates with steps, domain, and estimated time
   * @throws {Error} If the request fails
   */
  async getWorkflowTemplates(): Promise<WorkflowTemplate[]> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/workflows/templates`, { headers });
    if (!res.ok) throw new Error(`Failed to load workflow templates: ${res.status}`);
    const data = await res.json();
    return data.templates || [];
  },

  /**
   * Starts a new workflow instance from a template.
   *
   * @param templateId - The template ID to instantiate
   * @returns The created workflow instance with all steps initialized
   * @throws {Error} If workflow creation fails
   */
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

  /**
   * Fetches all active workflow instances for the authenticated user.
   *
   * @returns Array of workflow summaries with progress information
   * @throws {Error} If the request fails
   */
  async getActiveWorkflows(): Promise<WorkflowSummary[]> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/workflows`, { headers });
    if (!res.ok) throw new Error(`Failed to load workflows: ${res.status}`);
    const data = await res.json();
    return data.workflows || [];
  },

  /**
   * Fetches a complete workflow instance with all steps by ID.
   *
   * @param workflowId - The workflow instance's unique identifier
   * @returns Complete workflow instance with current progress
   * @throws {Error} If the workflow is not found or request fails
   */
  async getWorkflow(workflowId: string): Promise<WorkflowInstance> {
    const headers = await getAuthHeaders();
    const res = await fetchWithRetry(`${API_BASE}/workflows/${workflowId}`, { headers });
    if (!res.ok) throw new Error(`Failed to load workflow: ${res.status}`);
    const data = await res.json();
    return data.workflow;
  },

  /**
   * Updates the status of a specific step within a workflow.
   *
   * @param workflowId - The workflow instance's unique identifier
   * @param stepIndex - Zero-based index of the step to update
   * @param status - New status for the step (e.g., "completed", "skipped")
   * @returns Updated workflow instance reflecting the change
   * @throws {Error} If the update fails
   */
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

  /**
   * Searches for attorneys matching the user's state and legal area.
   *
   * @param state - Two-letter US state code to search within
   * @param legalArea - Optional legal domain to filter by (e.g., "landlord_tenant")
   * @returns Array of attorney referral suggestions with match reasons and relevance scores
   * @throws {Error} If the search fails
   */
  async findAttorneys(state: string, legalArea?: string): Promise<ReferralSuggestion[]> {
    const headers = await getAuthHeaders();
    let url = `${API_BASE}/attorneys/search?state=${state}`;
    if (legalArea) url += `&legal_area=${legalArea}`;
    const res = await fetchWithRetry(url, { headers });
    if (!res.ok) throw new Error(`Failed to search attorneys: ${res.status}`);
    const data = await res.json();
    return data.suggestions || [];
  },

  /**
   * Exports a legal document (letter, rights summary, etc.) as a downloadable PDF.
   *
   * @param params - Export parameters
   * @param params.type - Document type to export
   * @param params.content - Document content to render into PDF
   * @returns PDF file as a Blob
   * @throws {Error} If the export fails
   */
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

  /**
   * Exports a legal document by sending it to the specified email address.
   *
   * @param params - Export parameters
   * @param params.type - Document type to export
   * @param params.content - Document content to include in the email
   * @param params.email - Recipient email address
   * @throws {Error} If the email export fails
   */
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
