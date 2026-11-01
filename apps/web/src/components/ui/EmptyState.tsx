import React from 'react';
import Link from 'next/link';
import { LucideIcon, Inbox } from 'lucide-react';
import { Button } from './Button';

export interface EmptyStateProps {
  title: string;
  description: string;
  icon?: LucideIcon;
  actionLabel?: string;
  actionHref?: string;
  onAction?: () => void;
}

export function EmptyState({
  title,
  description,
  icon: Icon = Inbox,
  actionLabel,
  actionHref,
  onAction,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-8 md:p-12 text-center rounded-[var(--radius-panel)] border border-dashed border-border bg-surface/60 space-y-3">
      <div className="w-12 h-12 rounded-full bg-elevated text-muted-foreground flex items-center justify-center mb-1">
        <Icon className="w-6 h-6" />
      </div>
      <h3 className="text-base font-bold text-foreground">{title}</h3>
      <p className="text-xs text-muted-foreground max-w-sm leading-relaxed">{description}</p>
      {actionLabel && actionHref && (
        <div className="pt-2">
          <Link
            href={actionHref}
            className="inline-flex items-center justify-center font-medium transition-colors rounded-[var(--radius-control)] border border-border bg-surface text-foreground hover:bg-elevated text-xs px-3 py-1.5 min-h-[38px] cursor-pointer"
          >
            {actionLabel}
          </Link>
        </div>
      )}
      {actionLabel && !actionHref && onAction && (
        <div className="pt-2">
          <Button size="sm" variant="outline" onClick={onAction}>
            {actionLabel}
          </Button>
        </div>
      )}
    </div>
  );
}
