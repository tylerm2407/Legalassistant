import React, { useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  LayoutAnimation,
  Platform,
  UIManager,
} from "react-native";
import { colors, fonts, tokens } from "@/lib/theme";
import type { LegalProfile } from "@/lib/types";

if (Platform.OS === "android" && UIManager.setLayoutAnimationEnabledExperimental) {
  UIManager.setLayoutAnimationEnabledExperimental(true);
}

interface ChatProfileBarProps {
  profile: LegalProfile | null;
}

export default function ChatProfileBar({ profile }: ChatProfileBarProps) {
  const [expanded, setExpanded] = useState(false);

  if (!profile) return null;

  const toggle = () => {
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
    setExpanded(!expanded);
  };

  const openIssues = profile.active_issues.filter((i) => i.status === "open").length;

  return (
    <TouchableOpacity style={styles.container} onPress={toggle} activeOpacity={0.8}>
      <View style={styles.collapsedRow}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>
            {profile.display_name?.charAt(0)?.toUpperCase() || "?"}
          </Text>
        </View>
        <Text style={styles.name} numberOfLines={1}>{profile.display_name}</Text>
        <View style={styles.stateBadge}>
          <Text style={styles.stateText}>{profile.state}</Text>
        </View>
        <View style={styles.factsBadge}>
          <Text style={styles.factsText}>{profile.legal_facts.length} facts</Text>
        </View>
        <Text style={styles.chevron}>{expanded ? "▲" : "▼"}</Text>
      </View>

      {expanded && (
        <View style={styles.expandedContent}>
          <View style={styles.infoGrid}>
            <InfoPill label="Housing" value={profile.housing_situation} />
            <InfoPill label="Employment" value={profile.employment_type} />
            <InfoPill label="Family" value={profile.family_status} />
          </View>

          {openIssues > 0 && (
            <View style={styles.issuesRow}>
              <Text style={styles.issuesLabel}>Active Issues</Text>
              <Text style={styles.issuesCount}>{openIssues}</Text>
            </View>
          )}

          {profile.legal_facts.length > 0 && (
            <View style={styles.factsSection}>
              <Text style={styles.factsLabel}>Recent Facts</Text>
              {profile.legal_facts.slice(-3).map((fact, i) => (
                <View key={i} style={styles.factRow}>
                  <View style={styles.factDot} />
                  <Text style={styles.factText} numberOfLines={2}>{fact}</Text>
                </View>
              ))}
            </View>
          )}
        </View>
      )}
    </TouchableOpacity>
  );
}

function InfoPill({ label, value }: { label: string; value: string }) {
  const display = value.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
  return (
    <View style={styles.infoPill}>
      <Text style={styles.infoPillLabel}>{label}</Text>
      <Text style={styles.infoPillValue} numberOfLines={1}>{display}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  collapsedRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 12,
    paddingVertical: 8,
    gap: 8,
  },
  avatar: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: colors.primary,
    justifyContent: "center",
    alignItems: "center",
  },
  avatarText: { color: "#fff", fontSize: 13, fontWeight: "700" },
  name: { fontSize: 14, fontWeight: "600", color: colors.text, flex: 1 },
  stateBadge: {
    backgroundColor: colors.elevated,
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
  },
  stateText: { fontSize: 11, fontWeight: "700", color: colors.primary },
  factsBadge: {
    backgroundColor: colors.elevated,
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
  },
  factsText: { fontSize: 11, fontWeight: "600", color: colors.textSecondary },
  chevron: { fontSize: 10, color: colors.textMuted },
  expandedContent: {
    paddingHorizontal: 12,
    paddingBottom: 12,
    gap: 10,
  },
  infoGrid: {
    flexDirection: "row",
    gap: 8,
  },
  infoPill: {
    flex: 1,
    backgroundColor: colors.elevated,
    borderRadius: 8,
    padding: 8,
  },
  infoPillLabel: { fontSize: 10, color: colors.textMuted, fontWeight: "600", marginBottom: 2 },
  infoPillValue: { fontSize: 12, color: colors.text, fontWeight: "600" },
  issuesRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    backgroundColor: tokens.warningSubtle,
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  issuesLabel: { fontSize: 12, color: colors.warning, fontWeight: "600", fontFamily: fonts.sans },
  issuesCount: { fontSize: 16, color: colors.warning, fontWeight: "700", fontFamily: fonts.sans },
  factsSection: { gap: 6 },
  factsLabel: { fontSize: 12, color: colors.textMuted, fontWeight: "600" },
  factRow: { flexDirection: "row", alignItems: "flex-start", gap: 6 },
  factDot: {
    width: 5,
    height: 5,
    borderRadius: 2.5,
    backgroundColor: colors.primary,
    marginTop: 5,
  },
  factText: { flex: 1, fontSize: 12, color: colors.textSecondary, lineHeight: 17 },
});
