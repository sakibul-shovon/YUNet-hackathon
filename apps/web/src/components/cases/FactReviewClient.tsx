'use client';

import React, { useState, useEffect } from 'react';
import { Check, Edit3, HelpCircle, X, Shield, RefreshCw, AlertCircle, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Input } from '@/components/ui/Input';
import { apiFetch } from '@/lib/api';

interface FactItem {
  id: string;
  field_name: string;
  field_type: string;
  typed_value: any;
  original_text: string;
  origin: string;
  is_active: boolean;
  created_at: string;
}

interface FactReviewClientProps {
  caseId: string;
  locale: string;
  initialRemedy?: string;
}

export function FactReviewClient({ caseId, locale, initialRemedy = 'full_refund' }: FactReviewClientProps) {
  const isBangla = locale === 'bn';
  const [facts, setFacts] = useState<FactItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [correctionValue, setCorrectionValue] = useState('');
  const [correctionRationale, setCorrectionRationale] = useState('');
  const [desiredRemedy, setDesiredRemedy] = useState<string>(initialRemedy);
  const [savingRemedy, setSavingRemedy] = useState(false);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  const remedies = [
    { id: 'full_refund', label_en: 'Full Refund', label_bn: 'সম্পূর্ণ টাকা ফেরত' },
    { id: 'replacement', label_en: 'Replacement of Goods', label_bn: 'পণ্য প্রতিস্থাপন' },
    { id: 'repair', label_en: 'Free Repair / Remedy', label_bn: 'বিনামূল্যে মেরামত' },
    { id: 'partial_refund', label_en: 'Partial Compensation', label_bn: 'আংশিক ক্ষতিপূরণ' },
    { id: 'apology', label_en: 'Formal Written Apology', label_bn: 'লিখিত ক্ষমা প্রার্থনা' },
  ];

  const fetchFacts = async () => {
    try {
      setLoading(true);
      const res = await apiFetch(`/api/v1/cases/${caseId}/facts`);
      if (res.ok) {
        const data = await res.json();
        setFacts(data);
      }
    } catch {
      // Fallback
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFacts();
  }, [caseId]);

  const handleReview = async (assertionId: string, outcome: 'accepted' | 'corrected' | 'rejected' | 'unsure') => {
    try {
      const payload: any = { review_outcome: outcome };
      if (outcome === 'corrected') {
        payload.corrected_value = correctionValue;
        payload.corrected_original_text = correctionValue;
        payload.rationale = correctionRationale || 'User manual correction';
      }

      const res = await apiFetch(`/api/v1/cases/${caseId}/facts/${assertionId}/review`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        setEditingId(null);
        setCorrectionValue('');
        setCorrectionRationale('');
        setActionSuccess(
          isBangla
            ? `তথ্যের মূল্যায়ন সম্পন্ন হয়েছে (${outcome})`
            : `Fact review recorded (${outcome})`
        );
        setTimeout(() => setActionSuccess(null), 3000);
        await fetchFacts();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleRemedyChange = async (remedyId: string) => {
    setDesiredRemedy(remedyId);
    setSavingRemedy(true);
    try {
      await apiFetch(`/api/v1/cases/${caseId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ desired_outcomes: [remedyId] }),
      });
    } catch (err) {
      console.error(err);
    } finally {
      setSavingRemedy(false);
    }
  };

  const getDisplayValue = (fact: FactItem) => {
    if (fact.field_type === 'money' && fact.typed_value?.minor_units !== undefined) {
      const bdt = (fact.typed_value.minor_units / 100).toFixed(2);
      return `৳ ${bdt} BDT`;
    }
    if (fact.field_type === 'date' && fact.typed_value?.date) {
      return fact.typed_value.date;
    }
    if (typeof fact.typed_value === 'boolean') {
      return fact.typed_value
        ? (isBangla ? 'হ্যাঁ (সত্য)' : 'True / Yes')
        : (isBangla ? 'না (মিথ্যা/অপ্রাপ্ত)' : 'False / No');
    }
    return String(fact.typed_value);
  };

  return (
    <div className="space-y-8">
      {/* Desired Remedy Selector */}
      <Card className="border-brand/30 bg-surface">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base font-bold flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-brand" />
              <span>{isBangla ? 'আপনার কাঙ্ক্ষিত প্রতিকার নির্বাচন করুন' : 'Select Your Desired Remedy'}</span>
            </CardTitle>
            {savingRemedy && (
              <span className="text-[11px] text-muted-foreground animate-pulse">
                {isBangla ? 'সংরক্ষণ করা হচ্ছে...' : 'Saving...'}
              </span>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5">
            {remedies.map((rem) => {
              const isSelected = desiredRemedy === rem.id;
              return (
                <button
                  key={rem.id}
                  type="button"
                  onClick={() => handleRemedyChange(rem.id)}
                  className={`flex items-center justify-between p-3 rounded-lg border text-left text-xs transition-all ${
                    isSelected
                      ? 'border-brand bg-brand/10 text-brand-foreground font-semibold shadow-sm'
                      : 'border-border bg-canvas hover:border-brand/50 text-foreground'
                  }`}
                >
                  <span>{isBangla ? rem.label_bn : rem.label_en}</span>
                  {isSelected && <Check className="w-4 h-4 text-brand" />}
                </button>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Action Notification */}
      {actionSuccess && (
        <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400 rounded-lg text-xs flex items-center gap-2">
          <Check className="w-4 h-4" />
          <span>{actionSuccess}</span>
        </div>
      )}

      {/* Facts Review List */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground">
            {isBangla ? 'দাবিকৃত তথ্যের সত্যাসত্য পর্যালোচনা' : 'Extracted Claims & Facts Review'}
          </h2>
          <Button size="sm" variant="ghost" onClick={fetchFacts} className="text-xs gap-1.5">
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>{isBangla ? 'রিফ্রেশ' : 'Refresh'}</span>
          </Button>
        </div>

        {facts.length === 0 && !loading && (
          <div className="p-8 text-center border border-dashed rounded-lg bg-canvas text-muted-foreground text-xs">
            {isBangla
              ? 'এই কেসে এখনও পর্যালোচনার জন্য কোনো তথ্য পাওয়া যায়নি।'
              : 'No extracted facts currently pending review for this case.'}
          </div>
        )}

        {facts.map((fact) => {
          const isEditing = editingId === fact.id;

          return (
            <Card key={fact.id} className="border border-border bg-surface">
              <CardHeader className="pb-2 flex flex-row items-start justify-between">
                <div>
                  <div className="flex flex-wrap items-center gap-2 mb-1">
                    <span className="text-[11px] font-mono text-muted-foreground uppercase">
                      {fact.field_name.replace(/_/g, ' ')}
                    </span>
                    <Badge variant="neutral" className="text-[10px]">
                      {fact.origin}
                    </Badge>
                    {/* T09 Invariant: Clear non-inflated verification tag */}
                    <Badge variant="neutral" className="text-[10px] text-muted-foreground border border-border">
                      <Shield className="w-3 h-3 mr-1 text-muted-foreground" />
                      <span>{isBangla ? 'বাহ্যিক যাচাই: হয়নি (ব্যবহারকারীর বক্তব্য)' : 'External Verification: None (User Statement)'}</span>
                    </Badge>
                  </div>
                  <CardTitle className="text-base font-bold text-foreground">
                    {getDisplayValue(fact)}
                  </CardTitle>
                </div>
              </CardHeader>
              <CardContent className="space-y-3 pt-1 text-xs">
                {/* Verbatim quote from original story */}
                <div className="p-2.5 rounded bg-canvas border border-border text-muted-foreground text-[11px]">
                  <span className="font-semibold block text-[10px] uppercase text-muted-foreground mb-0.5">
                    {isBangla ? 'মূল বক্তব্য / উদ্ধৃতি:' : 'Verbatim Span Quote:'}
                  </span>
                  &ldquo;{fact.original_text}&rdquo;
                </div>

                {isEditing ? (
                  <div className="p-3 bg-elevated/40 border border-brand/40 rounded-lg space-y-2.5">
                    <div>
                      <label className="text-[11px] font-semibold block text-foreground mb-1">
                        {isBangla ? 'সঠিক মান লিখুন:' : 'Enter Corrected Value:'}
                      </label>
                      <Input
                        value={correctionValue}
                        onChange={(e) => setCorrectionValue(e.target.value)}
                        placeholder={isBangla ? 'যেমন: ৫,০০০ টাকা' : 'e.g. 5000 BDT'}
                        className="text-xs"
                      />
                    </div>
                    <div>
                      <label className="text-[11px] font-semibold block text-foreground mb-1">
                        {isBangla ? 'সংশোধনের কারণ (ঐচ্ছিক):' : 'Correction Reason (Optional):'}
                      </label>
                      <Input
                        value={correctionRationale}
                        onChange={(e) => setCorrectionRationale(e.target.value)}
                        placeholder={isBangla ? 'রসিদ অনুযায়ী' : 'According to memo / SMS'}
                        className="text-xs"
                      />
                    </div>
                    <div className="flex gap-2 pt-1">
                      <Button
                        size="sm"
                        variant="primary"
                        onClick={() => handleReview(fact.id, 'corrected')}
                        disabled={!correctionValue.trim()}
                        className="text-xs"
                      >
                        {isBangla ? 'সংরক্ষণ করুন' : 'Save Correction'}
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => setEditingId(null)}
                        className="text-xs"
                      >
                        {isBangla ? 'বাতিল' : 'Cancel'}
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-wrap items-center gap-2 pt-1">
                    <Button
                      size="sm"
                      variant="primary"
                      onClick={() => handleReview(fact.id, 'accepted')}
                      className="gap-1.5 text-xs"
                    >
                      <Check className="w-3.5 h-3.5" />
                      <span>{isBangla ? 'সঠিক নিশ্চিত করুন' : 'Confirm Correct'}</span>
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        setEditingId(fact.id);
                        setCorrectionValue(String(fact.typed_value?.minor_units ? (fact.typed_value.minor_units / 100) : fact.original_text));
                      }}
                      className="gap-1.5 text-xs"
                    >
                      <Edit3 className="w-3.5 h-3.5" />
                      <span>{isBangla ? 'সংশোধন' : 'Correct'}</span>
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleReview(fact.id, 'rejected')}
                      className="gap-1.5 text-xs text-rose-600 dark:text-rose-400"
                    >
                      <X className="w-3.5 h-3.5" />
                      <span>{isBangla ? 'প্রত্যাখ্যান' : 'Reject'}</span>
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleReview(fact.id, 'unsure')}
                      className="gap-1.5 text-xs text-muted-foreground"
                    >
                      <HelpCircle className="w-3.5 h-3.5" />
                      <span>{isBangla ? 'নিশ্চিত নই' : 'Unsure'}</span>
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
