"use client";

import React, { useState, useRef, useCallback } from "react";
import { api } from "@/lib/api";
import {
  Microphone,
  Stop,
  CheckCircle,
  X,
  UploadSimple,
  PaperPlaneTilt,
} from "@phosphor-icons/react";

/**
 * Accepted audio MIME types for file uploads.
 * Mirrors the backend's _ALLOWED_AUDIO_TYPES set.
 */
const ACCEPTED_AUDIO_TYPES = ".mp3,.mp4,.m4a,.wav,.webm,.ogg,.mpeg";

/**
 * Props for the AudioRecorder component.
 *
 * @property onTranscript - Callback invoked with the transcribed text (populates input for editing)
 * @property onTranscriptSend - Callback invoked when user wants to send transcript directly for legal advice
 * @property onClose - Callback invoked when the user dismisses the recorder
 */
interface AudioRecorderProps {
  onTranscript: (text: string) => void;
  onTranscriptSend: (text: string) => void;
  onClose: () => void;
}

/**
 * Audio input component that supports both browser microphone recording and
 * audio file uploads. After transcription, displays a preview with options
 * to send directly for legal advice or edit the transcript first.
 *
 * Recording uses the MediaRecorder API (WebM/Opus). File uploads accept
 * mp3, mp4, m4a, wav, webm, and ogg formats (max 25MB, Whisper API limit).
 *
 * @param props - Component props
 * @param props.onTranscript - Called to populate the chat input for editing
 * @param props.onTranscriptSend - Called to auto-send transcript for legal advice
 * @param props.onClose - Called when the recorder is dismissed
 */
