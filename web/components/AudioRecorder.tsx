"use client";

import React, { useState, useRef, useCallback } from "react";
import { api } from "@/lib/api";

/**
 * Props for the AudioRecorder component.
 *
 * @property onTranscript - Callback invoked with the transcribed text when recording completes
 * @property onClose - Callback invoked when the user dismisses the recorder
 */
interface AudioRecorderProps {
  onTranscript: (text: string) => void;
  onClose: () => void;
}

/**
 * Browser-based audio recorder that captures microphone input and sends it
 * to the CaseMate transcription endpoint.
 *
 * Uses the MediaRecorder API to capture audio from the user's microphone.
 * Displays a pulsing red dot while recording. On stop, sends the audio
 * blob to POST /api/audio/transcribe and returns the transcript via callback.
 *
 * @param props - Component props
 * @param props.onTranscript - Called with transcript text on successful transcription
 * @param props.onClose - Called when the recorder is dismissed
 */
export default function AudioRecorder({ onTranscript, onClose }: AudioRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const startRecording = useCallback(async () => {
    setError(null);
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
        // Stop all tracks to release the microphone
        stream.getTracks().forEach((track) => track.stop());

        const audioBlob = new Blob(chunksRef.current, { type: "audio/webm" });

        if (audioBlob.size === 0) {
          setError("No audio recorded.");
          return;
        }

        setIsTranscribing(true);
        try {
          const data = await api.transcribeAudio(audioBlob);
          onTranscript(data.transcript);
        } catch (err) {
          setError(err instanceof Error ? err.message : "Transcription failed.");
        } finally {
          setIsTranscribing(false);
        }
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
  }, [onTranscript]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  }, []);

  return (
    <div className="flex items-center gap-3 px-4 py-2 bg-white/[0.03] border border-white/10 rounded-xl">
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

      {/* Controls */}
      {!isRecording && !isTranscribing && (
        <button
          onClick={startRecording}
          className="px-3 py-1.5 text-sm bg-red-500/20 text-red-400 border border-red-500/30 rounded-lg hover:bg-red-500/30 transition-colors"
        >
          Start Recording
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
  );
}
