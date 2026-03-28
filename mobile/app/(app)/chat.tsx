import React, { useState, useRef, useEffect } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import ChatBubble from "@/components/ChatBubble";
import ActionSheet from "@/components/ActionSheet";
import { chat, getConversation } from "@/lib/api";
import { supabase } from "@/lib/supabase";
import type { Message } from "@/lib/types";

const WELCOME_MESSAGE: Message = {
  role: "assistant",
  content:
    "Hi, I'm CaseMate — your AI legal assistant. Tell me about your legal situation and I'll help you understand your rights, generate documents, and figure out next steps. What's going on?",
  timestamp: new Date(),
};

export default function ChatScreen() {
  const { conversationId: paramConvId } = useLocalSearchParams<{ conversationId?: string }>();
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([WELCOME_MESSAGE]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [showActions, setShowActions] = useState(false);
  const [currentLegalArea, setCurrentLegalArea] = useState("general");
  const flatListRef = useRef<FlatList<Message>>(null);

  const [userId, setUserId] = useState<string>("");

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.user?.id) {
        setUserId(session.user.id);
      }
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setUserId(session?.user?.id || "");
      }
    );

    return () => subscription.unsubscribe();
  }, []);

  useEffect(() => {
    if (paramConvId) {
      setConversationId(paramConvId);
      getConversation(paramConvId)
        .then((data) => {
          if (data.conversation?.messages) {
            setMessages(data.conversation.messages.map((m: any) => ({
              role: m.role,
              content: m.content,
              timestamp: new Date(m.timestamp || Date.now()),
              legalArea: m.legal_area,
            })));
          }
        })
        .catch(() => {});
    }
  }, [paramConvId]);

  const scrollToBottom = () => {
    setTimeout(() => {
      flatListRef.current?.scrollToEnd({ animated: true });
    }, 100);
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    const userMessage: Message = {
      role: "user",
      content: trimmed,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await chat(userId, trimmed, conversationId);

      if (!conversationId) {
        setConversationId(response.conversation_id);
      }

      if (response.legal_area) {
        setCurrentLegalArea(response.legal_area);
      }

      const assistantMessage: Message = {
        role: "assistant",
        content: response.answer,
        timestamp: new Date(),
        legalArea: response.legal_area,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Show suggested actions if any
      if (response.suggested_actions && response.suggested_actions.length > 0) {
        const actionsMessage: Message = {
          role: "assistant",
          content: `Suggested actions: ${response.suggested_actions.join(", ")}. Tap the ⚡ button to generate documents.`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, actionsMessage]);
      }
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Something went wrong";
      const errorMessage: Message = {
        role: "error",
        content: `Failed to get a response: ${message}. Please try again.`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const renderMessage = ({ item }: { item: Message }) => (
    <ChatBubble message={item} />
  );

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      keyboardVerticalOffset={Platform.OS === "ios" ? 90 : 0}
    >
      {/* Messages */}
      <FlatList
        ref={flatListRef}
        data={messages}
        renderItem={renderMessage}
        keyExtractor={(_, index) => index.toString()}
        contentContainerStyle={styles.messagesList}
        showsVerticalScrollIndicator={false}
        onContentSizeChange={scrollToBottom}
      />

      {/* Loading indicator */}
      {isLoading && (
        <View style={styles.typingIndicator}>
          <ActivityIndicator size="small" color="#1e40af" />
          <Text style={styles.typingText}>CaseMate is thinking...</Text>
        </View>
      )}

      {/* History button */}
      <TouchableOpacity
        style={styles.historyButton}
        onPress={() => router.push("/(app)/conversations" as any)}
      >
        <Text style={styles.historyButtonText}>📜 History</Text>
      </TouchableOpacity>

      {/* Input bar */}
      <View style={styles.inputBar}>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => setShowActions(true)}
          activeOpacity={0.7}
        >
          <Text style={styles.actionButtonIcon}>⚡</Text>
        </TouchableOpacity>

        <TextInput
          style={styles.input}
          placeholder="Describe your legal situation..."
          placeholderTextColor="#94a3b8"
          value={input}
          onChangeText={setInput}
          multiline
          maxLength={2000}
          editable={!isLoading}
        />

        <TouchableOpacity
          style={[
            styles.sendButton,
            (!input.trim() || isLoading) && styles.sendButtonDisabled,
          ]}
          onPress={handleSend}
          disabled={!input.trim() || isLoading}
          activeOpacity={0.7}
        >
          <Text style={styles.sendButtonIcon}>↑</Text>
        </TouchableOpacity>
      </View>

      {/* Action Sheet */}
      <ActionSheet
        visible={showActions}
        onDismiss={() => setShowActions(false)}
        userId={userId}
        issueType={currentLegalArea}
        issueDetails={
          messages
            .filter((m) => m.role === "user")
            .map((m) => m.content)
            .slice(-3)
            .join(" ") || ""
        }
      />
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f8fafc",
  },
  messagesList: {
    paddingVertical: 16,
    paddingBottom: 8,
  },
  typingIndicator: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    paddingHorizontal: 20,
    paddingVertical: 8,
  },
  typingText: {
    fontSize: 13,
    color: "#64748b",
    fontStyle: "italic",
  },
  historyButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: "#eff6ff",
    alignSelf: "center",
    borderRadius: 16,
    marginBottom: 4,
  },
  historyButtonText: {
    fontSize: 13,
    color: "#1e40af",
    fontWeight: "600",
  },
  inputBar: {
    flexDirection: "row",
    alignItems: "flex-end",
    paddingHorizontal: 12,
    paddingVertical: 10,
    backgroundColor: "#ffffff",
    borderTopWidth: 1,
    borderTopColor: "#e2e8f0",
    gap: 8,
  },
  actionButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: "#eff6ff",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 2,
  },
  actionButtonIcon: {
    fontSize: 18,
  },
  input: {
    flex: 1,
    backgroundColor: "#f1f5f9",
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    fontSize: 15,
    color: "#0f172a",
    maxHeight: 120,
    minHeight: 40,
  },
  sendButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: "#1e40af",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 2,
  },
  sendButtonDisabled: {
    backgroundColor: "#cbd5e1",
  },
  sendButtonIcon: {
    color: "#ffffff",
    fontSize: 20,
    fontWeight: "800",
  },
});
