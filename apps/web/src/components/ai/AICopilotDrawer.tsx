'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Sparkles,
  MessageSquare,
  X,
  Send,
  Scale,
  ArrowRight,
  ShieldAlert,
  Bot,
  User,
  RefreshCw,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { apiFetch } from '@/lib/api';

interface CopilotMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  statute?: string | null;
  actions?: Array<{
    id: string;
    label_en: string;
    label_bn: string;
    action_type: string;
    payload: string;
  }>;
}

interface AICopilotDrawerProps {
  locale: string;
}

export function AICopilotDrawer({ locale }: AICopilotDrawerProps) {
  const isBangla = locale === 'bn';
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const initialMessages: CopilotMessage[] = [
    {
      id: 'm-welcome',
      sender: 'assistant',
      text: isBangla
        ? 'আসসালামু আলাইকুম! আমি আপনার এবার কি? (EbarKi) এআই সহকারী। অনলাইন কেনাকাটা, বিকাশ/নগদ পেমেন্ট, কুরিয়ার বা ওয়ারেন্টি সংক্রান্ত যে কোনো সমস্যার কথা আমাকে জানান। আমি আপনাকে সঠিক আইনি সমাধান ও আবেদনপত্র প্রস্তুত করে দেব।'
        : 'Hello! I am your EbarKi AI Dispute Copilot. Tell me about your consumer issue (e.g. non-delivery, payment deduction, or defective warranty), and I will guide you with exact statutory rights under Bangladesh Law.',
      actions: [
        {
          id: 'quick-1',
          label_en: 'Paid advance but goods not delivered',
          label_bn: 'অগ্রিম দিয়েছি কিন্তু পণ্য ডেলিভারি হয়নি',
          action_type: 'prompt',
          payload: isBangla ? 'দারাজে অগ্রিম পেমেন্ট করেছিলাম, ডেলিভারি ডেট পার হয়ে গেলেও পণ্য পাইনি' : 'I ordered online and paid in advance, but goods were never delivered.',
        },
        {
          id: 'quick-2',
          label_en: 'bKash deducted but merchant pending',
          label_bn: 'বিকাশে টাকা কেটেছে কিন্তু মার্চেন্টে যায়নি',
          action_type: 'prompt',
          payload: isBangla ? 'বিকাশে মার্চেন্ট পেমেন্ট করার পর ব্যালেন্স কেটেছে কিন্তু অর্ডার কনফার্ম হয়নি' : 'bKash debited my wallet but merchant claims payment failed.',
        },
        {
          id: 'quick-3',
          label_en: 'Seller refuses to replace defective item',
          label_bn: 'দোকানদার বিক্রিত ত্রুটিপূর্ণ মাল ফেরত নিচ্ছে না',
          action_type: 'prompt',
          payload: isBangla ? 'দোকানদার বলছে বিক্রিত মাল ফেরত নেওয়া হয় না, এখন আমার আইনি অধিকার কী?' : 'Seller claims sold goods cannot be returned, what are my rights?',
        },
      ],
    },
  ];

  const [messages, setMessages] = useState<CopilotMessage[]>(initialMessages);

  const handleSend = async (textToSend?: string) => {
    const query = (textToSend || input).trim();
    if (!query) return;

    const userMsg: CopilotMessage = {
      id: `usr-${Date.now()}`,
      sender: 'user',
      text: query,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await apiFetch('/api/v1/copilot/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: query, locale }),
      });

      if (res.ok) {
        const data = await res.json();
        const replyText = isBangla ? data.reply_bn : data.reply_en;
        const botMsg: CopilotMessage = {
          id: `bot-${Date.now()}`,
          sender: 'assistant',
          text: replyText,
          statute: data.relevant_statute,
          actions: data.suggested_actions,
        };
        setMessages((prev) => [...prev, botMsg]);
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: `bot-err-${Date.now()}`,
          sender: 'assistant',
          text: isBangla
            ? 'দুঃখিত, সংযোগে সমস্যা হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।'
            : 'Sorry, connection error. Please try again.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Floating Launcher Button */}
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-40 inline-flex items-center gap-2.5 px-4 py-3 rounded-full bg-primary text-primary-foreground font-bold text-xs shadow-xl hover:scale-105 active:scale-95 transition-all group border-2 border-primary-foreground/20"
        aria-label="Open EbarKi AI Copilot"
      >
        <div className="w-6 h-6 rounded-full bg-primary-foreground/20 flex items-center justify-center animate-pulse">
          <Bot className="w-4 h-4 text-primary-foreground" />
        </div>
        <span>{isBangla ? 'এবার কি? AI কোপাইলট' : 'EbarKi AI Copilot'}</span>
        <Sparkles className="w-3.5 h-3.5 text-amber-300" />
      </button>

      {/* Slide-out Drawer */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-end bg-black/60 backdrop-blur-sm transition-opacity">
          <div className="w-full max-w-lg h-full bg-surface border-l border-border p-5 flex flex-col justify-between shadow-2xl relative">
            {/* Drawer Header */}
            <div className="flex items-center justify-between pb-3.5 border-b border-border">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-xl bg-primary text-primary-foreground flex items-center justify-center shadow-2xs">
                  <Bot className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-bold text-base text-foreground leading-tight flex items-center gap-1.5">
                    <span>{isBangla ? 'এবার কি? AI কোপাইলট' : 'EbarKi AI Copilot'}</span>
                    <Badge variant="brand" className="text-[9px] py-0">Agentic AI</Badge>
                  </h3>
                  <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground mt-0.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse inline-block" />
                    <span>{isBangla ? 'Groq LLaMA 3.3 ও লিগ্যাল রিজনিং ইঞ্জিন যুক্ত' : 'Powered by Groq LLaMA 3.3 & Legal Reasoner'}</span>
                  </div>
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-elevated transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Chat Messages Stream */}
            <div className="flex-1 overflow-y-auto py-4 space-y-4 text-xs pr-1">
              {messages.map((m) => (
                <div
                  key={m.id}
                  className={`flex gap-2.5 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {m.sender === 'assistant' && (
                    <div className="w-7 h-7 rounded-lg bg-[var(--brand-soft)] text-primary flex items-center justify-center shrink-0 mt-0.5">
                      <Sparkles className="w-3.5 h-3.5" />
                    </div>
                  )}

                  <div
                    className={`max-w-[85%] rounded-2xl p-3.5 space-y-2.5 leading-relaxed ${
                      m.sender === 'user'
                        ? 'bg-primary text-primary-foreground rounded-br-xs'
                        : 'bg-elevated/70 border border-border/80 text-foreground rounded-bl-xs shadow-2xs'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{m.text}</p>

                    {m.statute && (
                      <div className="p-2 rounded-lg bg-surface border border-primary/20 text-[11px] text-primary flex items-center gap-1.5 font-medium">
                        <Scale className="w-3.5 h-3.5 shrink-0" />
                        <span>{m.statute}</span>
                      </div>
                    )}

                    {m.actions && m.actions.length > 0 && (
                      <div className="pt-2 border-t border-border/50 flex flex-wrap gap-1.5">
                        {m.actions.map((act) => {
                          if (act.action_type === 'prompt') {
                            return (
                              <button
                                key={act.id}
                                onClick={() => handleSend(act.payload)}
                                className="px-2.5 py-1 rounded-lg bg-surface border border-border hover:border-primary text-foreground text-[11px] font-medium transition hover:bg-elevated shadow-2xs text-left"
                              >
                                💬 {isBangla ? act.label_bn : act.label_en}
                              </button>
                            );
                          }

                          return (
                            <Link
                              key={act.id}
                              href={`/${locale}${act.payload}`}
                              onClick={() => setIsOpen(false)}
                              className="inline-flex items-center gap-1 px-3 py-1 rounded-lg bg-primary text-primary-foreground text-[11px] font-bold hover:opacity-90 shadow-2xs transition"
                            >
                              <span>{isBangla ? act.label_bn : act.label_en}</span>
                              <ArrowRight className="w-3 h-3" />
                            </Link>
                          );
                        })}
                      </div>
                    )}
                  </div>

                  {m.sender === 'user' && (
                    <div className="w-7 h-7 rounded-lg bg-surface border border-border text-foreground flex items-center justify-center shrink-0 mt-0.5">
                      <User className="w-3.5 h-3.5" />
                    </div>
                  )}
                </div>
              ))}

              {loading && (
                <div className="p-3.5 rounded-xl border border-primary/30 bg-primary/5 space-y-2">
                  <div className="flex items-center gap-2 text-xs font-semibold text-primary">
                    <RefreshCw className="w-3.5 h-3.5 animate-spin text-primary" />
                    <span>{isBangla ? 'এআই এজেন্ট আইনি যুক্তি প্রক্রিয়া করছে...' : 'AI Agent Reasoning Across Legal Statutes...'}</span>
                  </div>
                  <div className="space-y-1 text-[11px] text-muted-foreground font-mono pl-5">
                    <div className="flex items-center gap-1.5">
                      <span className="w-1 h-1 rounded-full bg-emerald-500 animate-pulse" />
                      <span>{isBangla ? 'ভোক্তা অধিকার সংরক্ষণ আইন ২০০৯ (ধারা ৪৫/৪১) যাচাই...' : 'Auditing CRPA 2009 provisions (Sec 45 & 41)...'}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span className="w-1 h-1 rounded-full bg-primary animate-pulse" />
                      <span>{isBangla ? 'বিকাশ/মার্চেন্ট অভিযোগের পদ্ধতি ও তামাদি সময়সীমা নির্ধারণ...' : 'Formulating Stage 1 notice & 30-day limitation...'}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Input Form */}
            <div className="pt-3 border-t border-border">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSend();
                }}
                className="flex items-center gap-2"
              >
                <input
                  type="text"
                  placeholder={
                    isBangla
                      ? 'আপনার সমস্যা বা প্রশ্ন লিখুন (যেমন: দারাজে টাকা মেরে দিলে কি করব?)...'
                      : 'Ask anything (e.g. How do I get refund from Daraz?)...'
                  }
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  className="flex-1 p-2.5 rounded-xl border border-border bg-elevated/50 text-xs text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
                />
                <Button
                  type="submit"
                  size="sm"
                  variant="primary"
                  disabled={loading || !input.trim()}
                  className="shrink-0"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </form>
              <span className="text-[10px] text-muted-foreground block mt-1.5 text-center">
                {isBangla
                  ? '🔒 এআই পরামর্শ ও ধারা জাতীয় ভোক্তা অধিকার সংরক্ষণ আইন ও বিটিআরসি নির্দেশিকা দ্বারা ভেরিফাইড।'
                  : '🔒 AI guidance verified against official Bangladesh consumer protection acts.'}
              </span>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

