'use client';

import React, { useState, useEffect } from 'react';
import { Copy, Check, AlertTriangle, Shield, FileText, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { apiFetch } from '@/lib/api';

interface DraftData {
  document_type: string;
  locale: string;
  subject: string;
  recipient: string;
  body_text: string;
  citations: string[];
  lifecycle_state: string;
  is_sent: boolean;
  is_filed: boolean;
  unsubmitted_banner_notice_en: string;
  unsubmitted_banner_notice_bn: string;
}

interface ActionDraftViewerProps {
  caseId: string;
  initialLocale: string;
}

export function ActionDraftViewer({ caseId, initialLocale }: ActionDraftViewerProps) {
  const [draftLocale, setDraftLocale] = useState<string>(initialLocale);
  const [draft, setDraft] = useState<DraftData | null>(null);
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(true);

  const isBangla = draftLocale === 'bn';

  const fetchDraft = async (loc: string) => {
    try {
      setLoading(true);
      const res = await apiFetch(`/api/v1/cases/${caseId}/draft?locale=${loc}`);
      if (res.ok) {
        const data = await res.json();
        setDraft(data);
      }
    } catch {
      // Fallback
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDraft(draftLocale);
  }, [caseId, draftLocale]);

  const handleCopy = async () => {
    if (!draft) return;
    try {
      await navigator.clipboard.writeText(`${draft.subject}\n\n${draft.body_text}`);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch (err) {
      console.error('Failed to copy', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* T26 Mandatory Unsubmitted Draft Banner */}
      <div className="p-4 rounded-xl border-2 border-amber-500/40 bg-amber-500/10 text-amber-900 dark:text-amber-200">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-600 dark:text-amber-400 mt-0.5 shrink-0" />
          <div className="text-xs space-y-1">
            <span className="font-extrabold uppercase tracking-wide block">
              {isBangla ? 'অননুমোদিত খসড়া নোটিশ' : 'UNSUBMITTED DRAFT NOTICE'}
            </span>
            <p className="leading-relaxed">
              {isBangla ? draft?.unsubmitted_banner_notice_bn : draft?.unsubmitted_banner_notice_en}
            </p>
          </div>
        </div>
      </div>

      {/* Draft Document Box */}
      <Card className="border border-border bg-surface shadow-sm">
        <CardHeader className="pb-3 border-b border-border/60 flex flex-row items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-brand" />
            <CardTitle className="text-base font-bold">
              {isBangla ? 'পূর্ব-অভিযোগ আনুষ্ঠানিক চিঠি' : 'Pre-Filing Formal Dispute Letter'}
            </CardTitle>
          </div>

          <div className="flex items-center gap-2">
            {/* Language Switcher for Letter */}
            <div className="flex rounded-md border border-border p-0.5 text-xs">
              <button
                type="button"
                onClick={() => setDraftLocale('en')}
                className={`px-2.5 py-1 rounded font-medium transition-colors ${
                  draftLocale === 'en'
                    ? 'bg-brand text-brand-foreground font-bold'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                English
              </button>
              <button
                type="button"
                onClick={() => setDraftLocale('bn')}
                className={`px-2.5 py-1 rounded font-medium transition-colors ${
                  draftLocale === 'bn'
                    ? 'bg-brand text-brand-foreground font-bold'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                বাংলা
              </button>
            </div>

            <Button
              size="sm"
              variant={copied ? 'primary' : 'outline'}
              onClick={handleCopy}
              className="text-xs gap-1.5"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? (isBangla ? 'কপি হয়েছে!' : 'Copied!') : (isBangla ? 'কপি করুন' : 'Copy Text')}</span>
            </Button>
          </div>
        </CardHeader>

        <CardContent className="pt-4 space-y-4">
          {loading && (
            <div className="p-8 text-center text-xs text-muted-foreground animate-pulse">
              {isBangla ? 'খসড়া তৈরি হচ্ছে...' : 'Generating legal draft...'}
            </div>
          )}

          {!loading && draft && (
            <div className="space-y-4">
              <div className="space-y-1 text-xs">
                <span className="text-[11px] font-bold text-muted-foreground uppercase block">
                  {isBangla ? 'বিষয়:' : 'Subject:'}
                </span>
                <span className="font-semibold text-foreground">{draft.subject}</span>
              </div>

              <div className="p-4 rounded-lg bg-canvas border border-border font-mono text-xs text-foreground whitespace-pre-wrap leading-relaxed select-all">
                {draft.body_text}
              </div>

              {/* Citations Grounding */}
              {draft.citations.length > 0 && (
                <div className="pt-2 border-t border-border/40 text-xs">
                  <span className="text-[11px] font-bold text-muted-foreground uppercase block mb-1.5">
                    {isBangla ? 'আইনি ভিত্তি ও সংশ্লিষ্ট নির্দেশিকা:' : 'Statutory Basis & Grounded References:'}
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {draft.citations.map((c, idx) => (
                      <Badge key={idx} variant="neutral" className="text-[10px]">
                        <Shield className="w-3 h-3 mr-1 text-brand" />
                        <span>{c}</span>
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

