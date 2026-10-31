import { getTranslations } from 'next-intl/server';
import Link from 'next/link';
import { ArrowLeft, Lock, Trash2, ShieldCheck, EyeOff } from 'lucide-react';
import { Header } from '@/components/layout/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';

export default async function PrivacyPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: 'landing' });
  const tNav = await getTranslations({ locale, namespace: 'nav' });

  const isBangla = locale === 'bn';

  return (
    <div className="min-h-screen flex flex-col bg-canvas text-foreground">
      <Header
        locale={locale}
        labels={{
          home: tNav('home'),
          scenarios: tNav('scenarios'),
          cases: tNav('overview'),
          startCase: t('start_cta'),
        }}
      />

      <main className="flex-1 max-w-4xl mx-auto px-4 md:px-8 py-12 w-full">
        <Link
          href={`/${locale}`}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-muted-foreground hover:text-foreground mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>{isBangla ? 'হোমে ফিরে যান' : 'Back to home'}</span>
        </Link>

        <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight mb-4">
          {isBangla ? 'ব্যক্তিগত তথ্যের গোপনীয়তা ও নিরাপত্তা' : 'Privacy & Data Protection Policy'}
        </h1>
        <p className="text-muted-foreground text-base mb-10 leading-relaxed">
          {isBangla
            ? 'আপনার বিরোধের নথিপত্র এবং ব্যক্তিগত আর্থিক লেনদেনের তথ্যের ওপর আপনার পূর্ণ নিয়ন্ত্রণ রয়েছে।'
            : 'How ClaimCraft BD secures your dispute records, ensures tenant isolation, and provides absolute user control.'}
        </p>

        <div className="space-y-6">
          <Card>
            <CardHeader className="flex flex-row items-center gap-3">
              <Lock className="w-5 h-5 text-primary" />
              <CardTitle className="text-base font-bold">
                {isBangla ? 'শূন্য-প্রশিক্ষণ নীতি (Zero Training Guarantee)' : 'Zero AI Training Guarantee'}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground leading-relaxed">
              {isBangla
                ? 'আমরা পেইড এন্টারপ্রাইজ এআই এডাপ্টার ব্যবহার করি যেখানে ব্যবহারকারীর কোনো বক্তব্য, রসিদ বা নথি ভিত্তি মডেলের প্রশিক্ষণে ব্যবহৃত হয় না।'
                : 'ClaimCraft BD operates strictly under enterprise zero-data-retention agreements. Your prompts, receipts, voice recordings, and evidence are never used to train or fine-tune public foundation AI models.'}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center gap-3">
              <EyeOff className="w-5 h-5 text-primary" />
              <CardTitle className="text-base font-bold">
                {isBangla ? 'আইসোলেশন ও ব্যক্তিগত স্টোরেজ' : 'Strict Tenant Isolation'}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground leading-relaxed">
              {isBangla
                ? 'প্রতিটি কেসের ফাইল সম্পূর্ণ পৃথক ব্যক্তিগত কোয়ারেন্টাইন স্টোরেজে থাকে। কোনো অবস্থাতেই এক ব্যবহারকারীর ফাইল অন্য ব্যবহারকারী দেখতে পারবেন না।'
                : 'Every piece of uploaded evidence is encrypted in private storage buckets tied exclusively to your session principal. No public object URLs are ever generated for personal dispute files.'}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center gap-3">
              <Trash2 className="w-5 h-5 text-red-600" />
              <CardTitle className="text-base font-bold">
                {isBangla ? 'এক ক্লিকে স্থায়ীভাবে মুছে ফেলা' : 'Permanent One-Click Deletion'}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground leading-relaxed">
              {isBangla
                ? 'আপনি যেকোনো সময় আপনার কেস ডিলিট করতে পারেন। এর ফলে সম্পর্কিত সকল অডিও, রসিদ, এক্সট্রাক্ট করা টেক্সট এবং খসড়া স্থায়ীভাবে মুছে ফেলা হবে।'
                : 'You have the right to purge your case at any time. Deletion immediately revokes access, deletes original files and OCR derivatives, and records a cryptographic deletion receipt preventing backup resurrection.'}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}

