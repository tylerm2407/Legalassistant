"use client";

import React, { useState, useRef, useCallback } from "react";
import Button from "./ui/Button";
import { api } from "@/lib/api";
import { useTranslation } from "@/lib/i18n";
import { Upload, File, Warning, CheckCircle } from "@phosphor-icons/react";

/** MIME types accepted for document upload and legal analysis. */
const ACCEPTED_TYPES = [
  "application/pdf",
  "image/png",
  "image/jpeg",
  "image/gif",
  "text/plain",
];

/** File extensions string for the HTML file input accept attribute. */
const ACCEPTED_EXTENSIONS = ".pdf,.png,.jpg,.jpeg,.gif,.txt";

/**
 * Result returned from the document analysis API after upload.
 *
 * @property filename - Original filename of the uploaded document
 * @property key_facts - Legal facts extracted from the document by Claude
 * @property red_flags - Potential legal issues or concerns identified in the document
 * @property summary - Brief AI-generated summary of the document's contents
 */
interface UploadResult {
  filename: string;
  key_facts: string[];
  red_flags: string[];
  summary: string;
}

/**
 * Props for the DocumentUpload component.
 *
 * @property userId - The authenticated user's Supabase ID for associating uploaded documents
 * @property onUploadComplete - Optional callback fired after a successful upload and analysis
 */
interface DocumentUploadProps {
  userId: string;
  onUploadComplete?: () => void;
}

/**
 * Drag-and-drop document upload with legal analysis.
 *
 * Accepts PDFs, images, and text files up to 10MB. After upload, the backend
 * extracts text (via pdfplumber for PDFs, OCR for images), sends it to Claude
 * for legal analysis, and returns key facts, red flags, and a summary. Extracted
 * facts are automatically added to the user's legal profile in Supabase.
 *
 * @param props - Component props
 * @param props.userId - The authenticated user's Supabase ID
 * @param props.onUploadComplete - Optional callback invoked after successful upload
 */
export default function DocumentUpload({
  userId,
  onUploadComplete,
}: DocumentUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<UploadResult | null>(null);
  const [error, setError] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { t } = useTranslation();

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  async function uploadFile(file: File) {
    if (!ACCEPTED_TYPES.includes(file.type)) {
      setError("That file type isn't supported. Try a PDF, image, or text file.");
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setError("That file is too big. Please keep it under 10 MB.");
      return;
    }

    setUploading(true);
    setError("");
    setResult(null);
    setProgress(0);

    // Simulate progress since fetch doesn't support progress natively
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return 90;
        }
        return prev + 10;
      });
    }, 200);

    try {
      const data = await api.uploadDocument(userId, file);
      clearInterval(progressInterval);
      setProgress(100);
      setResult(data);
      onUploadComplete?.();
    } catch (err) {
      clearInterval(progressInterval);
      setError(
        err instanceof Error ? err.message : "We couldn't upload that. Let's try again."
      );
    } finally {
      setUploading(false);
    }
  }

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) uploadFile(file);
    },
    [userId]
  );

  function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) uploadFile(file);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  return (
    <div className="space-y-4">
      {/* Drop zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-lg p-10 text-center transition-colors ${
          isDragging
            ? "border-accent bg-accent-subtle"
            : "border-border hover:border-border-strong bg-white"
        }`}
      >
        <Upload className="w-10 h-10 text-ink-secondary mx-auto mb-4" weight="regular" />
        <p className="text-base font-sans text-ink-primary mb-1">
          {t("dragAndDrop")}
        </p>
        <p className="text-sm font-sans text-ink-tertiary mb-4">
          {t("fileTypeHint")}
        </p>
        <input
          ref={fileInputRef}
          type="file"
          accept={ACCEPTED_EXTENSIONS}
          onChange={handleFileSelect}
          className="hidden"
        />
        <Button
          variant="secondary"
          size="sm"
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
        >
          {t("browseFiles")}
        </Button>
      </div>

      {/* Progress */}
      {uploading && (
        <div className="bg-white border border-border rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-sans text-ink-primary">{t("uploading")}</span>
            <span className="text-sm font-sans text-ink-secondary">{progress}%</span>
          </div>
          <div className="w-full bg-bg rounded-md h-1.5 overflow-hidden">
            <div
              className="bg-accent h-1.5 rounded-md transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="flex items-start gap-2 bg-warning-subtle border border-warning/30 rounded-md p-3">
          <Warning className="w-4 h-4 text-warning shrink-0 mt-0.5" weight="regular" />
          <p className="text-sm font-sans text-warning">{error}</p>
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="bg-white border border-border rounded-lg p-6">
          <div className="flex items-center gap-3 mb-5">
            <File className="w-5 h-5 text-ink-secondary" weight="regular" />
            <h3 className="font-serif font-medium tracking-tight text-ink-primary text-lg leading-tight">
              {t("documentAnalysis")}: {result.filename}
            </h3>
          </div>

          <div className="space-y-5">
            {/* Summary */}
            <div>
              <p className="text-xs font-sans font-medium text-ink-tertiary uppercase tracking-wider mb-2">
                {t("summary")}
              </p>
              <p className="text-sm font-sans text-ink-primary leading-relaxed">
                {result.summary}
              </p>
            </div>

            {/* Key Facts */}
            {result.key_facts.length > 0 && (
              <div>
                <p className="text-xs font-sans font-medium text-ink-tertiary uppercase tracking-wider mb-2">
                  {t("keyFacts")}
                </p>
                <ul className="space-y-2">
                  {result.key_facts.map((fact: string, i: number) => (
                    <li
                      key={i}
                      className="text-sm font-sans text-ink-primary flex gap-2"
                    >
                      <CheckCircle className="w-4 h-4 text-accent shrink-0 mt-0.5" weight="regular" />
                      <span>{fact}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Red Flags */}
            {result.red_flags.length > 0 && (
              <div>
                <p className="text-xs font-sans font-medium text-warning uppercase tracking-wider mb-2">
                  {t("redFlags")}
                </p>
                <ul className="space-y-2">
                  {result.red_flags.map((flag: string, i: number) => (
                    <li
                      key={i}
                      className="text-sm font-sans text-warning flex gap-2"
                    >
                      <Warning className="w-4 h-4 shrink-0 mt-0.5" weight="regular" />
                      <span>{flag}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <p className="mt-5 pt-4 border-t border-border text-xs font-sans text-ink-tertiary leading-relaxed">
            {t("docDisclaimer")}
          </p>
        </div>
      )}
    </div>
  );
}
