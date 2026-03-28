import React, { useState, useEffect } from "react";
import { View, Text, ScrollView, StyleSheet, ActivityIndicator } from "react-native";
import { useLocalSearchParams } from "expo-router";
import { getRightsGuide } from "@/lib/api";
import type { RightsGuide } from "@/lib/types";

export default function RightsGuideScreen() {
  const { guideId } = useLocalSearchParams<{ guideId: string }>();
  const [guide, setGuide] = useState<RightsGuide | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (guideId) {
      getRightsGuide(guideId)
        .then((data) => setGuide(data.guide))
        .catch(() => {})
        .finally(() => setLoading(false));
    }
  }, [guideId]);

  if (loading) {
    return <View style={styles.center}><ActivityIndicator size="large" color="#1e40af" /></View>;
  }

  if (!guide) {
    return <View style={styles.center}><Text style={styles.errorText}>Guide not found.</Text></View>;
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>{guide.title}</Text>
      <Text style={styles.domain}>{guide.domain.replace("_", " ")}</Text>
      {guide.summary && <Text style={styles.summary}>{guide.summary}</Text>}
      {guide.content && <Text style={styles.body}>{guide.content}</Text>}
      {guide.action_steps && guide.action_steps.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Action Steps</Text>
          {guide.action_steps.map((step: string, i: number) => (
            <View key={i} style={styles.stepRow}>
              <Text style={styles.stepNum}>{i + 1}</Text>
              <Text style={styles.stepText}>{step}</Text>
            </View>
          ))}
        </View>
      )}
      {guide.statutes && guide.statutes.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Relevant Statutes</Text>
          {guide.statutes.map((s: string, i: number) => (
            <Text key={i} style={styles.statute}>{s}</Text>
          ))}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f8fafc" },
  content: { padding: 20 },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  errorText: { color: "#ef4444", fontSize: 16 },
  title: { fontSize: 22, fontWeight: "800", color: "#0f172a", marginBottom: 4 },
  domain: { fontSize: 13, color: "#1e40af", fontWeight: "600", textTransform: "capitalize", marginBottom: 16 },
  summary: { fontSize: 15, color: "#334155", lineHeight: 22, marginBottom: 16 },
  body: { fontSize: 14, color: "#475569", lineHeight: 22, marginBottom: 16 },
  section: { marginTop: 20 },
  sectionTitle: { fontSize: 17, fontWeight: "700", color: "#0f172a", marginBottom: 12 },
  stepRow: { flexDirection: "row", gap: 10, marginBottom: 10 },
  stepNum: { width: 24, height: 24, borderRadius: 12, backgroundColor: "#1e40af", color: "#ffffff", textAlign: "center", lineHeight: 24, fontSize: 13, fontWeight: "700", overflow: "hidden" },
  stepText: { flex: 1, fontSize: 14, color: "#334155", lineHeight: 20 },
  statute: { fontSize: 13, color: "#64748b", marginBottom: 6, paddingLeft: 8 },
});
