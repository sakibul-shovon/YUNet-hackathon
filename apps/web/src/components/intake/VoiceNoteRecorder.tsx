'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Mic, Square, Play, Pause, RotateCcw, Check, AlertCircle, Shield, FileText, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { apiFetch } from '@/lib/api';

export interface VoiceNoteRecorderProps {
  caseId?: string;
  locale: string;
  onTranscribeSuccess: (transcript: string, words?: any[], uncertainSpans?: any[]) => void;
  onSwitchToTyping: () => void;
}

export function VoiceNoteRecorder({
  caseId,
  locale,
  onTranscribeSuccess,
  onSwitchToTyping,
}: VoiceNoteRecorderProps) {
  const isBangla = locale === 'bn';

  const [consentGranted, setConsentGranted] = useState(true);
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [duration, setDuration] = useState(0);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [permissionError, setPermissionError] = useState<string | null>(null);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [transcribeError, setTranscribeError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const audioElementRef = useRef<HTMLAudioElement | null>(null);

  // Clean up timers and object URLs on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (audioUrl) URL.revokeObjectURL(audioUrl);
    };
  }, [audioUrl]);

  const startRecording = async () => {
    if (!consentGranted) {
      setPermissionError(
        isBangla
          ? 'ভয়েস প্রসেসিংয়ের জন্য সম্মতি প্রদান করা আবশ্যক।'
          : 'Consent is required before recording your voice.'
      );
      return;
    }

    setPermissionError(null);
    setTranscribeError(null);
    audioChunksRef.current = [];

    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('MEDIA_NOT_SUPPORTED');
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      // Determine supported MIME format across browsers (Chrome vs Safari vs Firefox)
      let mimeType = 'audio/webm;codecs=opus';
      if (!MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
        if (MediaRecorder.isTypeSupported('audio/mp4')) {
          mimeType = 'audio/mp4'; // Safari iOS
        } else if (MediaRecorder.isTypeSupported('audio/aac')) {
          mimeType = 'audio/aac';
        } else if (MediaRecorder.isTypeSupported('audio/ogg')) {
          mimeType = 'audio/ogg';
        } else {
          mimeType = ''; // Let browser choose default
        }
      }

      const recorder = mimeType
        ? new MediaRecorder(stream, { mimeType })
        : new MediaRecorder(stream);

      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      recorder.onstop = () => {
        const finalBlob = new Blob(audioChunksRef.current, {
          type: recorder.mimeType || 'audio/webm',
        });
        setAudioBlob(finalBlob);
        const url = URL.createObjectURL(finalBlob);
        setAudioUrl(url);

        // Stop all media tracks to release microphone hardware indicator
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorderRef.current = recorder;
      recorder.start(250); // Slice every 250ms
      setIsRecording(true);
      setIsPaused(false);
      setDuration(0);

      timerRef.current = setInterval(() => {
        setDuration((prev) => prev + 1);
      }, 1000);
    } catch (err: any) {
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setPermissionError(
          isBangla
            ? 'মাইক্রোফোন ব্যবহারের অনুমতি পাওয়া যায়নি। অনুগ্রহ করে অনুমতি দিন অথবা নিচে সরাসরি টাইপ করুন।'
            : 'Microphone permission denied. Please allow microphone access or switch to typing below.'
        );
      } else if (err.name === 'NotFoundError') {
        setPermissionError(
          isBangla
            ? 'কোনো মাইক্রোফোন ডিভাইস পাওয়া যায়নি। অনুগ্রহ করে নিচে টাইপ করে ঘটনাটি লিখুন।'
            : 'No microphone found. Please switch to typing your dispute narrative below.'
        );
      } else {
        setPermissionError(
          isBangla
            ? 'রেকর্ডিং শুরু করা যায়নি। নিচে সরাসরি টাইপ করে এগিয়ে যান।'
            : 'Unable to start voice recording. Please use the text input below.'
        );
      }
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsPaused(false);
      if (timerRef.current) clearInterval(timerRef.current);
    }
  };

  const resetRecording = () => {
    if (audioUrl) URL.revokeObjectURL(audioUrl);
    setAudioBlob(null);
    setAudioUrl(null);
    setDuration(0);
    setIsRecording(false);
    setIsPaused(false);
    setIsPlaying(false);
  };

  const togglePlayback = () => {
    if (!audioElementRef.current && audioUrl) {
      const audio = new Audio(audioUrl);
      audio.onended = () => setIsPlaying(false);
      audioElementRef.current = audio;
    }

    if (audioElementRef.current) {
      if (isPlaying) {
        audioElementRef.current.pause();
        setIsPlaying(false);
      } else {
        audioElementRef.current.play();
        setIsPlaying(true);
      }
    }
  };

  const handleTranscribe = async () => {
    if (!audioBlob) return;

    setIsTranscribing(true);
    setTranscribeError(null);

    try {
      const targetCaseId = caseId || '00000000-0000-0000-0000-000000000000';
      const formData = new FormData();
      formData.append('audio_file', audioBlob, 'voice_narrative.webm');
      formData.append('consent_granted', String(consentGranted));
      formData.append('language_hint', isBangla ? 'bn-BD' : 'en-BD');
      formData.append('client_duration', String(duration));

      const res = await apiFetch(`/api/v1/cases/${targetCaseId}/audio/transcribe`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(
          errData.detail ||
            (isBangla
              ? 'ভয়েস প্রসেসিং ব্যর্থ হয়েছে। অনুগ্রহ করে টাইপ করে লিখুন।'
              : 'Voice transcription failed. Please switch to typing.')
        );
      }

      const result = await res.json();
      onTranscribeSuccess(result.transcript_text, result.words, result.uncertain_spans);
    } catch (err: any) {
      setTranscribeError(err.message || 'Failed to process audio');
    } finally {
      setIsTranscribing(false);
    }
  };

  const formatTimer = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="p-4 rounded-xl border border-border bg-surface space-y-4">
      {/* Consent Notice Banner (NFR-12 / T22) */}
      <div className="flex items-start gap-3 p-3 rounded-lg bg-elevated/40 border border-border text-xs">
        <Shield className="w-4 h-4 text-primary shrink-0 mt-0.5" />
        <div className="flex-1 space-y-1.5">
          <label className="flex items-center gap-2 cursor-pointer font-medium text-foreground select-none">
            <input
              type="checkbox"
              checked={consentGranted}
              onChange={(e) => setConsentGranted(e.target.checked)}
              className="rounded border-border text-primary focus:ring-primary w-4 h-4"
            />
            <span>
              {isBangla
                ? 'আমি আমার ভয়েস রেকর্ডিং প্রক্রিয়াকরণে সম্মতি জানাচ্ছি (ভয়েস নোট যেকোনো সময় ডিলিট বা পরিবর্তনযোগ্য)'
                : 'I consent to voice processing for fact extraction (Recordings remain private and deletable at any time)'}
            </span>
          </label>
        </div>
      </div>

      {/* Permission / Runtime Error Notice */}
      {permissionError && (
        <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md text-xs text-destructive flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{permissionError}</span>
          </div>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={onSwitchToTyping}
            className="text-xs h-7 shrink-0"
          >
            {isBangla ? 'টাইপ করুন' : 'Type Instead'}
          </Button>
        </div>
      )}

      {transcribeError && (
        <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md text-xs text-destructive flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{transcribeError}</span>
        </div>
      )}

      {/* Recording Controls & States */}
      <div className="flex flex-col items-center justify-center p-6 rounded-lg bg-elevated/20 border border-dashed border-border space-y-4">
        {isRecording ? (
          <div className="flex flex-col items-center space-y-3">
            <div className="relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-destructive opacity-75" />
              <div className="relative p-4 rounded-full bg-destructive text-white shadow-lg">
                <Mic className="w-6 h-6 animate-pulse" />
              </div>
            </div>
            <div className="text-xl font-mono font-bold text-foreground">
              {formatTimer(duration)}
            </div>
            <span className="text-xs text-muted-foreground animate-pulse">
              {isBangla ? 'রেকর্ডিং হচ্ছে... আপনার বক্তব্য বলুন' : 'Recording... speak naturally'}
            </span>
            <div className="flex items-center gap-2 pt-2">
              <Button
                type="button"
                variant="danger"
                size="sm"
                onClick={stopRecording}
                className="gap-1.5 text-xs"
              >
                <Square className="w-3.5 h-3.5" />
                <span>{isBangla ? 'রেকর্ডিং শেষ করুন' : 'Stop Recording'}</span>
              </Button>
            </div>
          </div>
        ) : audioBlob ? (
          <div className="flex flex-col items-center space-y-3 w-full max-w-sm">
            <Badge variant="success" className="text-[10px]">
              {isBangla ? 'ভয়েস নোট প্রস্তুত' : 'Voice Note Ready'} ({formatTimer(duration)})
            </Badge>

            <div className="flex items-center justify-center gap-3 pt-2">
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={togglePlayback}
                className="gap-1.5 text-xs"
              >
                {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
                <span>{isPlaying ? (isBangla ? 'থামান' : 'Pause') : (isBangla ? 'শুনুন' : 'Play')}</span>
              </Button>

              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={resetRecording}
                className="gap-1.5 text-xs text-muted-foreground hover:text-foreground"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>{isBangla ? 'আবার রেকর্ড করুন' : 'Re-record'}</span>
              </Button>

              <Button
                type="button"
                variant="primary"
                size="sm"
                onClick={handleTranscribe}
                disabled={isTranscribing}
                className="gap-1.5 text-xs font-semibold"
              >
                {isTranscribing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Check className="w-3.5 h-3.5" />}
                <span>
                  {isTranscribing
                    ? (isBangla ? 'টেক্সটে রূপান্তর হচ্ছে...' : 'Transcribing...')
                    : (isBangla ? 'টেক্সটে রূপান্তর করুন' : 'Convert to Text')}
                </span>
              </Button>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center space-y-3 text-center">
            <div className="p-4 rounded-full bg-primary/10 text-primary">
              <Mic className="w-6 h-6" />
            </div>
            <div>
              <span className="text-sm font-semibold text-foreground block">
                {isBangla ? 'মুখোমুখি বলার মতো করে ঘটনাটি বলুন' : 'Describe your dispute with your voice'}
              </span>
              <span className="text-xs text-muted-foreground block mt-0.5">
                {isBangla ? 'বাংলা, ইংরেজি বা বাংলিশ যে কোনো ভাষায় বলতে পারেন' : 'Speak in Bangla, English or Banglish'}
              </span>
            </div>
            <Button
              type="button"
              variant="primary"
              size="sm"
              onClick={startRecording}
              disabled={!consentGranted}
              className="gap-1.5 text-xs"
            >
              <Mic className="w-3.5 h-3.5" />
              <span>{isBangla ? 'রেকর্ডিং শুরু করুন' : 'Start Recording'}</span>
            </Button>
          </div>
        )}
      </div>

      {/* Fallback to Typing Button (T22 Invariant: Typing fallback always accessible) */}
      <div className="flex justify-end pt-1">
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={onSwitchToTyping}
          className="text-xs text-muted-foreground hover:text-foreground gap-1.5"
        >
          <FileText className="w-3.5 h-3.5" />
          <span>{isBangla ? 'টাইপ করে বর্ণনা দিন' : 'Switch to Typing'}</span>
        </Button>
      </div>
    </div>
  );
}

