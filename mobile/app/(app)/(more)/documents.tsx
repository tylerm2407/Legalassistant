import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Modal,
  ScrollView,
} from "react-native";
import DocumentPickerComponent from "@/components/DocumentPicker";
import { getProfile } from "@/lib/api";
import { supabase } from "@/lib/supabase";
import { colors } from "@/lib/theme";

interface DocumentEntry {
  id: string;
  filename: string;
  uploadedAt: string;
  extractedFacts: string[];
}

export default function DocumentsScreen() {
  const [documents, setDocuments] = useState<DocumentEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedDoc, setSelectedDoc] = useState<DocumentEntry | null>(null);
  const [userId, setUserId] = useState("");

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.user?.id) setUserId(session.user.id);
    });
  }, []);

  useEffect(() => {
    if (userId) loadDocuments();
  }, [userId]);

  const loadDocuments = async () => {
    if (!userId) return;
    setIsLoading(true);
    try {
      const profile = await getProfile(userId);
      const docs: DocumentEntry[] = profile.documents.map((doc, index) => ({
        id: `doc_${index}`,
        filename: doc,
        uploadedAt: new Date().toISOString(),
        extractedFacts: [],
      }));
      setDocuments(docs);
    } catch {
      // Keep existing documents on error
    } finally {
      setIsLoading(false);
    }
  };

  const handleUploadComplete = (result: {
    document_id: string;
    extracted_facts: string[];
  }) => {
    const newDoc: DocumentEntry = {
      id: result.document_id,
      filename: `Document ${documents.length + 1}`,
      uploadedAt: new Date().toISOString(),
      extractedFacts: result.extracted_facts,
    };
    setDocuments((prev) => [newDoc, ...prev]);
  };

  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  const renderDocument = ({ item }: { item: DocumentEntry }) => (
    <TouchableOpacity
      style={styles.documentCard}
      onPress={() => setSelectedDoc(item)}
      activeOpacity={0.7}
    >
      <View style={styles.docIconContainer}>
        <Text style={styles.docIcon}>📄</Text>
      </View>
      <View style={styles.docInfo}>
        <Text style={styles.docFilename} numberOfLines={1}>
          {item.filename}
        </Text>
        <Text style={styles.docDate}>Uploaded {formatDate(item.uploadedAt)}</Text>
      </View>
      <View style={styles.docFactsBadge}>
        <Text style={styles.docFactsCount}>{item.extractedFacts.length}</Text>
        <Text style={styles.docFactsLabel}>facts</Text>
      </View>
    </TouchableOpacity>
  );

  const renderEmpty = () => {
    if (isLoading) return null;

    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyIcon}>📄</Text>
        <Text style={styles.emptyTitle}>No documents yet</Text>
        <Text style={styles.emptyText}>
          Upload legal documents like leases, contracts, or court papers. CaseMate
          will extract key facts to help with your case.
        </Text>
      </View>
    );
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Loading documents...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.pickerSection}>
        <DocumentPickerComponent
          userId={userId}
          onUploadComplete={handleUploadComplete}
        />
      </View>

      <FlatList
        data={documents}
        renderItem={renderDocument}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContent}
        ListEmptyComponent={renderEmpty}
        ListHeaderComponent={
          documents.length > 0 ? (
            <Text style={styles.listHeader}>
              {documents.length} document{documents.length !== 1 ? "s" : ""}
            </Text>
          ) : null
        }
        showsVerticalScrollIndicator={false}
      />

      <Modal
        visible={selectedDoc !== null}
        animationType="slide"
        transparent
        onRequestClose={() => setSelectedDoc(null)}
      >
        <TouchableOpacity
          style={styles.modalOverlay}
          activeOpacity={1}
          onPress={() => setSelectedDoc(null)}
        >
          <TouchableOpacity
            style={styles.modalSheet}
            activeOpacity={1}
            onPress={() => {}}
          >
            <View style={styles.modalHandle}>
              <View style={styles.handleBar} />
            </View>

            {selectedDoc && (
              <ScrollView showsVerticalScrollIndicator={false}>
                <Text style={styles.modalTitle}>{selectedDoc.filename}</Text>
                <Text style={styles.modalDate}>
                  Uploaded {formatDate(selectedDoc.uploadedAt)}
                </Text>

                <View style={styles.modalDivider} />

                <Text style={styles.modalSectionTitle}>
                  Extracted Facts ({selectedDoc.extractedFacts.length})
                </Text>

                {selectedDoc.extractedFacts.length === 0 ? (
                  <Text style={styles.noFactsText}>
                    No facts were extracted from this document. This may be
                    because the document is still being processed or the content
                    couldn't be parsed.
                  </Text>
                ) : (
                  <View style={styles.factsList}>
                    {selectedDoc.extractedFacts.map((fact, index) => (
                      <View key={index} style={styles.factRow}>
                        <View style={styles.factBullet} />
                        <Text style={styles.factText}>{fact}</Text>
                      </View>
                    ))}
                  </View>
                )}
              </ScrollView>
            )}

            <TouchableOpacity
              style={styles.closeButton}
              onPress={() => setSelectedDoc(null)}
              activeOpacity={0.7}
            >
              <Text style={styles.closeButtonText}>Close</Text>
            </TouchableOpacity>
          </TouchableOpacity>
        </TouchableOpacity>
      </Modal>
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
  pickerSection: {
    padding: 20,
    paddingBottom: 8,
  },
  listContent: {
    paddingHorizontal: 20,
    paddingBottom: 32,
    flexGrow: 1,
  },
  listHeader: {
    fontSize: 13,
    color: colors.textSecondary,
    fontWeight: "500",
    marginBottom: 12,
    marginTop: 8,
  },
  documentCard: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surface,
    borderRadius: 14,
    padding: 16,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: 10,
    gap: 14,
  },
  docIconContainer: {
    width: 44,
    height: 44,
    borderRadius: 10,
    backgroundColor: colors.elevated,
    justifyContent: "center",
    alignItems: "center",
  },
  docIcon: {
    fontSize: 22,
  },
  docInfo: {
    flex: 1,
    gap: 2,
  },
  docFilename: {
    fontSize: 15,
    fontWeight: "600",
    color: colors.text,
  },
  docDate: {
    fontSize: 12,
    color: colors.textMuted,
  },
  docFactsBadge: {
    alignItems: "center",
    backgroundColor: colors.elevated,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
  },
  docFactsCount: {
    fontSize: 16,
    fontWeight: "800",
    color: colors.primary,
  },
  docFactsLabel: {
    fontSize: 10,
    color: colors.textMuted,
    fontWeight: "500",
  },
  emptyContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: 40,
    paddingVertical: 40,
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: 16,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: "700",
    color: colors.text,
    marginBottom: 8,
  },
  emptyText: {
    fontSize: 15,
    color: colors.textSecondary,
    textAlign: "center",
    lineHeight: 22,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0, 0, 0, 0.4)",
    justifyContent: "flex-end",
  },
  modalSheet: {
    backgroundColor: colors.surface,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    paddingHorizontal: 24,
    paddingBottom: 40,
    maxHeight: "70%",
  },
  modalHandle: {
    alignItems: "center",
    paddingVertical: 12,
  },
  handleBar: {
    width: 40,
    height: 4,
    borderRadius: 2,
    backgroundColor: colors.border,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: "700",
    color: colors.text,
    marginBottom: 4,
  },
  modalDate: {
    fontSize: 13,
    color: colors.textMuted,
  },
  modalDivider: {
    height: 1,
    backgroundColor: colors.border,
    marginVertical: 16,
  },
  modalSectionTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: colors.text,
    marginBottom: 12,
  },
  noFactsText: {
    fontSize: 14,
    color: colors.textMuted,
    lineHeight: 20,
  },
  factsList: {
    gap: 10,
  },
  factRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 10,
  },
  factBullet: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: colors.primary,
    marginTop: 6,
  },
  factText: {
    flex: 1,
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  closeButton: {
    marginTop: 20,
    alignItems: "center",
    paddingVertical: 14,
    backgroundColor: colors.elevated,
    borderRadius: 12,
  },
  closeButtonText: {
    fontSize: 15,
    fontWeight: "600",
    color: colors.textSecondary,
  },
});
