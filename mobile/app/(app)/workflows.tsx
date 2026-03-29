import React, { useState, useEffect } from "react";
import { View, Text, TouchableOpacity, FlatList, StyleSheet, ActivityIndicator, Alert } from "react-native";
import { useRouter } from "expo-router";
import { getWorkflowTemplates, getActiveWorkflows, startWorkflow } from "@/lib/api";
import type { WorkflowTemplate, WorkflowSummary } from "@/lib/types";

export default function WorkflowsScreen() {
  const router = useRouter();
  const [templates, setTemplates] = useState<WorkflowTemplate[]>([]);
  const [active, setActive] = useState<WorkflowSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<"templates" | "active">("templates");

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [tData, aData] = await Promise.all([
        getWorkflowTemplates(),
        getActiveWorkflows(),
      ]);
      setTemplates(tData.templates);
      setActive(aData.workflows);
    } catch { /* ignore */ }
    finally { setLoading(false); }
  };

  const handleStart = async (templateId: string) => {
    try {
      const result = await startWorkflow(templateId);
      router.push({ pathname: "/(app)/workflow-wizard", params: { workflowId: result.workflow.id } } as any);
    } catch (err: unknown) {
      Alert.alert("Error", err instanceof Error ? err.message : "Failed to start workflow.");
    }
  };

  if (loading) {
    return <View style={styles.center}><ActivityIndicator size="large" color="#1e40af" /></View>;
  }

  return (
    <View style={styles.container}>
      <View style={styles.tabs}>
        <TouchableOpacity style={[styles.tab, tab === "templates" && styles.tabActive]} onPress={() => setTab("templates")}>
          <Text style={[styles.tabText, tab === "templates" && styles.tabTextActive]}>Templates</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.tab, tab === "active" && styles.tabActive]} onPress={() => setTab("active")}>
          <Text style={[styles.tabText, tab === "active" && styles.tabTextActive]}>Active ({active.length})</Text>
        </TouchableOpacity>
      </View>

      {tab === "templates" ? (
        <FlatList
          data={templates}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.list}
          renderItem={({ item }) => (
            <View style={styles.card}>
              <Text style={styles.cardTitle}>{item.title}</Text>
              <Text style={styles.cardDesc}>{item.description}</Text>
              <Text style={styles.cardMeta}>{item.steps.length} steps • {item.domain.replace("_", " ")}</Text>
              <TouchableOpacity style={styles.startBtn} onPress={() => handleStart(item.id)}>
                <Text style={styles.startBtnText}>Start Workflow</Text>
              </TouchableOpacity>
            </View>
          )}
        />
      ) : (
        <FlatList
          data={active}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.list}
          renderItem={({ item }) => (
            <TouchableOpacity
              style={styles.card}
              onPress={() => router.push({ pathname: "/(app)/workflow-wizard", params: { workflowId: item.id } } as any)}
            >
              <Text style={styles.cardTitle}>{item.title}</Text>
              <Text style={styles.cardMeta}>Status: {item.status} • {item.completed_steps}/{item.total_steps} steps</Text>
            </TouchableOpacity>
          )}
          ListEmptyComponent={<Text style={styles.emptyText}>No active workflows.</Text>}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f8fafc" },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  tabs: { flexDirection: "row", padding: 16, gap: 8 },
  tab: { flex: 1, paddingVertical: 10, borderRadius: 10, backgroundColor: "#f1f5f9", alignItems: "center" },
  tabActive: { backgroundColor: "#1e40af" },
  tabText: { fontSize: 14, fontWeight: "600", color: "#64748b" },
  tabTextActive: { color: "#ffffff" },
  list: { paddingHorizontal: 16, gap: 12, paddingBottom: 16 },
  card: {
    backgroundColor: "#ffffff", borderRadius: 12, padding: 16,
    borderWidth: 1, borderColor: "#e2e8f0",
  },
  cardTitle: { fontSize: 16, fontWeight: "700", color: "#0f172a", marginBottom: 4 },
  cardDesc: { fontSize: 13, color: "#64748b", lineHeight: 18, marginBottom: 8 },
  cardMeta: { fontSize: 12, color: "#94a3b8", textTransform: "capitalize" },
  startBtn: { marginTop: 12, backgroundColor: "#1e40af", paddingVertical: 10, borderRadius: 10, alignItems: "center" },
  startBtnText: { color: "#ffffff", fontWeight: "700", fontSize: 14 },
  emptyText: { color: "#94a3b8", fontSize: 14, textAlign: "center", padding: 40 },
});
