import React, { useState, useEffect } from "react";
import { View, Text, TouchableOpacity, ScrollView, StyleSheet, ActivityIndicator, Alert } from "react-native";
import { useLocalSearchParams } from "expo-router";
import { getWorkflow, updateWorkflowStep } from "@/lib/api";
import type { WorkflowInstance, WorkflowStep } from "@/lib/types";

export default function WorkflowWizardScreen() {
  const { workflowId } = useLocalSearchParams<{ workflowId: string }>();
  const [workflow, setWorkflow] = useState<WorkflowInstance | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (workflowId) {
      getWorkflow(workflowId)
        .then((data) => setWorkflow(data.workflow))
        .catch(() => {})
        .finally(() => setLoading(false));
    }
  }, [workflowId]);

  const handleStepComplete = async (stepIndex: number) => {
    if (!workflowId) return;
    try {
      const result = await updateWorkflowStep(workflowId, stepIndex, "completed");
      setWorkflow(result.workflow);
    } catch (err: unknown) {
      Alert.alert("Error", err instanceof Error ? err.message : "Failed to update step.");
    }
  };

  if (loading) {
    return <View style={styles.center}><ActivityIndicator size="large" color="#1e40af" /></View>;
  }

  if (!workflow) {
    return <View style={styles.center}><Text style={styles.errorText}>Workflow not found.</Text></View>;
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>{workflow.title}</Text>
      <Text style={styles.status}>Status: {workflow.status}</Text>
      <View style={styles.steps}>
        {workflow.steps.map((step: WorkflowStep, i: number) => (
          <View key={i} style={[styles.step, step.status === "completed" && styles.stepCompleted]}>
            <View style={styles.stepHeader}>
              <View style={[styles.stepCircle, step.status === "completed" && styles.stepCircleCompleted]}>
                <Text style={styles.stepCircleText}>{step.status === "completed" ? "✓" : i + 1}</Text>
              </View>
              <Text style={[styles.stepTitle, step.status === "completed" && styles.stepTitleCompleted]}>{step.title}</Text>
            </View>
            {step.explanation && <Text style={styles.stepDesc}>{step.explanation}</Text>}
            {step.status !== "completed" && (
              <TouchableOpacity style={styles.completeBtn} onPress={() => handleStepComplete(i)}>
                <Text style={styles.completeBtnText}>Mark Complete</Text>
              </TouchableOpacity>
            )}
          </View>
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f8fafc" },
  content: { padding: 20 },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  errorText: { color: "#ef4444", fontSize: 16 },
  title: { fontSize: 22, fontWeight: "800", color: "#0f172a", marginBottom: 4 },
  status: { fontSize: 13, color: "#64748b", marginBottom: 20, textTransform: "capitalize" },
  steps: { gap: 12 },
  step: {
    backgroundColor: "#ffffff", borderRadius: 12, padding: 16,
    borderWidth: 1, borderColor: "#e2e8f0",
  },
  stepCompleted: { opacity: 0.7, borderColor: "#22c55e" },
  stepHeader: { flexDirection: "row", alignItems: "center", gap: 12, marginBottom: 6 },
  stepCircle: {
    width: 28, height: 28, borderRadius: 14, backgroundColor: "#e2e8f0",
    justifyContent: "center", alignItems: "center",
  },
  stepCircleCompleted: { backgroundColor: "#22c55e" },
  stepCircleText: { color: "#ffffff", fontWeight: "700", fontSize: 13 },
  stepTitle: { fontSize: 15, fontWeight: "700", color: "#0f172a", flex: 1 },
  stepTitleCompleted: { textDecorationLine: "line-through", color: "#64748b" },
  stepDesc: { fontSize: 13, color: "#64748b", lineHeight: 18, marginLeft: 40 },
  completeBtn: { marginTop: 10, marginLeft: 40, backgroundColor: "#1e40af", paddingVertical: 8, paddingHorizontal: 16, borderRadius: 8, alignSelf: "flex-start" },
  completeBtnText: { color: "#ffffff", fontWeight: "600", fontSize: 13 },
});
