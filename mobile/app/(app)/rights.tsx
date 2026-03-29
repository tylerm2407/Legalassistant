import React, { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
} from "react-native";
import { useRouter } from "expo-router";
import { getRightsDomains, getRightsGuides } from "@/lib/api";
import type { RightsDomain, RightsGuide } from "@/lib/types";

const DOMAIN_ICONS: Record<string, string> = {
  landlord_tenant: "🏠",
  employment: "💼",
  consumer: "🛒",
  debt_collections: "💳",
  small_claims: "⚖️",
  contracts: "📝",
  traffic: "🚗",
  family_law: "👨‍👩‍👧",
  criminal_records: "📋",
  immigration: "🌍",
};

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
        <ActivityIndicator size="large" color="#1e40af" />
        <Text style={styles.loadingText}>Loading rights library...</Text>
      </View>
    );
  }

  // Guide list view
  if (selectedDomain) {
    const domainLabel = domains.find((d) => d.domain === selectedDomain)?.label || selectedDomain;

    return (
      <View style={styles.container}>
        {/* Back button + domain title */}
        <View style={styles.guideHeader}>
          <TouchableOpacity onPress={handleBackToDomains} style={styles.backBtn}>
            <Text style={styles.backBtnText}>← All Topics</Text>
          </TouchableOpacity>
          <Text style={styles.domainHeading}>{domainLabel}</Text>
        </View>

        {/* Search within guides */}
        <View style={styles.searchContainer}>
          <Text style={styles.searchIcon}>🔍</Text>
          <TextInput
            style={styles.searchInput}
            placeholder="Search guides..."
            placeholderTextColor="#94a3b8"
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
            <ActivityIndicator size="large" color="#1e40af" />
          </View>
        ) : error ? (
          <View style={styles.errorContainer}>
            <Text style={styles.errorIcon}>⚠️</Text>
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
                    {/* Explanation */}
                    {item.explanation ? (
                      <View style={styles.guideSection}>
                        <Text style={styles.guideSectionTitle}>Overview</Text>
                        <Text style={styles.guideSectionText}>{item.explanation}</Text>
                      </View>
                    ) : null}

                    {/* Your Rights */}
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

                    {/* Action Steps */}
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

                    {/* Deadlines */}
                    {item.deadlines && item.deadlines.length > 0 && (
                      <View style={styles.guideSection}>
                        <Text style={styles.guideSectionTitle}>Important Deadlines</Text>
                        {item.deadlines.map((deadline, i) => (
                          <View key={i} style={styles.deadlineRow}>
                            <Text style={styles.deadlineIcon}>⏰</Text>
                            <Text style={styles.deadlineText}>{deadline}</Text>
                          </View>
                        ))}
                      </View>
                    )}

                    {/* Common Mistakes */}
                    {item.common_mistakes && item.common_mistakes.length > 0 && (
                      <View style={styles.guideSection}>
                        <Text style={styles.guideSectionTitle}>Common Mistakes</Text>
                        {item.common_mistakes.map((mistake, i) => (
                          <View key={i} style={styles.bulletRow}>
                            <Text style={[styles.bulletDot, { color: "#dc2626" }]}>✕</Text>
                            <Text style={styles.bulletText}>{mistake}</Text>
                          </View>
                        ))}
                      </View>
                    )}

                    {/* When to Get a Lawyer */}
                    {item.when_to_get_a_lawyer ? (
                      <View style={[styles.guideSection, styles.lawyerSection]}>
                        <Text style={styles.lawyerTitle}>When to Get a Lawyer</Text>
                        <Text style={styles.lawyerText}>{item.when_to_get_a_lawyer}</Text>
                      </View>
                    ) : null}

                    {/* View full guide */}
                    <TouchableOpacity
                      style={styles.fullGuideButton}
                      onPress={() =>
                        router.push({
                          pathname: "/(app)/rights-guide",
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
                <Text style={styles.emptyIcon}>📭</Text>
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
      {/* Search bar */}
      <View style={styles.searchContainer}>
        <Text style={styles.searchIcon}>🔍</Text>
        <TextInput
          style={styles.searchInput}
          placeholder="Search legal topics..."
          placeholderTextColor="#94a3b8"
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
          <Text style={styles.errorIcon}>⚠️</Text>
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
              <View style={styles.domainIconContainer}>
                <Text style={styles.domainIcon}>
                  {DOMAIN_ICONS[item.domain] || "📖"}
                </Text>
              </View>
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
              <Text style={styles.emptyIcon}>🔍</Text>
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
    backgroundColor: "#f8fafc",
  },
  center: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    gap: 12,
  },
  loadingText: {
    fontSize: 15,
    color: "#64748b",
  },
  searchContainer: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#ffffff",
    marginHorizontal: 16,
    marginTop: 12,
    marginBottom: 4,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    paddingHorizontal: 14,
    height: 48,
    gap: 10,
  },
  searchIcon: {
    fontSize: 16,
  },
  searchInput: {
    flex: 1,
    fontSize: 15,
    color: "#0f172a",
    paddingVertical: 0,
  },
  clearIcon: {
    fontSize: 14,
    color: "#94a3b8",
    fontWeight: "700",
    padding: 4,
  },
  list: {
    padding: 16,
    gap: 10,
  },
  // Domain cards
  domainCard: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#ffffff",
    borderRadius: 14,
    padding: 16,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    gap: 14,
  },
  domainIconContainer: {
    width: 48,
    height: 48,
    borderRadius: 12,
    backgroundColor: "#eff6ff",
    justifyContent: "center",
    alignItems: "center",
  },
  domainIcon: {
    fontSize: 24,
  },
  domainInfo: {
    flex: 1,
  },
  domainTitle: {
    fontSize: 17,
    fontWeight: "700",
    color: "#0f172a",
    marginBottom: 2,
  },
  domainCount: {
    fontSize: 13,
    color: "#64748b",
  },
  domainChevron: {
    fontSize: 24,
    color: "#94a3b8",
    fontWeight: "300",
  },
  // Guide header
  guideHeader: {
    paddingHorizontal: 16,
    paddingTop: 12,
    gap: 4,
  },
  backBtn: {
    paddingVertical: 4,
  },
  backBtnText: {
    color: "#1e40af",
    fontSize: 15,
    fontWeight: "600",
  },
  domainHeading: {
    fontSize: 22,
    fontWeight: "800",
    color: "#0f172a",
  },
  // Guide cards
  guideCard: {
    backgroundColor: "#ffffff",
    borderRadius: 14,
    borderWidth: 1,
    borderColor: "#e2e8f0",
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
    fontSize: 16,
    fontWeight: "700",
    color: "#0f172a",
    marginBottom: 4,
  },
  guideDesc: {
    fontSize: 13,
    color: "#64748b",
    lineHeight: 18,
  },
  expandIcon: {
    fontSize: 12,
    color: "#94a3b8",
    marginTop: 4,
  },
  // Expanded guide content
  guideExpanded: {
    paddingHorizontal: 16,
    paddingBottom: 16,
    borderTopWidth: 1,
    borderTopColor: "#f1f5f9",
  },
  guideSection: {
    marginTop: 16,
  },
  guideSectionTitle: {
    fontSize: 15,
    fontWeight: "700",
    color: "#1e293b",
    marginBottom: 8,
  },
  guideSectionText: {
    fontSize: 14,
    color: "#475569",
    lineHeight: 21,
  },
  bulletRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 8,
    marginBottom: 6,
  },
  bulletDot: {
    fontSize: 14,
    color: "#1e40af",
    marginTop: 1,
    fontWeight: "700",
  },
  bulletText: {
    flex: 1,
    fontSize: 14,
    color: "#475569",
    lineHeight: 20,
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
    backgroundColor: "#1e40af",
    justifyContent: "center",
    alignItems: "center",
  },
  stepNumText: {
    color: "#ffffff",
    fontSize: 12,
    fontWeight: "700",
  },
  stepText: {
    flex: 1,
    fontSize: 14,
    color: "#334155",
    lineHeight: 20,
  },
  deadlineRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 8,
    marginBottom: 6,
  },
  deadlineIcon: {
    fontSize: 14,
    marginTop: 1,
  },
  deadlineText: {
    flex: 1,
    fontSize: 14,
    color: "#475569",
    lineHeight: 20,
  },
  lawyerSection: {
    backgroundColor: "#fef3c7",
    borderRadius: 10,
    padding: 14,
  },
  lawyerTitle: {
    fontSize: 15,
    fontWeight: "700",
    color: "#92400e",
    marginBottom: 6,
  },
  lawyerText: {
    fontSize: 14,
    color: "#78350f",
    lineHeight: 20,
  },
  fullGuideButton: {
    marginTop: 16,
    backgroundColor: "#eff6ff",
    paddingVertical: 12,
    borderRadius: 10,
    alignItems: "center",
  },
  fullGuideButtonText: {
    color: "#1e40af",
    fontSize: 15,
    fontWeight: "700",
  },
  // Error state
  errorContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 40,
    gap: 12,
  },
  errorIcon: {
    fontSize: 32,
  },
  errorText: {
    fontSize: 15,
    color: "#dc2626",
    textAlign: "center",
    lineHeight: 22,
  },
  retryButton: {
    backgroundColor: "#1e40af",
    paddingVertical: 10,
    paddingHorizontal: 24,
    borderRadius: 10,
    marginTop: 8,
  },
  retryButtonText: {
    color: "#ffffff",
    fontSize: 15,
    fontWeight: "700",
  },
  // Empty state
  emptyState: {
    alignItems: "center",
    padding: 40,
    gap: 12,
  },
  emptyIcon: {
    fontSize: 32,
  },
  emptyText: {
    color: "#94a3b8",
    fontSize: 15,
    textAlign: "center",
    lineHeight: 22,
  },
});
