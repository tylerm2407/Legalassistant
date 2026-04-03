import React, { useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
} from "react-native";
import * as ExpoDocumentPicker from "expo-document-picker";
import * as ImagePicker from "expo-image-picker";
import { uploadDocument } from "@/lib/api";
import { colors } from "@/lib/theme";

interface DocumentPickerProps {
  userId: string;
  onUploadComplete?: (result: {
    document_id: string;
    extracted_facts: string[];
  }) => void;
}

export default function DocumentPickerComponent({
  userId,
  onUploadComplete,
}: DocumentPickerProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [showOptions, setShowOptions] = useState(false);
  const [extractedFacts, setExtractedFacts] = useState<string[]>([]);

  const handleDocumentPick = async () => {
    setShowOptions(false);
    try {
      const result = await ExpoDocumentPicker.getDocumentAsync({
        type: [
          "application/pdf",
          "image/*",
          "text/plain",
          "application/msword",
          "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ],
        copyToCacheDirectory: true,
      });

      if (result.canceled || !result.assets?.[0]) return;

      const file = result.assets[0];
      await handleUpload(
        file.uri,
        file.name,
        file.mimeType || "application/octet-stream"
      );
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to pick document";
      Alert.alert("Error", message);
    }
  };

  const handleCameraPick = async () => {
    setShowOptions(false);
    try {
      const permissionResult = await ImagePicker.requestCameraPermissionsAsync();
      if (!permissionResult.granted) {
        Alert.alert(
          "Permission needed",
          "Camera access is required to take photos of documents."
        );
        return;
      }

      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        quality: 0.8,
      });

      if (result.canceled || !result.assets?.[0]) return;

      const asset = result.assets[0];
      const fileName = `photo_${Date.now()}.jpg`;
      await handleUpload(asset.uri, fileName, "image/jpeg");
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to take photo";
      Alert.alert("Error", message);
    }
  };

  const handleUpload = async (
    uri: string,
    fileName: string,
    mimeType: string
  ) => {
    setIsUploading(true);
    setUploadProgress(0);
    setExtractedFacts([]);

    const progressInterval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return 90;
        }
        return prev + 10;
      });
    }, 300);

    try {
      const result = await uploadDocument(userId, uri, fileName, mimeType);
      clearInterval(progressInterval);
      setUploadProgress(100);
      setExtractedFacts(result.extracted_facts);
      onUploadComplete?.(result);
    } catch (err: unknown) {
      clearInterval(progressInterval);
      const message = err instanceof Error ? err.message : "Upload failed";
      Alert.alert("Upload Failed", message);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity
        style={[styles.uploadButton, isUploading && styles.uploadButtonDisabled]}
        onPress={() => setShowOptions(!showOptions)}
        disabled={isUploading}
        activeOpacity={0.7}
      >
        <Text style={styles.uploadIcon}>📎</Text>
        <Text style={styles.uploadButtonText}>
          {isUploading ? "Uploading..." : "Upload Document"}
        </Text>
      </TouchableOpacity>

      {showOptions && !isUploading && (
        <View style={styles.optionsContainer}>
          <TouchableOpacity
            style={styles.optionButton}
            onPress={handleDocumentPick}
            activeOpacity={0.7}
          >
            <Text style={styles.optionIcon}>📄</Text>
            <Text style={styles.optionText}>Choose File</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.optionButton}
            onPress={handleCameraPick}
            activeOpacity={0.7}
          >
            <Text style={styles.optionIcon}>📷</Text>
            <Text style={styles.optionText}>Take Photo</Text>
          </TouchableOpacity>
        </View>
      )}

      {isUploading && (
        <View style={styles.progressContainer}>
          <View style={styles.progressTrack}>
            <View
              style={[styles.progressFill, { width: `${uploadProgress}%` }]}
            />
          </View>
          <View style={styles.progressInfo}>
            <ActivityIndicator size="small" color={colors.primary} />
            <Text style={styles.progressText}>{uploadProgress}%</Text>
          </View>
        </View>
      )}

      {extractedFacts.length > 0 && (
        <View style={styles.factsContainer}>
          <Text style={styles.factsTitle}>
            Extracted Facts ({extractedFacts.length})
          </Text>
          {extractedFacts.map((fact, index) => (
            <View key={index} style={styles.factItem}>
              <View style={styles.factBullet} />
              <Text style={styles.factText}>{fact}</Text>
            </View>
          ))}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    gap: 12,
  },
  uploadButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.elevated,
    borderWidth: 2,
    borderColor: colors.primary,
    borderStyle: "dashed",
    borderRadius: 14,
    paddingVertical: 20,
    gap: 10,
  },
  uploadButtonDisabled: {
    opacity: 0.6,
  },
  uploadIcon: {
    fontSize: 22,
  },
  uploadButtonText: {
    fontSize: 16,
    fontWeight: "700",
    color: colors.primary,
  },
  optionsContainer: {
    flexDirection: "row",
    gap: 12,
  },
  optionButton: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 12,
    paddingVertical: 14,
    gap: 8,
  },
  optionIcon: {
    fontSize: 18,
  },
  optionText: {
    fontSize: 15,
    fontWeight: "600",
    color: colors.text,
  },
  progressContainer: {
    gap: 8,
  },
  progressTrack: {
    height: 6,
    backgroundColor: colors.border,
    borderRadius: 3,
    overflow: "hidden",
  },
  progressFill: {
    height: "100%",
    backgroundColor: colors.primary,
    borderRadius: 3,
  },
  progressInfo: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
  },
  progressText: {
    fontSize: 13,
    color: colors.textSecondary,
    fontWeight: "600",
  },
  factsContainer: {
    backgroundColor: colors.success + "15",
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: colors.success,
  },
  factsTitle: {
    fontSize: 15,
    fontWeight: "700",
    color: colors.success,
    marginBottom: 10,
  },
  factItem: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 8,
    marginBottom: 6,
  },
  factBullet: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: colors.success,
    marginTop: 6,
  },
  factText: {
    flex: 1,
    fontSize: 14,
    color: colors.success,
    lineHeight: 20,
  },
});
