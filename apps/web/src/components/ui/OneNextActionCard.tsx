import React from 'react';
import Link from 'next/link';
import { ArrowRight, HelpCircle, AlertCircle, CheckCircle2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './Card';
import { Button } from './Button';
import { Badge } from './Badge';

export interface ActionChoice {
  id: string;
  label: string;
  description?: string;
  href?: string;
  onClick?: () => void;
  primary?: boolean;
}

export interface OneNextActionProps {
  title: string;
  category?: string;
  whyItMatters: string;
  choices: ActionChoice[];
  status?: 'pending' | 'clarification_needed' | 'ready';
  locale?: string;
}

export function OneNextActionCard({
  title,
  category = 'Next Best Action',
  whyItMatters,
  choices,
  status = 'clarification_needed',
  locale = 'en',
}: OneNextActionProps) {
  const isBangla = locale === 'bn';

  return (
    <Card className="border-l-4 border-l-primary bg-gradient-to-br from-surface to-elevated/40 shadow-sm">
      <CardHeader className="pb-3 flex flex-row items-start justify-between">
        <div>
          <Badge variant="brand" className="mb-2">
            {category}
          </Badge>
          <CardTitle className="text-xl md:text-2xl text-foreground font-bold">
            {title}
          </CardTitle>
        </div>
        {status === 'clarification_needed' && (
          <div className="w-8 h-8 rounded-full bg-[var(--warning-soft)] text-[var(--warning-ink)] flex items-center justify-center shrink-0">
            <AlertCircle className="w-5 h-5" />
          </div>
        )}
      </CardHeader>
      <CardContent className="space-y-5">
        <div className="p-3.5 rounded-[var(--radius-control)] bg-surface border border-border/80">
          <div className="flex items-start gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
            <HelpCircle className="w-3.5 h-3.5 mt-0.5 text-primary" />
            <span>{isBangla ? 'কেন এটি জরুরি' : 'Why this matters'}</span>
          </div>
          <p className="text-sm text-foreground/90 leading-relaxed font-medium">
            {whyItMatters}
          </p>
        </div>

        <div className="flex flex-wrap gap-3 pt-1">
          {choices.map((choice) => {
            if (choice.href) {
              return (
                <Link
                  key={choice.id}
                  href={choice.href}
                  className={
                    choice.primary
                      ? 'inline-flex items-center justify-center font-medium transition-colors rounded-[var(--radius-control)] min-h-[44px] min-w-[44px] px-4 py-2 cursor-pointer bg-primary text-primary-foreground hover:opacity-90 gap-2 text-sm'
                      : 'inline-flex items-center justify-center font-medium transition-colors rounded-[var(--radius-control)] min-h-[44px] min-w-[44px] px-4 py-2 cursor-pointer border border-border bg-surface text-foreground hover:bg-elevated gap-2 text-sm'
                  }
                >
                  <span>{choice.label}</span>
                  {choice.primary && <ArrowRight className="w-4 h-4" />}
                </Link>
              );
            }

            return (
              <Button
                key={choice.id}
                variant={choice.primary ? 'primary' : 'outline'}
                size="md"
                onClick={choice.onClick}
                className="gap-2"
              >
                <span>{choice.label}</span>
                {choice.primary && <ArrowRight className="w-4 h-4" />}
              </Button>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
