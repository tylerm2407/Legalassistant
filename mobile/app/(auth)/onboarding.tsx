import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import { useRouter } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { createProfile } from "@/lib/api";

const US_STATES = [
  "Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut",
  "Delaware","Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa",
  "Kansas","Kentucky","Louisiana","Maine","Maryland","Massachusetts","Michigan",
  "Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada",
  "New Hampshire","New Jersey","New Mexico","New York","North Carolina",
  "North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania","Rhode Island",
  "South Carolina","South Dakota","Tennessee","Texas","Utah","Vermont",
  "Virginia","Washington","West Virginia","Wisconsin","Wyoming",
];

const HOUSING_OPTIONS = [
  { label: "Renter", value: "renter" },
  { label: "Homeowner", value: "homeowner" },
  { label: "Living with family", value: "family" },
  { label: "Unhoused / Transitional", value: "unhoused" },
  { label: "Other", value: "other" },
];

const EMPLOYMENT_OPTIONS = [
  { label: "Full-time employee", value: "full-time" },
  { label: "Part-time employee", value: "part-time" },
  { label: "Self-employed / Freelancer", value: "self-employed" },
  { label: "Unemployed", value: "unemployed" },
  { label: "Student", value: "student" },
  { label: "Retired", value: "retired" },
];

const FAMILY_OPTIONS = [
  { label: "Single", value: "single" },
  { label: "Married", value: "married" },
  { label: "Divorced / Separated", value: "divorced" },
  { label: "Single parent", value: "single-parent" },
  { label: "Domestic partnership", value: "domestic-partnership" },
];

