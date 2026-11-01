'use client';

import React, { useState } from 'react';
import {
  FileText,
  Printer,
  Copy,
  Check,
  Mail,
  Download,
  X,
  Building2,
  AlertCircle,
  Sparkles,
  ExternalLink,
} from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';

export interface DncrpFormData {
  complainantName: string;
  complainantNid: string;
  complainantPhone: string;
  complainantAddress: string;
  merchantName: string;
  merchantAddress: string;
  merchantPhone: string;
  incidentDate: string;
  disputedAmountBdt: number;
  productDescription: string;
  statutorySections: string[];
  evidenceList: string[];
}

export function DncrpOfficialFormModal({
  isOpen,
  onClose,
  data,
  locale = 'bn',
}: {
  isOpen: boolean;
  onClose: () => void;
  data: DncrpFormData;
  locale?: string;
}) {
  const isBangla = locale === 'bn';
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const handlePrint = () => {
    if (typeof window !== 'undefined') {
      window.print();
    }
  };

  const emailSubject = `ভোক্তা-অধিকার সংরক্ষণ আইন ২০০৯ অনুসারে অভিযোগ — ${data.merchantName}-এর বিরুদ্ধে`;
  const emailBody = `বরাবর,\nমহাপরিচালক,\nজাতীয় ভোক্তা অধিকার সংরক্ষণ অধিদপ্তর, ঢাকা।\n\nবিষয়: ${data.merchantName}-এর বিরুদ্ধে প্রতারণা ও ভোক্তা অধিকার লংঘনের আনুষ্ঠানিক অভিযোগ।\n\nঅভিযোগকারীর বিবরণ:\nনাম: ${data.complainantName}\nমোবাইল: ${data.complainantPhone}\nএনআইডি: ${data.complainantNid}\n\nঅভিযুক্ত মার্চেন্ট:\nনাম: ${data.merchantName}\nঠিকানা/প্লাটফর্ম: ${data.merchantAddress}\n\nসংক্ষিপ্ত বিবরণ:\n${data.productDescription}\nদাবিকৃত অর্থ: ৳${data.disputedAmountBdt} টাকা।\n\nসংযুক্ত প্রমাণাদি:\n${data.evidenceList.map((e, i) => `${i + 1}. ${e}`).join('\n')}\n\nবিনীত,\n${data.complainantName}`;

  const handleCopyEmail = () => {
    if (typeof navigator !== 'undefined') {
      navigator.clipboard.writeText(`Subject: ${emailSubject}\n\n${emailBody}`);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-fadeIn">
      {/* Modal Container */}
      <div className="relative w-full max-w-4xl bg-surface border border-border shadow-2xl rounded-2xl max-h-[90vh] flex flex-col overflow-hidden animate-scaleUp">
        {/* Modal Toolbar (Screen Only) */}
        <div className="flex items-center justify-between gap-3 px-5 py-4 border-b border-border bg-elevated/70 print:hidden">
          <div className="flex items-center gap-2">
            <span className="p-1 rounded-md bg-primary text-white">
              <Building2 className="w-4 h-4" />
            </span>
            <div>
              <h3 className="text-sm sm:text-base font-bold text-foreground">
                {isBangla
                  ? 'জাতীয় ভোক্তা অধিকার সংরক্ষণ অধিদপ্তর — অফিশিয়াল অভিযোগ ফরম (তফসিল-১)'
                  : 'DNCRP Official Statutory Complaint Form (Schedule 1)'}
              </h3>
              <p className="text-[11px] text-muted-foreground">
                {isBangla
                  ? 'ভোক্তা-অধিকার সংরক্ষণ আইন, ২০০৯ ও বিধিমালা অনুযায়ী অটো-জেনারেটেড'
                  : 'Auto-compiled according to Consumer Rights Protection Rules 2010'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="outline"
              onClick={handleCopyEmail}
              className="text-xs gap-1.5 h-8"
              title="Copy Email Text"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
              <span className="hidden sm:inline">{isBangla ? 'ইমেইল কপি' : 'Copy Email'}</span>
            </Button>

            <a
              href={`mailto:dncrp@yahoo.com?subject=${encodeURIComponent(emailSubject)}&body=${encodeURIComponent(emailBody)}`}
              className="inline-flex items-center gap-1.5 px-3 py-1 rounded-[var(--radius-control)] border border-primary/30 bg-primary/10 text-primary text-xs font-semibold hover:bg-primary/20 transition h-8"
            >
              <Mail className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">{isBangla ? 'ইমেইল পাঠান' : 'Send Email'}</span>
            </a>

            <Button
              size="sm"
              variant="primary"
              onClick={handlePrint}
              className="text-xs gap-1.5 h-8 font-bold"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>{isBangla ? 'প্রিন্ট / PDF ডাউনলোড' : 'Print / Save PDF'}</span>
            </Button>

            <button
              type="button"
              onClick={onClose}
              className="p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-elevated transition ml-1"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Printable Official Bangla Form Body */}
        <div className="flex-1 overflow-y-auto p-6 sm:p-10 font-sans print:p-0 print:overflow-visible">
          <div className="max-w-2xl mx-auto border-2 border-foreground/30 p-8 sm:p-12 bg-white text-zinc-900 rounded-lg shadow-sm print:shadow-none print:border-none print:p-4 text-xs sm:text-sm leading-relaxed">
            {/* Form Header */}
            <div className="text-center pb-6 border-b-2 border-zinc-900 space-y-1">
              <span className="text-[11px] font-bold uppercase tracking-widest text-zinc-600 block">
                গণপ্রজাতন্ত্রী বাংলাদেশ সরকার
              </span>
              <h2 className="text-base sm:text-lg font-black text-zinc-950">
                জাতীয় ভোক্তা অধিকার সংরক্ষণ অধিদপ্তর
              </h2>
              <p className="text-xs text-zinc-700">
                ১ কারওয়ান বাজার (টিসিবি ভবন), ঢাকা-১২১৫ | হটলাইন: ১৬১২১ | ইমেইল: dncrp@yahoo.com
              </p>
              <div className="inline-block px-3 py-0.5 mt-2 rounded border border-zinc-900 font-bold text-xs bg-zinc-100">
                অভিযোগ দায়ের ফরম [ফরম-১, বিধি ৪(১) দ্রষ্টব্য]
              </div>
            </div>

            {/* Recipient */}
            <div className="mt-6 space-y-0.5">
              <p className="font-bold">বরাবর,</p>
              <p>মহাপরিচালক / উপ-পরিচালক,</p>
              <p>জাতীয় ভোক্তা অধিকার সংরক্ষণ অধিদপ্তর।</p>
            </div>

            {/* Subject */}
            <div className="mt-4 font-bold border-l-2 border-zinc-900 pl-2">
              বিষয়: {data.merchantName}-এর বিরুদ্ধে ভোক্তা অধিকার লংঘন ও প্রতারণার প্রতিকার প্রসঙ্গে।
            </div>

            {/* Section 1: Complainant Details */}
            <div className="mt-6 space-y-2">
              <h4 className="font-bold border-b pb-1 text-zinc-900">১. অভিযোগকারীর বিবরণ:</h4>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>(ক) নাম: <strong>{data.complainantName}</strong></div>
                <div>(খ) মোবাইল: <strong>{data.complainantPhone}</strong></div>
                <div>(গ) জাতীয় পরিচয়পত্র (NID): <strong>{data.complainantNid}</strong></div>
                <div>(ঘ) বর্তমান ঠিকানা: <strong>{data.complainantAddress}</strong></div>
              </div>
            </div>

            {/* Section 2: Opposite Party (Merchant) Details */}
            <div className="mt-5 space-y-2">
              <h4 className="font-bold border-b pb-1 text-zinc-900">২. অভিযুক্ত ব্যক্তি / প্রতিষ্ঠানের বিবরণ:</h4>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>(ক) প্রতিষ্ঠানের নাম: <strong>{data.merchantName}</strong></div>
                <div>(খ) ফোন/হোয়াটসঅ্যাপ: <strong>{data.merchantPhone}</strong></div>
                <div className="col-span-2">(গ) ঠিকানা / ফেসবুক পেইজ / ওয়েবসাইট: <strong>{data.merchantAddress}</strong></div>
              </div>
            </div>

            {/* Section 3: Grievance & Statutory Violation */}
            <div className="mt-5 space-y-2">
              <h4 className="font-bold border-b pb-1 text-zinc-900">৩. ঘটনার বিবরণ ও অভিযুক্ত অপরাধ:</h4>
              <p className="text-justify text-xs leading-relaxed">
                গত <strong>{data.incidentDate}</strong> তারিখে আমি অভিযুক্ত প্রতিষ্ঠানের নিকট থেকে <strong>৳{data.disputedAmountBdt.toLocaleString('bn-BD')}</strong> টাকা মূল্যের পণ্য ক্রয়ের উদ্দেশ্যে চুক্তি করি এবং এমএফএস (বিকাশ) মারফত উক্ত অর্থ পরিশোধ করি। কিন্তু অভিযুক্ত প্রতিষ্ঠান প্রতিশ্রুত পণ্য প্রদানে ব্যর্থ হয় এবং পরবর্তীতে যোগাযোগের মাধ্যমগুলোতে আমাকে অবরুদ্ধ (ব্লক) করে দেয়, যা <em>ভোক্তা-অধিকার সংরক্ষণ আইন, ২০০৯</em> এর নিম্নোক্ত ধারাসমূহের চরম লংঘন:
              </p>
              <ul className="list-disc list-inside pl-2 text-xs space-y-1 font-semibold text-zinc-800">
                {data.statutorySections.map((sec, idx) => (
                  <li key={idx}>{sec}</li>
                ))}
              </ul>
            </div>

            {/* Section 4: Attached Evidentiary Proofs */}
            <div className="mt-5 space-y-2">
              <h4 className="font-bold border-b pb-1 text-zinc-900">৪. সংযুক্ত প্রমাণাদির তালিকা (ডিজিটাল এভিডেন্স ভল্ট):</h4>
              <ol className="list-decimal list-inside pl-2 text-xs space-y-1 text-zinc-800">
                {data.evidenceList.map((ev, idx) => (
                  <li key={idx}>{ev}</li>
                ))}
              </ol>
            </div>

            {/* Section 5: Prayer / Relief Requested */}
            <div className="mt-5 space-y-1.5">
              <h4 className="font-bold border-b pb-1 text-zinc-900">৫. প্রার্থিত প্রতিকার:</h4>
              <p className="text-justify text-xs leading-relaxed">
                অতএব, মহোদয়ের সমীপে বিনীত প্রার্থনা, উক্ত ঘটনার সঠিক তদন্তপূর্বক অভিযুক্ত প্রতিষ্ঠানকে আইনানুগ শাস্তির আওতায় এনে আমার দাবিকৃত অর্থ ফেরত প্রদান এবং আইনের ধারা ৭৬(১) অনুযায়ী সরকারি অর্থদণ্ডের ২৫% অংশ নগদ প্রদানের যথাযথ আদেশ দানে বাধিত করবেন।
              </p>
            </div>

            {/* Signatures */}
            <div className="mt-12 flex justify-between items-end text-xs">
              <div>
                <p>তারিখ: <strong>{new Date().toLocaleDateString('bn-BD')}</strong></p>
                <p className="text-[10px] text-zinc-500">এবার কি? (EbarKi) ভেরিফায়েড ডিজিটাল ডসিয়ার</p>
              </div>
              <div className="text-center">
                <div className="w-40 border-b border-zinc-900 mb-1" />
                <p className="font-bold">{data.complainantName}</p>
                <p className="text-[10px] text-zinc-600">অভিযোগকারীর স্বাক্ষর</p>
              </div>
            </div>
          </div>
        </div>

        {/* Modal Footer Instructions (Screen Only) */}
        <div className="px-5 py-3 border-t border-border bg-elevated/70 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs text-muted-foreground print:hidden">
          <div className="flex items-center gap-1.5">
            <Sparkles className="w-4 h-4 text-amber-500 shrink-0" />
            <span>
              {isBangla
                ? 'অনলাইন সাবমিশন: ফরমটি ডাউনলোড বা ইমেইল কপি করে সরাসরি dncrp@yahoo.com এ পাঠিয়ে দিন।'
                : 'Direct filing: Send this PDF attachment to dncrp@yahoo.com or submit at national consumer office.'}
            </span>
          </div>
          <span className="text-[11px] font-mono text-primary font-bold">
            DNCRP Format Verified
          </span>
        </div>
      </div>
    </div>
  );
}

