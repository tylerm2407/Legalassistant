import React, { useState, useEffect, useCallback } from "react";
import { View, Text, TouchableOpacity, FlatList, StyleSheet, ActivityIndicator, Alert } from "react-native";
import { useRouter } from "expo-router";
import { supabase } from "@/lib/supabase";
import { getConversations, deleteConversation } from "@/lib/api";
import { colors, fonts } from "@/lib/theme";
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
    return <View style={styles.center}><ActivityIndicator size="large" color={colors.primary} /></View>;
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
          onPress={() => router.push({ pathname: "/(app)/(chat)", params: { conversationId: item.id } } as any)}
          onLongPress={() => handleDelete(item.id)}
        >
          <View style={styles.cardHeader}>
            <Text style={styles.cardArea}>{(item.legal_area || "general").replace("_", " ")}</Text>
            <Text style={styles.cardDate}>{new Date(item.updated_at).toLocaleDateString()}</Text>
          </View>
          <Text style={styles.cardPreview} numberOfLines={2}>{item.preview || "No messages"}</Text>
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
  container: { flex: 1, backgroundColor: colors.background },
  center: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: colors.background },
  list: { padding: 16, gap: 12 },
  card: {
    backgroundColor: colors.surface, borderRadius: 12, padding: 16,
    borderWidth: 1, borderColor: colors.border,
  },
  cardHeader: { flexDirection: "row", justifyContent: "space-between", marginBottom: 6 },
  cardArea: { fontSize: 11, color: colors.primary, fontWeight: "600", textTransform: "uppercase", letterSpacing: 1.2, fontFamily: fonts.sans },
  cardDate: { fontSize: 12, color: colors.textMuted },
  cardPreview: { fontSize: 14, color: colors.textSecondary, lineHeight: 20, marginBottom: 6 },
  cardCount: { fontSize: 12, color: colors.textMuted },
  empty: { padding: 40, alignItems: "center" },
  emptyText: { color: colors.textSecondary, fontSize: 14, textAlign: "center" },
});
