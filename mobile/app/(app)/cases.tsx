import React, { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  RefreshControl,
  ActivityIndicator,
} from "react-native";
import IssueCard from "@/components/IssueCard";
import { getProfile } from "@/lib/api";
import type { LegalIssue, IssueStatus } from "@/lib/types";

type FilterOption = "all" | IssueStatus;

const FILTERS: { label: string; value: FilterOption }[] = [
  { label: "All", value: "all" },
  { label: "Open", value: "open" },
  { label: "Resolved", value: "resolved" },
  { label: "Watching", value: "watching" },
  { label: "Escalated", value: "escalated" },
];

export default function CasesScreen() {
  const [issues, setIssues] = useState<LegalIssue[]>([]);
  const [filter, setFilter] = useState<FilterOption>("all");
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const loadCases = useCallback(async () => {
    try {
      const profile = await getProfile("user_placeholder");
      setIssues(profile.active_issues);
    } catch {
      // Keep existing issues on error
    }
  }, []);

  useEffect(() => {
    const load = async () => {
      setIsLoading(true);
      await loadCases();
      setIsLoading(false);
    };
    load();
  }, [loadCases]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await loadCases();
    setIsRefreshing(false);
  };

  const filteredIssues =
    filter === "all"
      ? issues
      : issues.filter((issue) => issue.status === filter);

  const renderItem = ({ item }: { item: LegalIssue }) => (
    <View style={styles.cardWrapper}>
      <IssueCard issue={item} />
    </View>
  );

  const renderEmpty = () => {
    if (isLoading) return null;

    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyIcon}>📁</Text>
        <Text style={styles.emptyTitle}>No active cases</Text>
        <Text style={styles.emptyText}>
          {filter === "all"
            ? "Ask CaseMate about a legal issue to get started. Your cases will appear here."
            : `No ${filter} cases found. Try changing the filter.`}
        </Text>
      </View>
    );
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#1e40af" />
        <Text style={styles.loadingText}>Loading your cases...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Filter bar */}
      <View style={styles.filterBar}>
        <FlatList
          horizontal
          data={FILTERS}
          renderItem={({ item }) => (
            <TouchableOpacity
              style={[
                styles.filterChip,
                filter === item.value && styles.filterChipActive,
              ]}
              onPress={() => setFilter(item.value)}
              activeOpacity={0.7}
            >
              <Text
                style={[
                  styles.filterChipText,
                  filter === item.value && styles.filterChipTextActive,
                ]}
              >
                {item.label}
              </Text>
            </TouchableOpacity>
          )}
          keyExtractor={(item) => item.value}
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.filterList}
        />
      </View>

      {/* Issues count */}
      {filteredIssues.length > 0 && (
        <Text style={styles.countText}>
          {filteredIssues.length} case{filteredIssues.length !== 1 ? "s" : ""}
        </Text>
      )}

      {/* Issues list */}
      <FlatList
        data={filteredIssues}
        renderItem={renderItem}
        keyExtractor={(_, index) => index.toString()}
        contentContainerStyle={styles.listContent}
        ListEmptyComponent={renderEmpty}
        refreshControl={
          <RefreshControl
            refreshing={isRefreshing}
            onRefresh={handleRefresh}
            tintColor="#1e40af"
            colors={["#1e40af"]}
          />
        }
        showsVerticalScrollIndicator={false}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f8fafc",
  },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    gap: 12,
  },
  loadingText: {
    fontSize: 15,
    color: "#64748b",
  },
  filterBar: {
    backgroundColor: "#ffffff",
    borderBottomWidth: 1,
    borderBottomColor: "#e2e8f0",
  },
  filterList: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    gap: 8,
  },
  filterChip: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: "#f1f5f9",
    marginRight: 8,
  },
  filterChipActive: {
    backgroundColor: "#1e40af",
  },
  filterChipText: {
    fontSize: 14,
    fontWeight: "600",
    color: "#64748b",
  },
  filterChipTextActive: {
    color: "#ffffff",
  },
  countText: {
    fontSize: 13,
    color: "#64748b",
    fontWeight: "500",
    paddingHorizontal: 20,
    paddingTop: 14,
    paddingBottom: 4,
  },
  listContent: {
    padding: 16,
    paddingBottom: 32,
    flexGrow: 1,
  },
  cardWrapper: {
    marginBottom: 12,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: 40,
    paddingVertical: 60,
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: 16,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: "700",
    color: "#0f172a",
    marginBottom: 8,
  },
  emptyText: {
    fontSize: 15,
    color: "#64748b",
    textAlign: "center",
    lineHeight: 22,
  },
});
