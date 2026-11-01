'use client';

import React, { useState, useEffect } from 'react';
import {
  AlertCircle,
  AlertTriangle,
  ArrowRight,
  Bell,
  Calendar,
  Check,
  CheckCircle2,
  Clock,
  ExternalLink,
  GitCompare,
  Layers,
  Lock,
  Plus,
  RefreshCw,
  ShieldAlert,
  Trash2,
} from 'lucide-react';

import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';

interface SemanticDiff {
  prior_version: number;
  new_version: number;
  prior_primary_action: string;
  new_primary_action: string;
  is_decision_changed: boolean;
  changed_routes: Array<{ issue_type: string; old_status: string | null; new_status: string }>;
  unchanged_routes: string[];
  changed_actions: string[];
  unchanged_actions: string[];
}

interface TimelineEvent {
  id: string;
  case_id: string;
  event_sequence: number;
  event_type: string;
  actor_type: string;
  origin: string; // 'user_reported', 'official_receipt', 'system_event'
  title: string;
  description: string;
  reference_number?: string | null;
  created_at: string;
  decision_diff?: SemanticDiff | null;
}

interface Reminder {
  id: string;
  case_id: string;
  reminder_title: string;
  remind_at: string;
  category: string;
  notes?: string | null;
  is_completed: boolean;
  is_legal_caution: boolean;
  disclaimer_notice: string;
  created_at: string;
}

interface Props {
  caseId: string;
  locale: string;
}

