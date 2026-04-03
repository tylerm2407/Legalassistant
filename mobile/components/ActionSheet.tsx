import React, { useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  Modal,
  ActivityIndicator,
  Alert,
} from "react-native";
import * as Clipboard from "expo-clipboard";
import {
  generateLetter,
  generateRights,
  generateChecklist,
} from "@/lib/api";
import { colors } from "@/lib/theme";

interface ActionSheetProps {
  visible: boolean;
  onDismiss: () => void;
  userId: string;
  issueType: string;
  issueDetails: string;
}

type ActionType = "letter" | "rights" | "checklist" | null;

export default function ActionSheet({
  visible,
  onDismiss,
  userId,
  issueType,
  issueDetails,
}: ActionSheetProps) {
  const [loading, setLoading] = useState(false);
  const [activeAction, setActiveAction] = useState<ActionType>(null);
  const [resultText, setResultText] = useState("");

  const handleAction = async (action: ActionType) => {
    if (!action) return;
    setLoading(true);
    setActiveAction(action);
    setResultText("");

    try {
      switch (action) {
        case "letter": {
          const result = await generateLetter(userId, issueType, issueDetails);
          setResultText(result.letter_text);
          break;
        }
        case "rights": {
          const result = await generateRights(userId, issueType);
          const rightsDisplay = [
            result.summary_text,
            "",
            "Key Rights:",
            ...result.key_rights.map((r) => `  - ${r}`),
          ].join("\n");
          setResultText(rightsDisplay);
          break;
        }
        case "checklist": {
          const result = await generateChecklist(userId, issueType);
          const checklistDisplay = result.items
            .map((item, i) => {
              const deadline = result.deadlines[i];
              return deadline
                ? `[ ] ${item} (by ${deadline})`
                : `[ ] ${item}`;
            })
            .join("\n");
          setResultText(checklistDisplay);
          break;
        }
      }
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Something went wrong";
      setResultText(`Error: ${message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    await Clipboard.setStringAsync(resultText);
    Alert.alert("Copied", "Text copied to clipboard.");
  };

  const handleDismiss = () => {
    setActiveAction(null);
    setResultText("");
    setLoading(false);
    onDismiss();
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent
      onRequestClose={handleDismiss}
    >
      <TouchableOpacity
        style={styles.overlay}
        activeOpacity={1}
        onPress={handleDismiss}
      >
        <TouchableOpacity
          style={styles.sheet}
          activeOpacity={1}
          onPress={() => {}}
        >
          {/* Handle */}
          <View style={styles.handleContainer}>
            <View style={styles.handle} />
          </View>

          <Text style={styles.title}>Generate Action</Text>
          <Text style={styles.subtitle}>
            Choose what you'd like CaseMate to generate for your issue.
          </Text>

          {/* Action buttons */}
          {!resultText && !loading && (
            <View style={styles.actions}>
              <TouchableOpacity
                style={styles.actionButton}
                onPress={() => handleAction("letter")}
                activeOpacity={0.7}
              >
                <Text style={styles.actionIcon}>✉</Text>
                <View style={styles.actionInfo}>
                  <Text style={styles.actionLabel}>Demand Letter</Text>
                  <Text style={styles.actionDesc}>
                    Professional letter asserting your rights
                  </Text>
                </View>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.actionButton}
                onPress={() => handleAction("rights")}
                activeOpacity={0.7}
              >
                <Text style={styles.actionIcon}>⚖</Text>
                <View style={styles.actionInfo}>
                  <Text style={styles.actionLabel}>Rights Summary</Text>
                  <Text style={styles.actionDesc}>
                    Overview of your legal rights for this issue
                  </Text>
                </View>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.actionButton}
                onPress={() => handleAction("checklist")}
                activeOpacity={0.7}
              >
                <Text style={styles.actionIcon}>✓</Text>
                <View style={styles.actionInfo}>
                  <Text style={styles.actionLabel}>Action Checklist</Text>
                  <Text style={styles.actionDesc}>
                    Step-by-step checklist with deadlines
                  </Text>
                </View>
              </TouchableOpacity>
            </View>
          )}

          {/* Loading */}
          {loading && (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color={colors.primary} />
              <Text style={styles.loadingText}>
                Generating your{" "}
                {activeAction === "letter"
                  ? "demand letter"
                  : activeAction === "rights"
                  ? "rights summary"
                  : "checklist"}
                ...
              </Text>
            </View>
          )}

          {/* Result */}
          {resultText && !loading && (
            <View style={styles.resultContainer}>
              <ScrollView
                style={styles.resultScroll}
                showsVerticalScrollIndicator
              >
                <Text style={styles.resultText}>{resultText}</Text>
              </ScrollView>

              <View style={styles.resultActions}>
                <TouchableOpacity
                  style={styles.copyButton}
                  onPress={handleCopy}
                  activeOpacity={0.7}
                >
                  <Text style={styles.copyButtonText}>Copy to Clipboard</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={styles.newActionButton}
                  onPress={() => {
                    setResultText("");
                    setActiveAction(null);
                  }}
                  activeOpacity={0.7}
                >
                  <Text style={styles.newActionButtonText}>
                    Generate Another
                  </Text>
                </TouchableOpacity>
              </View>
            </View>
          )}

          {/* Dismiss */}
          <TouchableOpacity
            style={styles.dismissButton}
            onPress={handleDismiss}
            activeOpacity={0.7}
          >
            <Text style={styles.dismissButtonText}>Close</Text>
          </TouchableOpacity>
        </TouchableOpacity>
      </TouchableOpacity>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: "rgba(0, 0, 0, 0.4)",
    justifyContent: "flex-end",
  },
  sheet: {
    backgroundColor: colors.surface,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    paddingHorizontal: 24,
    paddingBottom: 40,
    maxHeight: "85%",
  },
  handleContainer: {
    alignItems: "center",
    paddingVertical: 12,
  },
  handle: {
    width: 40,
    height: 4,
    borderRadius: 2,
    backgroundColor: colors.border,
  },
  title: {
    fontSize: 22,
    fontWeight: "800",
    color: colors.text,
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: 20,
  },
  actions: {
    gap: 12,
  },
  actionButton: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.elevated,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 14,
    padding: 16,
    gap: 14,
  },
  actionIcon: {
    fontSize: 28,
    width: 44,
    textAlign: "center",
  },
  actionInfo: {
    flex: 1,
  },
  actionLabel: {
    fontSize: 16,
    fontWeight: "700",
    color: colors.text,
    marginBottom: 2,
  },
  actionDesc: {
    fontSize: 13,
    color: colors.textSecondary,
  },
  loadingContainer: {
    alignItems: "center",
    paddingVertical: 40,
    gap: 16,
  },
  loadingText: {
    fontSize: 15,
    color: colors.textSecondary,
  },
  resultContainer: {
    flex: 1,
  },
  resultScroll: {
    maxHeight: 300,
    backgroundColor: colors.elevated,
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: colors.border,
  },
  resultText: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 22,
  },
  resultActions: {
    flexDirection: "row",
    gap: 12,
    marginTop: 14,
  },
  copyButton: {
    flex: 1,
    backgroundColor: colors.primary,
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: "center",
  },
  copyButtonText: {
    color: "#ffffff",
    fontSize: 15,
    fontWeight: "700",
  },
  newActionButton: {
    flex: 1,
    backgroundColor: colors.elevated,
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: "center",
  },
  newActionButtonText: {
    color: colors.textSecondary,
    fontSize: 15,
    fontWeight: "600",
  },
  dismissButton: {
    marginTop: 16,
    alignItems: "center",
    paddingVertical: 12,
  },
  dismissButtonText: {
    fontSize: 15,
    color: colors.textMuted,
    fontWeight: "600",
  },
});
