'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import {
  Search,
  Sparkles,
  FileCheck2,
  Scan,
  Scale,
  Radar,
  ArrowRight,
  CornerDownLeft,
  X,
  Compass,
  FileText,
  ShieldAlert,
  Bot,
  Sliders,
  CheckCircle2,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface CommandItem {
  id: string;
  titleEn: string;
  titleBn: string;
  categoryEn: string;
  categoryBn: string;
  descriptionEn: string;
  descriptionBn: string;
  icon: React.ElementType;
  badge?: string;
  badgeVariant?: 'brand' | 'warning' | 'danger' | 'neutral';
  action: (router: any, locale: string) => void;
}

export function AgentCommandPalette({
  locale = 'en',
  activeCaseId,
}: {
  locale?: string;
  activeCaseId?: string;
}) {
  const isBangla = locale === 'bn';
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  // Define commands
  const commands: CommandItem[] = [
    {
      id: 'draft-notice',
      titleEn: 'Draft 72-Hour Statutory Pre-Action Demand Notice',
      titleBn: '৭২ ঘণ্টার আইনি প্রি-অ্যাকশন নোটিশ প্রস্তুত করুন',
      categoryEn: 'Autonomous Agent Actions',
      categoryBn: 'স্বয়ংক্রিয় এজেন্ট অ্যাকশনস',
      descriptionEn: 'Generates formal letter under Consumer Rights Protection Act 2009 s.45',
      descriptionBn: 'ভোক্তা অধিকার সংরক্ষণ আইন ২০০৯ এর ৪৫ ধারা অনুযায়ী নোটিশ খসড়া',
      icon: FileCheck2,
      badge: 'Agent Draft',
      badgeVariant: 'brand',
      action: (r, loc) => {
        if (activeCaseId) {
          r.push(`/${loc}/cases/${activeCaseId}/actions`);
        } else {
          r.push(`/${loc}/cases`);
        }
      },
    },
    {
      id: 'inspect-ocr',
      titleEn: 'Inspect Multimodal Evidence & OCR Bounding Boxes',
      titleBn: 'মাল্টিমোডাল প্রমাণপত্র ও ওসিআর বাউন্ডিং বক্স পরীক্ষা করুন',
      categoryEn: 'Autonomous Agent Actions',
      categoryBn: 'স্বয়ংক্রিয় এজেন্ট অ্যাকশনস',
      descriptionEn: 'Cross-verifies bKash TrxID, courier tracking slips, and WhatsApp chats',
      descriptionBn: 'বিকাশ TrxID ও কুরিয়ার স্লিপের ডিজিটাল সত্যতা ও ডেটা ক্রস-চেক',
      icon: Scan,
      badge: 'Forensic VLM',
      badgeVariant: 'neutral',
      action: (r, loc) => {
        if (activeCaseId) {
          r.push(`/${loc}/cases/${activeCaseId}/evidence`);
        } else {
          r.push(`/${loc}/cases`);
        }
      },
    },
    {
      id: 'scam-radar',
      titleEn: 'Query Merchant Scam Radar Network',
      titleBn: 'মার্চেন্ট স্ক্যাম রাডার ডাটাবেজ অনুসন্ধান করুন',
      categoryEn: 'Consumer Protection Intelligence',
      categoryBn: 'ভোক্তা অধিকার গোয়েন্দা ডাটাবেজ',
      descriptionEn: 'Investigates repeat offender rogue Facebook pages & e-commerce shops',
      descriptionBn: 'প্রতারক ফেসবুক পেইজ ও ই-কমার্স মার্চেন্টের পূর্ববর্তী রেকর্ড যাচাই',
      icon: Radar,
      badge: 'Public Defense',
      badgeVariant: 'danger',
      action: (r, loc) => {
        r.push(`/${loc}/merchants`);
      },
    },
    {
      id: 'procedural-routes',
      titleEn: 'Compare Procedural Legal Paths & Venues (DNCRP vs ADR)',
      titleBn: 'আইনি প্রক্রিয়া ও ফোরাম তুলনা করুন (ভোক্তা অধিদপ্তর বনাম মধ্যস্থতা)',
      categoryEn: 'Statutory Strategy',
      categoryBn: 'আইনি কৌশল ও ফোরাম',
      descriptionEn: 'Deterministic viability analysis with 25% statutory compensation modeling',
      descriptionBn: '২৫% সরকারি জরিমানা ক্ষতিপূরণ ও এডিআর মীমাংসার সম্ভাবনা বিশ্লেষণ',
      icon: Compass,
      action: (r, loc) => {
        if (activeCaseId) {
          r.push(`/${loc}/cases/${activeCaseId}/paths`);
        } else {
          r.push(`/${loc}/cases`);
        }
      },
    },
    {
      id: 'limitation-audit',
      titleEn: 'Audit 30-Day Consumer Act Limitation Countdown',
      titleBn: '৩০ দিনের আইনি তামাদি সময়সীমা অডিট করুন',
      categoryEn: 'Statutory Strategy',
      categoryBn: 'আইনি কৌশল ও ফোরাম',
      descriptionEn: 'Calculates strict statutory deadline under Section 60(1)',
      descriptionBn: '৬০(১) ধারা অনুসারে অভিযোগ দাখিলের কঠোর সময়সীমা হিসাব',
      icon: Scale,
      action: (r, loc) => {
        if (activeCaseId) {
          r.push(`/${loc}/cases/${activeCaseId}`);
        } else {
          r.push(`/${loc}/cases`);
        }
      },
    },
    {
      id: 'community-forum',
      titleEn: 'Browse Consumer Community & Precedent Forum',
      titleBn: 'ভোক্তা কমিউনিটি ফোরাম ও সমাধানের নজির দেখুন',
      categoryEn: 'Community & Collective Action',
      categoryBn: 'কমিউনিটি ও অভিজ্ঞতা',
      descriptionEn: 'Crowdsourced resolution tips and collective consumer advocacy',
      descriptionBn: 'অন্যান্য ভোক্তাদের সফল সমাধানের অভিজ্ঞতা ও পরামর্শ',
      icon: FileText,
      action: (r, loc) => {
        r.push(`/${loc}/community`);
      },
    },
    {
      id: 'admin-panel',
      titleEn: 'Open Super Admin Oversight Command Center',
      titleBn: 'সুপার অ্যাডমিন কমান্ড সেন্টারে প্রবেশ করুন',
      categoryEn: 'System Administration',
      categoryBn: 'সিস্টেম অ্যাডমিনিস্ট্রেশন',
      descriptionEn: 'Manage rogue merchants, review cases, broadcast emergency scam bulletins',
      descriptionBn: 'মার্চেন্ট ব্যবস্থাপনা, কেস রিভিউ ও সিস্টেম টেলিমেট্রি নিরীক্ষা',
      icon: Bot,
      badge: 'Super Admin',
      badgeVariant: 'warning',
      action: (r, loc) => {
        r.push(`/${loc}/admin`);
      },
    },
  ];

  // Filter commands by query
  const query = search.trim().toLowerCase();
  const filtered = commands.filter((c) => {
    if (!query) return true;
    return (
      c.titleEn.toLowerCase().includes(query) ||
      c.titleBn.toLowerCase().includes(query) ||
      c.descriptionEn.toLowerCase().includes(query) ||
      c.descriptionBn.toLowerCase().includes(query) ||
      c.categoryEn.toLowerCase().includes(query)
    );
  });

  // Global Keyboard listener for Ctrl+K or Cmd+K
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setIsOpen((prev) => !prev);
      } else if (e.key === 'Escape' && isOpen) {
        setIsOpen(false);
      }
    };

    const handleCustomOpen = () => {
      setIsOpen(true);
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('claimcraft:open-palette', handleCustomOpen);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('claimcraft:open-palette', handleCustomOpen);
    };
  }, [isOpen]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
      setSelectedIndex(0);
    } else {
      setSearch('');
    }
  }, [isOpen]);

  const handleSelectCommand = (cmd: CommandItem) => {
    setIsOpen(false);
    cmd.action(router, locale);
  };

  const handleInputKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev + 1) % (filtered.length || 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev - 1 + (filtered.length || 1)) % (filtered.length || 1));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (filtered[selectedIndex]) {
        handleSelectCommand(filtered[selectedIndex]);
      }
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-16 sm:pt-24 px-4 bg-background/80 backdrop-blur-sm animate-fadeIn">
      {/* Backdrop click to dismiss */}
      <div className="absolute inset-0" onClick={() => setIsOpen(false)} />

      {/* Palette Modal Box */}
      <div className="relative w-full max-w-2xl bg-surface border border-border shadow-2xl rounded-2xl overflow-hidden flex flex-col z-10 animate-scaleUp">
        {/* Top search bar with glowing accent */}
        <div className="flex items-center gap-3 px-4 py-3.5 border-b border-border bg-elevated/40">
          <Sparkles className="w-5 h-5 text-amber-500 shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setSelectedIndex(0);
            }}
            onKeyDown={handleInputKeyDown}
            placeholder={
              isBangla
                ? 'আইনি নির্দেশ দিন বা অ্যাকশন খুঁজুন... (যেমন: নোটিশ, বিকাশ TrxID, তামাদি)'
                : 'Type an agent instruction or action... (e.g. Draft notice, OCR, Radar)'
            }
            className="w-full bg-transparent border-none outline-none text-sm md:text-base text-foreground placeholder:text-muted-foreground focus:ring-0"
          />
          {search && (
            <button
              onClick={() => setSearch('')}
              className="p-1 rounded text-muted-foreground hover:text-foreground"
            >
              <X className="w-4 h-4" />
            </button>
          )}
          <kbd className="hidden sm:inline-flex items-center text-[10px] font-mono text-muted-foreground bg-surface border border-border px-1.5 py-0.5 rounded shadow-2xs">
            ESC
          </kbd>
        </div>

        {/* Command list */}
        <div className="max-h-[380px] overflow-y-auto p-2 divide-y divide-border/40">
          {filtered.length === 0 ? (
            <div className="py-12 text-center text-muted-foreground">
              <Bot className="w-8 h-8 mx-auto mb-2 opacity-40 text-primary" />
              <p className="text-sm font-medium">
                {isBangla ? 'কোনো মেলানো অ্যাকশন পাওয়া যায়নি' : 'No matching agent command found'}
              </p>
              <p className="text-xs text-muted-foreground/80 mt-1">
                {isBangla
                  ? 'অন্য কোনো শব্দ যেমন "নোটিশ", "ওসিআর", বা "মার্চেন্ট" দিয়ে অনুসন্ধান করুন।'
                  : 'Try searching for "notice", "evidence", "radar", or "dncrp".'}
              </p>
            </div>
          ) : (
            filtered.map((cmd, idx) => {
              const Icon = cmd.icon;
              const isSelected = idx === selectedIndex;

              return (
                <div
                  key={cmd.id}
                  onClick={() => handleSelectCommand(cmd)}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  className={cn(
                    'flex items-center justify-between gap-3 p-3 rounded-xl cursor-pointer transition-all duration-150',
                    isSelected
                      ? 'bg-primary/10 text-primary-foreground border-l-4 border-l-primary'
                      : 'hover:bg-elevated/60 text-foreground'
                  )}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div
                      className={cn(
                        'w-8 h-8 rounded-lg flex items-center justify-center shrink-0 border transition-colors',
                        isSelected
                          ? 'bg-primary text-white border-primary'
                          : 'bg-elevated text-muted-foreground border-border/80'
                      )}
                    >
                      <Icon className="w-4 h-4" />
                    </div>

                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-xs sm:text-sm font-semibold truncate text-foreground">
                          {isBangla ? cmd.titleBn : cmd.titleEn}
                        </span>
                        {cmd.badge && (
                          <span className="text-[9px] font-mono uppercase tracking-wider px-1.5 py-0.2 rounded border bg-surface text-muted-foreground shrink-0">
                            {cmd.badge}
                          </span>
                        )}
                      </div>
                      <p className="text-[11px] text-muted-foreground truncate mt-0.5">
                        {isBangla ? cmd.descriptionBn : cmd.descriptionEn}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-1.5 shrink-0">
                    <span className="hidden sm:inline-flex text-[10px] text-muted-foreground font-mono">
                      {isBangla ? cmd.categoryBn : cmd.categoryEn}
                    </span>
                    <ArrowRight
                      className={cn(
                        'w-4 h-4 transition-transform',
                        isSelected ? 'translate-x-1 text-primary' : 'text-muted-foreground/40'
                      )}
                    />
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer shortcuts hint */}
        <div className="px-4 py-2 bg-elevated/70 border-t border-border flex items-center justify-between text-[11px] text-muted-foreground font-mono">
          <div className="flex items-center gap-3">
            <span>
              <kbd className="bg-surface px-1 py-0.5 rounded border border-border">↑</kbd>{' '}
              <kbd className="bg-surface px-1 py-0.5 rounded border border-border">↓</kbd>{' '}
              {isBangla ? 'নেভিগেট' : 'Navigate'}
            </span>
            <span>
              <kbd className="bg-surface px-1.5 py-0.5 rounded border border-border">↵</kbd>{' '}
              {isBangla ? 'নির্বাচন' : 'Execute'}
            </span>
          </div>
          <span className="text-[10px] text-primary font-semibold">
            {isBangla ? 'এবার কি? মাল্টি-এজেন্ট সোয়ার্ম' : 'EbarKi Multi-Agent Swarm'}
          </span>
        </div>
      </div>
    </div>
  );
}

