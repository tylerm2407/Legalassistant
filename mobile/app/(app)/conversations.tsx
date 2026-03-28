import React, { useState, useEffect, useCallback } from "react";
import { View, Text, TouchableOpacity, FlatList, StyleSheet, ActivityIndicator, Alert } from "react-native";
import { useRouter } from "expo-router";
import { supabase } from "@/lib/supabase";
import { getConversations, deleteConversation } from "@/lib/api";
import type { ConversationSummary } from "@/lib/types";

export default function ConversationsScreen() {
  const router = useRouter();
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [userId, setUserId] = useState("");

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.user?.id) setUserId(session.user.id);
    });
  }, []);

  const load = useCallback(async () => {
    if (!userId) return;
    setLoading(true);
    try {
      const data = await getConversations(userId);
      setConversations(data.conversations);
    } catch { /* ignore */ }
    finally { setLoading(false); }
  }, [userId]);

  useEffect(() => { load(); }, [load]);

  const handleDelete = (id: string) => {
    Alert.alert("Delete", "Delete this conversation?", [
      { text: "Cancel", style: "cancel" },
      { text: "Delete", style: "destructive", onPress: async () => {
        try { await deleteConversation(id); load(); } catch { /* ignore */ }
      }},
    ]);
  };

  if (loading) {
    return <View style={styles.center}><ActivityIndicator size="large" color="#1e40af" /></View>;
  }

  return (
    <FlatList
      data={conversations}
      keyExtractor={(item) => item.id}
      contentContainerStyle={styles.list}
      style={styles.container}
      renderItem={({ item }) => (
        <TouchableOpacity
          style={styles.card}
          onPress={() => router.push({ pathname: "/(app)/chat", params: { conversationId: item.id } } as any)}
          onLongPress={() => handleDelete(item.id)}
        >
          <View style={styles.cardHeader}>
            <Text style={styles.cardArea}>{(item.legal_area || "general").replace("_", " ")}</Text>
            <Text style={styles.cardDate}>{new Date(item.updated_at).toLocaleDateString()}</Text>
          </View>
          <Text style={styles.cardPreview} numberOfLines={2}>{item.last_message || "No messages"}</Text>
          <Text style={styles.cardCount}>{item.message_count} messages</Text>
        </TouchableOpacity>
      )}
      ListEmptyComponent={
        <View style={styles.empty}>
          <Text style={styles.emptyText}>No conversations yet. Start chatting with CaseMate!</Text>
        </View>
      }
    />
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f8fafc" },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  list: { padding: 16, gap: 12 },
  card: {
    backgroundColor: "#ffffff", borderRadius: 12, padding: 16,
    borderWidth: 1, borderColor: "#e2e8f0",
  },
  cardHeader: { flexDirection: "row", justifyContent: "space-between", marginBottom: 6 },
  cardArea: { fontSize: 13, color: "#1e40af", fontWeight: "600", textTransform: "capitalize" },
  cardDate: { fontSize: 12, color: "#94a3b8" },
  cardPreview: { fontSize: 14, color: "#334155", lineHeight: 20, marginBottom: 6 },
  cardCount: { fontSize: 12, color: "#94a3b8" },
  empty: { padding: 40, alignItems: "center" },
  emptyText: { color: "#94a3b8", fontSize: 14, textAlign: "center" },
});
