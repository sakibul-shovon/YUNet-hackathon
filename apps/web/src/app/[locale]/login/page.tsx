'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter, useParams } from 'next/navigation';
import { Shield, Sparkles, Lock, ArrowRight, AlertCircle, CheckCircle2, User, KeyRound } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { apiFetch } from '@/lib/api';

export default function LoginPage() {
  const router = useRouter();
  const params = useParams();
  const locale = (params?.locale as string) || 'bn';
  const isBangla = locale === 'bn';

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isJudgeLoading, setIsJudgeLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const res = await apiFetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim(), password }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || (isBangla ? 'ইমেইল বা পাসওয়ার্ড সঠিক নয়।' : 'Invalid email or password.'));
      }

      const user = await res.json();
      if (typeof window !== 'undefined') {
        localStorage.setItem('claimcraft_user', JSON.stringify(user));
      }
      router.push(`/${locale}/cases`);
      router.refresh();
    } catch (err: any) {
      setErrorMessage(err.message || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleJudgeDemoLogin = async () => {
    setIsJudgeLoading(true);
    setErrorMessage(null);

    try {
      const res = await apiFetch('/api/v1/auth/judge-demo', {
        method: 'POST',
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || 'Demo login failed');
      }

      const user = await res.json();
      if (typeof window !== 'undefined') {
        localStorage.setItem('claimcraft_user', JSON.stringify(user));
      }
      router.push(`/${locale}/cases`);
      router.refresh();
    } catch (err: any) {
      setErrorMessage(err.message || 'Judge demo login failed');
    } finally {
      setIsJudgeLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-canvas text-foreground flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold">
          <Shield className="w-4 h-4" />
          <span>{isBangla ? 'এবার কি? (EbarKi)' : 'EbarKi'} • YUNet AIgnite 2026</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground">
          {isBangla ? 'এবার কি?-তে প্রবেশ করুন' : 'Sign in to EbarKi'}
        </h1>
        <p className="text-xs text-muted-foreground">
          {isBangla
            ? 'আপনার কেস, প্রমাণাদি ভল্ট এবং আইনি নথিপত্রে প্রবেশ করুন'
            : 'Access your consumer dispute workspace, evidence vault, and legal drafts'}
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md space-y-5">
        {/* ⚡ Hackathon Judge 1-Click Access Card */}
        <Card className="border-2 border-primary/40 bg-gradient-to-br from-primary/10 via-surface to-primary/5 shadow-md overflow-hidden relative">
          <div className="absolute top-0 right-0 bg-primary text-primary-foreground text-[10px] font-bold px-2.5 py-0.5 rounded-bl-lg flex items-center gap-1 font-mono">
            <Sparkles className="w-3 h-3 animate-spin" />
            <span>HACKATHON EVALUATION</span>
          </div>
          <CardHeader className="pb-3 pt-4">
            <div className="flex items-center gap-2">
              <span className="text-xl">👨‍⚖️</span>
              <div>
                <CardTitle className="text-sm font-bold text-foreground">
                  {isBangla ? 'হ্যাকথন জাজ ১-ক্লিক ডেমো এক্সেস' : 'Hackathon Judge 1-Click Access'}
                </CardTitle>
                <CardDescription className="text-[11px] text-muted-foreground">
                  {isBangla
                    ? 'কোনো পাসওয়ার্ড ছাড়াই তাৎক্ষণিক প্রি-সিড করা কেসসহ প্রবেশ করুন'
                    : 'Instant evaluation with pre-seeded live cases and full workspace access'}
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="pt-0">
            <Button
              type="button"
              variant="primary"
              size="md"
              className="w-full gap-2 font-bold shadow-xs"
              onClick={handleJudgeDemoLogin}
              disabled={isJudgeLoading || isLoading}
            >
              {isJudgeLoading ? (
                <span>{isBangla ? 'লগইন হচ্ছে...' : 'Entering Sandbox...'}</span>
              ) : (
                <>
                  <span>⚡</span>
                  <span>{isBangla ? 'বিচারক হিসেবে ১-ক্লিকে প্রবেশ করুন' : 'Judge 1-Click Instant Access'}</span>
                  <ArrowRight className="w-4 h-4 ml-auto" />
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Standard Consumer Login Card */}
        <Card className="border border-border bg-surface shadow-xs">
          <CardHeader className="pb-3">
            <CardTitle className="text-base font-bold text-foreground">
              {isBangla ? 'সাধারণ ব্যবহারকারী লগইন' : 'Consumer Account Login'}
            </CardTitle>
            <CardDescription className="text-xs">
              {isBangla
                ? 'আপনার ইমেইল ও পাসওয়ার্ড দিয়ে প্রবেশ করুন'
                : 'Enter your registered email and password to continue'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {errorMessage && (
              <div className="mb-4 p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-xs text-destructive flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{errorMessage}</span>
              </div>
            )}

            <form onSubmit={handleLogin} className="space-y-4">
              <Input
                label={isBangla ? 'ইমেইল ঠিকানা' : 'Email Address'}
                type="email"
                required
                placeholder="name@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isLoading || isJudgeLoading}
              />

              <Input
                label={isBangla ? 'পাসওয়ার্ড' : 'Password'}
                type="password"
                required
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading || isJudgeLoading}
              />

              <Button
                type="submit"
                variant="primary"
                size="md"
                className="w-full gap-2 font-semibold"
                disabled={isLoading || isJudgeLoading}
              >
                {isLoading ? (
                  <span>{isBangla ? 'যাচাই করা হচ্ছে...' : 'Verifying...'}</span>
                ) : (
                  <>
                    <KeyRound className="w-4 h-4" />
                    <span>{isBangla ? 'লগইন করুন' : 'Sign In'}</span>
                  </>
                )}
              </Button>
            </form>

            <div className="mt-5 pt-4 border-t border-border text-center text-xs text-muted-foreground">
              <span>{isBangla ? 'কোনো অ্যাকাউন্ট নেই? ' : "Don't have an account? "}</span>
              <Link
                href={`/${locale}/register`}
                className="text-primary font-bold hover:underline"
              >
                {isBangla ? 'এখানে সাইন আপ করুন' : 'Sign up here'}
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Security Invariant Notice */}
        <div className="p-3 rounded-xl bg-surface/50 border border-border text-[11px] text-muted-foreground flex items-center gap-2">
          <Lock className="w-4 h-4 text-emerald-500 shrink-0" />
          <span>
            {isBangla
              ? 'নিরাপত্তা নিশ্চয়তা: এবার কি? কখনোই ওটিপি, পিন, ব্যাংক পাসওয়ার্ড বা সিভিবির তথ্য চায় না।'
              : 'Security Invariant: EbarKi never collects OTP, PIN, bank passwords, or CVV numbers.'}
          </span>
        </div>
      </div>
    </div>
  );
}
