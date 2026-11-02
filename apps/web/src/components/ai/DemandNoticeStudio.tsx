'use client';

import React, { useState, useEffect } from 'react';
import { Copy, Check, FileDown, Sparkles, Scale, AlertTriangle, ShieldCheck, MessageCircle, Send, Phone } from 'lucide-react';
import { Button } from '@/components/ui/Button';

interface DemandNoticeStudioProps {
  caseReference?: string;
  merchantName?: string;
  amountBdt?: number;
  itemDescription?: string;
  className?: string;
}

type ToneType = 'formal' | 'urgent' | 'amicable';

function getNoticeTemplates(vars: {
  merchantName: string;
  amountBdt: number;
  itemDescription: string;
  caseReference: string;
  dateStr: string;
}): Record<ToneType, { label: string; badge: string; text: string }> {
  const { merchantName, amountBdt, itemDescription, caseReference, dateStr } = vars;
  const formattedAmt =
    amountBdt > 0 ? `BDT ${amountBdt.toLocaleString('en-US')}.00` : 'the disputed sum stated in order details';

  return {
    formal: {
      label: '⚖️ Formal Statutory (DNCRP Compliant)',
      badge: 'Recommended Legal Standard',
      text: `FORMAL LEGAL DEMAND NOTICE
Under Section 45 & 53 of the Consumer Rights Protection Act, 2009

Date: ${dateStr}
To: The Authorized Representative, ${merchantName}

Subject: Final demand for settlement regarding non-delivery of prepaid goods (Ref #${caseReference})

Dear Sir/Madam,

The undersigned consumer remitted ${formattedAmt} via verified digital payment for the purchase of "${itemDescription}". The promised delivery deadline has expired without resolution.

Despite repeated communications, you have failed to deliver the purchased item or issue a full refund, constituting an unlawful trade practice under Section 45 of the Consumer Rights Protection Act, 2009.

You are hereby formally requested to refund the entire disputed sum of ${formattedAmt} within seven (7) business days from the receipt of this notice. Failure to do so will result in formal complaint escalation to the National Consumer Rights Protection Directorate (DNCRP) and relevant regulatory bodies without further notice.

Yours faithfully,
Aggrieved Consumer (ClaimCraft BD Verified Dispute #${caseReference})`,
    },
    urgent: {
      label: '⚡ Strict & Urgent (72-Hour Pre-Action)',
      badge: 'High Pressure / Escrow Freeze Warning',
      text: `LEGAL NOTICE OF INTENT TO ESCALATE — 72-HOUR NOTICE
Pursuant to Bangladesh Penal Code Section 420 and Consumer Rights Protection Act 2009

To: ${merchantName}
Merchant Reference: #${caseReference} | Disputed Sum: ${formattedAmt}

TAKE NOTICE that your failure to deliver the ordered merchandise ("${itemDescription}") or provide refund constitutes willful breach and unjust enrichment.

Unless the complete sum of ${formattedAmt} is refunded to the originating payment account within seventy-two (72) hours of this communication, formal complaints will be initiated with:
1. Directorate of National Consumer Rights Protection (DNCRP) for punitive administrative fines.
2. Bangladesh Bank Payment Systems Department for merchant wallet review.
3. Cyber Police Centre for digital commerce fraudulent non-delivery tracking.

Consider this our final pre-action communication before formal docketing.`,
    },
    amicable: {
      label: '🤝 Settlement Negotiation (Good Faith)',
      badge: 'Bilateral Amicable Resolution',
      text: `REQUEST FOR RESOLUTION & MUTUAL SETTLEMENT

To: Customer Care Management, ${merchantName}
Re: Case #${caseReference} (Disputed Sum ${formattedAmt})

Dear Management,

I am writing regarding my recent order for "${itemDescription}", which has not arrived past the agreed schedule. I understand that courier delays occasionally happen, but after waiting, I kindly request an amicable cancellation of the order and a prompt refund of ${formattedAmt} to my account.

I appreciate your past service and hope we can resolve this matter directly between consumer and merchant within the next 3 days, avoiding the need for third-party regulatory dispute filings.

Thank you for your prompt attention.`,
    },
  };
}

