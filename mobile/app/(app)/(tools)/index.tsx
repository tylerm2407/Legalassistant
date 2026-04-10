import React from "react";
import { View, Text, TouchableOpacity, ScrollView, StyleSheet } from "react-native";
import { useRouter } from "expo-router";
import { colors, fonts } from "@/lib/theme";

const TOOLS = [
  { title: "Documents", description: "Upload and analyze legal documents", route: "/(app)/(more)/documents" },
  { title: "Know Your Rights", description: "Browse rights guides by legal area", route: "/(app)/(rights)" },
  { title: "Legal Workflows", description: "Step-by-step guides for legal processes", route: "/(app)/(tools)/workflows" },
  { title: "Find Attorneys", description: "Search for attorneys by state and specialty", route: "/(app)/(more)/attorneys" },
];

export default function ToolsScreen() {
  const router = useRouter();

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.eyebrow}>TOOLKIT</Text>
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
            <Text style={styles.cardTitle}>{tool.title}</Text>
            <Text style={styles.cardDescription}>{tool.description}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: 20, paddingTop: 32 },
  eyebrow: {
    fontSize: 11,
    fontWeight: "600",
    color: colors.textMuted,
    letterSpacing: 2,
    textTransform: "uppercase",
    marginBottom: 12,
    fontFamily: fonts.sans,
  },
  heading: {
    fontSize: 36,
    fontWeight: "500",
    color: colors.text,
    marginBottom: 8,
    fontFamily: fonts.serif,
    letterSpacing: -0.5,
  },
  subheading: {
    fontSize: 15,
    color: colors.textSecondary,
    marginBottom: 28,
    fontFamily: fonts.sans,
    lineHeight: 22,
  },
  grid: { gap: 12 },
  card: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 20,
    borderWidth: 1,
    borderColor: colors.border,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: "500",
    color: colors.text,
    marginBottom: 6,
    fontFamily: fonts.serif,
    letterSpacing: -0.3,
  },
  cardDescription: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
    fontFamily: fonts.sans,
  },
});
