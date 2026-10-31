import React from 'react';
import { Loader2 } from 'lucide-react';

export interface LoadingStateProps {
  message?: string;
  submessage?: string;
}

export function LoadingState({
  message = 'Loading case details...',
  submessage = 'Verifying evidence and evaluating statutory routes...',
}: LoadingStateProps) {
  return (
    <div
      role="status"
      aria-live="polite"
      className="flex flex-col items-center justify-center p-12 text-center rounded-[var(--radius-panel)] border border-border bg-surface/50 space-y-3"
    >
      <Loader2 className="w-8 h-8 text-primary animate-spin" />
      <p className="text-sm font-semibold text-foreground">{message}</p>
      {submessage && (
        <p className="text-xs text-muted-foreground max-w-xs">{submessage}</p>
      )}
    </div>
  );
}

