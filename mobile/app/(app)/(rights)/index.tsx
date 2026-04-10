import React, { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  ActivityIndicator,
} from "react-native";
import { useRouter } from "expo-router";
import { getRightsDomains, getRightsGuides } from "@/lib/api";
import { colors, fonts, tokens } from "@/lib/theme";
import type { RightsDomain, RightsGuide } from "@/lib/types";

interface ExpandedGuide extends RightsGuide {
  expanded: boolean;
}

export default function RightsScreen() {
  const router = useRouter();
  const [domains, setDomains] = useState<RightsDomain[]>([]);
  const [guides, setGuides] = useState<ExpandedGuide[]>([]);
  const [selectedDomain, setSelectedDomain] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [guidesLoading, setGuidesLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDomains();
  }, []);

  const loadDomains = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getRightsDomains();
      setDomains(data.domains);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to load rights domains";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const loadGuides = async (domain: string) => {
    setSelectedDomain(domain);
    setGuidesLoading(true);
    setError(null);
    setSearchQuery("");
    try {
      const data = await getRightsGuides(domain);
      setGuides(data.guides.map((g) => ({ ...g, expanded: false })));
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to load guides";
      setError(message);
      setGuides([]);
    } finally {
      setGuidesLoading(false);
    }
  };

  const toggleGuide = useCallback((guideId: string) => {
    setGuides((prev) =>
      prev.map((g) =>
        g.id === guideId ? { ...g, expanded: !g.expanded } : g
      )
    );
  }, []);

  const filteredDomains = domains.filter((d) =>
    d.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
    d.domain.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredGuides = guides.filter((g) =>
    g.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    g.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleBackToDomains = () => {
    setSelectedDomain(null);
    setGuides([]);
    setSearchQuery("");
    setError(null);
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Loading rights library...</Text>
      </View>
    );
  }

  // Guide list view
  if (selectedDomain) {
    const domainLabel = domains.find((d) => d.domain === selectedDomain)?.label || selectedDomain;

    return (
      <View style={styles.container}>
        <View style={styles.guideHeader}>
          <TouchableOpacity onPress={handleBackToDomains} style={styles.backBtn}>
            <Text style={styles.backBtnText}>← All Topics</Text>
          </TouchableOpacity>
          <Text style={styles.domainHeading}>{domainLabel}</Text>
        </View>

        <View style={styles.searchContainer}>
          <TextInput
            style={styles.searchInput}
            placeholder="Search guides..."
            placeholderTextColor={colors.textMuted}
            value={searchQuery}
            onChangeText={setSearchQuery}
            autoCorrect={false}
          />
          {searchQuery.length > 0 && (
            <TouchableOpacity onPress={() => setSearchQuery("")}>
              <Text style={styles.clearIcon}>✕</Text>
            </TouchableOpacity>
          )}
        </View>

        {guidesLoading ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color={colors.primary} />
          </View>
        ) : error ? (
          <View style={styles.errorContainer}>
            <Text style={styles.errorText}>{error}</Text>
            <TouchableOpacity
              style={styles.retryButton}
              onPress={() => loadGuides(selectedDomain)}
            >
              <Text style={styles.retryButtonText}>Retry</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <FlatList
            data={filteredGuides}
            keyExtractor={(item) => item.id}
            contentContainerStyle={styles.list}
            showsVerticalScrollIndicator={false}
            renderItem={({ item }) => (
              <View style={styles.guideCard}>
                <TouchableOpacity
                  style={styles.guideTitleRow}
                  onPress={() => toggleGuide(item.id)}
                  activeOpacity={0.7}
                >
                  <View style={styles.guideTitleContent}>
                    <Text style={styles.guideTitle}>{item.title}</Text>
                    <Text style={styles.guideDesc} numberOfLines={item.expanded ? undefined : 2}>
                      {item.description}
                    </Text>
                  </View>
                  <Text style={styles.expandIcon}>
                    {item.expanded ? "▲" : "▼"}
                  </Text>
                </TouchableOpacity>

                {item.expanded && (
                  <View style={styles.guideExpanded}>
                    {item.explanation ? (
                      <View style={styles.guideSection}>
                        <Text style={styles.guideSectionTitle}>Overview</Text>
                        <Text style={styles.guideSectionText}>{item.explanation}</Text>
                      </View>
                    ) : null}

                    {item.your_rights && item.your_rights.length > 0 && (
                      <View style={styles.guideSection}>
                        <Text style={styles.guideSectionTitle}>Your Rights</Text>
                        {item.your_rights.map((right, i) => (
                          <View key={i} style={styles.bulletRow}>
                            <Text style={styles.bulletDot}>•</Text>
                            <Text style={styles.bulletText}>{right}</Text>
                          </View>
                        ))}
                      </View>
                    )}

                    {item.action_steps && item.action_steps.length > 0 && (
                      <View style={styles.guideSection}>
                        <Text style={styles.guideSectionTitle}>Action Steps</Text>
                        {item.action_steps.map((step, i) => (
                          <View key={i} style={styles.stepRow}>
                            <View style={styles.stepNum}>
                              <Text style={styles.stepNumText}>{i + 1}</Text>
                            </View>
                            <Text style={styles.stepText}>{step}</Text>
                          </View>
                        ))}
                      </View>
                    )}

                    {item.deadlines && item.deadlines.length > 0 && (
                      <View style={styles.guideSection}>
                        <Text style={styles.guideSectionTitle}>Important Deadlines</Text>
                        {item.deadlines.map((deadline, i) => (
                          <View key={i} style={styles.deadlineRow}>
                            <Text style={styles.deadlineText}>{deadline}</Text>
                          </View>
                        ))}
                      </View>
                    )}

                    {item.common_mistakes && item.common_mistakes.length > 0 && (
                      <View style={styles.guideSection}>
                        <Text style={styles.guideSectionTitle}>Common Mistakes</Text>
                        {item.common_mistakes.map((mistake, i) => (
                          <View key={i} style={styles.bulletRow}>
                            <Text style={[styles.bulletDot, { color: colors.warning }]}>✕</Text>
                            <Text style={styles.bulletText}>{mistake}</Text>
                          </View>
                        ))}
                      </View>
                    )}

                    {item.when_to_get_a_lawyer ? (
                      <View style={[styles.guideSection, styles.lawyerSection]}>
                        <Text style={styles.lawyerTitle}>When to Get a Lawyer</Text>
                        <Text style={styles.lawyerText}>{item.when_to_get_a_lawyer}</Text>
                      </View>
                    ) : null}

                    <TouchableOpacity
                      style={styles.fullGuideButton}
                      onPress={() =>
                        router.push({
                          pathname: "/(app)/(rights)/[guideId]",
                          params: { guideId: item.id },
                        } as never)
                      }
                      activeOpacity={0.7}
                    >
                      <Text style={styles.fullGuideButtonText}>View Full Guide →</Text>
                    </TouchableOpacity>
                  </View>
                )}
              </View>
            )}
            ListEmptyComponent={
              <View style={styles.emptyState}>
                <Text style={styles.emptyText}>
                  {searchQuery
                    ? `No guides matching "${searchQuery}"`
                    : "No guides available for this topic."}
                </Text>
              </View>
            }
          />
        )}
      </View>
    );
  }

  // Domain list view
  return (
    <View style={styles.container}>
      <View style={styles.searchContainer}>
        <TextInput
          style={styles.searchInput}
          placeholder="Search legal topics..."
          placeholderTextColor={colors.textMuted}
          value={searchQuery}
          onChangeText={setSearchQuery}
          autoCorrect={false}
        />
        {searchQuery.length > 0 && (
          <TouchableOpacity onPress={() => setSearchQuery("")}>
            <Text style={styles.clearIcon}>✕</Text>
          </TouchableOpacity>
        )}
      </View>

      {error ? (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity style={styles.retryButton} onPress={loadDomains}>
            <Text style={styles.retryButtonText}>Retry</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <FlatList
          data={filteredDomains}
          keyExtractor={(item) => item.domain}
          contentContainerStyle={styles.list}
          showsVerticalScrollIndicator={false}
          renderItem={({ item }) => (
            <TouchableOpacity
              style={styles.domainCard}
              onPress={() => loadGuides(item.domain)}
              activeOpacity={0.7}
            >
              <View style={styles.domainInfo}>
                <Text style={styles.domainTitle}>{item.label}</Text>
                <Text style={styles.domainCount}>
                  {item.guide_count} {item.guide_count === 1 ? "guide" : "guides"}
                </Text>
              </View>
              <Text style={styles.domainChevron}>›</Text>
            </TouchableOpacity>
          )}
          ListEmptyComponent={
            <View style={styles.emptyState}>
              <Text style={styles.emptyText}>
                {searchQuery
                  ? `No topics matching "${searchQuery}"`
                  : "No rights guides available."}
              </Text>
            </View>
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  center: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    gap: 12,
    backgroundColor: colors.background,
  },
  loadingText: {
    fontSize: 15,
    color: colors.textSecondary,
    fontFamily: fonts.sans,
  },
  searchContainer: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surface,
    marginHorizontal: 16,
    marginTop: 12,
    marginBottom: 4,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: 14,
    height: 48,
    gap: 10,
  },
  searchInput: {
    flex: 1,
    fontSize: 15,
    color: colors.text,
    paddingVertical: 0,
    fontFamily: fonts.sans,
  },
  clearIcon: {
    fontSize: 14,
    color: colors.textMuted,
    fontWeight: "700",
    padding: 4,
  },
  list: {
    padding: 16,
    gap: 10,
  },
  domainCard: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: colors.border,
    gap: 14,
  },
  domainInfo: {
    flex: 1,
  },
  domainTitle: {
    fontSize: 17,
    fontWeight: "600",
    color: colors.text,
    marginBottom: 2,
    fontFamily: fonts.sans,
  },
  domainCount: {
    fontSize: 12,
    color: colors.textMuted,
    fontFamily: fonts.sans,
    letterSpacing: 1.2,
    textTransform: "uppercase",
  },
  domainChevron: {
    fontSize: 24,
    color: colors.textMuted,
    fontWeight: "300",
  },
  guideHeader: {
    paddingHorizontal: 16,
    paddingTop: 12,
    gap: 8,
  },
  backBtn: {
    paddingVertical: 4,
  },
  backBtnText: {
    color: colors.primary,
    fontSize: 14,
    fontWeight: "600",
    fontFamily: fonts.sans,
  },
  domainHeading: {
    fontSize: 28,
    fontWeight: "500",
    color: colors.text,
    fontFamily: fonts.serif,
    letterSpacing: -0.4,
  },
  guideCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.border,
    overflow: "hidden",
  },
  guideTitleRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    padding: 16,
    gap: 12,
  },
  guideTitleContent: {
    flex: 1,
  },
  guideTitle: {
    fontSize: 18,
    fontWeight: "500",
    color: colors.text,
    marginBottom: 4,
    fontFamily: fonts.serif,
    letterSpacing: -0.3,
  },
  guideDesc: {
    fontSize: 13,
    color: colors.textSecondary,
    lineHeight: 18,
    fontFamily: fonts.sans,
  },
  expandIcon: {
    fontSize: 12,
    color: colors.textMuted,
    marginTop: 4,
  },
  guideExpanded: {
    paddingHorizontal: 16,
    paddingBottom: 16,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  guideSection: {
    marginTop: 16,
  },
  guideSectionTitle: {
    fontSize: 12,
    fontWeight: "600",
    color: colors.textMuted,
    marginBottom: 8,
    fontFamily: fonts.sans,
    letterSpacing: 1.5,
    textTransform: "uppercase",
  },
  guideSectionText: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 21,
    fontFamily: fonts.sans,
  },
  bulletRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 8,
    marginBottom: 6,
  },
  bulletDot: {
    fontSize: 14,
    color: colors.primary,
    marginTop: 1,
    fontWeight: "700",
  },
  bulletText: {
    flex: 1,
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
    fontFamily: fonts.sans,
  },
  stepRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 10,
    marginBottom: 10,
  },
  stepNum: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: colors.primary,
    justifyContent: "center",
    alignItems: "center",
  },
  stepNumText: {
    color: "#ffffff",
    fontSize: 12,
    fontWeight: "700",
    fontFamily: fonts.sans,
  },
  stepText: {
    flex: 1,
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
    fontFamily: fonts.sans,
  },
  deadlineRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 8,
    marginBottom: 6,
  },
  deadlineText: {
    flex: 1,
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
    fontFamily: fonts.sans,
  },
  lawyerSection: {
    backgroundColor: tokens.warningSubtle,
    borderRadius: 8,
    padding: 14,
  },
  lawyerTitle: {
    fontSize: 12,
    fontWeight: "600",
    color: colors.warning,
    marginBottom: 6,
    fontFamily: fonts.sans,
    letterSpacing: 1.5,
    textTransform: "uppercase",
  },
  lawyerText: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
    fontFamily: fonts.sans,
  },
  fullGuideButton: {
    marginTop: 16,
    backgroundColor: colors.elevated,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: "center",
  },
  fullGuideButtonText: {
    color: colors.primary,
    fontSize: 14,
    fontWeight: "600",
    fontFamily: fonts.sans,
  },
  errorContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 40,
    gap: 12,
  },
  errorText: {
    fontSize: 15,
    color: colors.error,
    textAlign: "center",
    lineHeight: 22,
    fontFamily: fonts.sans,
  },
  retryButton: {
    backgroundColor: colors.primary,
    paddingVertical: 10,
    paddingHorizontal: 24,
    borderRadius: 8,
    marginTop: 8,
  },
  retryButtonText: {
    color: "#ffffff",
    fontSize: 14,
    fontWeight: "600",
    fontFamily: fonts.sans,
  },
  emptyState: {
    alignItems: "center",
    padding: 40,
    gap: 12,
  },
  emptyText: {
    color: colors.textSecondary,
    fontSize: 15,
    textAlign: "center",
    lineHeight: 22,
    fontFamily: fonts.sans,
  },
});
