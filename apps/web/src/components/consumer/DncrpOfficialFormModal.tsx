'use client';

import React, { useState, useEffect } from 'react';
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
  Edit3,
  Save,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';

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
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState<DncrpFormData>(data);

  // Sync props data & check user profile in localStorage
  useEffect(() => {
    let initial = { ...data };
    if (typeof window !== 'undefined') {
      try {
        const savedProfile = localStorage.getItem('claimcraft_user_profile');
        if (savedProfile) {
          const profile = JSON.parse(savedProfile);
          if (profile.full_name) initial.complainantName = profile.full_name;
          if (profile.phone) initial.complainantPhone = profile.phone;
          if (profile.nid) initial.complainantNid = profile.nid;
          if (profile.address) initial.complainantAddress = profile.address;
        }
      } catch {
        // ignore storage error
      }
    }
    setFormData(initial);
  }, [data]);

  if (!isOpen) return null;

  const handlePrint = () => {
    if (typeof window !== 'undefined') {
      window.print();
    }
  };

  const emailSubject = `ভোক্তা-অধিকার সংরক্ষণ আইন ২০০৯ অনুসারে অভিযোগ — ${formData.merchantName}-এর বিরুদ্ধে`;
  const emailBody = `বরাবর,\nমহাপরিচালক,\nজাতীয় ভোক্তা অধিকার সংরক্ষণ অধিদপ্তর, ঢাকা।\n\nবিষয়: ${formData.merchantName}-এর বিরুদ্ধে প্রতারণা ও ভোক্তা অধিকার লংঘনের আনুষ্ঠানিক অভিযোগ।\n\nঅভিযোগকারীর বিবরণ:\nনাম: ${formData.complainantName}\nমোবাইল: ${formData.complainantPhone}\nএনআইডি: ${formData.complainantNid}\nঠিকানা: ${formData.complainantAddress}\n\nঅভিযুক্ত মার্চেন্ট:\nনাম: ${formData.merchantName}\nফোন: ${formData.merchantPhone}\nঠিকানা/প্লাটফর্ম: ${formData.merchantAddress}\n\nসংক্ষিপ্ত বিবরণ:\n${formData.productDescription}\nদাবিকৃত অর্থ: ৳${formData.disputedAmountBdt.toLocaleString('bn-BD')} টাকা।\n\nসংযুক্ত প্রমাণাদি:\n${formData.evidenceList.map((e, i) => `${i + 1}. ${e}`).join('\n')}\n\nবিনীত,\n${formData.complainantName}`;

  const handleCopyEmail = () => {
    if (typeof navigator !== 'undefined') {
      navigator.clipboard.writeText(`Subject: ${emailSubject}\n\n${emailBody}`);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleSaveProfile = () => {
    if (typeof window !== 'undefined') {
      try {
        localStorage.setItem(
          'claimcraft_user_profile',
          JSON.stringify({
            full_name: formData.complainantName,
            phone: formData.complainantPhone,
            nid: formData.complainantNid,
            address: formData.complainantAddress,
          })
        );
      } catch {
        // ignore
      }
    }
    setIsEditing(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-fadeIn">
      {/* Modal Container */}
      <div className="relative w-full max-w-4xl bg-surface border border-border shadow-2xl rounded-2xl max-h-[90vh] flex flex-col overflow-hidden animate-scaleUp">
        {/* Modal Toolbar (Screen Only) */}
        <div className="flex flex-wrap items-center justify-between gap-3 px-5 py-4 border-b border-border bg-elevated/70 print:hidden">
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

          <div className="flex flex-wrap items-center gap-2">
            <Button
              size="sm"
              variant={isEditing ? 'primary' : 'outline'}
              onClick={() => {
                if (isEditing) {
                  handleSaveProfile();
                } else {
                  setIsEditing(true);
                }
              }}
              className="text-xs gap-1.5 h-8 font-semibold"
            >
              {isEditing ? <Save className="w-3.5 h-3.5" /> : <Edit3 className="w-3.5 h-3.5" />}
              <span>{isEditing ? (isBangla ? 'সংরক্ষণ করুন' : 'Save Changes') : (isBangla ? 'তথ্য সম্পাদনা' : 'Edit Info')}</span>
            </Button>

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
              href={`mailto:complaint@dncrp.gov.bd?cc=dncrp@yahoo.com&subject=${encodeURIComponent(emailSubject)}&body=${encodeURIComponent(emailBody)}`}
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
              <span>{isBangla ? 'প্রিন্ট / PDF' : 'Print / PDF'}</span>
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

        {/* Inline Editor Drawer (if editing active) */}
        {isEditing && (
          <div className="p-4 bg-primary/5 border-b border-primary/20 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs print:hidden animate-fadeIn">
            <div>
              <label className="text-[11px] font-bold text-foreground block mb-1">
                {isBangla ? 'আপনার নাম:' : 'Complainant Name:'}
              </label>
              <input
                type="text"
                value={formData.complainantName}
                onChange={(e) => setFormData({ ...formData, complainantName: e.target.value })}
                className="w-full p-1.5 rounded-lg border border-border bg-surface text-xs text-foreground"
              />
            </div>
            <div>
              <label className="text-[11px] font-bold text-foreground block mb-1">
                {isBangla ? 'মোবাইল নম্বর:' : 'Phone Number:'}
              </label>
              <input
                type="text"
                value={formData.complainantPhone}
                onChange={(e) => setFormData({ ...formData, complainantPhone: e.target.value })}
                className="w-full p-1.5 rounded-lg border border-border bg-surface text-xs text-foreground"
              />
            </div>
            <div>
              <label className="text-[11px] font-bold text-foreground block mb-1">
                {isBangla ? 'এনআইডি (NID):' : 'National ID (NID):'}
              </label>
              <input
                type="text"
                value={formData.complainantNid}
                onChange={(e) => setFormData({ ...formData, complainantNid: e.target.value })}
                className="w-full p-1.5 rounded-lg border border-border bg-surface text-xs text-foreground"
              />
            </div>
            <div>
              <label className="text-[11px] font-bold text-foreground block mb-1">
                {isBangla ? 'দাবিকৃত অর্থ (৳):' : 'Disputed Sum (BDT):'}
              </label>
              <input
                type="number"
                value={formData.disputedAmountBdt}
                onChange={(e) => setFormData({ ...formData, disputedAmountBdt: Number(e.target.value) })}
                className="w-full p-1.5 rounded-lg border border-border bg-surface text-xs text-foreground"
              />
            </div>
            <div className="sm:col-span-2">
              <label className="text-[11px] font-bold text-foreground block mb-1">
                {isBangla ? 'আপনার ঠিকানা:' : 'Your Address:'}
              </label>
              <input
                type="text"
                value={formData.complainantAddress}
                onChange={(e) => setFormData({ ...formData, complainantAddress: e.target.value })}
                className="w-full p-1.5 rounded-lg border border-border bg-surface text-xs text-foreground"
              />
            </div>
            <div className="sm:col-span-2">
              <label className="text-[11px] font-bold text-foreground block mb-1">
                {isBangla ? 'মার্চেন্টের নাম ও ঠিকানা:' : 'Merchant Name & Channel:'}
              </label>
              <input
                type="text"
                value={formData.merchantName}
                onChange={(e) => setFormData({ ...formData, merchantName: e.target.value })}
                className="w-full p-1.5 rounded-lg border border-border bg-surface text-xs text-foreground"
              />
            </div>
          </div>
        )}

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
                ১ কারওয়ান বাজার (টিসিবি ভবন), ঢাকা-১২১৫ | হটলাইন: ১৬১২১ | ইমেইল: complaint@dncrp.gov.bd
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
              বিষয়: {formData.merchantName}-এর বিরুদ্ধে ভোক্তা অধিকার লংঘন ও প্রতারণার প্রতিকার প্রসঙ্গে।
            </div>

            {/* Section 1: Complainant Details */}
            <div className="mt-6 space-y-2">
              <h4 className="font-bold border-b pb-1 text-zinc-900">১. অভিযোগকারীর বিবরণ:</h4>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>(ক) নাম: <strong>{formData.complainantName}</strong></div>
                <div>(খ) মোবাইল: <strong>{formData.complainantPhone}</strong></div>
                <div>(গ) জাতীয় পরিচয়পত্র (NID): <strong>{formData.complainantNid}</strong></div>
                <div>(ঘ) বর্তমান ঠিকানা: <strong>{formData.complainantAddress}</strong></div>
              </div>
            </div>

            {/* Section 2: Opposite Party (Merchant) Details */}
            <div className="mt-5 space-y-2">
              <h4 className="font-bold border-b pb-1 text-zinc-900">২. অভিযুক্ত ব্যক্তি / প্রতিষ্ঠানের বিবরণ:</h4>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>(ক) প্রতিষ্ঠানের নাম: <strong>{formData.merchantName}</strong></div>
                <div>(খ) ফোন/হোয়াটসঅ্যাপ: <strong>{formData.merchantPhone}</strong></div>
                <div className="col-span-2">(গ) ঠিকানা / ফেসবুক পেইজ / ওয়েবসাইট: <strong>{formData.merchantAddress}</strong></div>
              </div>
            </div>

            {/* Section 3: Grievance & Statutory Violation */}
            <div className="mt-5 space-y-2">
              <h4 className="font-bold border-b pb-1 text-zinc-900">৩. ঘটনার বিবরণ ও অভিযুক্ত অপরাধ:</h4>
              <p className="text-justify text-xs leading-relaxed">
                গত <strong>{formData.incidentDate}</strong> তারিখে আমি অভিযুক্ত প্রতিষ্ঠানের নিকট থেকে <strong>৳{formData.disputedAmountBdt.toLocaleString('bn-BD')}</strong> টাকা মূল্যের পণ্য ক্রয়ের উদ্দেশ্যে চুক্তি করি এবং এমএফএস (বিকাশ/নগদ) মারফত উক্ত অর্থ পরিশোধ করি। কিন্তু অভিযুক্ত প্রতিষ্ঠান প্রতিশ্রুত পণ্য প্রদানে ব্যর্থ হয় এবং পরবর্তীতে যোগাযোগের মাধ্যমগুলোতে আমাকে অবরুদ্ধ (ব্লক) করে দেয়, যা <em>ভোক্তা-অধিকার সংরক্ষণ আইন, ২০০৯</em> এর নিম্নোক্ত ধারাসমূহের চরম লংঘন:
              </p>
              <ul className="list-disc list-inside pl-2 text-xs space-y-1 font-semibold text-zinc-800">
                {formData.statutorySections.map((sec, idx) => (
                  <li key={idx}>{sec}</li>
                ))}
              </ul>
            </div>

            {/* Section 4: Attached Evidentiary Proofs */}
            <div className="mt-5 space-y-2">
              <h4 className="font-bold border-b pb-1 text-zinc-900">৪. সংযুক্ত প্রমাণাদির তালিকা (ডিজিটাল এভিডেন্স ভল্ট):</h4>
              <ol className="list-decimal list-inside pl-2 text-xs space-y-1 text-zinc-800">
                {formData.evidenceList.map((ev, idx) => (
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
                <p className="font-bold">{formData.complainantName}</p>
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
                ? 'অনলাইন সাবমিশন: ফরমটি ডাউনলোড বা ইমেইল কপি করে সরাসরি complaint@dncrp.gov.bd এ পাঠিয়ে দিন।'
                : 'Direct filing: Send this PDF attachment to complaint@dncrp.gov.bd or submit at national consumer office.'}
            </span>
          </div>
          <span className="text-[11px] font-mono text-primary font-bold">
            DNCRP Format-1 Verified
          </span>
        </div>
      </div>
    </div>
  );
}
