"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useTranslation } from "@/lib/i18n";
import { Plus, X, CircleNotch } from "@phosphor-icons/react";

/**
 * Summary of a past conversation for display in the history sidebar.
 *
 * @property id - Unique conversation identifier from Supabase
 * @property legal_area - The classified legal domain of the conversation (e.g., "landlord_tenant")
 * @property updated_at - ISO timestamp of the last message in the conversation
 * @property preview - Truncated text preview of the conversation's first message
 * @property message_count - Total number of messages in the conversation
 */
interface ConversationSummary {
  id: string;
  legal_area: string | null;
  updated_at: string;
  preview: string;
  message_count: number;
}

/**
 * Props for the ConversationHistory component.
 *
 * @property activeConversationId - ID of the currently active conversation (highlighted in the list)
 * @property onSelectConversation - Callback when the user clicks a past conversation to load it
 * @property onNewConversation - Callback when the user clicks "New conversation" to start fresh
 */
interface ConversationHistoryProps {
  activeConversationId?: string;
  onSelectConversation: (id: string) => void;
  onNewConversation: () => void;
}

/**
 * Sidebar panel listing past conversations with navigation and deletion controls.
 *
 * Shows a chronological list of the user's past legal conversations, each with
 * a text preview, legal area tag, and date. Supports creating new conversations,
 * switching between existing ones, and deleting conversations from history.
 *
 * @param props - Component props
 * @param props.activeConversationId - Currently active conversation ID for highlighting
 * @param props.onSelectConversation - Handler for loading a past conversation
 * @param props.onNewConversation - Handler for starting a fresh conversation
 */
export default function ConversationHistory({
  activeConversationId,
  onSelectConversation,
  onNewConversation,
}: ConversationHistoryProps) {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const { t } = useTranslation();

  useEffect(() => {
    loadConversations();
  }, []);

  async function loadConversations() {
    try {
      const data = await api.getConversations();
      setConversations(data);
    } catch {
      // Fail silently — conversation history is non-critical
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id: string, e: React.MouseEvent) {
    e.stopPropagation();
    try {
      await api.deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
    } catch {
      // Fail silently
    }
  }

  return (
    <div className="flex flex-col h-full bg-bg">
      <div className="p-4 border-b border-border">
        <button
          onClick={onNewConversation}
          className="w-full flex items-center justify-center gap-2 bg-accent text-white px-4 py-3 rounded-md font-sans font-medium hover:bg-accent-hover transition-colors"
        >
          <Plus className="w-4 h-4" weight="regular" />
          {t("newConversation")}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="flex justify-center py-10">
            <CircleNotch className="w-5 h-5 text-ink-tertiary animate-spin" weight="regular" />
          </div>
        ) : conversations.length === 0 ? (
          <p className="text-sm font-sans text-ink-tertiary text-center py-10 px-4">
            {t("noPreviousConversations")}
          </p>
        ) : (
          <div className="p-3 space-y-1">
            {conversations.map((c: ConversationSummary) => {
              const isActive = c.id === activeConversationId;
              return (
                <div
                  key={c.id}
                  onClick={() => onSelectConversation(c.id)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => { if (e.key === "Enter") onSelectConversation(c.id); }}
                  className={`w-full text-left p-3 rounded-md transition-colors group cursor-pointer border ${
                    isActive
                      ? "bg-white border-border-strong"
                      : "bg-transparent border-transparent hover:bg-bg-hover"
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-sm font-sans text-ink-primary line-clamp-2 flex-1 leading-snug">
                      {c.preview}
                    </p>
                    <button
                      onClick={(e) => handleDelete(c.id, e)}
                      className="opacity-0 group-hover:opacity-100 text-ink-tertiary hover:text-warning transition-all shrink-0"
                      aria-label="Delete conversation"
                    >
                      <X className="w-4 h-4" weight="regular" />
                    </button>
                  </div>
                  <div className="flex items-center gap-2 mt-2">
                    {c.legal_area && (
                      <span className="text-xs font-sans text-accent capitalize">
                        {c.legal_area.replace(/_/g, " ")}
                      </span>
                    )}
                    <span className="text-xs font-sans text-ink-tertiary">
                      {new Date(c.updated_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
