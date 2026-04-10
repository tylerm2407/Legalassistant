import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { colors, fonts, tokens } from "@/lib/theme";
import type { Message } from "@/lib/types";

interface ChatBubbleProps {
  message: Message;
}

function formatBoldText(text: string): React.ReactNode[] {
  const parts = text.split(/(\*\*.*?\*\*)/g);
  return parts.map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <Text key={index} style={styles.boldText}>
          {part.slice(2, -2)}
        </Text>
      );
    }
    return <Text key={index}>{part}</Text>;
  });
}

function formatTimestamp(date: Date): string {
  const d = new Date(date);
  return d.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
}

export default function ChatBubble({ message }: ChatBubbleProps) {
  const isUser = message.role === "user";
  const isError = message.role === "error";

  return (
    <View
      style={[
        styles.container,
        isUser ? styles.containerUser : styles.containerAssistant,
      ]}
    >
      <View
        style={[
          styles.bubble,
          isUser && styles.bubbleUser,
          !isUser && !isError && styles.bubbleAssistant,
          isError && styles.bubbleError,
        ]}
      >
        {message.legalArea && !isUser && (
          <View style={styles.legalAreaTag}>
            <Text style={styles.legalAreaText}>
              {message.legalArea}
            </Text>
          </View>
        )}

        <Text
          style={[
            styles.messageText,
            isUser && styles.messageTextUser,
            isError && styles.messageTextError,
          ]}
        >
          {formatBoldText(message.content)}
        </Text>

        <Text
          style={[
            styles.timestamp,
            isUser ? styles.timestampUser : styles.timestampAssistant,
            isError && styles.timestampError,
          ]}
        >
          {formatTimestamp(message.timestamp)}
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 12,
    marginVertical: 4,
  },
  containerUser: {
    alignItems: "flex-end",
  },
  containerAssistant: {
    alignItems: "flex-start",
  },
  bubble: {
    maxWidth: "80%",
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 12,
  },
  bubbleUser: {
    backgroundColor: colors.primary,
    borderBottomRightRadius: 4,
  },
  bubbleAssistant: {
    backgroundColor: colors.surface,
    borderBottomLeftRadius: 4,
    borderWidth: 1,
    borderColor: colors.border,
  },
  bubbleError: {
    backgroundColor: colors.errorMuted,
    borderBottomLeftRadius: 4,
    borderWidth: 1,
    borderColor: colors.error,
  },
  legalAreaTag: {
    backgroundColor: colors.elevated,
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 8,
    alignSelf: "flex-start",
    marginBottom: 6,
  },
  legalAreaText: {
    fontSize: 11,
    fontWeight: "600",
    color: colors.primary,
    textTransform: "uppercase",
    letterSpacing: 1.5,
    fontFamily: fonts.sans,
  },
  messageText: {
    fontSize: 15,
    lineHeight: 22,
    color: colors.text,
    fontFamily: fonts.sans,
  },
  messageTextUser: {
    color: "#ffffff",
  },
  messageTextError: {
    color: colors.error,
  },
  boldText: {
    fontWeight: "700",
  },
  timestamp: {
    fontSize: 11,
    marginTop: 4,
  },
  timestampUser: {
    color: tokens.accentSubtle,
    textAlign: "right",
    opacity: 0.8,
  },
  timestampAssistant: {
    color: colors.textMuted,
  },
  timestampError: {
    color: colors.error,
  },
});
