import React, { useState, useEffect, useCallback } from "react";
import {
  View, Text, TouchableOpacity, FlatList, TextInput,
  StyleSheet, ActivityIndicator, Alert, Modal,
} from "react-native";
import { supabase } from "@/lib/supabase";
import { getDeadlines, createDeadline, deleteDeadline } from "@/lib/api";
import { colors, fonts, tokens } from "@/lib/theme";
import type { Deadline } from "@/lib/types";

type Urgency = { fg: string; bg: string };

function getUrgency(dateStr: string): Urgency {
  const days = Math.ceil((new Date(dateStr).getTime() - Date.now()) / 86400000);
  if (days < 0) return { fg: colors.error, bg: colors.errorMuted };
  if (days <= 3) return { fg: colors.warning, bg: tokens.warningSubtle };
  if (days <= 7) return { fg: colors.warning, bg: tokens.warningSubtle };
  return { fg: tokens.accent, bg: tokens.accentSubtle };
}

function DeadlineCard({ deadline, onDelete }: { deadline: Deadline; onDelete: () => void }) {
  const urgency = getUrgency(deadline.date);
  const daysLeft = Math.ceil((new Date(deadline.date).getTime() - Date.now()) / 86400000);
  const label = daysLeft < 0 ? `${Math.abs(daysLeft)}d overdue` : daysLeft === 0 ? "Today" : `${daysLeft}d left`;

  return (
    <View style={[styles.deadlineCard, { borderLeftColor: urgency.fg }]}>
      <View style={styles.deadlineHeader}>
        <Text style={styles.deadlineTitle}>{deadline.title}</Text>
        <View style={[styles.urgencyBadge, { backgroundColor: urgency.bg }]}>
          <Text style={[styles.urgencyText, { color: urgency.fg }]}>{label}</Text>
        </View>
      </View>
      <Text style={styles.deadlineDate}>{new Date(deadline.date).toLocaleDateString()}</Text>
      {deadline.legal_area && (
        <Text style={styles.deadlineArea}>{deadline.legal_area.replace("_", " ")}</Text>
      )}
      {deadline.notes && <Text style={styles.deadlineNotes}>{deadline.notes}</Text>}
      <TouchableOpacity onPress={onDelete} style={styles.deleteBtn}>
        <Text style={styles.deleteBtnText}>Delete</Text>
      </TouchableOpacity>
    </View>
  );
}

