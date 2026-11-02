'use client';

import React, { useState } from 'react';
import {
  PhoneCall,
  ShieldAlert,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  Clock,
  Sparkles,
  Lock,
} from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';

interface HelplineItem {
  id: string;
  nameEn: string;
  nameBn: string;
  agencyEn: string;
  agencyBn: string;
  number: string;
  hoursEn: string;
  hoursBn: string;
  accent: string;
}

const HELPLINES: HelplineItem[] = [
  {
    id: 'dncrp',
    nameEn: 'National Consumer Directorate',
    nameBn: 'ভোক্তা অধিকার সংরক্ষণ অধিদপ্তর (DNCRP)',
    agencyEn: 'Govt. Consumer Rights Ministry',
    agencyBn: 'বাণিজ্য মন্ত্রণালয় অধীনস্থ অধিদপ্তর',
    number: '16121',
    hoursEn: '9:00 AM – 5:00 PM (Govt. Days)',
    hoursBn: 'সকাল ৯টা – বিকাল ৫টা (সরকারি কার্যদিবস)',
    accent: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20',
  },
  {
    id: 'bkash',
    nameEn: 'bKash Fraud & Wallet Hold Cell',
    nameBn: 'বিকাশ ফ্রড ট্রানজ্যাকশন ও ওয়ালেট হোল্ড সেল',
    agencyEn: 'MFS Disputed Trx Cell',
    agencyBn: 'লেনদেন প্রতারণা ও অ্যাকাউন্ট ফ্রিজ',
    number: '16247',
    hoursEn: '24/7 Toll-Free Support',
    hoursBn: '২৪ ঘণ্টা সার্বক্ষণিক সেবা',
    accent: 'bg-pink-500/10 text-pink-600 dark:text-pink-400 border-pink-500/20',
  },
  {
    id: 'bb-cipc',
    nameEn: 'Bangladesh Bank CIPC Cell',
    nameBn: 'বাংলাদেশ ব্যাংক ফাইন্যান্সিয়াল ইন্টেগ্রিটি সেল (CIPC)',
    agencyEn: 'Central Bank Banking & MFS Ombudsman',
    agencyBn: 'কেন্দ্রীয় ব্যাংক আর্থিক ন্যায়পাল',
    number: '16236',
    hoursEn: '10:00 AM – 6:00 PM',
    hoursBn: 'সকাল ১০টা – সন্ধ্যা ৬টা',
    accent: 'bg-primary/10 text-primary border-primary/20',
  },
  {
    id: 'national-999',
    nameEn: 'National Emergency Service (Cyber Crime)',
    nameBn: 'জাতীয় জরুরি সেবা (পুলিশ সাইবার ক্রাইম)',
    agencyEn: 'Bangladesh Police CID',
    agencyBn: 'বাংলাদেশ পুলিশ সাইবার সাপোর্ট',
    number: '999',
    hoursEn: '24/7 Immediate Response',
    hoursBn: '২৪ ঘণ্টা জরুরি সেবা',
    accent: 'bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/20',
  },
  {
    id: 'nagad',
    nameEn: 'Nagad Fraud Helpline',
    nameBn: 'নগদ প্রতারণা প্রতিরোধ হেল্পলাইন',
    agencyEn: 'MFS Security Cell',
    agencyBn: 'ডাক বিভাগীয় এমএফএস সিকিউরিটি',
    number: '16167',
    hoursEn: '24/7 Customer Care',
    hoursBn: '২৪ ঘণ্টা কাস্টমার কেয়ার',
    accent: 'bg-orange-500/10 text-orange-600 dark:text-orange-400 border-orange-500/20',
  },
  {
    id: 'btrc',
    nameEn: 'BTRC Telecom & ISP Grievance',
    nameBn: 'বিটিআরসি টেলিকম ও ইন্টারনেট অভিযোগ',
    agencyEn: 'Telecom Regulatory Commission',
    agencyBn: 'টেলিযোগাযোগ নিয়ন্ত্রণ কমিশন',
    number: '100',
    hoursEn: 'Office Hours',
    hoursBn: 'অফিস চলাকালীন',
    accent: 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20',
  },
];

