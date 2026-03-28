import React, { useState } from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
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
    backgroundColor: "#ffffff",
    borderRadius: 14,
    padding: 16,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.04,
    shadowRadius: 2,
    elevation: 1,
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
    color: "#0f172a",
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
    color: "#475569",
    lineHeight: 20,
    marginBottom: 10,
  },
  date: {
    fontSize: 12,
    color: "#94a3b8",
    marginBottom: 4,
  },
  notesSection: {
    marginTop: 10,
    borderTopWidth: 1,
    borderTopColor: "#f1f5f9",
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
    color: "#1e40af",
  },
  notesChevron: {
    fontSize: 10,
    color: "#1e40af",
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
    backgroundColor: "#cbd5e1",
    marginTop: 6,
  },
  noteText: {
    flex: 1,
    fontSize: 13,
    color: "#475569",
    lineHeight: 19,
  },
});