export default function DeadlinesScreen() {
  const [deadlines, setDeadlines] = useState<Deadline[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState("");
  const [date, setDate] = useState("");
  const [legalArea, setLegalArea] = useState("");
  const [notes, setNotes] = useState("");
  const [userId, setUserId] = useState("");

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.user?.id) setUserId(session.user.id);
    });
  }, []);

  const loadDeadlines = useCallback(async () => {
    if (!userId) return;
    setLoading(true);
    try {
      const data = await getDeadlines(userId);
      setDeadlines(data.deadlines);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => { loadDeadlines(); }, [loadDeadlines]);

  const handleCreate = async () => {
    if (!title.trim() || !date.trim()) {
      Alert.alert("Error", "Title and date are required.");
      return;
    }
    try {
      await createDeadline({ title, date, legal_area: legalArea || undefined, notes: notes || undefined });
      setTitle(""); setDate(""); setLegalArea(""); setNotes("");
      setShowForm(false);
      loadDeadlines();
    } catch (err: unknown) {
      Alert.alert("Error", err instanceof Error ? err.message : "Failed to create deadline.");
    }
  };

  const handleDelete = async (id: string) => {
    Alert.alert("Delete Deadline", "Are you sure?", [
      { text: "Cancel", style: "cancel" },
      { text: "Delete", style: "destructive", onPress: async () => {
        try { await deleteDeadline(id); loadDeadlines(); } catch { /* ignore */ }
      }},
    ]);
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={deadlines}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <DeadlineCard deadline={item} onDelete={() => handleDelete(item.id)} />
        )}
        contentContainerStyle={styles.list}
        ListEmptyComponent={
          <View style={styles.empty}>
            <Text style={styles.emptyText}>No deadlines yet. Add one to stay on track.</Text>
          </View>
        }
      />
      <TouchableOpacity style={styles.fab} onPress={() => setShowForm(true)}>
        <Text style={styles.fabText}>+</Text>
      </TouchableOpacity>

      <Modal visible={showForm} animationType="slide" transparent>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>New Deadline</Text>
            <TextInput style={styles.input} placeholder="Title" value={title} onChangeText={setTitle} placeholderTextColor={colors.textMuted} />
            <TextInput style={styles.input} placeholder="Date (YYYY-MM-DD)" value={date} onChangeText={setDate} placeholderTextColor={colors.textMuted} />
            <TextInput style={styles.input} placeholder="Legal area (optional)" value={legalArea} onChangeText={setLegalArea} placeholderTextColor={colors.textMuted} />
            <TextInput style={styles.input} placeholder="Notes (optional)" value={notes} onChangeText={setNotes} placeholderTextColor={colors.textMuted} multiline />
            <View style={styles.modalButtons}>
              <TouchableOpacity style={styles.cancelBtn} onPress={() => setShowForm(false)}>
                <Text style={styles.cancelBtnText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.createBtn} onPress={handleCreate}>
                <Text style={styles.createBtnText}>Create</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  center: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: colors.background },
  list: { padding: 16, gap: 12 },
  empty: { padding: 40, alignItems: "center" },
  emptyText: { color: colors.textSecondary, fontSize: 14, fontFamily: fonts.sans },
  deadlineCard: {
    backgroundColor: colors.surface, borderRadius: 12, padding: 16,
    borderWidth: 1, borderColor: colors.border, borderLeftWidth: 4,
  },
  deadlineHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 6 },
  deadlineTitle: {
    fontSize: 18,
    fontWeight: "500",
    color: colors.text,
    flex: 1,
    fontFamily: fonts.serif,
    letterSpacing: -0.3,
  },
  urgencyBadge: { paddingHorizontal: 8, paddingVertical: 3, borderRadius: 8 },
  urgencyText: {
    fontSize: 10,
    fontWeight: "600",
    textTransform: "uppercase",
    letterSpacing: 1.2,
    fontFamily: fonts.sans,
  },
  deadlineDate: { fontSize: 13, color: colors.textSecondary, marginBottom: 4, fontFamily: fonts.sans },
  deadlineArea: {
    fontSize: 11,
    color: colors.primary,
    fontWeight: "600",
    marginBottom: 4,
    textTransform: "uppercase",
    letterSpacing: 1.2,
    fontFamily: fonts.sans,
  },
  deadlineNotes: { fontSize: 13, color: colors.textSecondary, marginTop: 4, fontFamily: fonts.sans },
  deleteBtn: { alignSelf: "flex-end", marginTop: 8 },
  deleteBtnText: { color: colors.error, fontSize: 13, fontWeight: "600", fontFamily: fonts.sans },
  fab: {
    position: "absolute", bottom: 24, right: 24, width: 56, height: 56,
    borderRadius: 28, backgroundColor: colors.primary, justifyContent: "center",
    alignItems: "center", elevation: 4, shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.25, shadowRadius: 4,
  },
  fabText: { color: "#ffffff", fontSize: 28, fontWeight: "400", marginTop: -2 },
  modalOverlay: { flex: 1, justifyContent: "flex-end", backgroundColor: "rgba(0,0,0,0.4)" },
  modalContent: { backgroundColor: colors.surface, borderTopLeftRadius: 12, borderTopRightRadius: 12, padding: 24, gap: 12 },
  modalTitle: {
    fontSize: 24,
    fontWeight: "500",
    color: colors.text,
    marginBottom: 4,
    fontFamily: fonts.serif,
    letterSpacing: -0.3,
  },
  input: {
    backgroundColor: colors.inputBg, borderRadius: 8, paddingHorizontal: 14,
    paddingVertical: 12, fontSize: 15, color: colors.text, fontFamily: fonts.sans,
    borderWidth: 1, borderColor: colors.border,
  },
  modalButtons: { flexDirection: "row", gap: 12, marginTop: 8 },
  cancelBtn: { flex: 1, paddingVertical: 14, borderRadius: 8, alignItems: "center", backgroundColor: colors.elevated },
  cancelBtnText: { color: colors.textSecondary, fontWeight: "600", fontSize: 14, fontFamily: fonts.sans },
  createBtn: { flex: 1, paddingVertical: 14, borderRadius: 8, alignItems: "center", backgroundColor: colors.primary },
  createBtnText: { color: "#ffffff", fontWeight: "600", fontSize: 14, fontFamily: fonts.sans },
});
