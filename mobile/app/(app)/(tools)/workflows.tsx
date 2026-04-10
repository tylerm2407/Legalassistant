import React, { useState, useEffect } from "react";
import { View, Text, TouchableOpacity, FlatList, StyleSheet, ActivityIndicator, Alert } from "react-native";
import { useRouter } from "expo-router";
import { getWorkflowTemplates, getActiveWorkflows, startWorkflow } from "@/lib/api";
import { colors, fonts } from "@/lib/theme";
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
      router.push({ pathname: "/(app)/(tools)/workflow-wizard", params: { workflowId: result.workflow.id } } as any);
    } catch (err: unknown) {
      Alert.alert("Error", err instanceof Error ? err.message : "Failed to start workflow.");
    }
  };

  if (loading) {
    return <View style={styles.center}><ActivityIndicator size="large" color={colors.primary} /></View>;
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
              onPress={() => router.push({ pathname: "/(app)/(tools)/workflow-wizard", params: { workflowId: item.id } } as any)}
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
  container: { flex: 1, backgroundColor: colors.background },
  center: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: colors.background },
  tabs: { flexDirection: "row", padding: 16, gap: 8 },
  tab: { flex: 1, paddingVertical: 10, borderRadius: 8, backgroundColor: colors.elevated, alignItems: "center" },
  tabActive: { backgroundColor: colors.primary },
  tabText: { fontSize: 13, fontWeight: "600", color: colors.textSecondary, fontFamily: fonts.sans },
  tabTextActive: { color: "#ffffff" },
  list: { paddingHorizontal: 16, gap: 12, paddingBottom: 16 },
  card: {
    backgroundColor: colors.surface, borderRadius: 12, padding: 16,
    borderWidth: 1, borderColor: colors.border,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: "500",
    color: colors.text,
    marginBottom: 4,
    fontFamily: fonts.serif,
    letterSpacing: -0.3,
  },
  cardDesc: { fontSize: 14, color: colors.textSecondary, lineHeight: 20, marginBottom: 8, fontFamily: fonts.sans },
  cardMeta: {
    fontSize: 11,
    color: colors.textMuted,
    textTransform: "uppercase",
    letterSpacing: 1.2,
    fontFamily: fonts.sans,
  },
  startBtn: { marginTop: 12, backgroundColor: colors.primary, paddingVertical: 12, borderRadius: 8, alignItems: "center" },
  startBtnText: { color: "#ffffff", fontWeight: "600", fontSize: 14, fontFamily: fonts.sans },
  emptyText: { color: colors.textSecondary, fontSize: 14, textAlign: "center", padding: 40, fontFamily: fonts.sans },
});
