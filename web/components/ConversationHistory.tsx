"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useTranslation } from "@/lib/i18n";

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
  const [error, setError] = useState("");
  const { t } = useTranslation();

  useEffect(() => {
    loadConversations();
  }, []);

  async function loadConversations() {
    try {
      const data = await api.getConversations();
      setConversations(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("failedToLoadConversations"));
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id: string, e: React.MouseEvent) {
    e.stopPropagation();
    try {
      await api.deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : t("failedToDelete"));
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="p-3 border-b border-white/10">
        <button
          onClick={onNewConversation}
          className="w-full text-left px-3 py-2 text-sm text-white bg-blue-500/10 border border-blue-500/20 rounded-lg hover:bg-blue-500/20 transition-colors flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
          {t("newConversation")}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto scrollbar-thin">
        {error && (
          <p className="text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg p-2 mx-2 mt-2">{error}</p>
        )}
        {loading ? (
          <div className="flex justify-center py-8">
            <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : conversations.length === 0 ? (
          <p className="text-xs text-gray-500 text-center py-8 px-4">{t("noPreviousConversations")}</p>
        ) : (
          <div className="p-2 space-y-1">
            {conversations.map((c: ConversationSummary) => (
              <button
                key={c.id}
                onClick={() => onSelectConversation(c.id)}
                className={`w-full text-left p-2.5 rounded-lg text-sm transition-all group ${
                  c.id === activeConversationId
                    ? "bg-white/[0.06] border border-white/10"
                    : "hover:bg-white/[0.03]"
                }`}
              >
                <div className="flex items-start justify-between gap-1">
                  <p className="text-gray-300 text-xs line-clamp-2 flex-1">{c.preview}</p>
                  <button
                    onClick={(e) => handleDelete(c.id, e)}
                    className="opacity-0 group-hover:opacity-100 p-0.5 text-gray-500 hover:text-red-400 transition-all shrink-0"
                  >
                    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                <div className="flex items-center gap-2 mt-1">
                  {c.legal_area && (
                    <span className="text-[10px] text-blue-400/70">{c.legal_area.replace(/_/g, " ")}</span>
                  )}
                  <span className="text-[10px] text-gray-600">
                    {new Date(c.updated_at).toLocaleDateString()}
                  </span>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
