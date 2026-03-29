"use client";

import React, { useState, useRef, useEffect } from "react";
import Button from "./ui/Button";
import LegalProfileSidebar from "./LegalProfileSidebar";
import ConversationHistory from "./ConversationHistory";
import ActionGenerator from "./ActionGenerator";
import type { LegalProfile, Message } from "@/lib/types";
import { api } from "@/lib/api";

/**
 * Renders a single chat message bubble with role-based styling.
 *
 * User messages appear right-aligned with a blue gradient background.
 * Assistant messages appear left-aligned with a glass-morphism style.
 * Error messages are styled with a red border for visibility.
 *
 * @param props - Component props
 * @param props.message - The chat message to render, including role, content, and optional legal area tag
 */
function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";
  const isError = message.role === "error";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm ${
          isUser
            ? "bg-gradient-to-r from-blue-600 to-blue-500 text-white shadow-glow-sm"
            : isError
            ? "bg-red-500/10 text-red-400 border border-red-500/20"
            : "bg-white/[0.03] backdrop-blur text-gray-200 border border-white/10"
        }`}
      >
        {message.content}
        {message.legalArea && (
          <span className="block mt-1 text-xs opacity-70">
            {message.legalArea.replace("_", " ")}
          </span>
        )}
      </div>
    </div>
  );
}

/**
 * Animated typing indicator displayed while CaseMate is generating a response.
 *
 * Shows three bouncing dots to indicate the AI assistant is processing
 * the user's legal question through the memory-injected Claude pipeline.
 */
function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="bg-white/[0.03] border border-white/10 rounded-2xl px-4 py-3">
        <div className="flex gap-1">
          <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" />
          <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce [animation-delay:0.1s]" />
          <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce [animation-delay:0.2s]" />
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
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: `Hi ${profile.display_name}! I'm CaseMate, your AI legal assistant. I have your profile loaded for ${profile.state}. How can I help you today?`,
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

    // Phase 1: New conversation — use POST to get conversation_id
    if (!conversationId) {
      setIsLoading(true);
      try {
        const response = await api.chat({
          userId: profile.user_id,
          question,
          conversationId,
        });

        setConversationId(response.conversation_id);
        setLastLegalArea(response.legal_area);

        const assistantMessage: Message = {
          role: "assistant",
          content: response.answer,
          timestamp: new Date(),
          legalArea: response.legal_area,
        };

        setMessages((prev) => [...prev, assistantMessage]);
      } catch (err) {
        const errorMessage: Message = {
          role: "error",
          content:
            err instanceof Error
              ? err.message
              : "Something went wrong. Please try again.",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
      return;
    }

    // Phase 2: Existing conversation — use SSE streaming
    setIsStreaming(true);
    setStreamingContent("");

    const cleanup = api.streamChat({
      conversationId,
      message: question,
      onToken: (chunk) => {
        setStreamingContent((prev) => prev + chunk);
      },
      onDone: (meta) => {
        setStreamingContent((current) => {
          const finalContent = current;
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant" as const,
              content: finalContent,
              timestamp: new Date(),
              legalArea: meta.legal_area,
            },
          ]);
          return "";
        });
        setLastLegalArea(meta.legal_area);
        setIsStreaming(false);
        abortStreamRef.current = null;
      },
      onError: (message) => {
        setStreamingContent("");
        setIsStreaming(false);
        abortStreamRef.current = null;
        setMessages((prev) => [
          ...prev,
          {
            role: "error" as const,
            content: message,
            timestamp: new Date(),
          },
        ]);
      },
    });

    abortStreamRef.current = cleanup;
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!isStreaming) handleSend();
    }
  }

  function handleStopStream() {
    if (abortStreamRef.current) {
      abortStreamRef.current();
      abortStreamRef.current = null;
      // Flush whatever we have so far as a message
      setStreamingContent((current) => {
        if (current) {
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant" as const,
              content: current + "\n\n[Stopped]",
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
    setConversationId(undefined);
    setLastLegalArea("");
    setMessages([
      {
        role: "assistant",
        content: `Hi ${profile.display_name}! I'm CaseMate, your AI legal assistant. I have your profile loaded for ${profile.state}. How can I help you today?`,
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
    <div className="flex h-screen bg-[#050505]">
      {/* Profile Sidebar */}
      <LegalProfileSidebar profile={profile} />

      {/* Conversation History */}
      {showHistory && (
        <div className="w-[240px] shrink-0 border-r border-white/10 bg-white/[0.01]">
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
        <header className="bg-white/[0.03] backdrop-blur-xl border-b border-white/10 px-6 py-3 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="p-1.5 text-gray-500 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
              title={showHistory ? "Hide history" : "Show history"}
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
              </svg>
            </button>
            <div>
              <h1 className="text-lg font-semibold text-white">CaseMate</h1>
              <p className="text-xs text-gray-500">AI Legal Assistant</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {lastLegalArea && (
              <span className="text-xs bg-blue-500/10 text-blue-400 border border-blue-500/20 px-2.5 py-1 rounded-full font-medium">
                {lastLegalArea.replace(/_/g, " ")}
              </span>
            )}
            <nav className="flex items-center gap-1 ml-3">
              <a href="/rights" className="text-xs text-gray-500 hover:text-white px-2 py-1 rounded transition-colors">Rights</a>
              <a href="/workflows" className="text-xs text-gray-500 hover:text-white px-2 py-1 rounded transition-colors">Workflows</a>
              <a href="/deadlines" className="text-xs text-gray-500 hover:text-white px-2 py-1 rounded transition-colors">Deadlines</a>
              <a href="/attorneys" className="text-xs text-gray-500 hover:text-white px-2 py-1 rounded transition-colors">Attorneys</a>
            </nav>
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4 scrollbar-thin">
          {messages.map((msg: Message, i: number) => (
            <MessageBubble key={i} message={msg} />
          ))}
          {isLoading && <TypingIndicator />}
          {isStreaming && streamingContent && (
            <div className="flex justify-start">
              <div className="max-w-[80%] px-4 py-3 rounded-2xl text-sm bg-white/[0.03] backdrop-blur text-gray-200 border border-white/10">
                {streamingContent}
                <span className="inline-block w-1.5 h-4 bg-blue-400 ml-0.5 animate-pulse" />
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
        <div className="bg-white/[0.03] backdrop-blur-xl border-t border-white/10 px-6 py-4 shrink-0">
          <div className="flex items-end gap-3 max-w-4xl mx-auto">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Describe your legal question..."
              rows={1}
              className="flex-1 px-4 py-2.5 bg-white/[0.03] text-white border border-white/10 rounded-xl text-sm resize-none focus:outline-none focus:ring-2 focus:border-blue-500/50 focus:ring-blue-500/20 focus:shadow-glow-sm placeholder:text-gray-600"
            />
            {isStreaming ? (
              <Button
                onClick={handleStopStream}
                size="md"
              >
                Stop
              </Button>
            ) : (
              <Button
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                size="md"
              >
                Send
              </Button>
            )}
          </div>
          <p className="text-xs text-gray-500 mt-2 text-center flex items-center justify-center gap-1.5">
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
            </svg>
            AI assistant — not legal advice. Your data is encrypted and private.
          </p>
        </div>
      </div>
    </div>
  );
}
