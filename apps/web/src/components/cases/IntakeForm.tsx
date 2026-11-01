'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Mic, Upload, Shield, Loader2, FileText, CheckCircle2, Store, DollarSign } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Textarea } from '@/components/ui/Textarea';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { VoiceNoteRecorder } from '@/components/intake/VoiceNoteRecorder';
import { apiFetch, getClientSessionToken } from '@/lib/api';

interface IntakeFormProps {
  locale: string;
  labels: {
    story_label: string;
    story_hint: string;
    story_placeholder: string;
    title_label: string;
    title_placeholder: string;
    outcome_label: string;
    outcome_refund: string;
    outcome_replacement: string;
    outcome_apology: string;
    attachments_label: string;
    attachments_hint: string;
    privacy_notice: string;
    submit_btn: string;
    submitting_btn: string;
  };
}

export function IntakeForm({ locale, labels }: IntakeFormProps) {
  const router = useRouter();
  const [title, setTitle] = useState('');
  const [merchantName, setMerchantName] = useState('');
  const [disputedAmount, setDisputedAmount] = useState('');
  const [story, setStory] = useState('');
  const [remedy, setRemedy] = useState('full_refund');
  const [inputMode, setInputMode] = useState<'type' | 'voice'>('type');
  const [hasVoiceTranscribed, setHasVoiceTranscribed] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [statusStep, setStatusStep] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const isBangla = locale === 'bn';

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!story.trim()) {
      setErrorMsg(isBangla ? 'অনুগ্রহ করে আপনার ঘটনার বিবরণ লিখুন বা কথা বলে জানান।' : 'Please describe what happened using text or voice.');
      return;
    }

    setIsSubmitting(true);
    setErrorMsg(null);

    try {
      setStatusStep(isBangla ? '১/৩: নিরাপদ কেস সেশন তৈরি হচ্ছে...' : '1/3: Establishing secure case session...');
      // 1. Ensure active guest session and persist token in localStorage
      const token = await getClientSessionToken();

      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      // Determine an intuitive title if blank
      const trimmedMerchant = merchantName.trim();
      const finalTitle =
        title.trim() ||
        (trimmedMerchant
          ? `${trimmedMerchant} ${isBangla ? 'বিরোধ ও প্রতিকার আবেদন' : 'Dispute Claim'}`
          : (isBangla ? 'অনলাইন কেনাকাটা বিরোধ' : 'Consumer Rights Dispute'));

      const todayStr = new Date().toISOString().split('T')[0];

      // 2. Submit case to backend
      const caseRes = await apiFetch('/api/v1/cases', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          title: finalTitle,
          jurisdiction: 'BD',
          locale: locale === 'bn' ? 'bn-BD' : 'en-BD',
          desired_outcomes: [remedy],
          story_narrative: story.trim(),
          merchant_name: trimmedMerchant || undefined,
          incident_date: todayStr,
        }),
      });

      if (!caseRes.ok) {
        const errJson = await caseRes.json().catch(() => ({}));
        throw new Error(errJson.detail?.message || errJson.detail || 'Failed to create case');
      }

      const newCase = await caseRes.json();
      const newCaseId = newCase.id;

      // 3. Automated AI fact & timeline extraction from narrative
      setStatusStep(isBangla ? '২/৩: এআই দিয়ে ঘটনা ও তথ্য বিশ্লেষণ করা হচ্ছে...' : '2/3: AI extracting facts & timeline...');
      try {
        await apiFetch(`/api/v1/cases/${newCaseId}/extract?auto_persist=true`, {
          method: 'POST',
          headers,
        });
      } catch (extErr) {
        console.warn('AI Fact extraction warning:', extErr);
      }

      // 4. If user manually entered amount, persist explicitly
      if (disputedAmount.trim()) {
        try {
          await apiFetch(`/api/v1/cases/${newCaseId}/facts`, {
            method: 'POST',
            headers,
            body: JSON.stringify({
              field_name: 'amount_paid',
              field_type: 'money',
              raw_value: disputedAmount.trim(),
              original_text: disputedAmount.trim(),
              origin: 'user_statement',
            }),
          });
        } catch (amtErr) {
          console.warn('Amount assertion warning:', amtErr);
        }
      }

      // 5. If user manually entered merchant, persist explicitly
      if (trimmedMerchant) {
        try {
          await apiFetch(`/api/v1/cases/${newCaseId}/facts`, {
            method: 'POST',
            headers,
            body: JSON.stringify({
              field_name: 'merchant_name',
              field_type: 'string',
              raw_value: trimmedMerchant,
              original_text: trimmedMerchant,
              origin: 'user_statement',
            }),
          });
        } catch (merchErr) {
          console.warn('Merchant assertion warning:', merchErr);
        }
      }

      setStatusStep(isBangla ? '৩/৩: কেস ড্যাশবোর্ডে প্রবেশ করা হচ্ছে...' : '3/3: Opening your case workspace...');
      router.push(`/${locale}/cases/${newCaseId}`);
    } catch (err: unknown) {
      console.error('Case submission error:', err);
      const msg = err instanceof Error ? err.message : String(err);
      setErrorMsg(isBangla ? `কেস সংরক্ষণ করতে সমস্যা হয়েছে: ${msg}` : `Failed to save case: ${msg}`);
      setIsSubmitting(false);
      setStatusStep(null);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {errorMsg && (
        <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-[var(--radius-control)] text-xs text-red-600 font-medium">
          {errorMsg}
        </div>
      )}

      {/* 1. Dispute Story & Voice Note (Primary Input) */}
      <Card>
        <CardHeader className="pb-3 flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-base font-bold">{labels.story_label}</CardTitle>
            <CardDescription className="text-xs">{labels.story_hint}</CardDescription>
          </div>
          <div className="flex items-center gap-1.5">
            <Button
              type="button"
              variant={inputMode === 'type' ? 'secondary' : 'outline'}
              size="sm"
              onClick={() => setInputMode('type')}
              className="gap-1.5 text-xs h-7"
            >
              <FileText className="w-3.5 h-3.5" />
              <span>{isBangla ? 'টাইপ করুন' : 'Type'}</span>
            </Button>
            <Button
              type="button"
              variant={inputMode === 'voice' ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setInputMode('voice')}
              className="gap-1.5 text-xs h-7"
            >
              <Mic className="w-3.5 h-3.5" />
              <span>{isBangla ? 'ভয়েস নোট' : 'Voice'}</span>
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {inputMode === 'voice' ? (
            <VoiceNoteRecorder
              locale={locale}
              onSwitchToTyping={() => setInputMode('type')}
              onTranscribeSuccess={(transcript) => {
                setStory(transcript);
                setHasVoiceTranscribed(true);
                setInputMode('type');
                if (!title) {
                  setTitle(isBangla ? 'ভয়েস বর্ণনাকৃত অভিযোগ' : 'Voice-Transcribed Complaint');
                }
              }}
            />
          ) : (
            <>
              {hasVoiceTranscribed && (
                <div className="flex items-center gap-2 p-2.5 rounded-[var(--radius-control)] bg-success/10 border border-success/30 text-xs text-success">
                  <CheckCircle2 className="w-4 h-4 shrink-0" />
                  <span>
                    {isBangla
                      ? '🎙️ ভয়েস নোট সফলভাবে টেক্সটে রূপান্তর হয়েছে! প্রয়োজনে নিচের বক্সে সম্পাদনা করুন।'
                      : '🎙️ Voice note transcribed successfully! You can review and edit below.'}
                  </span>
                </div>
              )}
              <Textarea
                rows={5}
                value={story}
                onChange={(e) => setStory(e.target.value)}
                placeholder={labels.story_placeholder}
                required
                className="text-sm font-medium"
              />
            </>
          )}
        </CardContent>
      </Card>

      {/* 2. Structured Details (Merchant & Amount) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Merchant / Seller Name */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
              <Store className="w-3.5 h-3.5 text-primary" />
              <span>{isBangla ? 'বিক্রেতা বা প্রতিষ্ঠানের নাম' : 'Merchant / Seller Name'}</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Input
              value={merchantName}
              onChange={(e) => setMerchantName(e.target.value)}
              placeholder={isBangla ? 'যেমন: চালডাল, দারাজ, অথবা ফেসবুক পেজ' : 'e.g. Chaldal, Daraz, or Facebook page'}
              className="text-xs font-medium"
            />
            <p className="text-[11px] text-muted-foreground mt-1">
              {isBangla ? 'খালি রাখলে বিবরণ থেকে স্বয়ংক্রিয়ভাবে সনাক্ত হবে' : 'Auto-detected from story if left blank'}
            </p>
          </CardContent>
        </Card>

        {/* Disputed Amount */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
              <DollarSign className="w-3.5 h-3.5 text-primary" />
              <span>{isBangla ? 'দাবিকৃত টাকার পরিমাণ (ঐচ্ছিক)' : 'Disputed Amount in BDT'}</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Input
              value={disputedAmount}
              onChange={(e) => setDisputedAmount(e.target.value)}
              placeholder={isBangla ? 'যেমন: ১২০০' : 'e.g. 1200 or 5500'}
              className="text-xs font-medium font-mono"
            />
            <p className="text-[11px] text-muted-foreground mt-1">
              {isBangla ? 'টাকার অঙ্ক জানা থাকলে লিখুন, অন্যথায় বিবরণ থেকে নেওয়া হবে' : 'Enter amount if known, or extracted from story'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Case Title (Optional) */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
            {labels.title_label}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder={labels.title_placeholder}
            className="text-xs font-medium"
          />
        </CardContent>
      </Card>

      {/* 3. Desired Outcome */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-bold">{labels.outcome_label}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2.5">
            <label
              onClick={() => setRemedy('full_refund')}
              className={`inline-flex items-center gap-2 px-3.5 py-2 rounded-[var(--radius-control)] border text-xs font-semibold cursor-pointer transition-colors ${
                remedy === 'full_refund'
                  ? 'border-primary bg-[var(--brand-soft)] text-primary'
                  : 'border-border bg-surface text-foreground hover:bg-elevated'
              }`}
            >
              <input
                type="radio"
                name="remedy"
                checked={remedy === 'full_refund'}
                onChange={() => setRemedy('full_refund')}
                className="accent-primary"
              />
              <span>{labels.outcome_refund}</span>
            </label>

            <label
              onClick={() => setRemedy('replacement')}
              className={`inline-flex items-center gap-2 px-3.5 py-2 rounded-[var(--radius-control)] border text-xs font-semibold cursor-pointer transition-colors ${
                remedy === 'replacement'
                  ? 'border-primary bg-[var(--brand-soft)] text-primary'
                  : 'border-border bg-surface text-foreground hover:bg-elevated'
              }`}
            >
              <input
                type="radio"
                name="remedy"
                checked={remedy === 'replacement'}
                onChange={() => setRemedy('replacement')}
                className="accent-primary"
              />
              <span>{labels.outcome_replacement}</span>
            </label>

            <label
              onClick={() => setRemedy('apology')}
              className={`inline-flex items-center gap-2 px-3.5 py-2 rounded-[var(--radius-control)] border text-xs font-semibold cursor-pointer transition-colors ${
                remedy === 'apology'
                  ? 'border-primary bg-[var(--brand-soft)] text-primary'
                  : 'border-border bg-surface text-foreground hover:bg-elevated'
              }`}
            >
              <input
                type="radio"
                name="remedy"
                checked={remedy === 'apology'}
                onChange={() => setRemedy('apology')}
                className="accent-primary"
              />
              <span>{labels.outcome_apology}</span>
            </label>
          </div>
        </CardContent>
      </Card>

      {/* Privacy Notice & Submit Button */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <Shield className="w-4 h-4 text-primary shrink-0" />
          <span>{labels.privacy_notice}</span>
        </div>

        <div className="w-full sm:w-auto flex flex-col items-end gap-1">
          {statusStep && (
            <span className="text-xs text-primary font-medium animate-pulse">
              {statusStep}
            </span>
          )}
          <Button
            type="submit"
            size="lg"
            variant="primary"
            disabled={isSubmitting}
            className="w-full sm:w-auto font-semibold gap-2 min-h-[44px]"
          >
            {isSubmitting && <Loader2 className="w-4 h-4 animate-spin" />}
            <span>{isSubmitting ? (statusStep || labels.submitting_btn) : labels.submit_btn}</span>
          </Button>
        </div>
      </div>
    </form>
  );
}
