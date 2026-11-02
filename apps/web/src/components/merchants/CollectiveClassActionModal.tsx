'use client';

import React, { useState } from 'react';
import {
  Users,
  ShieldAlert,
  Building2,
  FileText,
  Printer,
  Mail,
  CheckCircle2,
  X,
  Scale,
  Sparkles,
  Download,
} from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';

interface CollectiveClassActionModalProps {
  isOpen: boolean;
  onClose: () => void;
  merchantName: string;
  platform: string;
  complaintCount: number;
  totalDisputedBdt: number;
  locale?: string;
}

export function CollectiveClassActionModal({
  isOpen,
  onClose,
  merchantName,
  platform,
  complaintCount,
  totalDisputedBdt,
  locale = 'bn',
}: CollectiveClassActionModalProps) {
  const isBangla = locale === 'bn';
  const [joined, setJoined] = useState(false);
  const [activeCount, setActiveCount] = useState(complaintCount);
  const [activeTotal, setActiveTotal] = useState(totalDisputedBdt);

  if (!isOpen) return null;

  const handleJoin = () => {
    if (!joined) {
      setJoined(true);
      setActiveCount((prev) => prev + 1);
      setActiveTotal((prev) => prev + 3500);
    }
  };

  const handlePrint = () => {
    if (typeof window !== 'undefined') {
      window.print();
    }
  };

  const projectedFine = Math.max(activeTotal * 2.5, 100000);
  const projectedReward = projectedFine * 0.25;

  const memoSubject = `যৌথ গণ-অভিযোগ ও স্মারকলিপি — ${merchantName}-এর বিরুদ্ধে ধারাবাহিক ভোক্তা প্রতারণা`;
  const memoBody = `বরাবর,\nমহাপরিচালক,\nজাতীয় ভোক্তা অধিকার সংরক্ষণ অধিদপ্তর (DNCRP), ঢাকা।\n\nবিষয়: ${merchantName} (${platform})-এর বিরুদ্ধে ${activeCount} জন ভুক্তভোগী ভোক্তার যৌথ গণ-অভিযোগ ও প্রশাসনিক ব্যবস্থার আবেদন।\n\nমহোদয়,\nআমরা নিম্নস্বাক্ষরকারী ভুক্তভোগী ভোক্তাগণ উক্ত মার্চেন্টের প্রতারণামূলক বাণিজ্য কর্মকাণ্ডের শিকার। মোট আত্মসাৎকৃত অর্থ: ৳${activeTotal.toLocaleString()} টাকা।\n\nভোক্তা অধিকার সংরক্ষণ আইন ২০০৯ এর ৪৫, ৪৬ ও ৭৬(১) ধারা অনুসারে উক্ত মার্চেন্টের বিরুদ্ধে মোবাইল কোর্ট পরিচালনা ও ২৫% প্রণোদনা অর্থ প্রদানের বিনীত আবেদন জানাচ্ছি।\n\nভুক্তভোগী নাগরিক জোট (ClaimCraft BD প্ল্যাটফর্ম কর্তৃক একত্রিত)`;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-fadeIn">
      <div className="relative w-full max-w-3xl bg-surface border border-border shadow-2xl rounded-3xl max-h-[90vh] flex flex-col overflow-hidden animate-scaleUp">
        {/* Header */}
        <div className="flex items-center justify-between gap-3 px-6 py-4 border-b border-border bg-elevated/70 print:hidden">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-rose-500/10 text-rose-500 border border-rose-500/30 flex items-center justify-center">
              <Users className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base sm:text-lg font-extrabold text-foreground flex items-center gap-2">
                <span>{isBangla ? 'যৌথ গণ-অভিযোগ জোট (Collective Class Action)' : 'Collective Consumer Class Action'}</span>
                <Badge variant="danger" className="text-[10px]">High Impact</Badge>
              </h3>
              <p className="text-xs text-muted-foreground">
                {merchantName} • {platform}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-elevated transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Class Metrics */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3.5 rounded-2xl bg-elevated/60 border border-border">
              <span className="text-[11px] text-muted-foreground block font-medium">
                {isBangla ? 'একত্রিত ভুক্তভোগী' : 'United Victims'}
              </span>
              <span className="text-xl font-extrabold text-foreground font-mono">
                {activeCount} {isBangla ? 'জন' : 'Citizens'}
              </span>
            </div>
            <div className="p-3.5 rounded-2xl bg-elevated/60 border border-border">
              <span className="text-[11px] text-muted-foreground block font-medium">
                {isBangla ? 'মোট আত্মসাৎকৃত অর্থ' : 'Aggregate Claim'}
              </span>
              <span className="text-xl font-extrabold text-foreground font-mono">
                ৳{activeTotal.toLocaleString()}
              </span>
            </div>
            <div className="p-3.5 rounded-2xl bg-rose-500/10 border border-rose-500/30">
              <span className="text-[11px] text-rose-600 dark:text-rose-400 block font-medium">
                {isBangla ? 'সম্ভাব্য সরকারি জরিমানা' : 'Projected Fine'}
              </span>
              <span className="text-xl font-extrabold text-rose-600 dark:text-rose-400 font-mono">
                ৳{projectedFine.toLocaleString()}
              </span>
            </div>
            <div className="p-3.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/30">
              <span className="text-[11px] text-emerald-600 dark:text-emerald-400 block font-medium">
                {isBangla ? 'ভোক্তা রিওয়ার্ড (২৫%)' : '25% Cash Bounty'}
              </span>
              <span className="text-xl font-extrabold text-emerald-600 dark:text-emerald-400 font-mono">
                ৳{projectedReward.toLocaleString()}
              </span>
            </div>
          </div>

          {/* Join Banner */}
          {!joined ? (
            <div className="p-4 rounded-2xl bg-primary/10 border border-primary/20 flex flex-col sm:flex-row items-center justify-between gap-4">
              <div>
                <h4 className="text-sm font-bold text-foreground">
                  {isBangla ? 'আপনিও কি এই মার্চেন্টের শিকার?' : 'Were you also affected by this merchant?'}
                </h4>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {isBangla
                    ? 'আপনার দাবিটি যুক্ত করলে সরকারের কাছে আবেদনের আইনি ওজন বহুগুণ বৃদ্ধি পাবে।'
                    : 'Add your claim to maximize legal leverage and magistrate attention under CRPA 2009.'}
                </p>
              </div>
              <Button
                size="sm"
                variant="primary"
                onClick={handleJoin}
                className="font-bold text-xs shrink-0 gap-1.5"
              >
                <Users className="w-3.5 h-3.5" />
                <span>{isBangla ? 'যৌথ পিটিশনে যুক্ত হোন (+১)' : 'Join Class Action (+1)'}</span>
              </Button>
            </div>
          ) : (
            <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center gap-3">
              <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0" />
              <div>
                <h4 className="text-sm font-bold text-emerald-600 dark:text-emerald-400">
                  {isBangla ? 'আপনি সফলভাবে যৌথ পিটিশনে যুক্ত হয়েছেন!' : 'Successfully Joined Class Action!'}
                </h4>
                <p className="text-xs text-muted-foreground">
                  {isBangla
                    ? 'আপনার ক্লেইম সংযুক্ত করা হয়েছে। নিচের অফিশিয়াল স্মারকলিপি ডাউনলোড বা সরাসরি DNCRP-তে ইমেইল করুন।'
                    : 'Your claim is now consolidated. Export or dispatch the joint petition below.'}
                </p>
              </div>
            </div>
          )}

          {/* Official Dossier Preview */}
          <div className="border border-border rounded-2xl bg-white text-zinc-900 p-6 text-xs font-sans leading-relaxed space-y-4 print:p-0 print:border-none">
            <div className="text-center border-b pb-3 space-y-1">
              <span className="text-[11px] font-bold uppercase tracking-wider text-zinc-500 block">
                গণপ্রজাতন্ত্রী বাংলাদেশ সরকার — জাতীয় ভোক্তা অধিকার সংরক্ষণ অধিদপ্তর
              </span>
              <h3 className="text-sm font-extrabold text-zinc-900">
                যৌথ গণ-অভিযোগ ও বিশেষ প্রশাসনিক স্মারকলিপি
              </h3>
              <p className="text-[11px] text-zinc-600">
                ভোক্তা অধিকার সংরক্ষণ আইন, ২০০৯ এর ধারা ৪৫, ৪৬ ও ৭৬(১) মোতাবেক
              </p>
            </div>

            <div className="space-y-2 text-zinc-800">
              <p>
                <strong>বরাবর:</strong> মহাপরিচালক, জাতীয় ভোক্তা অধিকার সংরক্ষণ অধিদপ্তর, ঢাকা।
              </p>
              <p>
                <strong>অভিযুক্ত পক্ষ:</strong> {merchantName} ({platform})
              </p>
              <p>
                <strong>একত্রিত ভুক্তভোগী সংখ্যা:</strong> {activeCount} জন নাগরিক (ClaimCraft BD দ্বারা যাচাইকৃত)
              </p>
              <p>
                <strong>দাবিকৃত মোট আত্মসাৎকৃত অর্থ:</strong> ৳{activeTotal.toLocaleString()} টাকা।
              </p>
              <p className="pt-2 text-justify">
                <strong>অভিযোগের মূল বিবরণ:</strong> অভিযুক্ত মার্চেন্ট ডিজিটাল প্ল্যাটফর্ম ও সামাজিক যোগাযোগ মাধ্যমে পণ্যের বিজ্ঞাপন প্রচার করিয়া ভোক্তাগণের নিকট হইতে অগ্রিম অর্থ গ্রহণপূর্বক প্রতিশ্রুত পণ্য ডেলিভারি না করিয়া অথবা ত্রুটিপূর্ণ সামগ্রী সরবরাহ করিয়া যোগাযোগ বিচ্ছিন্ন করিয়াছে। ইহা ভোক্তা অধিকার সংরক্ষণ আইন ২০০৯ এর ৪৫ ধারা অনুসারে দণ্ডনীয় অপরাধ।
              </p>
              <p className="pt-1 text-justify">
                <strong>প্রার্থনা:</strong> অবিলম্বে অভিযুক্ত মার্চেন্টের বিরুদ্ধে ম্যাজিস্ট্রেট টিম গঠন করিয়া মোবাইল কোর্ট পরিচালনা ও ব্যাংক/বিকাশ একাউন্ট সাময়িক জব্দ করিবার আদেশ প্রদান করা হউক এবং আইন অনুযায়ী আদায়কৃত জরিমানার ২৫% অর্থ ভুক্তভোগী ভোক্তাদের মাঝে বণ্টন করা হউক।
              </p>
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="p-4 border-t border-border bg-elevated/70 flex flex-wrap items-center justify-between gap-3 print:hidden">
          <div className="text-xs text-muted-foreground flex items-center gap-1.5">
            <Scale className="w-3.5 h-3.5 text-primary" />
            <span>CRPA 2009 Sec 76(1) Enforceable</span>
          </div>

          <div className="flex items-center gap-2">
            <a
              href={`mailto:complaint@dncrp.gov.bd?cc=dncrp@yahoo.com&subject=${encodeURIComponent(memoSubject)}&body=${encodeURIComponent(memoBody)}`}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-primary/30 bg-primary/10 text-primary text-xs font-semibold hover:bg-primary/20 transition h-8"
            >
              <Mail className="w-3.5 h-3.5" />
              <span>{isBangla ? 'DNCRP-তে ইমেইল' : 'Email DNCRP'}</span>
            </a>

            <Button
              size="sm"
              variant="primary"
              onClick={handlePrint}
              className="text-xs font-bold gap-1.5 h-8"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>{isBangla ? 'প্রিন্ট / PDF সেভ' : 'Print / PDF'}</span>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

