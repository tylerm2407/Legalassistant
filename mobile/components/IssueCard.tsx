import React, { useState } from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { colors } from "@/lib/theme";
import type { LegalIssue, IssueStatus } from "@/lib/types";

interface IssueCardProps {
  issue: LegalIssue;
}

const STATUS_CONFIG: Record<
  IssueStatus,
  { label: string; bg: string; text: string }
> = {
  open: { label: "Open", bg: "#fef3c7", text: "#92400e" },
  resolved: { label: "Resolved", bg: "#d1fae5", text: "#065f46" },
  watching: { label: "Watching", bg: "#dbeafe", text: "#1e40af" },
  escalated: { label: "Escalated", bg: "#fee2e2", text: "#991b1b" },
};

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export default function IssueCard({ issue }: IssueCardProps) {
  const [showNotes, setShowNotes] = useState(false);
  const statusConfig = STATUS_CONFIG[issue.status];

  return (
    <View style={styles.card}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.issueType}>{issue.issue_type}</Text>
        <View
          style={[styles.statusBadge, { backgroundColor: statusConfig.bg }]}
        >
          <Text style={[styles.statusText, { color: statusConfig.text }]}>
            {statusConfig.label}
          </Text>
        </View>
      </View>

      {/* Summary */}
      <Text style={styles.summary}>{issue.summary}</Text>

      {/* Date */}
      <Text style={styles.date}>Started {formatDate(issue.started_at)}</Text>

      {/* Notes */}
      {issue.notes.length > 0 && (
        <View style={styles.notesSection}>
          <TouchableOpacity
            style={styles.notesToggle}
            onPress={() => setShowNotes(!showNotes)}
            activeOpacity={0.7}
          >
            <Text style={styles.notesToggleText}>
              {showNotes ? "Hide" : "Show"} Notes ({issue.notes.length})
            </Text>
            <Text style={styles.notesChevron}>
              {showNotes ? "▲" : "▼"}
            </Text>
          </TouchableOpacity>

          {showNotes && (
            <View style={styles.notesList}>
              {issue.notes.map((note, index) => (
                <View key={index} style={styles.noteItem}>
                  <View style={styles.noteBullet} />
                  <Text style={styles.noteText}>{note}</Text>
                </View>
              ))}
            </View>
          )}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    borderRadius: 14,
    padding: 16,
    borderWidth: 1,
    borderColor: colors.border,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 10,
  },
  issueType: {
    fontSize: 17,
    fontWeight: "700",
    color: colors.text,
    textTransform: "capitalize",
    flex: 1,
    marginRight: 8,
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  statusText: {
    fontSize: 12,
    fontWeight: "700",
    textTransform: "uppercase",
    letterSpacing: 0.3,
  },
  summary: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
    marginBottom: 10,
  },
  date: {
    fontSize: 12,
    color: colors.textMuted,
    marginBottom: 4,
  },
  notesSection: {
    marginTop: 10,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    paddingTop: 10,
  },
  notesToggle: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  notesToggleText: {
    fontSize: 13,
    fontWeight: "600",
    color: colors.primary,
  },
  notesChevron: {
    fontSize: 10,
    color: colors.primary,
  },
  notesList: {
    marginTop: 10,
    gap: 8,
  },
  noteItem: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 8,
  },
  noteBullet: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: colors.textMuted,
    marginTop: 6,
  },
  noteText: {
    flex: 1,
    fontSize: 13,
    color: colors.textSecondary,
    lineHeight: 19,
  },
});
