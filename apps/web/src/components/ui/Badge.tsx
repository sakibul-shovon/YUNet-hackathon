import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'neutral' | 'brand' | 'warning' | 'danger' | 'success';
}

export function Badge({ className, variant = 'neutral', children, ...props }: BadgeProps) {
  const variants = {
    neutral: 'bg-elevated text-muted-foreground border-border',
    brand: 'bg-[var(--brand-soft)] text-[var(--brand)] border-[var(--brand)]/30',
    warning: 'bg-[var(--warning-soft)] text-[var(--warning-ink)] border-[var(--warning-ink)]/30',
    danger: 'bg-[var(--danger-soft)] text-[var(--danger-ink)] border-[var(--danger-ink)]/30',
    success: 'bg-emerald-100 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800',
  };

  return (
    <span
      className={twMerge(
        clsx(
          'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border',
          variants[variant],
          className
        )
      )}
      {...props}
    >
      {children}
    </span>
  );
}
