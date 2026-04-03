import React from "react";
import { View, Text, TouchableOpacity, ScrollView, StyleSheet, Linking } from "react-native";
import { colors } from "@/lib/theme";

export default function SubscriptionScreen() {
  const handleUpgrade = () => {
    Linking.openURL("https://casemate.legal/subscribe");
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.planCard}>
        <Text style={styles.planLabel}>Current Plan</Text>
        <Text style={styles.planName}>Free</Text>
        <Text style={styles.planDescription}>
          Basic legal guidance with limited conversations per day.
        </Text>
      </View>

      <View style={styles.proCard}>
        <Text style={styles.proLabel}>CaseMate Pro</Text>
        <Text style={styles.proPrice}>$20/month</Text>
        <View style={styles.features}>
          {[
            "Unlimited conversations",
            "Full legal profile memory",
            "Document analysis",
            "Demand letter generation",
            "Priority response times",
            "Attorney referrals",
          ].map((feature) => (
            <View key={feature} style={styles.featureRow}>
              <Text style={styles.featureCheck}>✓</Text>
              <Text style={styles.featureText}>{feature}</Text>
            </View>
          ))}
        </View>
        <TouchableOpacity style={styles.upgradeButton} onPress={handleUpgrade} activeOpacity={0.85}>
          <Text style={styles.upgradeButtonText}>Upgrade to Pro</Text>
        </TouchableOpacity>
      </View>

      <Text style={styles.disclaimer}>
        You'll be redirected to our secure checkout page. Subscription can be cancelled at any time.
      </Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: 20 },
  planCard: {
    backgroundColor: colors.surface,
    borderRadius: 14,
    padding: 20,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: 20,
  },
  planLabel: { fontSize: 13, color: colors.textSecondary, fontWeight: "600", marginBottom: 4 },
  planName: { fontSize: 28, fontWeight: "800", color: colors.text, marginBottom: 6 },
  planDescription: { fontSize: 14, color: colors.textMuted, lineHeight: 20 },
  proCard: {
    backgroundColor: colors.elevated,
    borderRadius: 14,
    padding: 20,
    borderWidth: 1,
    borderColor: colors.primary,
    marginBottom: 20,
  },
  proLabel: { fontSize: 20, fontWeight: "800", color: colors.primary, marginBottom: 4 },
  proPrice: { fontSize: 32, fontWeight: "800", color: colors.text, marginBottom: 16 },
  features: { gap: 10, marginBottom: 20 },
  featureRow: { flexDirection: "row", alignItems: "center", gap: 10 },
  featureCheck: { fontSize: 16, color: colors.success, fontWeight: "700" },
  featureText: { fontSize: 15, color: colors.text },
  upgradeButton: {
    backgroundColor: colors.primary,
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: "center",
  },
  upgradeButtonText: { color: "#ffffff", fontSize: 17, fontWeight: "700" },
  disclaimer: { fontSize: 12, color: colors.textMuted, textAlign: "center", lineHeight: 18 },
});