export default function AudioRecorder({ onTranscript, onTranscriptSend, onClose }: AudioRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [transcript, setTranscript] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  /**
   * Sends an audio blob to the transcription endpoint and stores the result.
   */
  const transcribeBlob = useCallback(async (audioBlob: Blob) => {
    if (audioBlob.size === 0) {
      setError("We didn't catch any audio. Give it another try.");
      return;
    }

    setIsTranscribing(true);
    setError(null);
    try {
      const data = await api.transcribeAudio(audioBlob);
      const text = data.transcript.trim();
      if (!text) {
        setError("We couldn't hear anything in that clip. Try again.");
        return;
      }
      setTranscript(text);
    } catch (err) {
      setError(err instanceof Error ? err.message : "We couldn't transcribe that. Try again.");
    } finally {
      setIsTranscribing(false);
    }
  }, []);

  const startRecording = useCallback(async () => {
    setError(null);
    setTranscript(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
          ? "audio/webm;codecs=opus"
          : "audio/webm",
      });

      chunksRef.current = [];

      mediaRecorder.ondataavailable = (event: BlobEvent) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach((track) => track.stop());
        const audioBlob = new Blob(chunksRef.current, { type: "audio/webm" });
        await transcribeBlob(audioBlob);
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "We couldn't reach your microphone. Check your browser permissions."
      );
    }
  }, [transcribeBlob]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  }, []);

  /**
   * Handles audio file selection from the file input.
   * Validates size (25MB max) then sends to transcription.
   */
  const handleFileUpload = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Reset file input so re-selecting the same file triggers onChange
    e.target.value = "";

    const maxBytes = 25 * 1024 * 1024;
    if (file.size > maxBytes) {
      setError("That file is a bit too big. The limit is 25MB.");
      return;
    }

    setTranscript(null);
    await transcribeBlob(file);
  }, [transcribeBlob]);

  /**
   * Sends the transcript directly to chat for instant legal advice.
   */
  const handleSendForAdvice = useCallback(() => {
    if (transcript) {
      onTranscriptSend(transcript);
      setTranscript(null);
    }
  }, [transcript, onTranscriptSend]);

  /**
   * Populates the chat input with the transcript for editing before sending.
   */
  const handleEditTranscript = useCallback(() => {
    if (transcript) {
      onTranscript(transcript);
      setTranscript(null);
    }
  }, [transcript, onTranscript]);

  // -- Transcript preview view --
  if (transcript) {
    return (
      <div className="bg-white border border-border rounded-lg overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-border">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-accent" weight="regular" />
            <span className="text-sm font-sans font-medium text-ink-primary">Transcript ready</span>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-ink-tertiary hover:text-ink-primary transition-colors"
            title="Close"
          >
            <X className="w-4 h-4" weight="regular" />
          </button>
        </div>

        {/* Transcript text */}
        <div className="px-4 py-3 max-h-32 overflow-y-auto">
          <p className="text-sm font-sans text-ink-secondary leading-relaxed">{transcript}</p>
        </div>

        {/* Action buttons */}
        <div className="flex items-center gap-2 px-4 py-3 border-t border-border bg-bg">
          <button
            onClick={handleSendForAdvice}
            className="flex-1 bg-accent text-white px-4 py-2 rounded-md font-sans font-medium text-sm hover:bg-accent-hover transition-colors flex items-center justify-center gap-2"
          >
            <PaperPlaneTilt className="w-4 h-4" weight="regular" />
            Send for advice
          </button>
          <button
            onClick={handleEditTranscript}
            className="bg-transparent text-ink-primary border border-border-strong rounded-md px-4 py-2 font-sans text-sm hover:bg-bg-hover transition-colors"
          >
            Edit first
          </button>
        </div>
      </div>
    );
  }

  // -- Recording / Upload view --
  return (
    <div className="bg-white border border-border rounded-lg">
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept={ACCEPTED_AUDIO_TYPES}
        onChange={handleFileUpload}
        className="hidden"
      />

      <div className="flex items-center gap-3 px-4 py-3">
        {/* Recording indicator */}
        {isRecording && (
          <div className="flex items-center gap-2 bg-accent-subtle border border-accent/30 rounded-md px-3 py-1.5">
            <div className="w-2 h-2 bg-accent rounded-full animate-pulse" />
            <span className="text-sm font-sans text-accent">Recording</span>
          </div>
        )}

        {isTranscribing && (
          <div className="flex items-center gap-2 bg-accent-subtle border border-accent/30 rounded-md px-3 py-1.5">
            <div className="w-2 h-2 bg-accent rounded-full animate-pulse" />
            <span className="text-sm font-sans text-accent">Transcribing</span>
          </div>
        )}

        {error && !isRecording && !isTranscribing && (
          <span className="text-sm font-sans text-warning bg-warning-subtle border border-warning/30 rounded-md px-3 py-1.5">
            {error}
          </span>
        )}

        {/* Controls — shown when not recording and not transcribing */}
        {!isRecording && !isTranscribing && !error && (
          <>
            <button
              onClick={startRecording}
              className="bg-accent-subtle text-accent border border-accent/30 rounded-md px-4 py-2 text-sm font-sans font-medium hover:bg-accent/10 transition-colors flex items-center gap-2"
            >
              <Microphone className="w-4 h-4" weight="regular" />
              Record
            </button>
            <span className="text-xs font-sans text-ink-tertiary">or</span>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="bg-transparent text-ink-primary border border-border-strong rounded-md px-4 py-2 text-sm font-sans hover:bg-bg-hover transition-colors flex items-center gap-2"
            >
              <UploadSimple className="w-4 h-4 text-ink-secondary" weight="regular" />
              Upload audio
            </button>
          </>
        )}

        {/* Error retry */}
        {error && !isRecording && !isTranscribing && (
          <button
            onClick={() => { setError(null); }}
            className="bg-transparent text-ink-primary border border-border-strong rounded-md px-4 py-2 text-sm font-sans hover:bg-bg-hover transition-colors"
          >
            Try again
          </button>
        )}

        {isRecording && (
          <button
            onClick={stopRecording}
            className="bg-warning-subtle text-warning border border-warning/30 rounded-md px-4 py-2 text-sm font-sans font-medium hover:bg-warning/10 transition-colors flex items-center gap-2"
          >
            <Stop className="w-4 h-4" weight="regular" />
            Stop
          </button>
        )}

        <button
          onClick={onClose}
          disabled={isTranscribing}
          className="ml-auto p-1 text-ink-tertiary hover:text-ink-primary transition-colors disabled:opacity-50"
          title="Close recorder"
        >
          <X className="w-4 h-4" weight="regular" />
        </button>
      </div>
    </div>
  );
}
