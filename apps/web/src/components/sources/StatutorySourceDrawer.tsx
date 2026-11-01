'use client';

import React, { useState } from 'react';
import { BookOpen, ExternalLink, ShieldCheck, ChevronRight, Copy, Check, Search } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';

interface ProvisionItem {
  citation_handle: string;
  section_number: string;
  section_bn: string;
  title_en: string;
  title_bn: string;
  canonical_text_bn: string;
  qualifications: string[];
  official_url: string;
}

const CANONICAL_PROVISIONS_LIST: ProvisionItem[] = [
  {
    citation_handle: 'crpa2009:sec:45',
    section_number: '45',
    section_bn: '৪৫',
    title_en: 'Punishment for failure to sell or deliver promised goods or services',
    title_bn: 'প্রতিশ্রুত পণ্য বা সেবা যথাযথভাবে বিক্রয় বা সরবরাহ না করার দণ্ড',
    canonical_text_bn: 'কোনো ব্যক্তি কোনো পণ্যের নির্ধারিত বা প্রতিশ্রুত মূল্য বা পণ্যের মূল্যের অংশবিশেষ গ্রহণ করিয়া বা সেবা প্রদানের উদ্দেশ্যে প্রতিশ্রুত সেবা মূল্যের অংশবিশেষ গ্রহণ করিয়া যদি প্রতিশ্রুত পণ্য বা সেবা যথাযথভাবে বিক্রয় বা সরবরাহ না করেন, তাহা হইলে তিনি অনধিক ১ বৎসর কারাদণ্ড বা অনধিক ৫০,০০০ টাকা অর্থদণ্ড বা উভয় দণ্ডে দণ্ডিত হইবেন।',
    qualifications: [
      'তবে শর্ত থাকে যে, কোনো অনিবার্য কারণবশত বা যুক্তিসঙ্গত কারণে সরবরাহ সম্ভব না হইলে অনতিবিলম্বে ক্রেতাকে সমুদয় অর্থ ফেরত প্রদান করিতে হইবে।'
    ],
    official_url: 'http://bdlaws.minlaw.gov.bd/act-1014.html',
  },
  {
    citation_handle: 'crpa2009:sec:45(2)',
    section_number: '45(2)',
    section_bn: '৪৫(২)',
    title_en: 'Mandatory refund proviso upon failure to supply',
    title_bn: 'সরবরাহে ব্যর্থতায় অবিলম্বে মূল্য ফেরত প্রদানের বাধ্যবাধকতা',
    canonical_text_bn: 'তবে শর্ত থাকে যে, কোনো অনিবার্য কারণবশত বা যুক্তিসঙ্গত কারণে পণ্য বা সেবা সরবরাহ সম্ভব না হইলে অনতিবিলম্বে ক্রেতা বা ভোক্তাকে গৃহীত সমুদয় অর্থ ফেরত প্রদান করিতে হইবে।',
    qualifications: [
      'অনতিবিলম্বে ক্রেতাকে সমুদয় অর্থ ফেরত প্রদান করিতে হইবে (ব্যতিক্রমহীন সম্পূর্ণ মূল্য ফেরত)।'
    ],
    official_url: 'http://bdlaws.minlaw.gov.bd/act-1014.html',
  },
  {
    citation_handle: 'crpa2009:sec:60',
    section_number: '60',
    section_bn: '৬০',
    title_en: 'Limitation period for filing consumer complaints (30 Days)',
    title_bn: 'অভিযোগ দায়েরের তামাদি বা সময়সীমা (৩০ দিন)',
    canonical_text_bn: 'এই আইনের অধীন কোনো অপরাধ সংঘটিত হইবার বা কারণ উদ্ভব হইবার তারিখ হইতে ৩০ (ত্রিশ) দিনের মধ্যে মহাপরিচালক বা তদকর্তৃক ক্ষমতাপ্রাপ্ত কোনো কর্মকর্তার নিকট লিখিতভাবে অভিযোগ দায়ের না করিলে উক্ত অভিযোগ গ্রহণযোগ্য হইবে না।',
    qualifications: [
      '৩০ দিনের সময়সীমা কঠোরভাবে বাধ্যতামূলক; কারণ উদ্ভব হইবার ৩০ দিন অতিক্রান্ত হইলে সাধারণ অভিযোগ তামাদি বলিয়া বিবেচিত হইবে।'
    ],
    official_url: 'http://bdlaws.minlaw.gov.bd/act-1014.html',
  },
  {
    citation_handle: 'crpa2009:sec:76',
    section_number: '76',
    section_bn: '৭৬',
    title_en: 'Disbursement of 25% collected fine to the complainant',
    title_bn: 'অভিযোগকারীকে আদায়কৃত অর্থদণ্ডের শতকরা ২৫ ভাগ প্রদান',
    canonical_text_bn: 'এই আইনের ধারা ৭০ এর অধীন কোনো অপরাধের জন্য আরোপিত অর্থদণ্ড আদায় করা হইলে, আদায়কৃত অর্থদণ্ডের শতকরা ২৫ ভাগ অর্থ তাৎক্ষণিকভাবে অভিযোগকারীকে প্রদান করিতে হইবে।',
    qualifications: [
      'অর্থদণ্ড অবশ্যই আনুষ্ঠানিকভাবে আদায় বা উসুল হইতে হইবে; শুধুমাত্র জরিমানা ধার্য হওয়াই অর্থপ্রাপ্তির নিশ্চয়তা নহে।'
    ],
    official_url: 'http://bdlaws.minlaw.gov.bd/act-1014.html',
  },
  {
    citation_handle: 'bb_cipc:stage:provider_grievance',
    section_number: 'stage-1',
    section_bn: 'স্তর-১',
    title_en: 'Mandatory Stage 1: Grievance submission to bank or MFS provider',
    title_bn: 'বাধ্যতামূলক স্তর ১: ব্যাংক বা এমএফএস প্রতিষ্ঠানের নিকট অভিযোগ দায়ের',
    canonical_text_bn: 'আক্রান্ত গ্রাহককে সর্বপ্রথম সংশ্লিষ্ট তফসিলি ব্যাংক বা মোবাইল ফাইন্যান্সিয়াল সার্ভিস (এমএফএস) প্রতিষ্ঠানের নিকট আনুষ্ঠানিকভাবে অভিযোগ দায়ের করিতে হইবে এবং টিকিট নম্বর সংরক্ষণ করিতে হইবে। প্রতিষ্ঠানকে অনধিক ১০ কার্যদিবসের মধ্যে অভিযোগ নিষ্পত্তি করিতে হইবে।',
    qualifications: [
      'ব্যাংক বা এমএফএস প্রতিষ্ঠানের টিকিট নম্বর ছাড়া সরাসরি বাংলাদেশ ব্যাংকে প্রেরিত অভিযোগ সাধারণত প্রাথমিক পর্যালোচনায় প্রতিষ্ঠানে ফেরত পাঠানো হয়।'
    ],
    official_url: 'https://bb.org.bd/en/index.php/services/cipc_procedure',
  },
];