export function LivingCaseActivityClient({ caseId, locale }: Props) {
  const isBangla = locale === 'bn';

  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [currentVersion, setCurrentVersion] = useState<number>(1);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Modal / Form state
  const [isUpdateModalOpen, setIsUpdateModalOpen] = useState<boolean>(false);
  const [updateType, setUpdateType] = useState<string>('seller_response');
  const [authorityOrChannel, setAuthorityOrChannel] = useState<string>('merchant_direct');
  const [referenceNumber, setReferenceNumber] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [factFlag, setFactFlag] = useState<string>('none');
  const [isSubmittingUpdate, setIsSubmittingUpdate] = useState<boolean>(false);
  const [staleTabError, setStaleTabError] = useState<string | null>(null);

  // Reminder form state
  const [isReminderFormOpen, setIsReminderFormOpen] = useState<boolean>(false);
  const [reminderTitle, setReminderTitle] = useState<string>('');
  const [remindAtDate, setRemindAtDate] = useState<string>('');
  const [reminderCategory, setReminderCategory] = useState<string>('personal_follow_up');
  const [reminderNotes, setReminderNotes] = useState<string>('');
  const [isSubmittingReminder, setIsSubmittingReminder] = useState<boolean>(false);

  async function loadData() {
    setIsLoading(true);
    setStaleTabError(null);
    try {
      const [caseRes, timelineRes, remindersRes] = await Promise.all([
        fetch(`/api/v1/cases/${caseId}`),
        fetch(`/api/v1/cases/${caseId}/activity/timeline`),
        fetch(`/api/v1/cases/${caseId}/reminders`),
      ]);

      if (caseRes.ok) {
        const c = await caseRes.json();
        setCurrentVersion(c.row_version);
      }
      if (timelineRes.ok) setTimeline(await timelineRes.json());
      if (remindersRes.ok) setReminders(await remindersRes.json());
    } catch (e) {
      console.error('Failed to load living activity data', e);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, [caseId]);

  const handleRecordUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmittingUpdate(true);
    setStaleTabError(null);

    const additional_facts: Record<string, any> = {};
    if (factFlag === 'seller_refused') {
      additional_facts['seller_refused_refund'] = true;
    } else if (factFlag === 'provider_ticket_obtained') {
      additional_facts['provider_ticket_filed'] = true;
      if (referenceNumber) additional_facts['provider_ticket_number'] = referenceNumber;
    }

    try {
      const res = await fetch(`/api/v1/cases/${caseId}/activity/updates`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          update_type: updateType,
          authority_or_channel: authorityOrChannel,
          description,
          reference_number: referenceNumber ? referenceNumber.trim() : null,
          additional_facts,
          expected_version: currentVersion, // T41: Stale tab race prevention
        }),
      });

      if (res.status === 409) {
        setStaleTabError(
          isBangla
            ? 'অন্য উইন্ডোতে কেসটি আপডেট করা হয়েছে। সর্বশেষ তথ্য পেতে রিফ্রেশ করুন (T41)।'
            : 'This case has been modified in another session. Please reload to prevent stale overwrites (T41).'
        );
        return;
      }

      if (res.ok) {
        setIsUpdateModalOpen(false);
        setDescription('');
        setReferenceNumber('');
        setFactFlag('none');
        await loadData();
      }
    } catch (err) {
      console.error('Failed to record external update', err);
    } finally {
      setIsSubmittingUpdate(false);
    }
  };

  const handleCreateReminder = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reminderTitle || !remindAtDate) return;
    setIsSubmittingReminder(true);

    try {
      const res = await fetch(`/api/v1/cases/${caseId}/reminders`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          reminder_title: reminderTitle,
          remind_at: new Date(remindAtDate).toISOString(),
          category: reminderCategory,
          notes: reminderNotes || null,
        }),
      });

      if (res.ok) {
        setIsReminderFormOpen(false);
        setReminderTitle('');
        setRemindAtDate('');
        setReminderNotes('');
        await loadData();
      }
    } catch (err) {
      console.error('Failed to create reminder', err);
    } finally {
      setIsSubmittingReminder(false);
    }
  };

  const handleDeleteReminder = async (id: string) => {
    try {
      const res = await fetch(`/api/v1/cases/${caseId}/reminders/${id}`, {
        method: 'DELETE',
      });
      if (res.ok) {
        setReminders(reminders.filter((r) => r.id !== id));
      }
    } catch (err) {
      console.error('Failed to cancel reminder', err);
    }
  };

  if (isLoading) {
    return (
      <Card className="border border-border p-8 text-center bg-surface">
        <RefreshCw className="w-8 h-8 animate-spin mx-auto text-primary mb-3" />
        <p className="text-sm font-medium text-muted-foreground">
          {isBangla ? 'কেস টাইমলাইন লোড হচ্ছে...' : 'Loading Living Case Timeline...'}
        </p>
      </Card>
    );
  }

  return (
    <div className="space-y-8">
      {/* Stale Tab Alert (T41) */}
      {staleTabError && (
        <div className="p-4 rounded-lg bg-red-50 dark:bg-red-950/40 border border-red-300 dark:border-red-800 text-red-900 dark:text-red-200 flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-semibold">
            <AlertCircle className="w-4 h-4 shrink-0 text-red-600" />
            <span>{staleTabError}</span>
          </div>
          <Button size="sm" variant="outline" onClick={loadData} className="text-xs h-8">
            <RefreshCw className="w-3.5 h-3.5 mr-1" />
            <span>{isBangla ? 'রিফ্রেশ করুন' : 'Reload Latest'}</span>
          </Button>
        </div>
      )}

      {/* Action Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-lg border border-border bg-surface">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-bold text-foreground">
              {isBangla ? 'কেস কার্যক্রম ও টাইমলাইন' : 'Living Case Milestones & Timeline'}
            </h3>
            <Badge variant="neutral">v{currentVersion}</Badge>
          </div>
          <p className="text-xs text-muted-foreground mt-0.5">
            {isBangla
              ? 'বিক্রেতার জবাব, সরকারি পোর্টালে দাখিল বা নিষ্পত্তির অগ্রগতি রেকর্ড করুন।'
              : 'Track seller replies, official portal filings, and procedural reassessment (T38, T39).'}
          </p>
        </div>

        <div className="flex gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => setIsReminderFormOpen(!isReminderFormOpen)}
            className="text-xs gap-1.5"
          >
            <Bell className="w-3.5 h-3.5" />
            <span>{isBangla ? 'রিমাইন্ডার সেট করুন' : 'Set Reminder'}</span>
          </Button>

          <Button
            size="sm"
            variant="primary"
            onClick={() => setIsUpdateModalOpen(true)}
            className="text-xs gap-1.5"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>{isBangla ? 'নতুন আপডেট যোগ করুন' : 'Record External Update'}</span>
          </Button>
        </div>
      </div>

      {/* 1. In-App Personal Reminders Section (P10.4 & T40) */}
      {(isReminderFormOpen || reminders.length > 0) && (
        <Card className="border border-border bg-surface">
          <CardHeader className="pb-3 flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-sm font-bold text-foreground flex items-center gap-2">
                <Bell className="w-4 h-4 text-primary" />
                <span>{isBangla ? 'ব্যক্তিগত ফলো-আপ রিমাইন্ডার (T40)' : 'Personal Follow-Up Reminders (T40)'}</span>
              </CardTitle>
              <CardDescription className="text-xs mt-0.5">
                {isBangla
                  ? 'ব্যক্তিগত ট্র্যাকিংয়ের সুবিধার্থে। ৬০ ধারার আইনি তামাদির সময়সীমা পরিবর্তন করে না।'
                  : 'Timezone-safe personal alerts. Distinct from statutory limitation under Section 60.'}
              </CardDescription>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Reminder Form */}
            {isReminderFormOpen && (
              <form onSubmit={handleCreateReminder} className="p-3 rounded-md border border-border bg-elevated/40 space-y-3">
                <div className="grid gap-3 sm:grid-cols-2">
                  <div>
                    <label className="text-[11px] font-bold text-muted-foreground uppercase">
                      {isBangla ? 'রিমাইন্ডারের শিরোনাম' : 'Reminder Title'}
                    </label>
                    <input
                      type="text"
                      required
                      value={reminderTitle}
                      onChange={(e) => setReminderTitle(e.target.value)}
                      placeholder={isBangla ? 'যেমন: বিক্রেতার রিপ্লাই যাচাই' : 'e.g., Check seller WhatsApp reply'}
                      className="w-full text-xs p-2 rounded border border-border bg-surface text-foreground mt-1"
                    />
                  </div>
                  <div>
                    <label className="text-[11px] font-bold text-muted-foreground uppercase">
                      {isBangla ? 'ফলো-আপের তারিখ ও সময়' : 'Follow-Up Date & Time'}
                    </label>
                    <input
                      type="datetime-local"
                      required
                      value={remindAtDate}
                      onChange={(e) => setRemindAtDate(e.target.value)}
                      className="w-full text-xs p-2 rounded border border-border bg-surface text-foreground mt-1"
                    />
                  </div>
                </div>

                <div className="flex justify-end gap-2 pt-2">
                  <Button
                    type="button"
                    size="sm"
                    variant="ghost"
                    onClick={() => setIsReminderFormOpen(false)}
                    className="text-xs h-8"
                  >
                    {isBangla ? 'বাতিল' : 'Cancel'}
                  </Button>
                  <Button
                    type="submit"
                    size="sm"
                    variant="primary"
                    disabled={isSubmittingReminder}
                    className="text-xs h-8"
                  >
                    {isSubmittingReminder
                      ? isBangla
                        ? 'সংরক্ষণ হচ্ছে...'
                        : 'Saving...'
                      : isBangla
                      ? 'রিমাইন্ডার সংরক্ষণ'
                      : 'Save Reminder'}
                  </Button>
                </div>
              </form>
            )}

            {/* Active Reminders List */}
            {reminders.length > 0 ? (
              <div className="grid gap-2 sm:grid-cols-2">
                {reminders.map((r) => (
                  <div
                    key={r.id}
                    className="p-3 rounded-md border border-border bg-elevated/20 flex items-start justify-between gap-3"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-foreground">{r.reminder_title}</span>
                        <Badge variant="brand">{r.category.replace('_', ' ')}</Badge>
                      </div>
                      <div className="flex items-center gap-1.5 text-[11px] text-muted-foreground">
                        <Calendar className="w-3.5 h-3.5 text-primary" />
                        <span>{new Date(r.remind_at).toLocaleString()}</span>
                      </div>
                    </div>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleDeleteReminder(r.id)}
                      className="text-xs h-7 px-2 text-muted-foreground hover:text-red-600"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </Button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-muted-foreground italic">
                {isBangla ? 'কোনো সক্রিয় রিমাইন্ডার নেই।' : 'No active reminders.'}
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* 2. Chronological Living Timeline (P10.1 & T38) */}
      <Card className="border border-border bg-surface">
        <CardContent className="p-6">
          {timeline.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground space-y-2">
              <Clock className="w-8 h-8 mx-auto text-muted-foreground/60" />
              <p className="text-xs font-medium">
                {isBangla
                  ? 'এখনও কোনো বহিরাগত আপডেট রেকর্ড করা হয়নি।'
                  : 'No external updates recorded yet. Did the seller reply or did you file a complaint?'}
              </p>
            </div>
          ) : (
            <div className="relative pl-6 border-l-2 border-border space-y-8">
              {timeline.map((event) => {
                const isUserReported = event.origin === 'user_reported';
                const hasDiff = event.decision_diff && event.decision_diff.is_decision_changed;

                return (
                  <div key={event.id} className="relative">
                    <span
                      className={`absolute -left-[31px] top-1 w-3 h-3 rounded-full ${
                        isUserReported ? 'bg-amber-500' : 'bg-primary'
                      }`}
                    />

                    <div className="space-y-2">
                      <div className="flex flex-wrap items-center gap-2">
                        <Badge variant={isUserReported ? 'warning' : 'neutral'}>
                          {isUserReported
                            ? isBangla
                              ? 'ব্যবহারকারীর নিজস্ব রিপোর্ট (T38)'
                              : 'User-Reported Milestone (T38)'
                            : event.event_type.replace('_', ' ')}
                        </Badge>

                        <span className="text-[11px] font-mono text-muted-foreground">
                          {new Date(event.created_at).toLocaleString()}
                        </span>
                      </div>

                      <h4 className="text-sm font-bold text-foreground">{event.title}</h4>
                      <p className="text-xs text-muted-foreground leading-relaxed">
                        {event.description}
                      </p>

                      {/* Reference Number if attached */}
                      {event.reference_number && (
                        <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-elevated border border-border text-[11px] font-mono text-foreground">
                          <Lock className="w-3 h-3 text-primary" />
                          <span>Ref: {event.reference_number}</span>
                        </div>
                      )}

                      {/* Semantic Decision Diff Card (P10.2 & T39) */}
                      {hasDiff && event.decision_diff && (
                        <div className="p-3.5 rounded-md bg-primary/5 border border-primary/20 space-y-2.5 mt-2">
                          <div className="flex items-center gap-1.5 text-xs font-bold text-primary">
                            <GitCompare className="w-3.5 h-3.5" />
                            <span>
                              {isBangla
                                ? 'আইনি সিদ্ধান্তের পরিবর্তন ও পথ রূপান্তর (T39)'
                                : 'Procedural Decision Transition (T39)'}
                            </span>
                          </div>

                          <div className="text-xs space-y-1">
                            <div className="flex items-center gap-2 text-foreground font-medium">
                              <span className="text-muted-foreground">
                                {event.decision_diff.prior_primary_action}
                              </span>
                              <ArrowRight className="w-3.5 h-3.5 text-primary" />
                              <span className="font-bold text-primary">
                                {event.decision_diff.new_primary_action}
                              </span>
                            </div>

                            {event.decision_diff.changed_routes.map((cr, i) => (
                              <p key={i} className="text-[11px] text-muted-foreground">
                                • Route <strong>{cr.issue_type}</strong> transitioned to{' '}
                                <span className="font-bold text-emerald-600">{cr.new_status}</span>
                              </p>
                            ))}

                            {event.decision_diff.unchanged_routes.length > 0 && (
                              <p className="text-[11px] text-muted-foreground italic">
                                Stable unimpacted routes:{' '}
                                {event.decision_diff.unchanged_routes.join(', ')}
                              </p>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* 3. Record External Update Modal / Drawer */}
      {isUpdateModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4">
          <Card className="w-full max-w-lg border border-border bg-surface shadow-2xl">
            <CardHeader className="pb-3">
              <CardTitle className="text-base font-bold text-foreground">
                {isBangla ? 'বাইরের অগ্রগতি বা বিক্রেতার উত্তর রেকর্ড করুন' : 'Record External Milestone or Response'}
              </CardTitle>
              <CardDescription className="text-xs mt-1">
                {isBangla
                  ? 'বিক্রেতার জবাব বা পোর্টালে দাখিলের ট্র্যাকিং নম্বর রেকর্ড করুন। তথ্যের উৎস ব্যবহারকারীর নিজস্ব রিপোর্ট হিসেবে চিহ্নিত থাকবে (T38)।'
                  : 'Document seller responses or portal submission tracking numbers. Origin is strictly recorded as user-reported (T38).'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleRecordUpdate} className="space-y-4">
                <div className="grid gap-3 sm:grid-cols-2">
                  <div>
                    <label className="text-[11px] font-bold text-muted-foreground uppercase">
                      {isBangla ? 'আপডেটের ধরন' : 'Update Category'}
                    </label>
                    <select
                      value={updateType}
                      onChange={(e) => setUpdateType(e.target.value)}
                      className="w-full text-xs p-2 rounded border border-border bg-surface text-foreground mt-1"
                    >
                      <option value="seller_response">Seller Response / Offer</option>
                      <option value="portal_submission">Official Portal Filing</option>
                      <option value="hearing_notice">Mediation / Hearing Notice</option>
                      <option value="settlement_reached">Settlement / Refund Received</option>
                    </select>
                  </div>

                  <div>
                    <label className="text-[11px] font-bold text-muted-foreground uppercase">
                      {isBangla ? 'মাধ্যম বা কর্তৃপক্ষ' : 'Authority or Channel'}
                    </label>
                    <select
                      value={authorityOrChannel}
                      onChange={(e) => setAuthorityOrChannel(e.target.value)}
                      className="w-full text-xs p-2 rounded border border-border bg-surface text-foreground mt-1"
                    >
                      <option value="merchant_direct">Merchant Direct (WhatsApp/Email/Call)</option>
                      <option value="dncrp_ccms">DNCRP CCMS Portal</option>
                      <option value="bb_cipc">Bangladesh Bank CIPC</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="text-[11px] font-bold text-muted-foreground uppercase">
                    {isBangla ? 'অফিশিয়াল ট্র্যাকিং / অভিযোগ নম্বর (ঐচ্ছিক)' : 'Tracking / Complaint Reference (Optional)'}
                  </label>
                  <input
                    type="text"
                    value={referenceNumber}
                    onChange={(e) => setReferenceNumber(e.target.value)}
                    placeholder="e.g., DNCRP-2026-DH-XXXXX or TKT-XXXX"
                    className="w-full text-xs p-2 rounded border border-border bg-surface text-foreground mt-1"
                  />
                </div>

                <div>
                  <label className="text-[11px] font-bold text-muted-foreground uppercase">
                    {isBangla ? 'ঘটনার বিবরণ' : 'Event Description'}
                  </label>
                  <textarea
                    required
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder={
                      isBangla
                        ? 'বিক্রেতা কী বলেছেন বা সরকারি পোর্টালে কী স্ট্যাটাস দেখিয়েছে লিখুন...'
                        : 'Describe what the seller said or the status shown on the official portal...'
                    }
                    className="w-full text-xs p-2 rounded border border-border bg-surface text-foreground mt-1 min-h-[70px]"
                  />
                </div>

                {/* Counterfactual fact triggers */}
                <div>
                  <label className="text-[11px] font-bold text-muted-foreground uppercase">
                    {isBangla ? 'সম্পর্কিত তথ্য পরিবর্তন' : 'Trigger Fact Transition (Optional)'}
                  </label>
                  <select
                    value={factFlag}
                    onChange={(e) => setFactFlag(e.target.value)}
                    className="w-full text-xs p-2 rounded border border-border bg-surface text-foreground mt-1"
                  >
                    <option value="none">No substantive fact change</option>
                    <option value="seller_refused">Seller officially refused refund / delivery</option>
                    <option value="provider_ticket_obtained">Stage 1 provider dispute ticket filed</option>
                  </select>
                </div>

                <div className="flex justify-end gap-2 pt-3 border-t border-border">
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => setIsUpdateModalOpen(false)}
                    className="text-xs"
                  >
                    {isBangla ? 'বাতিল' : 'Cancel'}
                  </Button>
                  <Button
                    type="submit"
                    variant="primary"
                    size="sm"
                    disabled={isSubmittingUpdate}
                    className="text-xs"
                  >
                    {isSubmittingUpdate
                      ? isBangla
                        ? 'সংরক্ষণ হচ্ছে...'
                        : 'Saving...'
                      : isBangla
                      ? 'সংরক্ষণ করুন'
                      : 'Record Milestone'}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

