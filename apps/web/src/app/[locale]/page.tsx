import type { Metadata } from 'next';
import { EbarkiLanding } from '@/features/landing/EbarkiLanding';
import '@/features/landing/landing.css';

export async function generateMetadata({ params }: { params: Promise<{ locale: string }> }): Promise<Metadata> {
  const { locale } = await params;
  const title = locale === 'bn' ? 'Ebarki — পরের পদক্ষেপ, এখন স্পষ্ট।' : 'Ebarki — The next step, made clear.';
  const description = locale === 'bn'
    ? 'প্রমাণ গুছিয়ে, সম্ভাব্য পথ বুঝে, ভোক্তা অভিযোগের পরের পদক্ষেপের প্রস্তুতি নিন।'
    : 'Organize your evidence, understand possible routes, and prepare your next step. A Bangladesh-first consumer resolution copilot.';
  return { title, description, applicationName: 'Ebarki', openGraph: { title, description, siteName: 'Ebarki', locale: locale === 'bn' ? 'bn_BD' : 'en_BD', type: 'website' }, twitter: { card: 'summary_large_image', title, description }, icons: { icon: '/ebarki-mark.svg', apple: '/ebarki-mark.svg' } };
}

export default async function HomePage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  return <EbarkiLanding locale={locale} />;
}
