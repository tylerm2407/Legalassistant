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
import { supabase } from "@/lib/supabase";
import { colors, fonts } from "@/lib/theme";
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
  const [userId, setUserId] = useState("");

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.user?.id) setUserId(session.user.id);
    });
  }, []);

  const loadCases = useCallback(async () => {
    if (!userId) return;
    try {
      const profile = await getProfile(userId);
      setIssues(profile.active_issues);
    } catch {
      // Keep existing issues on error
    }
  }, [userId]);

  useEffect(() => {
    if (!userId) return;
    const load = async () => {
      setIsLoading(true);
      await loadCases();
      setIsLoading(false);
    };
    load();
  }, [loadCases, userId]);

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
        <ActivityIndicator size="large" color={colors.primary} />
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
            tintColor={colors.primary}
            colors={[colors.primary]}
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
    backgroundColor: colors.background,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    gap: 12,
    backgroundColor: colors.background,
  },
  loadingText: {
    fontSize: 15,
    color: colors.textSecondary,
  },
  filterBar: {
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  filterList: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    gap: 8,
  },
  filterChip: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
    backgroundColor: colors.elevated,
    marginRight: 8,
  },
  filterChipActive: {
    backgroundColor: colors.primary,
  },
  filterChipText: {
    fontSize: 14,
    fontWeight: "600",
    color: colors.textSecondary,
    fontFamily: fonts.sans,
  },
  filterChipTextActive: {
    color: "#ffffff",
  },
  countText: {
    fontSize: 13,
    color: colors.textSecondary,
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
  emptyTitle: {
    fontSize: 24,
    fontWeight: "500",
    color: colors.text,
    marginBottom: 8,
    fontFamily: fonts.serif,
    letterSpacing: -0.3,
  },
  emptyText: {
    fontSize: 15,
    color: colors.textSecondary,
    textAlign: "center",
    lineHeight: 22,
    fontFamily: fonts.sans,
  },
});
