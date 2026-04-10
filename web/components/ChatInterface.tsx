"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";
import { List, Microphone } from "@phosphor-icons/react";
import Button from "./ui/Button";
import LegalProfileSidebar from "./LegalProfileSidebar";
import ConversationHistory from "./ConversationHistory";
import ActionGenerator from "./ActionGenerator";
import AudioRecorder from "./AudioRecorder";
import type { LegalProfile, Message } from "@/lib/types";
import { api } from "@/lib/api";
import { useTranslation } from "@/lib/i18n";
import translations from "@/lib/i18n/translations";

/**
 * Renders a single chat message bubble with role-based styling.
 *
 * User messages appear right-aligned with a warm accent-subtle background.
 * Assistant messages appear left-aligned on white with a hairline border.
 * Error messages use the muted terracotta warning palette — never red.
 */
function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";
  const isError = message.role === "error";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[70ch] px-6 py-4 rounded-lg text-base font-sans leading-relaxed ${
          isUser
            ? "bg-accent-subtle text-ink-primary border border-accent/20"
            : isError
            ? "bg-warning-subtle text-ink-primary border border-warning/30"
            : "bg-white text-ink-primary border border-border"
        }`}
      >
        <div className="whitespace-pre-wrap">{message.content}</div>
        {message.legalArea && (
          <span className="block mt-2 text-xs font-sans text-ink-tertiary capitalize">
            {message.legalArea.replace(/_/g, " ")}
          </span>
        )}
      </div>
    </div>
  );
}

/**
 * Animated typing indicator displayed while CaseMate is generating a response.
 * Three quiet dots on a white card — no glow, no color shift.
 */
function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="bg-white border border-border rounded-lg px-6 py-4">
        <div className="flex gap-1.5">
          <div className="w-1.5 h-1.5 bg-ink-tertiary rounded-full animate-bounce" />
          <div className="w-1.5 h-1.5 bg-ink-tertiary rounded-full animate-bounce [animation-delay:0.1s]" />
          <div className="w-1.5 h-1.5 bg-ink-tertiary rounded-full animate-bounce [animation-delay:0.2s]" />
        </div>
      </div>
    </div>
  );
}

/**
 * Props for the ChatInterface component.
 *
 * @property profile - The authenticated user's legal profile, used to personalize
 *   greetings, inject context into the sidebar, and pass user_id to the chat API
 */
interface ChatInterfaceProps {
  profile: LegalProfile;
}

/**
 * Main chat interface with conversation history, profile sidebar, and action generator.
 *
 * This is the primary interaction surface for CaseMate. It displays the user's
 * legal profile in a sidebar, maintains conversation history, sends questions
 * to the backend (which injects the user's memory/profile into Claude's system prompt),
 * and provides access to action generators for demand letters, rights summaries,
 * and checklists.
 *
 * @param props - Component props
 * @param props.profile - The authenticated user's complete legal profile from Supabase
 */
export default function ChatInterface({ profile }: ChatInterfaceProps) {
  const { t, locale } = useTranslation();
  const greeting = translations.chatGreeting[locale];

  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: typeof greeting === "function" ? greeting(profile.display_name, profile.state) : greeting,
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [lastLegalArea, setLastLegalArea] = useState<string>("");
  const [showHistory, setShowHistory] = useState(true);
  const [streamingContent, setStreamingContent] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [showRecorder, setShowRecorder] = useState(false);
  const abortStreamRef = useRef<(() => void) | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading, streamingContent]);

  async function handleSend() {
    const question = input.trim();
    if (!question || isLoading || isStreaming) return;

    const userMessage: Message = {
      role: "user",
      content: question,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    setIsStreaming(true);
    setStreamingContent("");

    const controller = new AbortController();
    abortStreamRef.current = () => controller.abort();

    try {
      const history = messages
        .filter((m) => m.role === "user" || m.role === "assistant")
        .map((m) => ({ role: m.role, content: m.content }));

      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: question,
          profile: {
            display_name: profile.display_name,
            state: profile.state,
            housing_situation: profile.housing_situation,
            employment_type: profile.employment_type,
            family_status: profile.family_status,
            language_preference: profile.language_preference,
            active_issues: profile.active_issues,
            legal_facts: profile.legal_facts,
          },
          history,
        }),
        signal: controller.signal,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ error: `HTTP ${res.status}` }));
        throw new Error(err.error || `Chat failed: ${res.status}`);
      }

      const reader = res.body?.getReader();
      if (!reader) throw new Error("No response body");

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const jsonStr = line.slice(6).trim();
          if (!jsonStr) continue;

          try {
            const event = JSON.parse(jsonStr);
            if (event.type === "token") {
              setStreamingContent((prev) => prev + event.content);
            } else if (event.type === "done") {
              setStreamingContent((current) => {
                const finalContent = current;
                setMessages((prev) => [
                  ...prev,
                  {
                    role: "assistant" as const,
                    content: finalContent,
                    timestamp: new Date(),
                    legalArea: event.legal_area,
                  },
                ]);
                return "";
              });
              setLastLegalArea(event.legal_area || "");
            } else if (event.type === "error") {
              throw new Error(event.message || "Stream error");
            }
          } catch (parseErr) {
            if (parseErr instanceof Error && parseErr.message !== "Stream error") {
              // ignore malformed SSE
            } else {
              throw parseErr;
            }
          }
        }
      }
    } catch (err) {
      if ((err as Error).name !== "AbortError") {
        setStreamingContent("");
        setMessages((prev) => [
          ...prev,
          {
            role: "error" as const,
            content: err instanceof Error ? err.message : t("somethingWentWrong"),
            timestamp: new Date(),
          },
        ]);
      }
    } finally {
      setIsStreaming(false);
      abortStreamRef.current = null;
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!isStreaming) handleSend();
    }
  }

  const handleTranscript = useCallback((text: string) => {
    setShowRecorder(false);
    const trimmed = text.trim();
    if (trimmed) {
      setInput(trimmed);
    }
  }, []);

  const pendingSendRef = useRef(false);

  const handleTranscriptSend = useCallback((text: string) => {
    setShowRecorder(false);
    const trimmed = text.trim();
    if (trimmed) {
      setInput(trimmed);
      pendingSendRef.current = true;
    }
  }, []);

  useEffect(() => {
    if (pendingSendRef.current && input.trim() && !isLoading && !isStreaming) {
      pendingSendRef.current = false;
      handleSend();
    }
  }, [input]); // eslint-disable-line react-hooks/exhaustive-deps

  function handleStopStream() {
    if (abortStreamRef.current) {
      abortStreamRef.current();
      abortStreamRef.current = null;
      setStreamingContent((current) => {
        if (current) {
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant" as const,
              content: current + `\n\n${t("stopped")}`,
              timestamp: new Date(),
            },
          ]);
        }
        return "";
      });
      setIsStreaming(false);
    }
  }

  function handleNewConversation() {
    const greet = translations.chatGreeting[locale];
    setConversationId(undefined);
    setLastLegalArea("");
    setMessages([
      {
        role: "assistant",
        content: typeof greet === "function" ? greet(profile.display_name, profile.state) : greet,
        timestamp: new Date(),
      },
    ]);
  }

  async function handleSelectConversation(id: string) {
    try {
      const conv = await api.getConversation(id);
      setConversationId(conv.id);
      setMessages(
        conv.messages.map((m: { role: string; content: string; timestamp: string; legal_area?: string | null }) => ({
          role: m.role as "user" | "assistant" | "error",
          content: m.content,
          timestamp: new Date(m.timestamp),
          legalArea: m.legal_area || undefined,
        }))
      );
      setLastLegalArea(conv.legal_area || "");
    } catch {
      // silent
    }
  }

  return (
    <div className="flex h-screen bg-bg">
      {/* Profile Sidebar */}
      <LegalProfileSidebar profile={profile} />

      {/* Conversation History */}
      {showHistory && (
        <div className="w-[260px] shrink-0 border-r border-border bg-bg">
          <ConversationHistory
            activeConversationId={conversationId}
            onSelectConversation={handleSelectConversation}
            onNewConversation={handleNewConversation}
          />
        </div>
      )}

      {/* Main chat area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="bg-bg border-b border-border px-8 py-5 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="p-2 text-ink-secondary hover:text-ink-primary hover:bg-bg-hover rounded-md transition-colors"
              title={showHistory ? t("hideHistory") : t("showHistory")}
              aria-label="Toggle conversation history"
            >
              <List className="w-5 h-5" weight="regular" />
            </button>
            <div>
              <h1 className="font-serif text-xl font-medium text-ink-primary">CaseMate</h1>
              <p className="text-sm font-sans text-ink-secondary">{t("chatSubtitle")}</p>
            </div>
          </div>
          {lastLegalArea && (
            <span className="text-sm font-sans font-medium text-accent bg-accent-subtle border border-accent/20 px-3 py-1 rounded-md capitalize">
              {lastLegalArea.replace(/_/g, " ")}
            </span>
          )}
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-8 py-6 space-y-6 scrollbar-thin bg-bg">
          {messages.map((msg: Message, i: number) => (
            <MessageBubble key={i} message={msg} />
          ))}
          {isLoading && <TypingIndicator />}
          {isStreaming && streamingContent && (
            <div className="flex justify-start">
              <div className="max-w-[70ch] px-6 py-4 rounded-lg text-base font-sans leading-relaxed bg-white text-ink-primary border border-border">
                <div className="whitespace-pre-wrap">{streamingContent}</div>
                <span className="inline-block w-[2px] h-4 bg-accent ml-0.5 animate-pulse align-middle" />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Action generator */}
        {messages.length > 1 && (
          <ActionGenerator userId={profile.user_id} />
        )}

        {/* Input */}
        <div className="bg-bg border-t border-border px-8 py-5 shrink-0">
          {showRecorder && (
            <div className="max-w-4xl mx-auto mb-4">
              <AudioRecorder
                onTranscript={handleTranscript}
                onTranscriptSend={handleTranscriptSend}
                onClose={() => setShowRecorder(false)}
              />
            </div>
          )}
          <div className="flex items-end gap-3 max-w-4xl mx-auto">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={t("chatPlaceholder")}
              rows={1}
              className="flex-1 px-4 py-3 bg-white text-ink-primary border border-border rounded-md text-base font-sans resize-none focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/20 placeholder:text-ink-tertiary"
            />
            <button
              onClick={() => setShowRecorder(!showRecorder)}
              className={`p-3 rounded-md border transition-colors ${
                showRecorder
                  ? "bg-accent-subtle border-accent/30 text-accent"
                  : "bg-white border-border text-ink-secondary hover:text-ink-primary hover:bg-bg-hover"
              }`}
              title={showRecorder ? t("closeRecorder") : t("voiceInput")}
              aria-label={showRecorder ? "Close recorder" : "Voice input"}
            >
              <Microphone className="w-5 h-5" weight="regular" />
            </button>
            {isStreaming ? (
              <Button onClick={handleStopStream} size="md">
                {t("stop")}
              </Button>
            ) : (
              <Button
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                size="md"
              >
                {t("send")}
              </Button>
            )}
          </div>
          <p className="text-xs font-sans text-ink-tertiary mt-3 text-center max-w-[60ch] mx-auto leading-relaxed">
            {t("chatDisclaimer")}
          </p>
        </div>
      </div>
    </div>
  );
}
