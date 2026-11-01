'use client';

import React, { useState } from 'react';
import {
  Truck,
  PackageCheck,
  Video,
  FileCheck,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Copy,
  Check,
  ShieldCheck,
} from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';

export function CourierDisputeProtocol({
  locale = 'en',
  courierName = 'Steadfast Courier',
  trackingId = 'SF-882910-BD',
  className,
}: {
  locale?: string;
  courierName?: string;
  trackingId?: string;
  className?: string;
}) {
  const isBangla = locale === 'bn';
  const [activeStep, setActiveStep] = useState<number>(1);
  const [copied, setCopied] = useState(false);

  const courierHoldMemo = `বরাবর,\nহাব ইন-চার্জ / কাস্টমার সাপোর্ট,\n${courierName}।\n\nবিষয়: ট্র্যাকিং আইডি #${trackingId} এর মার্চেন্ট পেমেন্ট ডিসবার্সমেন্ট সাময়িকভাবে স্থগিতকরণ প্রসঙ্গে।\n\nমহোদয়,\nউক্ত পার্সেলটিতে বিক্রেতা প্রতিশ্রুত পণ্যের পরিবর্তে সম্পূর্ণ ভিন্ন/ত্রুটিপূর্ণ পণ্য পাঠিয়েছে (প্রমাণস্বরূপ আনবক্সিং ভিডিও সংরক্ষিত)।\nভোক্তা অধিকার সংরক্ষণ আইন ২০০৯ অনুসারে এটি তদন্তাধীন। তদন্ত শেষ না হওয়া পর্যন্ত উক্ত ট্র্যাকিং কোডের বিপরীতে মার্চেন্টকে কোনো অর্থ ছাড় না দেওয়ার অনুরোধ জানাচ্ছি।\n\nবিনীত,\nভুক্তভোগী ভোক্তা`;

  const handleCopy = () => {
    if (typeof navigator !== 'undefined') {
      navigator.clipboard.writeText(courierHoldMemo);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const protocols = [
    {
      num: 1,
      titleEn: 'Right to Record Unboxing Video in Presence of Delivery Rider',
      titleBn: 'ডেলিভারি ম্যানের উপস্থিতিতে আনবক্সিং ভিডিও ধারণের আইনি অধিকার',
      icon: Video,
      descEn: 'Under Bangladesh consumer evidentiary standards, continuous unboxing footage showing the sealed label and package opening is 100% admissible proof.',
      descBn: 'সিলগালা প্যাকেটের লেবেল স্পষ্ট রেখে এক টেকে সম্পূর্ণ আনবক্সিং ভিডিও রেকর্ড করুন। এটি আইনি প্রমাণ হিসেবে শতভাগ গ্রহণযোগ্য।',
    },
    {
      num: 2,
      titleEn: 'Retain Courier Rider Memo & Hub Consignment Note',
      titleBn: 'কুরিয়ার মেমো, ট্র্যাকিং আইডি ও রাইডারের ফোন নম্বর সংরক্ষণ',
      icon: FileCheck,
      descEn: 'Take a clear photograph of the paper airway bill attached to the parcel before the rider departs.',
      descBn: 'পার্সেলের গায়ে সাঁটানো স্টিকার বা মেমোর স্পষ্ট ছবি তুলুন। কোনো অবস্থাতে আসল লেবেল নষ্ট বা ফেলে দেওয়া যাবে না।',
    },
    {
      num: 3,
      titleEn: 'Immediate Courier Merchant Payout Hold Notice',
      titleBn: 'কুরিয়ার হাব থেকে মার্চেন্টের ক্যাশআউট আটকানোর আইনি অনুরোধ',
      icon: PackageCheck,
      descEn: 'Couriers usually settle payment to merchants within 24–48 hours. Notifying the courier hub supervisor halts merchant payout.',
      descBn: 'কুরিয়ারগুলো সাধারণত ২৪ থেকে ৪৮ ঘণ্টার মধ্যে মার্চেন্টকে টাকা দেয়। সাথে সাথে হাবে লিখিত অভিযোগ দিলে মার্চেন্ট টাকা ক্যাশআউট করতে পারে না।',
    },
  ];

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
          <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-500 flex items-center justify-center shrink-0">
            <Truck className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm sm:text-base font-bold text-foreground">
                {isBangla
                  ? 'কুরিয়ার ডেলিভারি ও পার্সেল জালিয়াতি প্রতিরোধ প্রটোকল'
                  : 'Courier Delivery & Parcel Fraud Protocol'}
              </h3>
              <Badge variant="brand" className="text-[10px] uppercase font-mono">
                {isBangla ? 'স্টেডফাস্ট / পাঠাও / রেডএক্স' : 'Steadfast • Pathao • RedX'}
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground mt-0.5">
              {isBangla
                ? 'ছেঁড়া, খালি বা ভুল পণ্য ডেলিভারির ক্ষেত্রে টাকা উদ্ধারের সুনির্দিষ্ট পদক্ষেপ'
                : 'Step-by-step evidentiary procedure for courier delivery parcels and mismatched packages'}
            </p>
          </div>
        </div>

        <Button
          size="sm"
          variant="outline"
          onClick={handleCopy}
          className="text-xs gap-1.5 h-8 self-start sm:self-center"
        >
          {copied ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
          <span>{copied ? (isBangla ? 'মেমো কপি হয়েছে' : 'Copied') : (isBangla ? 'কুরিয়ার হোল্ড মেমো কপি' : 'Copy Hold Memo')}</span>
        </Button>
      </div>

      {/* 3 Step Protocol Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5 mt-4">
        {protocols.map((p) => {
          const Icon = p.icon;
          const isActive = activeStep === p.num;

          return (
            <div
              key={p.num}
              onClick={() => setActiveStep(p.num)}
              className={cn(
                'rounded-xl border p-4 cursor-pointer transition-all duration-200 text-xs flex flex-col justify-between',
                isActive
                  ? 'border-indigo-500/40 bg-indigo-500/5 ring-1 ring-indigo-500/20 text-foreground'
                  : 'border-border/60 bg-surface hover:bg-elevated/40 text-muted-foreground'
              )}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="w-6 h-6 rounded-full bg-elevated border font-mono text-[11px] font-bold flex items-center justify-center text-foreground">
                    {p.num}
                  </span>
                  <Icon className="w-4 h-4 text-indigo-500" />
                </div>
                <h4 className="font-bold text-foreground text-xs leading-snug mb-1.5">
                  {isBangla ? p.titleBn : p.titleEn}
                </h4>
                <p className="text-[11px] text-muted-foreground leading-relaxed">
                  {isBangla ? p.descBn : p.descEn}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

