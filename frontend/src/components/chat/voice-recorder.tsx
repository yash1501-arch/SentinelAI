"use client";

import { useState, useRef, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Mic, Square, Loader2 } from "lucide-react";
import { toast } from "sonner";
import * as voiceService from "@/services/voice";

type Props = {
  onTranscript: (text: string) => void;
  language?: string;
};

export function VoiceRecorder({ onTranscript, language = "en" }: Props) {
  const [recording, setRecording] = useState(false);
  const [processing, setProcessing] = useState(false);
  const mediaRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const recorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
          ? "audio/webm;codecs=opus"
          : "audio/webm",
      });
      chunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      recorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        if (blob.size < 1000) {
          toast.error("Recording too short");
          return;
        }
        setProcessing(true);
        try {
          const data = await voiceService.transcribeAudio(blob, language);
          onTranscript(data.transcript);
        } catch {
          toast.error("Transcription failed");
        } finally {
          setProcessing(false);
        }
      };

      recorder.start();
      mediaRef.current = recorder;
      setRecording(true);
    } catch {
      toast.error("Microphone access denied");
    }
  }, [language, onTranscript]);

  const stopRecording = useCallback(() => {
    if (mediaRef.current && mediaRef.current.state !== "inactive") {
      mediaRef.current.stop();
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
    }
    setRecording(false);
  }, []);

  if (processing) {
    return (
      <Button size="icon" variant="ghost" disabled>
        <Loader2 className="h-4 w-4 animate-spin" />
      </Button>
    );
  }

  return (
    <Button
      size="icon"
      variant={recording ? "destructive" : "ghost"}
      onClick={recording ? stopRecording : startRecording}
    >
      {recording ? (
        <Square className="h-4 w-4" />
      ) : (
        <Mic className="h-4 w-4" />
      )}
    </Button>
  );
}