interface Props {
  locale: string;
}

export function StatutorySourceDrawer({ locale }: Props) {
  const isBangla = locale === 'bn';
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCitation, setSelectedCitation] = useState<string | null>(null);
  const [copiedHandle, setCopiedHandle] = useState<string | null>(null);

  const filtered = CANONICAL_PROVISIONS_LIST.filter(p => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      p.citation_handle.toLowerCase().includes(q) ||
      p.section_number.includes(q) ||
      p.section_bn.includes(q) ||
      p.title_en.toLowerCase().includes(q) ||
      p.title_bn.includes(q) ||
      p.canonical_text_bn.includes(q)
    );
  });

  const handleCopy = (handle: string) => {
    navigator.clipboard.writeText(handle);
    setCopiedHandle(handle);
    setTimeout(() => setCopiedHandle(null), 2000);
  };

  return (
    <div className="space-y-6">
      <div className="relative">
        <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder={isBangla ? 'ধারা খুঁজুন (যেমন: ধারা ৪৫, ৬০, স্তর ১)...' : 'Search section or statute (e.g., sec:45, 60)...'}
          className="w-full pl-9 pr-4 py-2 text-sm rounded-lg border border-border bg-card text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
        />
      </div>

      <div className="grid gap-4">
        {filtered.map((item) => {
          const isSelected = selectedCitation === item.citation_handle;
          return (
            <Card
              key={item.citation_handle}
              className={`transition-all border ${isSelected ? 'ring-2 ring-primary border-transparent' : 'hover:border-primary/50'}`}
            >
              <CardHeader className="p-4 cursor-pointer" onClick={() => setSelectedCitation(isSelected ? null : item.citation_handle)}>
                <div className="flex items-start justify-between gap-2">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <Badge variant="brand">{isBangla ? `ধারা ${item.section_bn}` : `Sec ${item.section_number}`}</Badge>
                      <span className="text-xs font-mono text-muted-foreground">{item.citation_handle}</span>
                    </div>
                    <CardTitle className="text-base font-semibold leading-snug">
                      {isBangla ? item.title_bn : item.title_en}
                    </CardTitle>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleCopy(item.citation_handle);
                    }}
                    title="Copy citation handle"
                  >
                    {copiedHandle === item.citation_handle ? (
                      <Check className="w-3.5 h-3.5 text-success" />
                    ) : (
                      <Copy className="w-3.5 h-3.5" />
                    )}
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="px-4 pb-4 pt-0 space-y-3 text-xs leading-relaxed">
                <p className="text-foreground bg-muted/40 p-3 rounded border border-border/50">
                  {item.canonical_text_bn}
                </p>
                {item.qualifications.length > 0 && (
                  <div className="bg-warning/10 border border-warning/20 p-2.5 rounded text-warning text-xs space-y-1">
                    <div className="font-semibold flex items-center gap-1.5">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      <span>{isBangla ? 'আইনি ব্যতিক্রম ও শর্তাবলী:' : 'Qualifications & Provisos:'}</span>
                    </div>
                    {item.qualifications.map((q, idx) => (
                      <p key={idx}>{q}</p>
                    ))}
                  </div>
                )}
                <div className="flex items-center justify-between pt-1">
                  <a
                    href={item.official_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-primary hover:underline font-medium"
                  >
                    <span>{isBangla ? 'সরকারি গেজেট ও বিধান দেখুন' : 'View official gazette text'}</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}

