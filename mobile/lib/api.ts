import type {
  ChatResponse,
  LegalProfile,
  DemandLetter,
  RightsSummary,
  Checklist,
} from "./types";

const API_BASE =
  process.env.EXPO_PUBLIC_API_URL || "http://localhost:8000/api";

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${path}`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  const response = await fetch(url, { ...options, headers });

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
      user_id: userId,
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
    body: JSON.stringify(profile),
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
      user_id: userId,
      issue_type: issueType,
      details,
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
      user_id: userId,
      issue_type: issueType,
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
      user_id: userId,
      issue_type: issueType,
    }),
  });
}

export async function uploadDocument(
  userId: string,
  fileUri: string,
  fileName: string,
  mimeType: string
): Promise<{ document_id: string; extracted_facts: string[] }> {
  const formData = new FormData();
  formData.append("user_id", userId);
  formData.append("file", {
    uri: fileUri,
    name: fileName,
    type: mimeType,
  } as unknown as Blob);

  const url = `${API_BASE}/documents/upload`;
  const response = await fetch(url, {
    method: "POST",
    body: formData,
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  if (!response.ok) {
    const errorBody = await response.text().catch(() => "Unknown error");
    throw new Error(`Upload error ${response.status}: ${errorBody}`);
  }

  return response.json();
}