export default function OnboardingScreen() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [name, setName] = useState("");
  const [state, setState] = useState("");
  const [showStatePicker, setShowStatePicker] = useState(false);
  const [stateSearch, setStateSearch] = useState("");
  const [housing, setHousing] = useState("");
  const [employment, setEmployment] = useState("");
  const [family, setFamily] = useState("");
  const [legalIssue, setLegalIssue] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const totalSteps = 5;
  const progress = ((step + 1) / totalSteps) * 100;

  const canProceed = (): boolean => {
    switch (step) {
      case 0:
        return name.trim().length > 0 && state.length > 0;
      case 1:
        return housing.length > 0;
      case 2:
        return employment.length > 0;
      case 3:
        return family.length > 0;
      case 4:
        return true;
      default:
        return false;
    }
  };

  const handleNext = async () => {
    if (step < totalSteps - 1) {
      setStep(step + 1);
      return;
    }

    setIsSubmitting(true);
    try {
      const userId = `user_${Date.now()}`;
      await createProfile({
        user_id: userId,
        display_name: name.trim(),
        state,
        housing_situation: housing,
        employment_type: employment,
        family_status: family,
        active_issues: legalIssue.trim()
          ? [
              {
                issue_type: "general",
                summary: legalIssue.trim(),
                status: "open",
                started_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
                notes: [],
              },
            ]
          : [],
        legal_facts: [],
        documents: [],
      });
      router.replace("/(app)/chat");
    } catch {
      router.replace("/(app)/chat");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleBack = () => {
    if (step > 0) setStep(step - 1);
  };

  const filteredStates = US_STATES.filter((s) =>
    s.toLowerCase().includes(stateSearch.toLowerCase())
  );

  const renderOptionButton = (
    label: string,
    value: string,
    selectedValue: string,
    onSelect: (v: string) => void
  ) => (
    <TouchableOpacity
      key={value}
      style={[
        styles.optionButton,
        selectedValue === value && styles.optionButtonSelected,
      ]}
      onPress={() => onSelect(value)}
      activeOpacity={0.7}
    >
      <Text
        style={[
          styles.optionButtonText,
          selectedValue === value && styles.optionButtonTextSelected,
        ]}
      >
        {label}
      </Text>
    </TouchableOpacity>
  );

  const renderStep = () => {
    switch (step) {
      case 0:
        return (
          <View style={styles.stepContent}>
            <Text style={styles.stepTitle}>Welcome to Lex</Text>
            <Text style={styles.stepSubtitle}>
              Let's start with the basics so we can give you personalized
              legal guidance.
            </Text>

            <Text style={styles.label}>Your Name</Text>
            <TextInput
              style={styles.textInput}
              placeholder="Enter your name"
              placeholderTextColor="#94a3b8"
              value={name}
              onChangeText={setName}
              autoFocus
            />

            <Text style={styles.label}>Your State</Text>
            <TouchableOpacity
              style={styles.pickerButton}
              onPress={() => setShowStatePicker(!showStatePicker)}
            >
              <Text
                style={[
                  styles.pickerButtonText,
                  !state && { color: "#94a3b8" },
                ]}
              >
                {state || "Select your state"}
              </Text>
              <Text style={styles.pickerChevron}>
                {showStatePicker ? "▲" : "▼"}
              </Text>
            </TouchableOpacity>

            {showStatePicker && (
              <View style={styles.statePickerContainer}>
                <TextInput
                  style={styles.stateSearchInput}
                  placeholder="Search states..."
                  placeholderTextColor="#94a3b8"
                  value={stateSearch}
                  onChangeText={setStateSearch}
                />
                <ScrollView
                  style={styles.stateList}
                  nestedScrollEnabled
                  keyboardShouldPersistTaps="handled"
                >
                  {filteredStates.map((s) => (
                    <TouchableOpacity
                      key={s}
                      style={[
                        styles.stateItem,
                        state === s && styles.stateItemSelected,
                      ]}
                      onPress={() => {
                        setState(s);
                        setShowStatePicker(false);
                        setStateSearch("");
                      }}
                    >
                      <Text
                        style={[
                          styles.stateItemText,
                          state === s && styles.stateItemTextSelected,
                        ]}
                      >
                        {s}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </ScrollView>
              </View>
            )}
          </View>
        );

      case 1:
        return (
          <View style={styles.stepContent}>
            <Text style={styles.stepTitle}>Housing Situation</Text>
            <Text style={styles.stepSubtitle}>
              This helps us understand tenant rights, property laws, and
              housing protections that apply to you.
            </Text>
            {HOUSING_OPTIONS.map((opt) =>
              renderOptionButton(opt.label, opt.value, housing, setHousing)
            )}
          </View>
        );

      case 2:
        return (
          <View style={styles.stepContent}>
            <Text style={styles.stepTitle}>Employment Type</Text>
            <Text style={styles.stepSubtitle}>
              Your employment status affects labor protections, benefits, and
              legal rights available to you.
            </Text>
            {EMPLOYMENT_OPTIONS.map((opt) =>
              renderOptionButton(
                opt.label,
                opt.value,
                employment,
                setEmployment
              )
            )}
          </View>
        );

      case 3:
        return (
          <View style={styles.stepContent}>
            <Text style={styles.stepTitle}>Family Status</Text>
            <Text style={styles.stepSubtitle}>
              Family status is relevant for custody, benefits, tax rights,
              and family law matters.
            </Text>
            {FAMILY_OPTIONS.map((opt) =>
              renderOptionButton(opt.label, opt.value, family, setFamily)
            )}
          </View>
        );

      case 4:
        return (
          <View style={styles.stepContent}>
            <Text style={styles.stepTitle}>Current Legal Issue</Text>
            <Text style={styles.stepSubtitle}>
              Tell us briefly about any legal issue you're dealing with. This
              is optional — you can always describe it later in chat.
            </Text>
            <TextInput
              style={[styles.textInput, styles.textArea]}
              placeholder="e.g., My landlord is refusing to return my security deposit..."
              placeholderTextColor="#94a3b8"
              value={legalIssue}
              onChangeText={setLegalIssue}
              multiline
              numberOfLines={5}
              textAlignVertical="top"
            />
          </View>
        );

      default:
        return null;
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        style={styles.flex}
        behavior={Platform.OS === "ios" ? "padding" : "height"}
      >
        {/* Progress bar */}
        <View style={styles.progressContainer}>
          <View style={styles.progressTrack}>
            <View style={[styles.progressFill, { width: `${progress}%` }]} />
          </View>
          <Text style={styles.progressText}>
            Step {step + 1} of {totalSteps}
          </Text>
        </View>

        <ScrollView
          style={styles.flex}
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
        >
          {renderStep()}
        </ScrollView>

        {/* Navigation */}
        <View style={styles.navContainer}>
          {step > 0 ? (
            <TouchableOpacity
              style={styles.backButton}
              onPress={handleBack}
              activeOpacity={0.7}
            >
              <Text style={styles.backButtonText}>Back</Text>
            </TouchableOpacity>
          ) : (
            <View />
          )}

          <TouchableOpacity
            style={[
              styles.nextButton,
              !canProceed() && styles.nextButtonDisabled,
            ]}
            onPress={handleNext}
            disabled={!canProceed() || isSubmitting}
            activeOpacity={0.85}
          >
            <Text style={styles.nextButtonText}>
              {isSubmitting
                ? "Setting up..."
                : step === totalSteps - 1
                ? "Start Chatting"
                : "Continue"}
            </Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f8fafc",
  },
  flex: {
    flex: 1,
  },
  progressContainer: {
    paddingHorizontal: 24,
    paddingTop: 16,
    paddingBottom: 8,
  },
  progressTrack: {
    height: 6,
    backgroundColor: "#e2e8f0",
    borderRadius: 3,
    overflow: "hidden",
  },
  progressFill: {
    height: "100%",
    backgroundColor: "#1e40af",
    borderRadius: 3,
  },
  progressText: {
    marginTop: 8,
    fontSize: 13,
    color: "#64748b",
    textAlign: "center",
  },
  scrollContent: {
    padding: 24,
    paddingBottom: 40,
  },
  stepContent: {
    gap: 12,
  },
  stepTitle: {
    fontSize: 28,
    fontWeight: "800",
    color: "#0f172a",
    marginBottom: 4,
  },
  stepSubtitle: {
    fontSize: 15,
    color: "#64748b",
    lineHeight: 22,
    marginBottom: 12,
  },
  label: {
    fontSize: 14,
    fontWeight: "600",
    color: "#334155",
    marginTop: 8,
    marginBottom: 4,
  },
  textInput: {
    backgroundColor: "#ffffff",
    borderWidth: 1,
    borderColor: "#e2e8f0",
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 14,
    fontSize: 16,
    color: "#0f172a",
  },
  textArea: {
    minHeight: 140,
    paddingTop: 14,
  },
  pickerButton: {
    backgroundColor: "#ffffff",
    borderWidth: 1,
    borderColor: "#e2e8f0",
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 14,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  pickerButtonText: {
    fontSize: 16,
    color: "#0f172a",
  },
  pickerChevron: {
    fontSize: 12,
    color: "#64748b",
  },
  statePickerContainer: {
    backgroundColor: "#ffffff",
    borderWidth: 1,
    borderColor: "#e2e8f0",
    borderRadius: 12,
    maxHeight: 240,
    overflow: "hidden",
  },
  stateSearchInput: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 15,
    borderBottomWidth: 1,
    borderBottomColor: "#e2e8f0",
    color: "#0f172a",
  },
  stateList: {
    maxHeight: 192,
  },
  stateItem: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: "#f1f5f9",
  },
  stateItemSelected: {
    backgroundColor: "#eff6ff",
  },
  stateItemText: {
    fontSize: 15,
    color: "#334155",
  },
  stateItemTextSelected: {
    color: "#1e40af",
    fontWeight: "600",
  },
  optionButton: {
    backgroundColor: "#ffffff",
    borderWidth: 1.5,
    borderColor: "#e2e8f0",
    borderRadius: 12,
    paddingVertical: 16,
    paddingHorizontal: 20,
  },
  optionButtonSelected: {
    borderColor: "#1e40af",
    backgroundColor: "#eff6ff",
  },
  optionButtonText: {
    fontSize: 16,
    color: "#334155",
    fontWeight: "500",
  },
  optionButtonTextSelected: {
    color: "#1e40af",
    fontWeight: "700",
  },
  navContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 24,
    paddingVertical: 16,
    borderTopWidth: 1,
    borderTopColor: "#e2e8f0",
    backgroundColor: "#ffffff",
  },
  backButton: {
    paddingVertical: 12,
    paddingHorizontal: 20,
  },
  backButtonText: {
    fontSize: 16,
    color: "#64748b",
    fontWeight: "600",
  },
  nextButton: {
    backgroundColor: "#1e40af",
    paddingVertical: 14,
    paddingHorizontal: 32,
    borderRadius: 12,
  },
  nextButtonDisabled: {
    opacity: 0.4,
  },
  nextButtonText: {
    color: "#ffffff",
    fontSize: 16,
    fontWeight: "700",
  },
});
