import React from "react";
import { View, Text, TouchableOpacity, ScrollView, StyleSheet } from "react-native";
import { useRouter } from "expo-router";
import { colors } from "@/lib/theme";

const MENU_ITEMS = [
  { title: "Find Attorneys", icon: "👨‍⚖️", description: "Search for attorneys by state and specialty", route: "/(app)/(more)/attorneys" },
  { title: "Deadlines", icon: "⏰", description: "Track your legal deadlines", route: "/(app)/(more)/deadlines" },
  { title: "Documents", icon: "📄", description: "Upload and analyze legal documents", route: "/(app)/(more)/documents" },
  { title: "Subscription", icon: "💎", description: "Manage your CaseMate plan", route: "/(app)/(more)/subscription" },
];

export default function MoreScreen() {
  const router = useRouter();

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.heading}>More</Text>
      <Text style={styles.subheading}>Additional tools and settings</Text>
      <View style={styles.list}>
        {MENU_ITEMS.map((item) => (
          <TouchableOpacity
            key={item.title}
            style={styles.row}
            onPress={() => router.push(item.route as any)}
            activeOpacity={0.7}
          >
            <Text style={styles.rowIcon}>{item.icon}</Text>
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
  content: { padding: 20 },
  heading: { fontSize: 24, fontWeight: "800", color: colors.text, marginBottom: 4 },
  subheading: { fontSize: 14, color: colors.textSecondary, marginBottom: 24 },
  list: { gap: 12 },
  row: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surface,
    borderRadius: 14,
    padding: 16,
    borderWidth: 1,
    borderColor: colors.border,
    gap: 14,
  },
  rowIcon: { fontSize: 28 },
  rowInfo: { flex: 1 },
  rowTitle: { fontSize: 17, fontWeight: "700", color: colors.text, marginBottom: 2 },
  rowDescription: { fontSize: 13, color: colors.textSecondary },
  chevron: { fontSize: 24, color: colors.textMuted, fontWeight: "300" },
});
