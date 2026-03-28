"use client";

import React, { useState, useRef, useEffect } from "react";
import Button from "./ui/Button";
import LegalProfileSidebar from "./LegalProfileSidebar";
import ActionGenerator from "./ActionGenerator";
import type { LegalProfile, Message } from "@/lib/types";
import { api } from "@/lib/api";

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";
  const isError = message.role === "error";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm ${
          isUser
            ? "bg-blue-600 text-white"
            : isError
            ? "bg-red-50 text-red-700 border border-red-200"
            : "bg-white text-gray-800 border border-gray-200 shadow-sm"
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

function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3 shadow-sm">
        <div className="flex gap-1">
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.1s]" />
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.2s]" />
        </div>
      </div>
    </div>
  );
}

interface ChatInterfaceProps {
  profile: LegalProfile;
}

export default function ChatInterface({ profile }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: `Hi ${profile.display_name}! I'm Lex, your AI legal assistant. I have your profile loaded for ${profile.state}. How can I help you today?`,
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [lastLegalArea, setLastLegalArea] = useState<string>("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  async function handleSend() {
    const question = input.trim();
    if (!question || isLoading) return;

    const userMessage: Message = {
      role: "user",
      content: question,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
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
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <LegalProfileSidebar profile={profile} />

      {/* Main chat area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between shrink-0">
          <div>
            <h1 className="text-lg font-semibold text-gray-900">Lex</h1>
            <p className="text-xs text-gray-500">AI Legal Assistant</p>
          </div>
          {lastLegalArea && (
            <span className="text-xs bg-blue-50 text-blue-700 px-2.5 py-1 rounded-full font-medium">
              {lastLegalArea.replace(/_/g, " ")}
            </span>
          )}
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4 scrollbar-thin">
          {messages.map((msg, i) => (
            <MessageBubble key={i} message={msg} />
          ))}
          {isLoading && <TypingIndicator />}
          <div ref={messagesEndRef} />
        </div>

        {/* Action generator */}
        {messages.length > 1 && (
          <ActionGenerator userId={profile.user_id} />
        )}

        {/* Input */}
        <div className="bg-white border-t border-gray-200 px-6 py-4 shrink-0">
          <div className="flex items-end gap-3 max-w-4xl mx-auto">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Describe your legal question..."
              rows={1}
              className="flex-1 px-4 py-2.5 border border-gray-300 rounded-xl text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <Button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              size="md"
            >
              Send
            </Button>
          </div>
          <p className="text-xs text-gray-400 mt-2 text-center">
            Lex is an AI assistant, not a lawyer. For legal advice, consult a
            licensed attorney.
          </p>
        </div>
      </div>
    </div>
  );
}
