import React, { useState, useEffect, useCallback } from "react";
import {
  View, Text, TouchableOpacity, FlatList, TextInput,
  StyleSheet, ActivityIndicator, Alert, Modal,
} from "react-native";
import { supabase } from "@/lib/supabase";
import { getDeadlines, createDeadline, deleteDeadline } from "@/lib/api";
import type { Deadline } from "@/lib/types";

function getUrgencyColor(dateStr: string): string {
  const days = Math.ceil((new Date(dateStr).getTime() - Date.now()) / 86400000);
  if (days < 0) return "#ef4444";
  if (days <= 3) return "#f97316";
  if (days <= 7) return "#eab308";
  return "#22c55e";
}

function DeadlineCard({ deadline, onDelete }: { deadline: Deadline; onDelete: () => void }) {
  const urgencyColor = getUrgencyColor(deadline.date);
  const daysLeft = Math.ceil((new Date(deadline.date).getTime() - Date.now()) / 86400000);
  const label = daysLeft < 0 ? `${Math.abs(daysLeft)}d overdue` : daysLeft === 0 ? "Today" : `${daysLeft}d left`;

  return (
    <View style={[styles.deadlineCard, { borderLeftColor: urgencyColor }]}>
      <View style={styles.deadlineHeader}>
        <Text style={styles.deadlineTitle}>{deadline.title}</Text>
        <View style={[styles.urgencyBadge, { backgroundColor: urgencyColor + "20" }]}>
          <Text style={[styles.urgencyText, { color: urgencyColor }]}>{label}</Text>
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
        <ActivityIndicator size="large" color="#1e40af" />
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
            <TextInput style={styles.input} placeholder="Title" value={title} onChangeText={setTitle} placeholderTextColor="#94a3b8" />
            <TextInput style={styles.input} placeholder="Date (YYYY-MM-DD)" value={date} onChangeText={setDate} placeholderTextColor="#94a3b8" />
            <TextInput style={styles.input} placeholder="Legal area (optional)" value={legalArea} onChangeText={setLegalArea} placeholderTextColor="#94a3b8" />
            <TextInput style={styles.input} placeholder="Notes (optional)" value={notes} onChangeText={setNotes} placeholderTextColor="#94a3b8" multiline />
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
  container: { flex: 1, backgroundColor: "#f8fafc" },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  list: { padding: 16, gap: 12 },
  empty: { padding: 40, alignItems: "center" },
  emptyText: { color: "#94a3b8", fontSize: 14 },
  deadlineCard: {
    backgroundColor: "#ffffff", borderRadius: 12, padding: 16,
    borderWidth: 1, borderColor: "#e2e8f0", borderLeftWidth: 4,
  },
  deadlineHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 6 },
  deadlineTitle: { fontSize: 16, fontWeight: "700", color: "#0f172a", flex: 1 },
  urgencyBadge: { paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6 },
  urgencyText: { fontSize: 11, fontWeight: "700" },
  deadlineDate: { fontSize: 13, color: "#64748b", marginBottom: 4 },
  deadlineArea: { fontSize: 12, color: "#1e40af", fontWeight: "500", marginBottom: 4, textTransform: "capitalize" },
  deadlineNotes: { fontSize: 13, color: "#475569", marginTop: 4 },
  deleteBtn: { alignSelf: "flex-end", marginTop: 8 },
  deleteBtnText: { color: "#ef4444", fontSize: 13, fontWeight: "600" },
  fab: {
    position: "absolute", bottom: 24, right: 24, width: 56, height: 56,
    borderRadius: 28, backgroundColor: "#1e40af", justifyContent: "center",
    alignItems: "center", elevation: 4, shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.25, shadowRadius: 4,
  },
  fabText: { color: "#ffffff", fontSize: 28, fontWeight: "600", marginTop: -2 },
  modalOverlay: { flex: 1, justifyContent: "flex-end", backgroundColor: "rgba(0,0,0,0.4)" },
  modalContent: { backgroundColor: "#ffffff", borderTopLeftRadius: 20, borderTopRightRadius: 20, padding: 24, gap: 12 },
  modalTitle: { fontSize: 20, fontWeight: "700", color: "#0f172a", marginBottom: 4 },
  input: {
    backgroundColor: "#f1f5f9", borderRadius: 10, paddingHorizontal: 14,
    paddingVertical: 12, fontSize: 15, color: "#0f172a",
  },
  modalButtons: { flexDirection: "row", gap: 12, marginTop: 8 },
  cancelBtn: { flex: 1, paddingVertical: 14, borderRadius: 12, alignItems: "center", backgroundColor: "#f1f5f9" },
  cancelBtnText: { color: "#64748b", fontWeight: "600", fontSize: 15 },
  createBtn: { flex: 1, paddingVertical: 14, borderRadius: 12, alignItems: "center", backgroundColor: "#1e40af" },
  createBtnText: { color: "#ffffff", fontWeight: "700", fontSize: 15 },
});
