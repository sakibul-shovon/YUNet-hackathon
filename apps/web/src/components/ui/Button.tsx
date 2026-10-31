import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { Loader2 } from 'lucide-react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', isLoading = false, disabled, children, ...props }, ref) => {
    const baseStyles =
      'inline-flex items-center justify-center font-medium transition-colors rounded-[var(--radius-control)] disabled:opacity-50 disabled:pointer-events-none min-h-[44px] min-w-[44px] px-4 py-2 cursor-pointer focus-visible:outline-2 focus-visible:outline-offset-2';

    const variants = {
      primary: 'bg-primary text-primary-foreground hover:opacity-90',
      secondary: 'bg-elevated text-foreground hover:bg-border/40',
      outline: 'border border-border bg-surface text-foreground hover:bg-elevated',
      ghost: 'bg-transparent text-foreground hover:bg-elevated',
      danger: 'bg-red-600 text-white hover:bg-red-700',
    };

    const sizes = {
      sm: 'text-xs px-3 py-1.5 min-h-[38px]',
      md: 'text-sm px-4 py-2 min-h-[44px]',
      lg: 'text-base px-6 py-3 min-h-[48px]',
    };

    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={twMerge(clsx(baseStyles, variants[variant], sizes[size], className))}
        {...props}
      >
        {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';

