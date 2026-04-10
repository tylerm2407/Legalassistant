import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { useRouter } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { colors, fonts } from "@/lib/theme";

/**
 * Landing / splash screen. Editorial, quiet, trustworthy.
 * No emoji, no gradient, no glow — serif headline, forest green accent.
 */
export default function LandingScreen() {
  const router = useRouter();

  return (
    <SafeAreaView style={styles.container} edges={["top", "bottom"]}>
      <View style={styles.content}>
        <View style={styles.header}>
          <Text style={styles.eyebrow}>CASEMATE</Text>
          <Text style={styles.headline}>Your legal friend.</Text>
          <Text style={styles.subhead}>
            Personalized guidance that remembers your situation — so you never
            have to start from scratch.
          </Text>
        </View>

        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={styles.primaryButton}
            onPress={() => router.push("/(auth)/onboarding")}
            activeOpacity={0.85}
          >
            <Text style={styles.primaryButtonText}>Get started</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.secondaryButton}
            onPress={() => router.push("/(auth)/login")}
            activeOpacity={0.85}
          >
            <Text style={styles.secondaryButtonText}>I already have an account</Text>
          </TouchableOpacity>
        </View>

        <Text style={styles.disclaimer}>
          CaseMate provides legal information, not legal advice. For serious
          legal matters, consult a licensed attorney.
        </Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    flex: 1,
    justifyContent: "space-between",
    paddingHorizontal: 28,
    paddingTop: 64,
    paddingBottom: 32,
  },
  header: {
    marginTop: 48,
  },
  eyebrow: {
    fontFamily: fonts.sans,
    fontSize: 12,
    fontWeight: "600",
    letterSpacing: 2,
    color: colors.primary,
    marginBottom: 20,
  },
  headline: {
    fontFamily: fonts.serif,
    fontSize: 44,
    lineHeight: 50,
    fontWeight: "500",
    color: colors.text,
    marginBottom: 16,
    letterSpacing: -0.5,
  },
  subhead: {
    fontFamily: fonts.sans,
    fontSize: 17,
    lineHeight: 26,
    color: colors.textSecondary,
    maxWidth: 340,
  },
  buttonContainer: {
    width: "100%",
    gap: 12,
  },
  primaryButton: {
    backgroundColor: colors.primary,
    paddingVertical: 16,
    borderRadius: 8,
    alignItems: "center",
  },
  primaryButtonText: {
    color: "#FFFFFF",
    fontSize: 16,
    fontWeight: "600",
    fontFamily: fonts.sans,
  },
  secondaryButton: {
    backgroundColor: "transparent",
    paddingVertical: 16,
    borderRadius: 8,
    alignItems: "center",
    borderWidth: 1,
    borderColor: colors.border,
  },
  secondaryButtonText: {
    color: colors.text,
    fontSize: 16,
    fontWeight: "500",
    fontFamily: fonts.sans,
  },
  disclaimer: {
    fontSize: 12,
    lineHeight: 17,
    color: colors.textMuted,
    textAlign: "center",
    paddingHorizontal: 16,
    fontFamily: fonts.sans,
  },
});
