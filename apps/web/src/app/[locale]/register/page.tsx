'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter, useParams } from 'next/navigation';
import { Shield, Lock, ArrowRight, AlertCircle, UserPlus, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { apiFetch } from '@/lib/api';

export default function RegisterPage() {
  const router = useRouter();
  const params = useParams();
  const locale = (params?.locale as string) || 'bn';
  const isBangla = locale === 'bn';

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (password !== confirmPassword) {
      setErrorMessage(isBangla ? 'পাসওয়ার্ড দুটি মেলেনি।' : 'Passwords do not match.');
      return;
    }

    if (password.length < 6) {
      setErrorMessage(isBangla ? 'পাসওয়ার্ড কমপক্ষে ৬ অক্ষরের হতে হবে।' : 'Password must be at least 6 characters.');
      return;
    }

    setIsLoading(true);

    try {
      const res = await apiFetch('/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          full_name: fullName.trim(),
          email: email.trim(),
          phone: phone.trim() || undefined,
          password,
        }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || (isBangla ? 'নিবন্ধন সম্পন্ন করা যায়নি।' : 'Registration failed.'));
      }

      const user = await res.json();
      if (typeof window !== 'undefined') {
        localStorage.setItem('claimcraft_user', JSON.stringify(user));
      }
      router.push(`/${locale}/cases`);
      router.refresh();
    } catch (err: any) {
      setErrorMessage(err.message || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-canvas text-foreground flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold">
          <Shield className="w-4 h-4" />
          <span>{isBangla ? 'এবার কি? (EbarKi)' : 'EbarKi'} • Consumer Resolution</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground">
          {isBangla ? 'নতুন অ্যাকাউন্ট তৈরি করুন' : 'Create Consumer Account'}
        </h1>
        <p className="text-xs text-muted-foreground">
          {isBangla
            ? 'সম্পূর্ণ ফ্রি, এনক্রিপ্টেড ও সুরক্ষিত ভোক্তা বিরোধ নিষ্পত্তি অ্যাকাউন্ট'
            : 'Free, secure, and encrypted consumer dispute resolution workspace'}
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md space-y-5">
        <Card className="border border-border bg-surface shadow-xs">
          <CardHeader className="pb-3">
            <CardTitle className="text-base font-bold text-foreground">
              {isBangla ? 'ব্যবহারকারীর তথ্য' : 'Personal Details'}
            </CardTitle>
            <CardDescription className="text-xs">
              {isBangla
                ? 'আপনার অভিযোগ নথির জন্য সঠিক নাম ও ইমেইল প্রদান করুন'
                : 'Enter your name and contact details for legal complaint drafting'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {errorMessage && (
              <div className="mb-4 p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-xs text-destructive flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{errorMessage}</span>
              </div>
            )}

            <form onSubmit={handleRegister} className="space-y-3.5">
              <Input
                label={isBangla ? 'আপনার পুরো নাম' : 'Full Name'}
                type="text"
                required
                placeholder={isBangla ? 'যেমন: সাকিবুল ইসলাম' : 'e.g. John Doe'}
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                disabled={isLoading}
              />

              <Input
                label={isBangla ? 'ইমেইল ঠিকানা' : 'Email Address'}
                type="email"
                required
                placeholder="name@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isLoading}
              />

              <Input
                label={isBangla ? 'মোবাইল নম্বর (ঐচ্ছিক)' : 'Mobile Number (Optional)'}
                type="tel"
                placeholder="017XXXXXXXX"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                disabled={isLoading}
              />

              <Input
                label={isBangla ? 'পাসওয়ার্ড (কমপক্ষে ৬ অক্ষর)' : 'Password (min. 6 characters)'}
                type="password"
                required
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading}
              />

              <Input
                label={isBangla ? 'পাসওয়ার্ড নিশ্চিত করুন' : 'Confirm Password'}
                type="password"
                required
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                disabled={isLoading}
              />

              <Button
                type="submit"
                variant="primary"
                size="md"
                className="w-full gap-2 font-semibold mt-2"
                disabled={isLoading}
              >
                {isLoading ? (
                  <span>{isBangla ? 'অ্যাকাউন্ট তৈরি হচ্ছে...' : 'Creating account...'}</span>
                ) : (
                  <>
                    <UserPlus className="w-4 h-4" />
                    <span>{isBangla ? 'অ্যাকাউন্ট তৈরি করুন' : 'Create Free Account'}</span>
                  </>
                )}
              </Button>
            </form>

            <div className="mt-5 pt-4 border-t border-border text-center text-xs text-muted-foreground">
              <span>{isBangla ? 'ইতিমধ্যে অ্যাকাউন্ট আছে? ' : 'Already have an account? '}</span>
              <Link
                href={`/${locale}/login`}
                className="text-primary font-bold hover:underline"
              >
                {isBangla ? 'এখানে লগইন করুন' : 'Sign in here'}
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Security Invariant Notice */}
        <div className="p-3 rounded-xl bg-surface/50 border border-border text-[11px] text-muted-foreground flex items-center gap-2">
          <Lock className="w-4 h-4 text-emerald-500 shrink-0" />
          <span>
            {isBangla
              ? 'গোপনীয়তা সুরক্ষা: আপনার ব্যক্তিগত তথ্য এনক্রিপ্ট রাখা হয় এবং কখনোই অনুমতি ছাড়া তৃতীয় পক্ষের সাথে শেয়ার করা হয় না।'
              : 'Privacy Protected: Your personal dispute records are encrypted and never shared without consent.'}
          </span>
        </div>
      </div>
    </div>
  );
}
