import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from './Button';

export interface ErrorStateProps {
  title?: string;
  message?: string;
  errorCode?: string;
  onRetry?: () => void;
}

export function ErrorState({
  title = 'Something went wrong',
  message = 'We could not load this case view. Your saved progress has not been lost.',
  errorCode,
  onRetry,
}: ErrorStateProps) {
  return (
    <div
      role="alert"
      className="p-6 md:p-8 rounded-[var(--radius-panel)] border border-red-300 dark:border-red-900/60 bg-[var(--danger-soft)]/50 text-[var(--danger-ink)] space-y-4"
    >
      <div className="flex items-start gap-3">
        <AlertCircle className="w-5 h-5 shrink-0 mt-0.5 text-red-600 dark:text-red-400" />
        <div className="space-y-1">
          <h3 className="text-sm font-bold text-foreground">{title}</h3>
          <p className="text-xs text-muted-foreground leading-relaxed">{message}</p>
          {errorCode && (
            <p className="text-[10px] font-mono text-muted-foreground pt-1">
              Code: {errorCode}
            </p>
          )}
        </div>
      </div>
      {onRetry && (
        <div className="pt-1">
          <Button size="sm" variant="outline" onClick={onRetry} className="gap-1.5 text-xs">
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Try Again</span>
          </Button>
        </div>
      )}
    </div>
  );
}
