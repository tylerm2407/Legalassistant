import React from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { useRouter } from "expo-router";
import { colors, fonts, tokens } from "@/lib/theme";
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
  bg,
}: {
  label: string;
  count: number;
  color: string;
  bg: string;
}) {
  return (
    <View style={[styles.badge, { backgroundColor: bg }]}>
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
      router.push("/(app)/(profile)" as never);
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
          color={colors.primary}
          bg={tokens.accentSubtle}
        />
        <Badge
          label="Active Issues"
          count={profile.active_issues.filter((i) => i.status === "open").length}
          color={colors.warning}
          bg={tokens.warningSubtle}
        />
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 20,
    borderWidth: 1,
    borderColor: colors.border,
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
    backgroundColor: colors.primary,
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
    fontSize: 24,
    fontWeight: "500",
    color: colors.text,
    fontFamily: fonts.serif,
    letterSpacing: -0.3,
  },
  stateBadge: {
    backgroundColor: colors.elevated,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  stateBadgeText: {
    fontSize: 13,
    fontWeight: "700",
    color: colors.primary,
  },
  infoSection: {
    gap: 8,
    marginBottom: 16,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    paddingTop: 14,
  },
  infoRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  infoLabel: {
    fontSize: 14,
    color: colors.textSecondary,
    fontWeight: "500",
  },
  infoValue: {
    fontSize: 14,
    color: colors.text,
    fontWeight: "600",
  },
  badgeRow: {
    flexDirection: "row",
    gap: 12,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    paddingTop: 14,
  },
  badge: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 6,
    paddingVertical: 10,
    borderRadius: 8,
  },
  badgeCount: {
    fontSize: 20,
    fontWeight: "700",
    fontFamily: fonts.sans,
  },
  badgeLabel: {
    fontSize: 11,
    fontWeight: "600",
    textTransform: "uppercase",
    letterSpacing: 1.2,
    fontFamily: fonts.sans,
  },
});
