import React from "react";
import { View, Text, TouchableOpacity, ScrollView, StyleSheet } from "react-native";
import { useRouter } from "expo-router";
import { colors, fonts } from "@/lib/theme";

const MENU_ITEMS = [
  { title: "Find Attorneys", description: "Search for attorneys by state and specialty", route: "/(app)/(more)/attorneys" },
  { title: "Deadlines", description: "Track your legal deadlines", route: "/(app)/(more)/deadlines" },
  { title: "Documents", description: "Upload and analyze legal documents", route: "/(app)/(more)/documents" },
  { title: "Subscription", description: "Manage your CaseMate plan", route: "/(app)/(more)/subscription" },
];

export default function MoreScreen() {
  const router = useRouter();

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.eyebrow}>MORE</Text>
      <Text style={styles.heading}>Settings & Tools</Text>
      <Text style={styles.subheading}>Additional tools and settings</Text>
      <View style={styles.list}>
        {MENU_ITEMS.map((item) => (
          <TouchableOpacity
            key={item.title}
            style={styles.row}
            onPress={() => router.push(item.route as any)}
            activeOpacity={0.7}
          >
            <View style={styles.rowInfo}>
              <Text style={styles.rowTitle}>{item.title}</Text>
              <Text style={styles.rowDescription}>{item.description}</Text>
            </View>
            <Text style={styles.chevron}>›</Text>
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
  },
  list: { gap: 12 },
  row: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: colors.border,
    gap: 14,
  },
  rowInfo: { flex: 1 },
  rowTitle: {
    fontSize: 18,
    fontWeight: "500",
    color: colors.text,
    marginBottom: 2,
    fontFamily: fonts.serif,
    letterSpacing: -0.3,
  },
  rowDescription: {
    fontSize: 13,
    color: colors.textSecondary,
    fontFamily: fonts.sans,
  },
  chevron: { fontSize: 24, color: colors.textMuted, fontWeight: "300" },
});
