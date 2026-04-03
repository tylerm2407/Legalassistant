import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  TouchableOpacity,
} from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { getRightsGuide } from "@/lib/api";
import { colors } from "@/lib/theme";
import type { RightsGuide } from "@/lib/types";

export default function RightsGuideScreen() {
  const { guideId } = useLocalSearchParams<{ guideId: string }>();
  const router = useRouter();
  const [guide, setGuide] = useState<RightsGuide | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (guideId) {
      loadGuide(guideId);
    }
  }, [guideId]);

  const loadGuide = async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await getRightsGuide(id);
      setGuide(data.guide);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to load guide";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Loading guide...</Text>
      </View>
    );
  }

  if (error || !guide) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorIcon}>⚠️</Text>
        <Text style={styles.errorText}>{error || "Guide not found."}</Text>
        <TouchableOpacity
          style={styles.retryButton}
          onPress={() => guideId && loadGuide(guideId)}
        >
          <Text style={styles.retryButtonText}>Retry</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
          <Text style={styles.backButtonText}>← Go back</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>{guide.title}</Text>
      <View style={styles.domainBadge}>
        <Text style={styles.domainBadgeText}>
          {guide.domain.replace(/_/g, " ")}
        </Text>
      </View>

      {guide.description ? (
        <Text style={styles.description}>{guide.description}</Text>
      ) : null}

      {guide.explanation ? (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Overview</Text>
          <Text style={styles.sectionText}>{guide.explanation}</Text>
        </View>
      ) : null}

      {guide.your_rights && guide.your_rights.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Your Rights</Text>
          {guide.your_rights.map((right, i) => (
            <View key={i} style={styles.bulletRow}>
              <View style={styles.bulletDot} />
              <Text style={styles.bulletText}>{right}</Text>
            </View>
          ))}
        </View>
      )}

      {guide.action_steps && guide.action_steps.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Action Steps</Text>
          {guide.action_steps.map((step, i) => (
            <View key={i} style={styles.stepRow}>
              <View style={styles.stepNumCircle}>
                <Text style={styles.stepNumText}>{i + 1}</Text>
              </View>
              <Text style={styles.stepText}>{step}</Text>
            </View>
          ))}
        </View>
      )}

      {guide.deadlines && guide.deadlines.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Important Deadlines</Text>
          {guide.deadlines.map((deadline, i) => (
            <View key={i} style={styles.deadlineRow}>
              <Text style={styles.deadlineIcon}>⏰</Text>
              <Text style={styles.deadlineText}>{deadline}</Text>
            </View>
          ))}
        </View>
      )}

      {guide.common_mistakes && guide.common_mistakes.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Common Mistakes to Avoid</Text>
          {guide.common_mistakes.map((mistake, i) => (
            <View key={i} style={styles.mistakeRow}>
              <Text style={styles.mistakeIcon}>✕</Text>
              <Text style={styles.mistakeText}>{mistake}</Text>
            </View>
          ))}
        </View>
      )}

      {guide.when_to_get_a_lawyer ? (
        <View style={[styles.section, styles.lawyerSection]}>
          <Text style={styles.lawyerTitle}>When to Get a Lawyer</Text>
          <Text style={styles.lawyerText}>{guide.when_to_get_a_lawyer}</Text>
        </View>
      ) : null}

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    padding: 20,
  },
  center: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    gap: 12,
    padding: 40,
    backgroundColor: colors.background,
  },
  loadingText: {
    fontSize: 15,
    color: colors.textSecondary,
  },
  errorIcon: {
    fontSize: 32,
  },
  errorText: {
    color: colors.error,
    fontSize: 16,
    textAlign: "center",
  },
  retryButton: {
    backgroundColor: colors.primary,
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
  backButton: {
    paddingVertical: 8,
  },
  backButtonText: {
    color: colors.primary,
    fontSize: 15,
    fontWeight: "600",
  },
  title: {
    fontSize: 24,
    fontWeight: "800",
    color: colors.text,
    marginBottom: 8,
  },
  domainBadge: {
    backgroundColor: colors.elevated,
    paddingHorizontal: 12,
    paddingVertical: 5,
    borderRadius: 8,
    alignSelf: "flex-start",
    marginBottom: 16,
  },
  domainBadgeText: {
    fontSize: 13,
    fontWeight: "700",
    color: colors.primary,
    textTransform: "capitalize",
  },
  description: {
    fontSize: 15,
    color: colors.textSecondary,
    lineHeight: 23,
    marginBottom: 16,
  },
  section: {
    marginTop: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: colors.text,
    marginBottom: 12,
  },
  sectionText: {
    fontSize: 15,
    color: colors.textSecondary,
    lineHeight: 23,
  },
  bulletRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 10,
    marginBottom: 10,
  },
  bulletDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.primary,
    marginTop: 6,
  },
  bulletText: {
    flex: 1,
    fontSize: 15,
    color: colors.textSecondary,
    lineHeight: 22,
  },
  stepRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 12,
    marginBottom: 14,
  },
  stepNumCircle: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: colors.primary,
    justifyContent: "center",
    alignItems: "center",
  },
  stepNumText: {
    color: "#ffffff",
    fontSize: 13,
    fontWeight: "700",
  },
  stepText: {
    flex: 1,
    fontSize: 15,
    color: colors.textSecondary,
    lineHeight: 22,
  },
  deadlineRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 10,
    marginBottom: 10,
    backgroundColor: "#78350f20",
    borderRadius: 10,
    padding: 12,
  },
  deadlineIcon: {
    fontSize: 16,
    marginTop: 1,
  },
  deadlineText: {
    flex: 1,
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  mistakeRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 10,
    marginBottom: 10,
    backgroundColor: colors.error + "15",
    borderRadius: 10,
    padding: 12,
  },
  mistakeIcon: {
    fontSize: 14,
    color: colors.error,
    fontWeight: "700",
    marginTop: 2,
  },
  mistakeText: {
    flex: 1,
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  lawyerSection: {
    backgroundColor: "#78350f20",
    borderRadius: 14,
    padding: 18,
    marginTop: 24,
  },
  lawyerTitle: {
    fontSize: 17,
    fontWeight: "700",
    color: colors.warning,
    marginBottom: 8,
  },
  lawyerText: {
    fontSize: 15,
    color: colors.textSecondary,
    lineHeight: 22,
  },
});
