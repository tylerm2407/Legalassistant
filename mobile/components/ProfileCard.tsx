import React from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { useRouter } from "expo-router";
import type { LegalProfile } from "@/lib/types";

interface ProfileCardProps {
  profile: LegalProfile;
  onPress?: () => void;
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.infoRow}>
      <Text style={styles.infoLabel}>{label}</Text>
      <Text style={styles.infoValue}>{value}</Text>
    </View>
  );
}

function Badge({
  label,
  count,
  color,
}: {
  label: string;
  count: number;
  color: string;
}) {
  return (
    <View style={[styles.badge, { backgroundColor: color + "15" }]}>
      <Text style={[styles.badgeCount, { color }]}>{count}</Text>
      <Text style={[styles.badgeLabel, { color }]}>{label}</Text>
    </View>
  );
}

export default function ProfileCard({ profile, onPress }: ProfileCardProps) {
  const router = useRouter();

  const handlePress = () => {
    if (onPress) {
      onPress();
    } else {
      router.push("/(app)/profile");
    }
  };

  const formatStatus = (value: string): string => {
    return value
      .replace(/-/g, " ")
      .replace(/\b\w/g, (c) => c.toUpperCase());
  };

  return (
    <TouchableOpacity
      style={styles.card}
      onPress={handlePress}
      activeOpacity={0.7}
    >
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>
            {profile.display_name.charAt(0).toUpperCase()}
          </Text>
        </View>
        <View style={styles.headerInfo}>
          <Text style={styles.name}>{profile.display_name}</Text>
          <View style={styles.stateBadge}>
            <Text style={styles.stateBadgeText}>{profile.state}</Text>
          </View>
        </View>
      </View>

      {/* Info rows */}
      <View style={styles.infoSection}>
        <InfoRow label="Housing" value={formatStatus(profile.housing_situation)} />
        <InfoRow label="Employment" value={formatStatus(profile.employment_type)} />
        <InfoRow label="Family" value={formatStatus(profile.family_status)} />
      </View>

      {/* Badges */}
      <View style={styles.badgeRow}>
        <Badge
          label="Legal Facts"
          count={profile.legal_facts.length}
          color="#1e40af"
        />
        <Badge
          label="Active Issues"
          count={profile.active_issues.filter((i) => i.status === "open").length}
          color="#dc2626"
        />
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#ffffff",
    borderRadius: 16,
    padding: 20,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 3,
    elevation: 2,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 16,
  },
  avatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: "#1e40af",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 14,
  },
  avatarText: {
    color: "#ffffff",
    fontSize: 20,
    fontWeight: "700",
  },
  headerInfo: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  name: {
    fontSize: 20,
    fontWeight: "700",
    color: "#0f172a",
  },
  stateBadge: {
    backgroundColor: "#eff6ff",
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  stateBadgeText: {
    fontSize: 13,
    fontWeight: "700",
    color: "#1e40af",
  },
  infoSection: {
    gap: 8,
    marginBottom: 16,
    borderTopWidth: 1,
    borderTopColor: "#f1f5f9",
    paddingTop: 14,
  },
  infoRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  infoLabel: {
    fontSize: 14,
    color: "#64748b",
    fontWeight: "500",
  },
  infoValue: {
    fontSize: 14,
    color: "#0f172a",
    fontWeight: "600",
  },
  badgeRow: {
    flexDirection: "row",
    gap: 12,
    borderTopWidth: 1,
    borderTopColor: "#f1f5f9",
    paddingTop: 14,
  },
  badge: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 6,
    paddingVertical: 10,
    borderRadius: 10,
  },
  badgeCount: {
    fontSize: 20,
    fontWeight: "800",
  },
  badgeLabel: {
    fontSize: 12,
    fontWeight: "600",
  },
});