export function EmergencyHelplinesBar({
  locale = 'en',
  disputedTrxId = 'TRX-REF-PENDING',
  disputedAmount = 2500,
  merchantName = 'অনির্দিষ্ট অনলাইন মার্চেন্ট',
  className,
}: {
  locale?: string;
  disputedTrxId?: string;
  disputedAmount?: number;
  merchantName?: string;
  className?: string;
}) {
  const isBangla = locale === 'bn';
  const [showMfsScript, setShowMfsScript] = useState(false);
  const [copied, setCopied] = useState(false);

  const mfsScriptBangla = `“আসসালামু আলাইকুম। আমার বিকাশ অ্যাকাউন্ট থেকে একটি প্রতারণামূলক মার্চেন্ট ট্রানজ্যাকশন হয়েছে।
মার্চেন্টের নাম: ${merchantName}
লেনদেনের TrxID: ${disputedTrxId}
টাকার পরিমাণ: ৳${disputedAmount.toLocaleString('bn-BD')} টাকা।

আমি অগ্রিম টাকা পাঠিয়েছিলাম, কিন্তু বিক্রেতা কোনো পণ্য ডেলিভারি দেয়নি এবং এখন হোয়াটসঅ্যাপে ব্লক করে দিয়েছে।
বাংলাদেশ ব্যাংক এমএফএস রেগুলেশন ২০২২ অনুসারে প্রাপকের ওয়ালেট থেকে এই পরিমাণ টাকা ক্যাশআউট সাময়িকভাবে হোল্ড করে আমাকে একটি অফিসিয়াল অভিযোগ টিকিট নম্বর দিন।”`;

  const mfsScriptEnglish = `"Hello. I am reporting a fraudulent merchant transaction from my bKash account.
Merchant: ${merchantName}
Transaction TrxID: ${disputedTrxId}
Disputed Amount: ৳${disputedAmount.toLocaleString('en-US')} BDT.

I made an advance payment for goods, but the seller failed to deliver and blocked me on social media.
Under Bangladesh Bank MFS Directives 2022, I formally request you to place a temporary hold on the recipient's wallet cash-out and issue an official dispute ticket number."`;

  const currentScript = isBangla ? mfsScriptBangla : mfsScriptEnglish;

  const handleCopyScript = () => {
    if (typeof navigator !== 'undefined') {
      navigator.clipboard.writeText(currentScript);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div
      className={cn(
        'rounded-2xl border border-border/80 bg-surface/95 backdrop-blur-md p-4 sm:p-6 shadow-sm',
        className
      )}
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-border/60">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-red-500/10 border border-red-500/20 text-red-500 flex items-center justify-center shrink-0">
            <PhoneCall className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm sm:text-base font-bold text-foreground">
                {isBangla
                  ? 'জাতীয় ভোক্তা ও আর্থিক জরুরি হেল্পলাইন'
                  : 'National Consumer & Financial Emergency Hotlines'}
              </h3>
              <Badge variant="danger" className="text-[10px] uppercase font-mono">
                {isBangla ? '১-ক্লিকে কল' : 'Direct Dial'}
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground mt-0.5">
              {isBangla
                ? 'আইনি নোটিশের পাশাপাশি প্রতারক মার্চেন্টের বিকাশ ওয়ালেট দ্রুত হোল্ড করতে অবিলম্বে কল করুন'
                : 'Direct government and financial hotlines to freeze fraudster accounts and register disputes'}
            </p>
          </div>
        </div>

        {/* MFS Script Toggle */}
        <button
          type="button"
          onClick={() => setShowMfsScript(!showMfsScript)}
          className="text-xs text-primary font-bold flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary/10 border border-primary/20 hover:bg-primary/20 transition self-start sm:self-center"
        >
          <Lock className="w-3.5 h-3.5 text-primary" />
          <span>{isBangla ? 'বিকাশ ওয়ালেট হোল্ড স্ক্রিপ্ট' : 'bKash Freeze Script'}</span>
          {showMfsScript ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>
      </div>

      {/* Interactive bKash / Nagad Wallet Freeze Script Drawer */}
      {showMfsScript && (
        <div className="mt-4 p-4 rounded-xl bg-pink-500/5 border border-pink-500/25 animate-fadeIn text-xs">
          <div className="flex items-center justify-between pb-2 mb-2 border-b border-pink-500/20">
            <div className="flex items-center gap-2">
              <span className="p-1 rounded-md bg-pink-500 text-white font-bold text-[10px]">
                MFS
              </span>
              <span className="font-bold text-foreground">
                {isBangla
                  ? '১৬২৪৭ (বিকাশ) বা ১৬১৬৭ (নগদ) হেল্পলাইনে যা বলবেন (প্রস্তুতকৃত স্ক্রিপ্ট):'
                  : 'What to say to the bKash/Nagad representative (Pre-drafted script):'}
              </span>
            </div>
            <Button
              size="sm"
              variant="outline"
              onClick={handleCopyScript}
              className="text-[11px] gap-1 h-7 px-2 border-pink-500/30"
            >
              {copied ? <Check className="w-3 h-3 text-emerald-500" /> : <Copy className="w-3 h-3" />}
              <span>{copied ? (isBangla ? 'কপি হয়েছে' : 'Copied') : (isBangla ? 'স্ক্রিপ্ট কপি' : 'Copy')}</span>
            </Button>
          </div>

          <pre className="p-3 rounded-lg bg-surface border border-border/80 text-[11px] font-sans text-foreground whitespace-pre-wrap leading-relaxed select-all">
            {currentScript}
          </pre>

          <p className="text-[10px] text-muted-foreground mt-2 flex items-center gap-1">
            <Clock className="w-3 h-3 text-amber-500 shrink-0" />
            <span>
              {isBangla
                ? 'টিপস: পেমেন্টের ২৪ ঘণ্টার মধ্যে কল করলে মার্চেন্টের ক্যাশআউট আটকানোর সম্ভাবনা ৯০% বৃদ্ধি পায়।'
                : 'Tip: Calling within 24 hours of payment significantly increases the probability of halting merchant cashout.'}
            </span>
          </p>
        </div>
      )}

      {/* Grid of 6 Hotlines */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mt-4">
        {HELPLINES.map((item) => (
          <a
            key={item.id}
            href={`tel:${item.number}`}
            className="flex items-center justify-between gap-3 p-3 rounded-xl border border-border/70 bg-surface hover:bg-elevated/70 hover:border-primary/40 transition group shadow-2xs"
          >
            <div className="min-w-0">
              <div className="flex items-center gap-1.5 mb-0.5">
                <span className="text-xs font-bold text-foreground truncate group-hover:text-primary transition-colors">
                  {isBangla ? item.nameBn : item.nameEn}
                </span>
              </div>
              <span className="text-[10px] text-muted-foreground block truncate">
                {isBangla ? item.hoursBn : item.hoursEn}
              </span>
            </div>

            <div className="flex items-center gap-1.5 shrink-0">
              <span
                className={cn(
                  'text-xs font-mono font-extrabold px-2 py-1 rounded-lg border flex items-center gap-1',
                  item.accent
                )}
              >
                <PhoneCall className="w-3 h-3" />
                <span>{item.number}</span>
              </span>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}

