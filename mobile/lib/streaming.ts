import { supabase } from "./supabase";

const API_BASE = process.env.EXPO_PUBLIC_API_URL || "http://localhost:8000/api";

export async function* streamChat(
  message: string,
  conversationId?: string
): AsyncGenerator<{ type: "content" | "done" | "error"; data: string; conversationId?: string }> {
  const { data: { session } } = await supabase.auth.getSession();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (session?.access_token) {
    headers["Authorization"] = `Bearer ${session.access_token}`;
  }

  try {
    const response = await fetch(`${API_BASE}/chat/stream`, {
      method: "POST",
      headers,
      body: JSON.stringify({ message, conversation_id: conversationId }),
    });

    if (!response.ok) {
      yield { type: "error", data: `API error ${response.status}` };
      return;
    }

    if (!response.body) {
      // Fallback: no streaming support, read full response
      const json = await response.json();
      yield { type: "content", data: json.answer, conversationId: json.conversation_id };
      yield { type: "done", data: "" };
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const data = line.slice(6);
          if (data === "[DONE]") {
            yield { type: "done", data: "" };
            return;
          }
          try {
            const parsed = JSON.parse(data);
            if (parsed.content) {
              yield { type: "content", data: parsed.content, conversationId: parsed.conversation_id };
            }
          } catch {
            yield { type: "content", data };
          }
        }
      }
    }

    yield { type: "done", data: "" };
  } catch (err) {
    yield { type: "error", data: err instanceof Error ? err.message : "Streaming failed" };
  }
}
