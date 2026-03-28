"use client";

import React, { useState, useRef, useCallback } from "react";
import Button from "./ui/Button";
import Card from "./ui/Card";
import { api } from "@/lib/api";

const ACCEPTED_TYPES = [
  "application/pdf",
  "image/png",
  "image/jpeg",
  "image/gif",
  "text/plain",
];

const ACCEPTED_EXTENSIONS = ".pdf,.png,.jpg,.jpeg,.gif,.txt";

interface UploadResult {
  filename: string;
  key_facts: string[];
  red_flags: string[];
  summary: string;
}

interface DocumentUploadProps {
  userId: string;
  onUploadComplete?: () => void;
}

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
      setError("Unsupported file type. Please upload PDF, images, or text files.");
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setError("File too large. Maximum size is 10MB.");
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
        err instanceof Error ? err.message : "Upload failed. Please try again."
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
        className={`border-2 border-dashed rounded-xl p-8 text-center transition-all ${
          isDragging
            ? "border-blue-500 bg-blue-500/5 shadow-glow-md"
            : "border-white/15 hover:border-white/25 hover:bg-white/[0.02]"
        }`}
      >
        <svg
          className="w-10 h-10 text-gray-500 mx-auto mb-3"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={1.5}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.338-2.32 3.75 3.75 0 013.577 5.487A3.75 3.75 0 0117.25 19.5H6.75z"
          />
        </svg>
        <p className="text-sm text-gray-400 mb-1">
          Drag and drop a document here, or
        </p>
        <input
          ref={fileInputRef}
          type="file"
          accept={ACCEPTED_EXTENSIONS}
          onChange={handleFileSelect}
          className="hidden"
        />
        <Button
          variant="outline"
          size="sm"
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
        >
          Browse Files
        </Button>
        <p className="text-xs text-gray-500 mt-2">
          PDF, images, or text files up to 10MB
        </p>
      </div>

      {/* Progress */}
      {uploading && (
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-gray-400">Uploading...</span>
            <span className="text-xs text-gray-500">{progress}%</span>
          </div>
          <div className="w-full bg-white/10 rounded-full h-1.5">
            <div
              className="bg-gradient-to-r from-blue-600 to-violet-500 h-1.5 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <p className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg p-3">
          {error}
        </p>
      )}

      {/* Result */}
      {result && (
        <Card>
          <Card.Header>
            <h3 className="text-sm font-semibold text-white">
              Document Analysis: {result.filename}
            </h3>
          </Card.Header>
          <Card.Body>
            <div className="space-y-4">
              {/* Summary */}
              <div>
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">
                  Summary
                </p>
                <p className="text-sm text-gray-300">{result.summary}</p>
              </div>

              {/* Key Facts */}
              {result.key_facts.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">
                    Key Facts
                  </p>
                  <ul className="space-y-1">
                    {result.key_facts.map((fact, i) => (
                      <li
                        key={i}
                        className="text-sm text-gray-300 flex gap-2"
                      >
                        <span className="text-blue-400 shrink-0">&#8226;</span>
                        {fact}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Red Flags */}
              {result.red_flags.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-red-400 uppercase tracking-wider mb-1">
                    Red Flags
                  </p>
                  <ul className="space-y-1">
                    {result.red_flags.map((flag, i) => (
                      <li
                        key={i}
                        className="text-sm text-red-400 flex gap-2"
                      >
                        <span className="shrink-0">&#9888;</span>
                        {flag}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
            <p className="trust-disclaimer">
              Documents are analyzed locally and not shared with third parties.
            </p>
          </Card.Body>
        </Card>
      )}
    </div>
  );
}
