import React, { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  Alert,
  RefreshControl,
} from "react-native";
import ProfileCard from "@/components/ProfileCard";
import IssueCard from "@/components/IssueCard";
import { getProfile, createProfile } from "@/lib/api";
import { supabase } from "@/lib/supabase";
import { colors } from "@/lib/theme";
import type { LegalProfile } from "@/lib/types";

export default function ProfileScreen() {
  const [profile, setProfile] = useState<LegalProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [editName, setEditName] = useState("");
  const [editState, setEditState] = useState("");
  const [editHousing, setEditHousing] = useState("");
  const [editEmployment, setEditEmployment] = useState("");
  const [editFamily, setEditFamily] = useState("");
  const [userId, setUserId] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [showAllFacts, setShowAllFacts] = useState(false);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.user?.id) {
        setUserId(session.user.id);
      }
    });
  }, []);

  useEffect(() => {
    if (userId) loadProfile();
  }, [userId]);

  const loadProfile = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getProfile(userId);
      setProfile(data);
      setEditName(data.display_name);
      setEditState(data.state);
      setEditHousing(data.housing_situation);
      setEditEmployment(data.employment_type);
      setEditFamily(data.family_status);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to load profile";
      setError(message);
      setProfile({
        user_id: userId,
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
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true);
    try {
      const data = await getProfile(userId);
      setProfile(data);
      setEditName(data.display_name);
      setEditState(data.state);
      setEditHousing(data.housing_situation);
      setEditEmployment(data.employment_type);
      setEditFamily(data.family_status);
      setError(null);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to refresh profile";
      setError(message);
    } finally {
      setIsRefreshing(false);
    }
  }, [userId]);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const updated = await createProfile({
        user_id: userId,
        display_name: editName,
        state: editState,
        housing_situation: editHousing,
        employment_type: editEmployment,
        family_status: editFamily,
      });
      setProfile(updated);
      setIsEditing(false);
      Alert.alert("Saved", "Your profile has been updated.");
    } catch (err: unknown) {
      Alert.alert("Error", err instanceof Error ? err.message : "Failed to save profile.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleLogout = async () => {
    Alert.alert(
      "Sign Out",
      "Are you sure you want to sign out?",
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Sign Out",
          style: "destructive",
          onPress: async () => {
            await supabase.auth.signOut();
          },
        },
      ]
    );
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Loading profile...</Text>
      </View>
    );
  }

  const factsToShow = showAllFacts
    ? (profile?.legal_facts || [])
    : (profile?.legal_facts || []).slice(0, 5);

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl
          refreshing={isRefreshing}
          onRefresh={handleRefresh}
          tintColor={colors.primary}
          colors={[colors.primary]}
        />
      }
    >
      {/* Error banner */}
      {error && (
        <View style={styles.errorBanner}>
          <Text style={styles.errorBannerText}>{error}</Text>
          <TouchableOpacity onPress={loadProfile}>
            <Text style={styles.errorRetryText}>Retry</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Profile Card */}
      {profile && <ProfileCard profile={profile} onPress={() => {}} />}

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
              placeholderTextColor={colors.textMuted}
            />
          </View>

          <View style={styles.field}>
            <Text style={styles.fieldLabel}>State</Text>
            <TextInput
              style={styles.fieldInput}
              value={editState}
              onChangeText={setEditState}
              placeholder="Your state"
              placeholderTextColor={colors.textMuted}
            />
          </View>

          <View style={styles.field}>
            <Text style={styles.fieldLabel}>Housing</Text>
            <TextInput
              style={styles.fieldInput}
              value={editHousing}
              onChangeText={setEditHousing}
              placeholder="Housing situation"
              placeholderTextColor={colors.textMuted}
            />
          </View>

          <View style={styles.field}>
            <Text style={styles.fieldLabel}>Employment</Text>
            <TextInput
              style={styles.fieldInput}
              value={editEmployment}
              onChangeText={setEditEmployment}
              placeholder="Employment type"
              placeholderTextColor={colors.textMuted}
            />
          </View>

          <View style={styles.field}>
            <Text style={styles.fieldLabel}>Family Status</Text>
            <TextInput
              style={styles.fieldInput}
              value={editFamily}
              onChangeText={setEditFamily}
              placeholder="Family status"
              placeholderTextColor={colors.textMuted}
            />
          </View>

          <TouchableOpacity
            style={[styles.saveButton, isSaving && styles.saveButtonDisabled]}
            onPress={handleSave}
            disabled={isSaving}
            activeOpacity={0.85}
          >
            {isSaving ? (
              <ActivityIndicator size="small" color="#ffffff" />
            ) : (
              <Text style={styles.saveButtonText}>Save Changes</Text>
            )}
          </TouchableOpacity>
        </View>
      )}

      {/* Legal Facts -- THE core differentiator display */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>
            Legal Facts ({profile?.legal_facts.length || 0})
          </Text>
          <View style={styles.memoryBadge}>
            <Text style={styles.memoryBadgeText}>Memory</Text>
          </View>
        </View>
        <Text style={styles.sectionSubtitle}>
          Facts CaseMate has learned about your situation from conversations.
        </Text>
        {!profile?.legal_facts.length ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyIcon}>🧠</Text>
            <Text style={styles.emptyStateText}>
              No legal facts yet. Chat with CaseMate and it will automatically
              remember important details about your situation.
            </Text>
          </View>
        ) : (
          <View style={styles.factsList}>
            {factsToShow.map((fact, index) => (
              <View key={index} style={styles.factItem}>
                <View style={styles.factBullet} />
                <Text style={styles.factText}>{fact}</Text>
              </View>
            ))}
            {(profile?.legal_facts.length || 0) > 5 && (
              <TouchableOpacity
                style={styles.showMoreButton}
                onPress={() => setShowAllFacts(!showAllFacts)}
              >
                <Text style={styles.showMoreText}>
                  {showAllFacts
                    ? "Show less"
                    : `Show all ${profile?.legal_facts.length} facts`}
                </Text>
              </TouchableOpacity>
            )}
          </View>
        )}
      </View>

      {/* Active Issues */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>
          Active Issues ({profile?.active_issues.length || 0})
        </Text>
        {!profile?.active_issues.length ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyIcon}>📁</Text>
            <Text style={styles.emptyStateText}>
              No active issues. Chat with CaseMate to get started.
            </Text>
          </View>
        ) : (
          <View style={styles.issuesList}>
            {(profile?.active_issues || []).map((issue, index) => (
              <IssueCard key={index} issue={issue} />
            ))}
          </View>
        )}
      </View>

      {/* Documents */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>
          Documents ({profile?.documents.length || 0})
        </Text>
        {!profile?.documents.length ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyIcon}>📄</Text>
            <Text style={styles.emptyStateText}>
              No documents uploaded yet. Upload legal documents to extract facts automatically.
            </Text>
          </View>
        ) : (
          <View style={styles.documentsList}>
            {(profile?.documents || []).map((doc, index) => (
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
            <Text style={styles.statValue}>{profile?.conversation_count || 0}</Text>
            <Text style={styles.statLabel}>Conversations</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>{profile?.legal_facts.length || 0}</Text>
            <Text style={styles.statLabel}>Legal Facts</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>{profile?.documents.length || 0}</Text>
            <Text style={styles.statLabel}>Documents</Text>
          </View>
        </View>
        {profile?.member_since && (
          <Text style={styles.memberSince}>
            Member since {new Date(profile.member_since).toLocaleDateString("en-US", {
              month: "long",
              day: "numeric",
              year: "numeric",
            })}
          </Text>
        )}
      </View>

      {/* Logout */}
      <TouchableOpacity
        style={styles.logoutButton}
        onPress={handleLogout}
        activeOpacity={0.85}
      >
        <Text style={styles.logoutButtonText}>Sign Out</Text>
      </TouchableOpacity>

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
  errorBanner: {
    backgroundColor: colors.errorMuted + "20",
    borderWidth: 1,
    borderColor: colors.error,
    borderRadius: 12,
    padding: 14,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 16,
  },
  errorBannerText: {
    flex: 1,
    fontSize: 14,
    color: colors.error,
    marginRight: 12,
  },
  errorRetryText: {
    fontSize: 14,
    fontWeight: "700",
    color: colors.error,
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
    color: colors.primary,
  },
  editSection: {
    backgroundColor: colors.surface,
    borderRadius: 14,
    padding: 20,
    borderWidth: 1,
    borderColor: colors.border,
    marginTop: 8,
    gap: 14,
  },
  section: {
    marginTop: 24,
  },
  sectionHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 4,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: colors.text,
    marginBottom: 12,
  },
  sectionSubtitle: {
    fontSize: 13,
    color: colors.textSecondary,
    lineHeight: 18,
    marginBottom: 12,
    marginTop: -8,
  },
  memoryBadge: {
    backgroundColor: colors.elevated,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
    marginBottom: 12,
  },
  memoryBadgeText: {
    fontSize: 11,
    fontWeight: "700",
    color: colors.primary,
    textTransform: "uppercase",
    letterSpacing: 0.5,
  },
  field: {
    gap: 4,
  },
  fieldLabel: {
    fontSize: 13,
    fontWeight: "600",
    color: colors.textSecondary,
  },
  fieldInput: {
    backgroundColor: colors.inputBg,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontSize: 15,
    color: colors.text,
  },
  saveButton: {
    backgroundColor: colors.primary,
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 4,
  },
  saveButtonDisabled: {
    opacity: 0.6,
  },
  saveButtonText: {
    color: "#ffffff",
    fontSize: 16,
    fontWeight: "700",
  },
  factsList: {
    gap: 8,
  },
  factItem: {
    flexDirection: "row",
    alignItems: "flex-start",
    backgroundColor: colors.surface,
    borderRadius: 10,
    padding: 14,
    borderWidth: 1,
    borderColor: colors.border,
    gap: 10,
  },
  factBullet: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.primary,
    marginTop: 5,
  },
  factText: {
    flex: 1,
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  showMoreButton: {
    alignItems: "center",
    paddingVertical: 10,
  },
  showMoreText: {
    fontSize: 14,
    fontWeight: "600",
    color: colors.primary,
  },
  issuesList: {
    gap: 12,
  },
  emptyState: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 24,
    alignItems: "center",
    borderWidth: 1,
    borderColor: colors.border,
    gap: 8,
  },
  emptyIcon: {
    fontSize: 28,
  },
  emptyStateText: {
    fontSize: 14,
    color: colors.textSecondary,
    textAlign: "center",
    lineHeight: 20,
  },
  documentsList: {
    gap: 8,
  },
  documentItem: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surface,
    borderRadius: 10,
    padding: 14,
    borderWidth: 1,
    borderColor: colors.border,
    gap: 10,
  },
  documentIcon: {
    fontSize: 18,
  },
  documentName: {
    flex: 1,
    fontSize: 14,
    color: colors.textSecondary,
    fontWeight: "500",
  },
  statsRow: {
    flexDirection: "row",
    gap: 10,
  },
  statCard: {
    flex: 1,
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 14,
    alignItems: "center",
    borderWidth: 1,
    borderColor: colors.border,
  },
  statValue: {
    fontSize: 24,
    fontWeight: "800",
    color: colors.primary,
  },
  statLabel: {
    fontSize: 11,
    color: colors.textMuted,
    fontWeight: "500",
    marginTop: 4,
  },
  memberSince: {
    fontSize: 13,
    color: colors.textSecondary,
    textAlign: "center",
    marginTop: 12,
  },
  logoutButton: {
    marginTop: 32,
    backgroundColor: colors.error + "15",
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: "center",
  },
  logoutButtonText: {
    color: colors.error,
    fontSize: 16,
    fontWeight: "700",
  },
});
