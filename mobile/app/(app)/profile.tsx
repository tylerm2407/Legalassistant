import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  Alert,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import ProfileCard from "@/components/ProfileCard";
import IssueCard from "@/components/IssueCard";
import { getProfile } from "@/lib/api";
import type { LegalProfile } from "@/lib/types";

const EMPTY_PROFILE: LegalProfile = {
  user_id: "user_placeholder",
  display_name: "",
  state: "",
  housing_situation: "",
  employment_type: "",
  family_status: "",
  active_issues: [],
  legal_facts: [],
  documents: [],
  member_since: new Date().toISOString(),
  conversation_count: 0,
};

export default function ProfileScreen() {
  const [profile, setProfile] = useState<LegalProfile>(EMPTY_PROFILE);
  const [isLoading, setIsLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState("");
  const [editState, setEditState] = useState("");
  const [editHousing, setEditHousing] = useState("");
  const [editEmployment, setEditEmployment] = useState("");
  const [editFamily, setEditFamily] = useState("");

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    setIsLoading(true);
    try {
      const data = await getProfile("user_placeholder");
      setProfile(data);
      setEditName(data.display_name);
      setEditState(data.state);
      setEditHousing(data.housing_situation);
      setEditEmployment(data.employment_type);
      setEditFamily(data.family_status);
    } catch {
      // Use empty profile on error
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = () => {
    setProfile((prev) => ({
      ...prev,
      display_name: editName,
      state: editState,
      housing_situation: editHousing,
      employment_type: editEmployment,
      family_status: editFamily,
    }));
    setIsEditing(false);
    Alert.alert("Saved", "Your profile has been updated.");
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#1e40af" />
        <Text style={styles.loadingText}>Loading profile...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Profile Card */}
      <ProfileCard profile={profile} onPress={() => {}} />

      {/* Edit toggle */}
      <TouchableOpacity
        style={styles.editToggle}
        onPress={() => setIsEditing(!isEditing)}
        activeOpacity={0.7}
      >
        <Text style={styles.editToggleText}>
          {isEditing ? "Cancel Editing" : "Edit Profile"}
        </Text>
      </TouchableOpacity>

      {/* Editable fields */}
      {isEditing && (
        <View style={styles.editSection}>
          <Text style={styles.sectionTitle}>Edit Information</Text>

          <View style={styles.field}>
            <Text style={styles.fieldLabel}>Name</Text>
            <TextInput
              style={styles.fieldInput}
              value={editName}
              onChangeText={setEditName}
              placeholder="Your name"
              placeholderTextColor="#94a3b8"
            />
          </View>

          <View style={styles.field}>
            <Text style={styles.fieldLabel}>State</Text>
            <TextInput
              style={styles.fieldInput}
              value={editState}
              onChangeText={setEditState}
              placeholder="Your state"
              placeholderTextColor="#94a3b8"
            />
          </View>

          <View style={styles.field}>
            <Text style={styles.fieldLabel}>Housing</Text>
            <TextInput
              style={styles.fieldInput}
              value={editHousing}
              onChangeText={setEditHousing}
              placeholder="Housing situation"
              placeholderTextColor="#94a3b8"
            />
          </View>

          <View style={styles.field}>
            <Text style={styles.fieldLabel}>Employment</Text>
            <TextInput
              style={styles.fieldInput}
              value={editEmployment}
              onChangeText={setEditEmployment}
              placeholder="Employment type"
              placeholderTextColor="#94a3b8"
            />
          </View>

          <View style={styles.field}>
            <Text style={styles.fieldLabel}>Family Status</Text>
            <TextInput
              style={styles.fieldInput}
              value={editFamily}
              onChangeText={setEditFamily}
              placeholder="Family status"
              placeholderTextColor="#94a3b8"
            />
          </View>

          <TouchableOpacity
            style={styles.saveButton}
            onPress={handleSave}
            activeOpacity={0.85}
          >
            <Text style={styles.saveButtonText}>Save Changes</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Active Issues */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>
          Active Issues ({profile.active_issues.length})
        </Text>
        {profile.active_issues.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>
              No active issues. Chat with Lex to get started.
            </Text>
          </View>
        ) : (
          <View style={styles.issuesList}>
            {profile.active_issues.map((issue, index) => (
              <IssueCard key={index} issue={issue} />
            ))}
          </View>
        )}
      </View>

      {/* Documents */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>
          Documents ({profile.documents.length})
        </Text>
        {profile.documents.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>
              No documents uploaded yet.
            </Text>
          </View>
        ) : (
          <View style={styles.documentsList}>
            {profile.documents.map((doc, index) => (
              <View key={index} style={styles.documentItem}>
                <Text style={styles.documentIcon}>📄</Text>
                <Text style={styles.documentName}>{doc}</Text>
              </View>
            ))}
          </View>
        )}
      </View>

      {/* Stats */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Activity</Text>
        <View style={styles.statsRow}>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>{profile.conversation_count}</Text>
            <Text style={styles.statLabel}>Conversations</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>{profile.legal_facts.length}</Text>
            <Text style={styles.statLabel}>Legal Facts</Text>
          </View>
        </View>
      </View>

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f8fafc",
  },
  content: {
    padding: 20,
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
  editToggle: {
    alignSelf: "flex-end",
    marginTop: 12,
    paddingVertical: 8,
    paddingHorizontal: 16,
  },
  editToggleText: {
    fontSize: 15,
    fontWeight: "600",
    color: "#1e40af",
  },
  editSection: {
    backgroundColor: "#ffffff",
    borderRadius: 14,
    padding: 20,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    marginTop: 8,
    gap: 14,
  },
  section: {
    marginTop: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: "#0f172a",
    marginBottom: 12,
  },
  field: {
    gap: 4,
  },
  fieldLabel: {
    fontSize: 13,
    fontWeight: "600",
    color: "#64748b",
  },
  fieldInput: {
    backgroundColor: "#f8fafc",
    borderWidth: 1,
    borderColor: "#e2e8f0",
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontSize: 15,
    color: "#0f172a",
  },
  saveButton: {
    backgroundColor: "#1e40af",
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 4,
  },
  saveButtonText: {
    color: "#ffffff",
    fontSize: 16,
    fontWeight: "700",
  },
  issuesList: {
    gap: 12,
  },
  emptyState: {
    backgroundColor: "#ffffff",
    borderRadius: 12,
    padding: 24,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#e2e8f0",
  },
  emptyStateText: {
    fontSize: 14,
    color: "#94a3b8",
    textAlign: "center",
  },
  documentsList: {
    gap: 8,
  },
  documentItem: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#ffffff",
    borderRadius: 10,
    padding: 14,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    gap: 10,
  },
  documentIcon: {
    fontSize: 18,
  },
  documentName: {
    flex: 1,
    fontSize: 14,
    color: "#334155",
    fontWeight: "500",
  },
  statsRow: {
    flexDirection: "row",
    gap: 12,
  },
  statCard: {
    flex: 1,
    backgroundColor: "#ffffff",
    borderRadius: 12,
    padding: 16,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#e2e8f0",
  },
  statValue: {
    fontSize: 28,
    fontWeight: "800",
    color: "#1e40af",
  },
  statLabel: {
    fontSize: 12,
    color: "#64748b",
    fontWeight: "500",
    marginTop: 4,
  },
});
