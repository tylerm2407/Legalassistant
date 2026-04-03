import React, { useState, useRef, useEffect, useCallback } from "react";
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
  Alert,
} from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import ChatBubble from "@/components/ChatBubble";
import ActionSheet from "@/components/ActionSheet";
import { chat, getConversation } from "@/lib/api";
import { supabase } from "@/lib/supabase";
import { colors } from "@/lib/theme";
import type { Message, ConversationDetail } from "@/lib/types";

const WELCOME_MESSAGE: Message = {
  role: "assistant",
  content:
    "Hi, I'm CaseMate — your AI legal assistant. I remember everything about your situation so you never have to repeat yourself. Tell me about your legal issue and I'll help you understand your rights, generate documents, and figure out next steps. What's going on?",
  timestamp: new Date(),
};

export default function ChatScreen() {
  const { conversationId: paramConvId } = useLocalSearchParams<{ conversationId?: string }>();
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([WELCOME_MESSAGE]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
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
      setIsLoadingHistory(true);
      getConversation(paramConvId)
        .then((data: { conversation: ConversationDetail }) => {
          if (data.conversation?.messages) {
            const loadedMessages: Message[] = data.conversation.messages.map((m) => ({
              role: m.role,
              content: m.content,
              timestamp: new Date(m.timestamp || Date.now()),
              legalArea: m.legal_area || undefined,
            }));
            setMessages(loadedMessages);
            if (data.conversation.legal_area) {
              setCurrentLegalArea(data.conversation.legal_area);
            }
          }
        })
        .catch((err: unknown) => {
          const message = err instanceof Error ? err.message : "Failed to load conversation";
          Alert.alert("Error", message);
        })
        .finally(() => setIsLoadingHistory(false));
    }
  }, [paramConvId]);

  const scrollToBottom = useCallback(() => {
    setTimeout(() => {
      flatListRef.current?.scrollToEnd({ animated: true });
    }, 100);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const handleNewConversation = () => {
    setMessages([WELCOME_MESSAGE]);
    setConversationId(undefined);
    setInput("");
    setCurrentLegalArea("general");
  };

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    if (!userId) {
      Alert.alert("Not signed in", "Please sign in to use CaseMate.");
      return;
    }

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

      if (!conversationId && response.conversation_id) {
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

      if (response.suggested_actions && response.suggested_actions.length > 0) {
        const actionsMessage: Message = {
          role: "assistant",
          content: `I can help you take action. Available: ${response.suggested_actions.join(", ")}. Tap the lightning button below to generate documents.`,
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
      {/* Top bar with New Chat + History */}
      <View style={styles.topBar}>
        <TouchableOpacity
          style={styles.topBarButton}
          onPress={handleNewConversation}
          activeOpacity={0.7}
        >
          <Text style={styles.topBarButtonText}>+ New Chat</Text>
        </TouchableOpacity>

        {conversationId && (
          <View style={styles.legalAreaIndicator}>
            <Text style={styles.legalAreaIndicatorText}>
              {currentLegalArea.replace(/_/g, " ")}
            </Text>
          </View>
        )}

        <TouchableOpacity
          style={styles.topBarButton}
          onPress={() => router.push("/(app)/(chat)/conversations" as never)}
          activeOpacity={0.7}
        >
          <Text style={styles.topBarButtonText}>History</Text>
        </TouchableOpacity>
      </View>

      {/* Loading history indicator */}
      {isLoadingHistory ? (
        <View style={styles.historyLoading}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={styles.historyLoadingText}>Loading conversation...</Text>
        </View>
      ) : (
        <FlatList
          ref={flatListRef}
          data={messages}
          renderItem={renderMessage}
          keyExtractor={(_, index) => index.toString()}
          contentContainerStyle={styles.messagesList}
          showsVerticalScrollIndicator={false}
          onContentSizeChange={scrollToBottom}
        />
      )}

      {/* Typing indicator */}
      {isLoading && (
        <View style={styles.typingIndicator}>
          <View style={styles.typingDots}>
            <View style={[styles.typingDot, styles.typingDot1]} />
            <View style={[styles.typingDot, styles.typingDot2]} />
            <View style={[styles.typingDot, styles.typingDot3]} />
          </View>
          <Text style={styles.typingText}>CaseMate is thinking...</Text>
        </View>
      )}

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
          placeholderTextColor={colors.textMuted}
          value={input}
          onChangeText={setInput}
          multiline
          maxLength={2000}
          editable={!isLoading}
          onSubmitEditing={handleSend}
          returnKeyType="send"
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
    backgroundColor: colors.background,
  },
  topBar: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 12,
    paddingVertical: 8,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  topBarButton: {
    paddingVertical: 6,
    paddingHorizontal: 12,
    backgroundColor: colors.elevated,
    borderRadius: 8,
  },
  topBarButtonText: {
    fontSize: 13,
    color: colors.primary,
    fontWeight: "600",
  },
  legalAreaIndicator: {
    backgroundColor: colors.elevated,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  legalAreaIndicatorText: {
    fontSize: 11,
    color: colors.success,
    fontWeight: "700",
    textTransform: "capitalize",
  },
  historyLoading: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    gap: 12,
  },
  historyLoadingText: {
    fontSize: 15,
    color: colors.textSecondary,
  },
  messagesList: {
    paddingVertical: 16,
    paddingBottom: 8,
  },
  typingIndicator: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    paddingHorizontal: 20,
    paddingVertical: 10,
    backgroundColor: colors.surface,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  typingDots: {
    flexDirection: "row",
    gap: 4,
  },
  typingDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.primary,
    opacity: 0.4,
  },
  typingDot1: {
    opacity: 0.8,
  },
  typingDot2: {
    opacity: 0.6,
  },
  typingDot3: {
    opacity: 0.4,
  },
  typingText: {
    fontSize: 13,
    color: colors.textMuted,
    fontStyle: "italic",
  },
  inputBar: {
    flexDirection: "row",
    alignItems: "flex-end",
    paddingHorizontal: 12,
    paddingVertical: 10,
    backgroundColor: colors.surface,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    gap: 8,
  },
  actionButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.elevated,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 2,
  },
  actionButtonIcon: {
    fontSize: 18,
  },
  input: {
    flex: 1,
    backgroundColor: colors.inputBg,
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    fontSize: 15,
    color: colors.text,
    maxHeight: 120,
    minHeight: 40,
  },
  sendButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.primary,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 2,
  },
  sendButtonDisabled: {
    backgroundColor: colors.border,
  },
  sendButtonIcon: {
    color: "#ffffff",
    fontSize: 20,
    fontWeight: "800",
  },
});
