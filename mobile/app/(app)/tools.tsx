import React from "react";
import { View, Text, TouchableOpacity, ScrollView, StyleSheet } from "react-native";
import { useRouter } from "expo-router";

const TOOLS = [
  { title: "Documents", icon: "📄", description: "Upload and analyze legal documents", route: "/(app)/documents" },
  { title: "Know Your Rights", icon: "⚖️", description: "Browse rights guides by legal area", route: "/(app)/rights" },
  { title: "Legal Workflows", icon: "📋", description: "Step-by-step guides for legal processes", route: "/(app)/workflows" },
  { title: "Find Attorneys", icon: "👨‍⚖️", description: "Search for attorneys by state and specialty", route: "/(app)/attorneys" },
];

export default function ToolsScreen() {
  const router = useRouter();

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.heading}>Legal Tools</Text>
      <Text style={styles.subheading}>Everything you need to understand and act on your legal situation.</Text>
      <View style={styles.grid}>
        {TOOLS.map((tool) => (
          <TouchableOpacity
            key={tool.title}
            style={styles.card}
            onPress={() => router.push(tool.route as any)}
            activeOpacity={0.7}
          >
            <Text style={styles.cardIcon}>{tool.icon}</Text>
            <Text style={styles.cardTitle}>{tool.title}</Text>
            <Text style={styles.cardDescription}>{tool.description}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f8fafc" },
  content: { padding: 20 },
  heading: { fontSize: 24, fontWeight: "800", color: "#0f172a", marginBottom: 4 },
  subheading: { fontSize: 14, color: "#64748b", marginBottom: 24 },
  grid: { gap: 14 },
  card: {
    backgroundColor: "#ffffff",
    borderRadius: 14,
    padding: 20,
    borderWidth: 1,
    borderColor: "#e2e8f0",
  },
  cardIcon: { fontSize: 28, marginBottom: 8 },
  cardTitle: { fontSize: 17, fontWeight: "700", color: "#0f172a", marginBottom: 4 },
  cardDescription: { fontSize: 13, color: "#64748b", lineHeight: 18 },
});
