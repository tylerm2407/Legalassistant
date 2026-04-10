import React, { useState, useEffect } from "react";
import { View, Text, TouchableOpacity, ScrollView, StyleSheet, ActivityIndicator, Alert } from "react-native";
import { useLocalSearchParams } from "expo-router";
import { getWorkflow, updateWorkflowStep } from "@/lib/api";
import { colors, fonts } from "@/lib/theme";
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
    return <View style={styles.center}><ActivityIndicator size="large" color={colors.primary} /></View>;
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
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: 20 },
  center: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: colors.background },
  errorText: { color: colors.error, fontSize: 16, fontFamily: fonts.sans },
  title: {
    fontSize: 28,
    fontWeight: "500",
    color: colors.text,
    marginBottom: 4,
    fontFamily: fonts.serif,
    letterSpacing: -0.4,
  },
  status: {
    fontSize: 11,
    color: colors.textMuted,
    marginBottom: 24,
    textTransform: "uppercase",
    letterSpacing: 1.2,
    fontFamily: fonts.sans,
  },
  steps: { gap: 12 },
  step: {
    backgroundColor: colors.surface, borderRadius: 12, padding: 16,
    borderWidth: 1, borderColor: colors.border,
  },
  stepCompleted: { opacity: 0.7, borderColor: colors.success },
  stepHeader: { flexDirection: "row", alignItems: "center", gap: 12, marginBottom: 6 },
  stepCircle: {
    width: 28, height: 28, borderRadius: 14, backgroundColor: colors.elevated,
    justifyContent: "center", alignItems: "center",
  },
  stepCircleCompleted: { backgroundColor: colors.success },
  stepCircleText: { color: "#ffffff", fontWeight: "700", fontSize: 13, fontFamily: fonts.sans },
  stepTitle: {
    fontSize: 16,
    fontWeight: "500",
    color: colors.text,
    flex: 1,
    fontFamily: fonts.serif,
    letterSpacing: -0.2,
  },
  stepTitleCompleted: { textDecorationLine: "line-through", color: colors.textMuted },
  stepDesc: { fontSize: 14, color: colors.textSecondary, lineHeight: 20, marginLeft: 40, fontFamily: fonts.sans },
  completeBtn: { marginTop: 10, marginLeft: 40, backgroundColor: colors.primary, paddingVertical: 10, paddingHorizontal: 16, borderRadius: 8, alignSelf: "flex-start" },
  completeBtnText: { color: "#ffffff", fontWeight: "600", fontSize: 13, fontFamily: fonts.sans },
});