export function DemandNoticeStudio({
  caseReference = 'DEMO-GP-001',
  merchantName = 'Authorized Merchant',
  amountBdt = 0,
  itemDescription = 'Prepaid Goods / Services',
  className = '',
}: DemandNoticeStudioProps) {
  const [currentTone, setCurrentTone] = useState<ToneType>('formal');
  const [displayedText, setDisplayedText] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [copied, setCopied] = useState(false);
  const [merchantPhone, setMerchantPhone] = useState('');
  const [showPhoneInput, setShowPhoneInput] = useState(false);

  const dateStr = new Intl.DateTimeFormat('en-GB', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  }).format(new Date());

  const templates = getNoticeTemplates({
    merchantName,
    amountBdt,
    itemDescription,
    caseReference,
    dateStr,
  });

  const handleWhatsAppSend = () => {
    const rawText = templates[currentTone].text;
    const cleanPhone = merchantPhone.replace(/[^0-9]/g, '');
    const url = cleanPhone
      ? `https://wa.me/${cleanPhone.startsWith('88') ? cleanPhone : '88' + cleanPhone}?text=${encodeURIComponent(rawText)}`
      : `https://wa.me/?text=${encodeURIComponent(rawText)}`;
    if (typeof window !== 'undefined') {
      window.open(url, '_blank');
    }
  };

  // Typewriter streaming effect when tone changes
  useEffect(() => {
    const fullText = templates[currentTone].text;
    setIsStreaming(true);
    setDisplayedText('');

    let charIndex = 0;
    const interval = setInterval(() => {
      charIndex += 14; // Fast fluid typewriter chunking
      if (charIndex >= fullText.length) {
        setDisplayedText(fullText);
        setIsStreaming(false);
        clearInterval(interval);
      } else {
        setDisplayedText(fullText.slice(0, charIndex));
      }
    }, 18);

    return () => clearInterval(interval);
  }, [currentTone, merchantName, amountBdt, itemDescription, caseReference]);

  const handleCopy = () => {
    navigator.clipboard.writeText(templates[currentTone].text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <div
      className={`rounded-2xl border border-border bg-surface overflow-hidden shadow-xs space-y-0 ${className}`}
    >
      {/* Studio Header & Tone Switcher */}
      <div className="p-4 border-b border-border bg-surface flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-primary/10 text-primary border border-primary/20 flex items-center justify-center shrink-0">
            <Scale className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-foreground flex items-center gap-1.5">
              Generative Legal Notice Studio
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-primary/10 text-primary font-mono font-bold">
                AI Powered
              </span>
            </h4>
            <p className="text-[11px] text-muted-foreground">
              Select strategic tone to recalibrate statutory assertiveness
            </p>
          </div>
        </div>

        {/* Tone Selector Pills */}
        <div className="flex items-center gap-1 bg-elevated p-1 rounded-xl border border-border">
          {(['formal', 'urgent', 'amicable'] as ToneType[]).map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => setCurrentTone(t)}
              className={`text-[11px] px-2.5 py-1.5 rounded-lg font-medium transition-all ${
                currentTone === t
                  ? 'bg-surface text-foreground font-bold shadow-xs border border-border'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              {t === 'formal' ? 'Formal' : t === 'urgent' ? 'Urgent' : 'Amicable'}
            </button>
          ))}
        </div>
      </div>

      {/* Editor Canvas */}
      <div className="p-5 bg-slate-950/5 dark:bg-slate-950/40 relative">
        <div className="flex justify-between items-center pb-2 text-[11px] text-muted-foreground font-mono">
          <span>Tone: <strong>{templates[currentTone].label}</strong></span>
          <span className="text-emerald-600 dark:text-emerald-400 font-bold">
            {templates[currentTone].badge}
          </span>
        </div>

        {/* Text Container */}
        <div className="p-4 rounded-xl border border-border bg-surface text-foreground font-mono text-xs leading-relaxed whitespace-pre-line min-h-[260px] relative select-text">
          {displayedText}
          {isStreaming && (
            <span className="inline-block w-2 h-3.5 bg-primary ml-1 animate-pulse align-middle" />
          )}
        </div>

        {/* Phone Input Row for Direct WhatsApp */}
        {showPhoneInput && (
          <div className="mb-3 p-3 rounded-xl border border-emerald-500/30 bg-emerald-500/10 flex flex-col sm:flex-row items-center gap-2">
            <Phone className="w-4 h-4 text-emerald-500 shrink-0" />
            <span className="text-xs text-foreground font-medium shrink-0">
              Merchant WhatsApp:
            </span>
            <input
              type="text"
              placeholder="e.g. 01712345678"
              value={merchantPhone}
              onChange={(e) => setMerchantPhone(e.target.value)}
              className="flex-1 p-1.5 px-3 rounded-lg border border-border bg-surface text-xs text-foreground focus:outline-hidden focus:ring-1 focus:ring-emerald-500"
            />
            <Button
              type="button"
              size="sm"
              onClick={handleWhatsAppSend}
              className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold gap-1.5 shrink-0"
            >
              <Send className="w-3.5 h-3.5" />
              <span>Send Now</span>
            </Button>
          </div>
        )}

        {/* Bottom Actions Bar */}
        <div className="flex flex-col sm:flex-row justify-between items-center gap-3 pt-4">
          <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
            <ShieldCheck className="w-4 h-4 text-emerald-500" />
            <span>Pre-action compliance: Governed under CRPA 2009 Sec 45</span>
          </div>

          <div className="flex flex-wrap items-center gap-2 w-full sm:w-auto">
            <button
              type="button"
              onClick={() => {
                if (merchantPhone) {
                  handleWhatsAppSend();
                } else {
                  setShowPhoneInput(!showPhoneInput);
                }
              }}
              className="inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-xs transition-all active:scale-95 flex-1 sm:flex-none h-8"
              title="Send Legal Notice to Merchant via WhatsApp"
            >
              <MessageCircle className="w-3.5 h-3.5 fill-white" />
              <span>WhatsApp Notice</span>
            </button>
            <Button
              type="button"
              size="sm"
              variant="outline"
              onClick={handleCopy}
              className="text-xs flex items-center gap-1.5 flex-1 sm:flex-none h-8"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy Notice'}</span>
            </Button>
            <Button
              type="button"
              size="sm"
              onClick={handleCopy}
              className="text-xs font-bold flex items-center gap-1.5 flex-1 sm:flex-none h-8"
            >
              <FileDown className="w-3.5 h-3.5" />
              <span>Save PDF</span>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

