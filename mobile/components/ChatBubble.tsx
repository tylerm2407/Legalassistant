import React from "react";
import { View, Text, StyleSheet } from "react-native";
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
    borderRadius: 18,
  },
  bubbleUser: {
    backgroundColor: "#1e40af",
    borderBottomRightRadius: 4,
  },
  bubbleAssistant: {
    backgroundColor: "#ffffff",
    borderBottomLeftRadius: 4,
    borderWidth: 1,
    borderColor: "#e2e8f0",
  },
  bubbleError: {
    backgroundColor: "#fef2f2",
    borderBottomLeftRadius: 4,
    borderWidth: 1,
    borderColor: "#fecaca",
  },
  legalAreaTag: {
    backgroundColor: "#eff6ff",
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 8,
    alignSelf: "flex-start",
    marginBottom: 6,
  },
  legalAreaText: {
    fontSize: 11,
    fontWeight: "700",
    color: "#1e40af",
    textTransform: "uppercase",
    letterSpacing: 0.5,
  },
  messageText: {
    fontSize: 15,
    lineHeight: 21,
    color: "#1e293b",
  },
  messageTextUser: {
    color: "#ffffff",
  },
  messageTextError: {
    color: "#991b1b",
  },
  boldText: {
    fontWeight: "700",
  },
  timestamp: {
    fontSize: 11,
    marginTop: 4,
  },
  timestampUser: {
    color: "rgba(255, 255, 255, 0.6)",
    textAlign: "right",
  },
  timestampAssistant: {
    color: "#94a3b8",
  },
  timestampError: {
    color: "#f87171",
  },
});
