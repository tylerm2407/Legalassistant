"use client";

import React, { useState, useRef, useCallback } from "react";
import { api } from "@/lib/api";

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
      setError("No audio data to transcribe.");
      return;
    }

    setIsTranscribing(true);
    setError(null);
    try {
      const data = await api.transcribeAudio(audioBlob);
      const text = data.transcript.trim();
      if (!text) {
        setError("No speech detected in the audio. Try again.");
        return;
      }
      setTranscript(text);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Transcription failed.");
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
          : "Could not access microphone. Please check permissions."
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
      setError("Audio file too large. Maximum size is 25MB.");
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
      <div className="bg-white/[0.03] border border-white/10 rounded-xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-2 border-b border-white/10">
          <div className="flex items-center gap-2">
            <svg className="w-4 h-4 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-sm font-medium text-green-400">Transcript Ready</span>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-gray-500 hover:text-white transition-colors"
            title="Close"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Transcript text */}
        <div className="px-4 py-3 max-h-32 overflow-y-auto">
          <p className="text-sm text-gray-300 leading-relaxed">{transcript}</p>
        </div>

        {/* Action buttons */}
        <div className="flex items-center gap-2 px-4 py-2 border-t border-white/10 bg-white/[0.02]">
          <button
            onClick={handleSendForAdvice}
            className="flex-1 px-3 py-2 text-sm font-medium bg-blue-600 text-white rounded-lg hover:bg-blue-500 transition-colors flex items-center justify-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 18.75a6 6 0 006-6v-1.5m-6 7.5a6 6 0 01-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 01-3-3V4.5a3 3 0 116 0v8.25a3 3 0 01-3 3z" />
            </svg>
            Get Legal Advice
          </button>
          <button
            onClick={handleEditTranscript}
            className="px-3 py-2 text-sm text-gray-400 border border-white/10 rounded-lg hover:bg-white/[0.05] hover:text-white transition-colors"
          >
            Edit First
          </button>
        </div>
      </div>
    );
  }

  // -- Recording / Upload view --
  return (
    <div className="bg-white/[0.03] border border-white/10 rounded-xl">
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept={ACCEPTED_AUDIO_TYPES}
        onChange={handleFileUpload}
        className="hidden"
      />

      <div className="flex items-center gap-3 px-4 py-2">
        {/* Recording indicator */}
        {isRecording && (
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
            <span className="text-sm text-red-400">Recording...</span>
          </div>
        )}

        {isTranscribing && (
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse" />
            <span className="text-sm text-blue-400">Transcribing...</span>
          </div>
        )}

        {error && (
          <span className="text-sm text-red-400">{error}</span>
        )}

        {/* Controls — shown when not recording and not transcribing */}
        {!isRecording && !isTranscribing && !error && (
          <>
            <button
              onClick={startRecording}
              className="px-3 py-1.5 text-sm bg-red-500/20 text-red-400 border border-red-500/30 rounded-lg hover:bg-red-500/30 transition-colors flex items-center gap-1.5"
            >
              <div className="w-2 h-2 bg-red-500 rounded-full" />
              Record
            </button>
            <span className="text-xs text-gray-600">or</span>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="px-3 py-1.5 text-sm bg-white/[0.05] text-gray-400 border border-white/10 rounded-lg hover:bg-white/[0.08] hover:text-white transition-colors flex items-center gap-1.5"
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
              </svg>
              Upload Audio
            </button>
          </>
        )}

        {/* Error retry */}
        {error && !isRecording && !isTranscribing && (
          <button
            onClick={() => { setError(null); }}
            className="px-3 py-1.5 text-sm text-gray-400 border border-white/10 rounded-lg hover:bg-white/[0.05] transition-colors"
          >
            Try Again
          </button>
        )}

        {isRecording && (
          <button
            onClick={stopRecording}
            className="px-3 py-1.5 text-sm bg-white/10 text-white border border-white/20 rounded-lg hover:bg-white/20 transition-colors"
          >
            Stop
          </button>
        )}

        <button
          onClick={onClose}
          disabled={isTranscribing}
          className="ml-auto p-1 text-gray-500 hover:text-white transition-colors disabled:opacity-50"
          title="Close recorder"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  );
}
