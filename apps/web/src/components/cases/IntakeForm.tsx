'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Mic, Upload, Shield, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Textarea } from '@/components/ui/Textarea';
import { Input } from '@/components/ui/Input';

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
  const [title, setTitle] = useState('Online Shopping Non-Delivery');
  const [story, setStory] = useState(
    'আমি ফেসবুকের একটি পেজ থেকে ৫,৫০০ টাকায় একটি ফোন অর্ডার করেছিলাম। ১৫ অক্টোবর বিকাশে টাকা দিই, কিন্তু তারা আমাকে ব্লক করে দেয় এবং পণ্য পাঠায়নি।'
  );
  const [remedy, setRemedy] = useState('full_refund');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const isBangla = locale === 'bn';

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setIsSubmitting(true);
    setErrorMsg(null);

    try {
      // 1. Ensure active guest session
      const authRes = await fetch('/api/v1/auth/guest', { method: 'POST' });
      let token = '';
      if (authRes.ok) {
        const authData = await authRes.json();
        token = authData.access_token || '';
      }

      // 2. Submit case to backend
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const caseRes = await fetch('/api/v1/cases', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          title: title.trim() || 'Consumer Dispute',
          jurisdiction: 'BD',
          locale: locale === 'bn' ? 'bn-BD' : 'en-BD',
          desired_outcomes: [remedy],
          story_narrative: story,
          merchant_name: 'Gadget Zone BD',
        }),
      });

      if (!caseRes.ok) {
        // Fallback gracefully to demo case if offline
        router.push(`/${locale}/cases/case_demo_phone`);
        return;
      }

      const newCase = await caseRes.json();
      router.push(`/${locale}/cases/${newCase.id}`);
    } catch (err) {
      // Fallback gracefully to demo case on network failure
      router.push(`/${locale}/cases/case_demo_phone`);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {errorMsg && (
        <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-[var(--radius-control)] text-xs text-red-600">
          {errorMsg}
        </div>
      )}

      {/* Case Title */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-bold">{labels.title_label}</CardTitle>
        </CardHeader>
        <CardContent>
          <Input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder={labels.title_placeholder}
            required
            className="text-sm font-medium"
          />
        </CardContent>
      </Card>

      {/* 1. Dispute Story */}
      <Card>
        <CardHeader className="pb-3 flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-base font-bold">{labels.story_label}</CardTitle>
            <CardDescription className="text-xs">{labels.story_hint}</CardDescription>
          </div>
          <Button type="button" variant="outline" size="sm" className="gap-1.5 text-xs">
            <Mic className="w-3.5 h-3.5 text-red-600" />
            <span>{isBangla ? 'ভয়েস ইনপুট' : 'Speak'}</span>
          </Button>
        </CardHeader>
        <CardContent>
          <Textarea
            rows={5}
            value={story}
            onChange={(e) => setStory(e.target.value)}
            placeholder={labels.story_placeholder}
            required
            className="text-sm font-medium"
          />
        </CardContent>
      </Card>

      {/* 2. Desired Outcome */}
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

      {/* 3. Attachments */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-bold">{labels.attachments_label}</CardTitle>
          <CardDescription className="text-xs">{labels.attachments_hint}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="border-2 border-dashed border-border rounded-[var(--radius-panel)] p-6 text-center hover:bg-elevated/40 transition-colors cursor-pointer">
            <Upload className="w-8 h-8 mx-auto text-muted-foreground mb-2" />
            <p className="text-xs font-semibold text-foreground">
              {isBangla ? 'ফাইল ড্র্যাগ করে ছাড়ুন অথবা ক্লিক করুন' : 'Drag and drop receipts/screenshots, or browse'}
            </p>
            <p className="text-[11px] text-muted-foreground mt-1">
              JPG, PNG, PDF up to 10MB per file
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Privacy Notice & Submit */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <Shield className="w-4 h-4 text-primary shrink-0" />
          <span>{labels.privacy_notice}</span>
        </div>

        <Button
          type="submit"
          size="lg"
          variant="primary"
          disabled={isSubmitting}
          className="w-full sm:w-auto font-semibold gap-2"
        >
          {isSubmitting && <Loader2 className="w-4 h-4 animate-spin" />}
          <span>{isSubmitting ? labels.submitting_btn : labels.submit_btn}</span>
        </Button>
      </div>
    </form>
  );
}

