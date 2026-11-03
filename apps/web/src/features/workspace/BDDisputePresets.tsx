'use client';

import React from 'react';
import Link from 'next/link';

interface BDDisputePresetsProps {
  locale: string;
}

export function BDDisputePresets({ locale }: BDDisputePresetsProps) {
  const isBangla = locale === 'bn';

  const presets = [
    {
      icon: '🛒',
      title: isBangla ? 'দারাজ / ই-কমার্স রিফান্ড ও ডেলিভারি সমস্যা' : 'E-Commerce Non-Delivery & Refund Delay',
      desc: isBangla
        ? 'পণ্য না দিয়ে অর্ডার বাতিল, মেয়াদোত্তীর্ণ ডেলিভারি বা টাকা কেটে নিয়ে রিফান্ড না দেওয়া।'
        : 'Ordered item never dispatched or seller cancelled without instant automated refund.',
      reward: isBangla ? '২৫% নগদ পুরস্কার: ৳১,৩৭৫' : '25% Reward: ৳1,375',
      href: `/${locale}/cases/case_demo_phone`,
    },
    {
      icon: '📱',
      title: isBangla ? 'বিকাশ / নগদ এমএফএস বিরোধ (টাকা কেটেছে কিন্তু যায়নি)' : 'MFS Failed Transfer (Debit Without Credit)',
      desc: isBangla
        ? 'একাউন্ট থেকে টাকা কেটেছে কিন্তু মার্চেন্ট পায়নি বা ক্যাশ-ইন সম্পন্ন হয়নি।'
        : 'Account debited without merchant credit. Auto-triggers Bangladesh Bank PSD complaint.',
      reward: isBangla ? '৪৮ ঘণ্টায় নিষ্পত্তির বাধ্যবাধকতা' : '48-Hour Resolution SLA',
      href: `/${locale}/cases/case_demo_mfs`,
    },
    {
      icon: '🛍️',
      title: isBangla ? 'ফেসবুক পেজ অ্যাডভান্স পেমেন্ট প্রতারণা' : 'Facebook Page Advance Payment Scam',
      desc: isBangla
        ? 'অগ্রিম টাকা নিয়ে পেজ আনপাবলিশ, মেসেঞ্জারে ব্লক বা ভুয়া ট্র্যাকিং কোড সরবরাহ।'
        : 'Fake courier memo or blocked after delivery fee advance. Maps to Cyber Police & DNCRP.',
      reward: isBangla ? 'সাইবার পুলিশ ও ডিএনসিআরপি ট্র্যাকিং' : 'Cyber Security + DNCRP Track',
      href: `/${locale}/cases/new`,
    },
    {
      icon: '💊',
      title: isBangla ? 'ভেজাল পণ্য / এমআরপির বেশি দাম রাখা' : 'Counterfeit Item & Over-MRP Pricing',
      desc: isBangla
        ? 'প্যাকেটের নির্ধারিত মূল্যের চেয়ে বেশি দাম নেওয়া বা মেয়াদোত্তীর্ণ পণ্য বিক্রয়।'
        : 'Deceptive pricing beyond stamped MRP. Violates CRPA 2009 Section 40 directly.',
      reward: isBangla ? '২৫% সরকারি নগদ পুরস্কার প্রাপ্য' : 'Eligible for 25% Treasury Cash',
      href: `/${locale}/cases/case_demo_living`,
    },
  ];

  return (
    <div style={{ marginBottom: '32px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <div>
          <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 800, color: 'var(--ink)' }}>
            {isBangla ? '⚡ ১-ক্লিকে সাধারণ ভোক্তা বিরোধ প্রস্তুতি' : '⚡ 1-Click Common Bangladesh Dispute Templates'}
          </h3>
          <p style={{ margin: '4px 0 0', fontSize: '13px', color: 'var(--muted-ink)' }}>
            {isBangla
              ? 'আইনসম্মত ধারা ও প্রমাণাদির তালিকা সহ প্রস্তুতকৃত টেমপ্লেট বেছে নিন'
              : 'Choose a verified legal template with pre-mapped statutory sections'}
          </p>
        </div>
      </div>

      <div className="ui-presets-grid">
        {presets.map((preset, index) => (
          <Link href={preset.href} key={index} className="ui-preset-card">
            <span className="ui-preset-icon">{preset.icon}</span>
            <strong className="ui-preset-title">{preset.title}</strong>
            <p className="ui-preset-desc">{preset.desc}</p>
            <span className="ui-preset-reward">💰 {preset.reward}</span>
          </Link>
        ))}
      </div>
    </div>
  );
}
