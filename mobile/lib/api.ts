import type {
  ChatResponse,
  LegalProfile,
  DemandLetter,
  RightsSummary,
  Checklist,
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
