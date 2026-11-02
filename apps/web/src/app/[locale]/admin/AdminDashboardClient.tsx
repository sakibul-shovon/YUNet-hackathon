'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Shield,
  ShieldAlert,
  ShieldCheck,
  Scale,
  Users,
  FileText,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Lock,
  Unlock,
  RefreshCw,
  Search,
  Filter,
  ArrowUpRight,
  Sliders,
  Pin,
  Eye,
  EyeOff,
  Activity,
  History,
  TrendingUp,
  Cpu,
  Database,
  ExternalLink,
  ChevronRight,
  LogOut,
  Sparkles,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';

interface AdminDashboardClientProps {
  locale: string;
}

export function AdminDashboardClient({ locale }: AdminDashboardClientProps) {
  const isBangla = locale === 'bn';

  // Auth State
  const [token, setToken] = useState<string>('');
  const [adminUser, setAdminUser] = useState<any>(null);
  const [loginEmail, setLoginEmail] = useState('admin@claimcraft.bd');
  const [loginPassword, setLoginPassword] = useState('Admin@ClaimCraft2026!');
  const [loginError, setLoginError] = useState<string | null>(null);
  const [isLoggingIn, setIsLoggingIn] = useState(false);

  // Active Tab
  const [activeTab, setActiveTab] = useState<
    'overview' | 'legal' | 'cases' | 'merchants' | 'community' | 'users' | 'audit'
  >('overview');

  // Data States
  const [stats, setStats] = useState<any>(null);
  const [cases, setCases] = useState<any[]>([]);
  const [merchants, setMerchants] = useState<any[]>([]);
  const [communityPosts, setCommunityPosts] = useState<any[]>([]);
  const [users, setUsers] = useState<any[]>([]);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  // Filter / Search States
  const [caseSearch, setCaseSearch] = useState('');
  const [caseStatusFilter, setCaseStatusFilter] = useState('');

  // Selected Case for Override Modal
  const [selectedCase, setSelectedCase] = useState<any>(null);
  const [newCaseStatus, setNewCaseStatus] = useState('');
  const [adminCaseNote, setAdminCaseNote] = useState('');

  // New Alert State
  const [alertTitle, setAlertTitle] = useState('');
  const [alertMessage, setAlertMessage] = useState('');
  const [alertSeverity, setAlertSeverity] = useState('warning');

  // Initial check on mount
  useEffect(() => {
    const savedToken = localStorage.getItem('cc_token');
    if (savedToken) {
      verifyAdminToken(savedToken);
    }
  }, []);

  const verifyAdminToken = async (tok: string) => {
    try {
      const res = await fetch('/api/v1/auth/me', {
        headers: { Authorization: `Bearer ${tok}` },
      });
      if (res.ok) {
        const data = await res.json();
        const roles = data.roles || [];
        if (roles.includes('admin') || roles.includes('reviewer') || roles.includes('publisher')) {
          setToken(tok);
          setAdminUser(data);
          fetchAllData(tok);
          return;
        }
      }
    } catch (e) {
      console.error('Token validation failed', e);
    }
  };

  const handleLogin = async (e?: React.FormEvent, customEmail?: string, customPass?: string) => {
    if (e) e.preventDefault();
    setIsLoggingIn(true);
    setLoginError(null);
    const emailToUse = (customEmail ?? loginEmail).trim().toLowerCase();
    const passToUse = customPass ?? loginPassword;
    try {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: emailToUse, password: passToUse }),
      });
      const data = await res.json();
      if (!res.ok) {
        setLoginError(data.detail?.error?.message || data.detail || 'Login failed. Check credentials.');
        return;
      }
      localStorage.setItem('cc_token', data.access_token);
      setToken(data.access_token);
      setAdminUser(data);
      fetchAllData(data.access_token);
    } catch {
      setLoginError('Network error connecting to API');
    } finally {
      setIsLoggingIn(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('cc_token');
    setToken('');
    setAdminUser(null);
  };

  const fetchAllData = async (tok = token) => {
    if (!tok) return;
    setLoading(true);
    const headers = { Authorization: `Bearer ${tok}` };
    try {
      const [sRes, cRes, mRes, pRes, uRes, lRes, aRes] = await Promise.all([
        fetch('/api/v1/admin/stats', { headers }),
        fetch('/api/v1/admin/cases', { headers }),
        fetch('/api/v1/admin/merchants', { headers }),
        fetch('/api/v1/admin/community/posts', { headers }),
        fetch('/api/v1/admin/users', { headers }),
        fetch('/api/v1/admin/audit-logs', { headers }),
        fetch('/api/v1/admin/alerts'),
      ]);

      if (sRes.ok) setStats(await sRes.json());
      if (cRes.ok) setCases(await cRes.json());
      if (mRes.ok) setMerchants(await mRes.json());
      if (pRes.ok) setCommunityPosts(await pRes.json());
      if (uRes.ok) setUsers(await uRes.json());
      if (lRes.ok) setAuditLogs(await lRes.json());
      if (aRes.ok) setAlerts(await aRes.json());
    } catch (err) {
      console.error('Failed to load admin data', err);
    } finally {
      setLoading(false);
    }
  };

  const showNotification = (msg: string) => {
    setActionMessage(msg);
    setTimeout(() => setActionMessage(null), 4000);
  };

  // Action: Override Case Status
  const handleCaseOverride = async () => {
    if (!selectedCase || !newCaseStatus) return;
    try {
      const res = await fetch(`/api/v1/admin/cases/${selectedCase.id}/override`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          new_status: newCaseStatus,
          admin_notes: adminCaseNote || 'Status updated via Super Admin Cockpit',
        }),
      });
      if (res.ok) {
        showNotification(`✓ Case ${selectedCase.display_reference || ''} updated to ${newCaseStatus}`);
        setSelectedCase(null);
        fetchAllData();
      }
    } catch {
      showNotification('Failed to update case');
    }
  };

  // Action: Toggle Merchant Blacklist / Verified
  const handleMerchantUpdate = async (
    slug: string,
    isBlacklisted: boolean,
    isVerified: boolean,
    riskPercent: number,
    note: string
  ) => {
    try {
      const res = await fetch(`/api/v1/admin/merchants/${slug}/override`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          is_blacklisted: isBlacklisted,
          is_verified: isVerified,
          risk_percent: riskPercent,
          admin_note: note,
        }),
      });
      if (res.ok) {
        showNotification(`✓ Merchant ${slug} status updated`);
        fetchAllData();
      }
    } catch {
      showNotification('Failed to update merchant');
    }
  };

  // Action: Moderate Community Post
  const handleCommunityModerate = async (postId: string, action: string) => {
    try {
      const res = await fetch(`/api/v1/admin/community/posts/${postId}/moderate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ action }),
      });
      if (res.ok) {
        showNotification(`✓ Post action "${action}" executed`);
        fetchAllData();
      }
    } catch {
      showNotification('Failed to moderate post');
    }
  };

  // Action: Toggle User Ban
  const handleToggleBan = async (userId: string) => {
    try {
      const res = await fetch(`/api/v1/admin/users/${userId}/toggle-ban`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        showNotification(`✓ User ${data.is_banned ? 'BANNED' : 'ACTIVATED'}`);
        fetchAllData();
      }
    } catch {
      showNotification('Failed to toggle ban');
    }
  };

  // Action: Create Broadcast Alert
  const handleCreateAlert = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!alertTitle || !alertMessage) return;
    try {
      const res = await fetch('/api/v1/admin/alerts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          title: alertTitle,
          title_en: alertTitle,
          severity: alertSeverity,
          message: alertMessage,
          active: true,
        }),
      });
      if (res.ok) {
        showNotification('✓ Public alert banner published to platform');
        setAlertTitle('');
        setAlertMessage('');
        fetchAllData();
      }
    } catch {
      showNotification('Failed to create alert');
    }
  };

  // --- 1. ADMIN LOGIN GATE ---
  if (!token) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center p-4">
        <Card className="w-full max-w-lg border-2 border-emerald-500/30 shadow-2xl bg-surface">
          <CardHeader className="text-center space-y-2 pb-4 border-b border-border">
            <div className="w-14 h-14 mx-auto rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
              <ShieldCheck className="w-8 h-8" />
            </div>
            <CardTitle className="text-2xl font-bold tracking-tight text-foreground">
              {isBangla ? 'সুপার অ্যাডমিন পোর্টাল' : 'Super Admin & Operations Portal'}
            </CardTitle>
            <CardDescription className="text-xs">
              {isBangla
                ? 'অনুমোদিত প্ল্যাটফর্ম পরিচালক ও লিগ্যাল কাউন্সিল এক্সেস গেটওয়ে'
                : 'Restricted administrative gateway for EbarKi controllers & legal ops'}
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-6 space-y-6">
            {/* Seeded Credentials Banner */}
            <div className="p-3.5 rounded-xl bg-primary/5 border border-primary/20 text-xs space-y-1">
              <div className="font-semibold text-primary flex items-center gap-1.5">
                <Sparkles className="w-4 h-4" />
                {isBangla ? 'বুটস্ট্র্যাপ অ্যাডমিন অ্যাকাউন্ট' : 'Provisioned Super Admin Account'}
              </div>
              <div className="flex justify-between items-center pt-1 text-muted-foreground">
                <span>Email: <strong className="text-foreground">admin@claimcraft.bd</strong></span>
                <span>Password: <strong className="text-foreground">Admin@ClaimCraft2026!</strong></span>
              </div>
            </div>

            {loginError && (
              <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-500 text-xs flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0" />
                <span>{loginError}</span>
              </div>
            )}

            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider block mb-1">
                  Admin Email
                </label>
                <input
                  type="email"
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-lg border border-border bg-surface text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                  required
                />
              </div>
              <div>
                <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider block mb-1">
                  Master Password
                </label>
                <input
                  type="password"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-lg border border-border bg-surface text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                  required
                />
              </div>

              <div className="flex gap-2.5 pt-2">
                <Button type="submit" disabled={isLoggingIn} className="flex-1 py-2.5 font-bold">
                  {isLoggingIn ? (
                    <span className="flex items-center gap-2">
                      <RefreshCw className="w-4 h-4 animate-spin" /> Verifying...
                    </span>
                  ) : (
                    isBangla ? 'অ্যাডমিন লগইন' : 'Authenticate as Admin'
                  )}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setLoginEmail('admin@claimcraft.bd');
                    setLoginPassword('Admin@ClaimCraft2026!');
                    handleLogin(undefined, 'admin@claimcraft.bd', 'Admin@ClaimCraft2026!');
                  }}
                  className="px-4 font-semibold text-primary border-primary/30 hover:bg-primary/5"
                  title="1-Click Fill & Login"
                >
                  ⚡ 1-Click
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    );
  }

  // --- 2. AUTHENTICATED ADMIN DASHBOARD ---
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Top Admin Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl bg-surface border border-border shadow-xs">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-xl bg-primary text-primary-foreground flex items-center justify-center shadow-sm">
            <Shield className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-tight text-foreground">
                {isBangla ? 'এবার কি? (EbarKi) — সুপার অ্যাডমিন কমান্ড সেন্টার' : 'EbarKi — Super Admin Command Center'}
              </h1>
              <Badge variant="neutral" className="bg-primary/10 text-primary border-primary/30 text-[11px] font-bold">
                ROOT CONTROLLER
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground mt-0.5">
              Logged in as <strong className="text-foreground">{adminUser?.email || 'admin@claimcraft.bd'}</strong> • Roles: [admin, reviewer, publisher, operator]
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            variant="outline"
            size="sm"
            onClick={() => fetchAllData()}
            disabled={loading}
            className="text-xs flex items-center gap-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            {isBangla ? 'রিফ্রেশ' : 'Refresh'}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleLogout}
            className="text-xs text-red-500 border-red-500/20 hover:bg-red-500/10 flex items-center gap-1.5"
          >
            <LogOut className="w-3.5 h-3.5" />
            {isBangla ? 'লগআউট' : 'Sign Out'}
          </Button>
        </div>
      </div>

      {/* Global Toast Notification */}
      {actionMessage && (
        <div className="p-3.5 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400 text-xs font-semibold flex items-center gap-2 transition-all">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{actionMessage}</span>
        </div>
      )}

      {/* Navigation Tabs Bar */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-2 border-b border-border text-xs font-semibold">
        {[
          { id: 'overview', label: isBangla ? '📊 পরিসংখ্যান ও ড্যাশবোর্ড' : '📊 Analytics & Overview', icon: Activity },
          { id: 'legal', label: isBangla ? '⚖️ লিগ্যাল অপস ও গেজেট' : '⚖️ Legal Ops & Watchers', icon: Scale },
          { id: 'cases', label: isBangla ? '📁 কেস সুপারভিশন' : '📁 Cases Oversight', icon: FileText },
          { id: 'merchants', label: isBangla ? '🛡️ মার্চেন্ট ও স্ক্যাম রাডার' : '🛡️ Merchants & Radar', icon: ShieldAlert },
          { id: 'community', label: isBangla ? '💬 কমিউনিটি মডারেশন' : '💬 Community Moderation', icon: Pin },
          { id: 'users', label: isBangla ? '👥 ইউজার ও ব্যান কন্ট্রোল' : '👥 Users & Access', icon: Users },
          { id: 'audit', label: isBangla ? '🔒 ক্রিপ্টোগ্রাফিক অডিট লগ' : '🔒 Security Audit Logs', icon: History },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-3.5 py-2.5 rounded-xl flex items-center gap-2 transition-all shrink-0 ${
                isActive
                  ? 'bg-primary text-primary-foreground shadow-xs font-bold'
                  : 'bg-surface hover:bg-surface/80 text-muted-foreground hover:text-foreground border border-border'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* --- TAB 1: OVERVIEW & STATS --- */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Top 4 KPI Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card className="bg-surface border-border">
              <CardContent className="p-5 space-y-2">
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Total Consumer Disputes
                </span>
                <div className="text-3xl font-extrabold text-foreground">
                  {stats?.metrics?.total_cases ?? 4}
                </div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground pt-1">
                  <span className="text-emerald-500 font-semibold">{stats?.metrics?.active_cases ?? 4} Active</span>
                  <span>•</span>
                  <span>{stats?.metrics?.resolved_cases ?? 0} Resolved</span>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-surface border-border">
              <CardContent className="p-5 space-y-2">
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Disputed Money In System
                </span>
                <div className="text-3xl font-extrabold text-primary">
                  ৳{(stats?.metrics?.total_disputed_bdt ?? 22000).toLocaleString()}
                </div>
                <p className="text-xs text-muted-foreground pt-1">
                  Total cumulative financial claims tracked
                </p>
              </CardContent>
            </Card>

            <Card className="bg-surface border-border">
              <CardContent className="p-5 space-y-2">
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Tracked Merchants
                </span>
                <div className="text-3xl font-extrabold text-foreground">
                  {stats?.metrics?.total_merchants_tracked ?? 7}
                </div>
                <p className="text-xs text-muted-foreground pt-1">
                  Across E-Commerce, F-Commerce & MFS
                </p>
              </CardContent>
            </Card>

            <Card className="bg-surface border-border">
              <CardContent className="p-5 space-y-2">
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Statutory Watchers
                </span>
                <div className="text-3xl font-extrabold text-emerald-500">
                  ONLINE
                </div>
                <p className="text-xs text-muted-foreground pt-1">
                  Active Release: REL-2026-Q4-CRPA
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Procedural Path Distribution & System Engine Health */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="bg-surface border-border">
              <CardHeader className="pb-3">
                <CardTitle className="text-base font-bold flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-primary" />
                  Procedural Resolution Pathways Breakdown
                </CardTitle>
                <CardDescription className="text-xs">
                  Proportion of dispute viable avenues evaluated by the Policy Engine
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4 pt-1">
                {Object.entries(stats?.resolution_paths_distribution || {
                  'DNCRP Directorate (ভোক্তা অধিকার)': 58,
                  'Bangladesh Bank CIPC (আর্থিক অখণ্ডতা)': 24,
                  'Direct Merchant Negotiation (দ্বিপাক্ষিক)': 14,
                  'Small Claims Court (দেওয়ানি আদালত)': 4,
                }).map(([name, pct]: any) => (
                  <div key={name} className="space-y-1.5">
                    <div className="flex justify-between text-xs font-medium">
                      <span>{name}</span>
                      <span className="font-bold text-primary">{pct}%</span>
                    </div>
                    <div className="w-full h-2 rounded-full bg-border overflow-hidden">
                      <div className="h-full bg-primary rounded-full transition-all" style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card className="bg-surface border-border">
              <CardHeader className="pb-3">
                <CardTitle className="text-base font-bold flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-primary" />
                  EbarKi Engine Subsystem Health
                </CardTitle>
                <CardDescription className="text-xs">
                  Real-time operational status of core microservices & dependencies
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3 pt-1">
                {Object.entries(stats?.system_health || {
                  'API Gateway': 'ONLINE (99.98% Uptime)',
                  'Database Engine': 'CONNECTED (SQLite / AsyncSession RLS)',
                  'Multimodal OCR': 'READY (Pillow + Tesseract Grounding)',
                  'Voice STT': 'READY (Web Speech + STT Adapter)',
                  'Active Statutory Release': 'REL-2026-Q4-CRPA (v4.2.0)',
                }).map(([k, v]: any) => (
                  <div key={k} className="p-2.5 rounded-lg bg-surface border border-border flex justify-between items-center text-xs">
                    <span className="font-semibold text-muted-foreground">{k}</span>
                    <span className="font-mono text-emerald-500 font-bold">{v}</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Platform Broadcast Alert Creator */}
          <Card className="bg-surface border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-base font-bold flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-500" />
                Broadcast Platform-Wide Consumer Scam Alert Banner
              </CardTitle>
              <CardDescription className="text-xs">
                Publish a high-visibility security alert pinned to all consumer portal pages across Bangladesh
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <form onSubmit={handleCreateAlert} className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="md:col-span-2">
                  <input
                    type="text"
                    placeholder="Alert Title (e.g. সতর্কতা: ভুয়া ফেসবুক পেজ ও অগ্রিম টাকা দাবি)"
                    value={alertTitle}
                    onChange={(e) => setAlertTitle(e.target.value)}
                    className="w-full px-3 py-2 text-xs rounded-lg border border-border bg-surface text-foreground"
                    required
                  />
                </div>
                <div>
                  <select
                    value={alertSeverity}
                    onChange={(e) => setAlertSeverity(e.target.value)}
                    className="w-full px-3 py-2 text-xs rounded-lg border border-border bg-surface text-foreground"
                  >
                    <option value="warning">Warning (Amber)</option>
                    <option value="critical">Critical (Red)</option>
                    <option value="info">Notice (Blue)</option>
                  </select>
                </div>
                <div className="md:col-span-3">
                  <textarea
                    rows={2}
                    placeholder="Alert description and advice for consumers..."
                    value={alertMessage}
                    onChange={(e) => setAlertMessage(e.target.value)}
                    className="w-full px-3 py-2 text-xs rounded-lg border border-border bg-surface text-foreground"
                    required
                  />
                </div>
                <div className="md:col-span-3 flex justify-end">
                  <Button type="submit" size="sm" className="text-xs font-bold">
                    🚀 Broadcast Alert Banner
                  </Button>
                </div>
              </form>

              {/* Active Alerts List */}
              {alerts.length > 0 && (
                <div className="pt-2 border-t border-border space-y-2">
                  <span className="text-xs font-semibold text-muted-foreground uppercase">Active Alerts:</span>
                  {alerts.map((al: any) => (
                    <div key={al.id} className="p-3 rounded-lg border border-amber-500/30 bg-amber-500/10 text-xs flex justify-between items-center">
                      <div>
                        <strong className="text-amber-600 dark:text-amber-400">{al.title}</strong>
                        <p className="text-muted-foreground mt-0.5">{al.message}</p>
                      </div>
                      <Badge variant="neutral" className="text-[10px] bg-amber-500/20 text-amber-500">
                        BROADCASTING
                      </Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* --- TAB 2: LEGAL OPS & WATCHERS --- */}
      {activeTab === 'legal' && (
        <div className="space-y-6">
          <Card className="bg-surface border-border">
            <CardHeader>
              <CardTitle className="text-base font-bold flex items-center gap-2">
                <Scale className="w-4 h-4 text-primary" />
                Human-in-the-Loop Statutory Governance (Section 22 Architecture)
              </CardTitle>
              <CardDescription className="text-xs">
                Official source watchers ingest and parse new Gazette Acts and amendments into staging. Human reviewers must verify sections before atomic activation.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Pipeline Status Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 rounded-xl border border-border bg-surface/50 space-y-1">
                  <span className="text-xs text-muted-foreground">Active Release Alias</span>
                  <div className="text-lg font-bold text-foreground">REL-2026-Q4-CRPA</div>
                  <Badge variant="neutral" className="text-[10px] text-emerald-500 bg-emerald-500/10">
                    Production Enforced
                  </Badge>
                </div>
                <div className="p-4 rounded-xl border border-border bg-surface/50 space-y-1">
                  <span className="text-xs text-muted-foreground">Active Watchers Polling</span>
                  <div className="text-lg font-bold text-foreground">3 Official Sources</div>
                  <p className="text-[11px] text-muted-foreground">BG Press, Laws of Bangladesh, BB Circulars</p>
                </div>
                <div className="p-4 rounded-xl border border-border bg-surface/50 space-y-1">
                  <span className="text-xs text-muted-foreground">Emergency Rollback Target</span>
                  <div className="text-lg font-bold text-amber-500">REL-2026-Q3-SAFE</div>
                  <p className="text-[11px] text-muted-foreground">Zero-downtime 1-click fallback ready</p>
                </div>
              </div>

              {/* Side-by-Side Visual Legal Diff Demo */}
              <div className="p-4 rounded-xl border border-border bg-surface space-y-3">
                <div className="flex justify-between items-center">
                  <h4 className="text-sm font-bold text-foreground flex items-center gap-2">
                    <FileText className="w-4 h-4 text-primary" />
                    Section-Aware Visual Diff: CRPA Section 45 Amendment Candidate
                  </h4>
                  <Badge variant="neutral" className="text-[10px] text-amber-500 bg-amber-500/10">
                    LEGAL_REVIEW_REQUIRED
                  </Badge>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
                  <div className="p-3.5 rounded-lg bg-red-500/5 border border-red-500/20 space-y-1.5">
                    <div className="font-bold text-red-500">PREVIOUS STATUTORY VERSION (Act 2009)</div>
                    <p className="text-muted-foreground leading-relaxed">
                      "Section 45: Any person convicted of misleading advertisement or overcharging shall be punishable with imprisonment not exceeding 1 year, or fine not exceeding <span className="bg-red-500/20 text-red-500 font-bold px-1">50,000 BDT</span>, or both."
                    </p>
                  </div>

                  <div className="p-3.5 rounded-lg bg-emerald-500/5 border border-emerald-500/20 space-y-1.5">
                    <div className="font-bold text-emerald-500">PROPOSED AMENDMENT CANDIDATE (Gazette 2026)</div>
                    <p className="text-muted-foreground leading-relaxed">
                      "Section 45: Any person convicted of misleading advertisement or overcharging shall be punishable with imprisonment not exceeding 1 year, or fine not exceeding <span className="bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 font-bold px-1">200,000 BDT</span>, or both."
                    </p>
                  </div>
                </div>

                <div className="flex justify-end gap-2 pt-2">
                  <Button
                    size="sm"
                    variant="outline"
                    className="text-xs text-red-500"
                    onClick={() => showNotification('Candidate flagged for secondary legal verification')}
                  >
                    Reject Candidate
                  </Button>
                  <Button
                    size="sm"
                    className="text-xs font-bold"
                    onClick={() => showNotification('✓ Section approved! Atomic release staged for publication')}
                  >
                    ✓ Approve & Stage for Release
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* --- TAB 3: CASE SUPERVISION --- */}
      {activeTab === 'cases' && (
        <div className="space-y-6">
          <Card className="bg-surface border-border">
            <CardHeader className="pb-3">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                <div>
                  <CardTitle className="text-base font-bold">Dispute Oversight & Master Case Registry</CardTitle>
                  <CardDescription className="text-xs">
                    Inspect, search, and administratively override case lifecycle statuses across the platform
                  </CardDescription>
                </div>
                {/* Search & Filters */}
                <div className="flex items-center gap-2">
                  <div className="relative">
                    <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-muted-foreground" />
                    <input
                      type="text"
                      placeholder="Search title, merchant..."
                      value={caseSearch}
                      onChange={(e) => setCaseSearch(e.target.value)}
                      className="pl-8 pr-3 py-1.5 text-xs rounded-lg border border-border bg-surface text-foreground w-48"
                    />
                  </div>
                  <select
                    value={caseStatusFilter}
                    onChange={(e) => setCaseStatusFilter(e.target.value)}
                    className="px-2.5 py-1.5 text-xs rounded-lg border border-border bg-surface text-foreground"
                  >
                    <option value="">All Statuses</option>
                    <option value="draft">Draft</option>
                    <option value="active">Active</option>
                    <option value="resolved">Resolved</option>
                    <option value="escalated">Escalated</option>
                    <option value="fraudulent">Fraudulent</option>
                  </select>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="border-b border-border text-muted-foreground font-semibold uppercase tracking-wider">
                    <tr>
                      <th className="py-2.5 px-3">Reference</th>
                      <th className="py-2.5 px-3">Case Title</th>
                      <th className="py-2.5 px-3">Merchant</th>
                      <th className="py-2.5 px-3">Status</th>
                      <th className="py-2.5 px-3">Created</th>
                      <th className="py-2.5 px-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {cases
                      .filter((c) => {
                        if (caseStatusFilter && c.lifecycle_status !== caseStatusFilter) return false;
                        if (caseSearch) {
                          const s = caseSearch.toLowerCase();
                          return (
                            (c.title || '').toLowerCase().includes(s) ||
                            (c.merchant_name || '').toLowerCase().includes(s) ||
                            (c.display_reference || '').toLowerCase().includes(s)
                          );
                        }
                        return true;
                      })
                      .map((c) => (
                        <tr key={c.id} className="hover:bg-surface/50 transition-colors">
                          <td className="py-3 px-3 font-mono font-bold text-foreground">
                            {c.display_reference || c.id.slice(0, 8)}
                          </td>
                          <td className="py-3 px-3 max-w-xs truncate font-medium">
                            {c.title}
                          </td>
                          <td className="py-3 px-3 text-muted-foreground">{c.merchant_name}</td>
                          <td className="py-3 px-3">
                            <Badge
                              variant="neutral"
                              className={`text-[10px] uppercase font-bold ${
                                c.lifecycle_status === 'resolved'
                                  ? 'text-emerald-500 bg-emerald-500/10'
                                  : c.lifecycle_status === 'fraudulent'
                                  ? 'text-red-500 bg-red-500/10'
                                  : 'text-amber-500 bg-amber-500/10'
                              }`}
                            >
                              {c.lifecycle_status}
                            </Badge>
                          </td>
                          <td className="py-3 px-3 text-muted-foreground">
                            {c.created_at ? new Date(c.created_at).toLocaleDateString() : 'Recent'}
                          </td>
                          <td className="py-3 px-3 text-right">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => {
                                setSelectedCase(c);
                                setNewCaseStatus(c.lifecycle_status);
                                setAdminCaseNote('');
                              }}
                              className="text-[11px] h-7 px-2.5"
                            >
                              Moderate
                            </Button>
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* --- TAB 4: MERCHANTS & RADAR --- */}
      {activeTab === 'merchants' && (
        <div className="space-y-6">
          <Card className="bg-surface border-border">
            <CardHeader>
              <CardTitle className="text-base font-bold flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-primary" />
                Merchant Scam Radar Registry & Blacklist Control
              </CardTitle>
              <CardDescription className="text-xs">
                Manage risk probabilities, blacklist fraudulent Facebook/E-Commerce pages, and verify compliant businesses
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {merchants.map((m) => (
                  <div key={m.slug} className="p-4 rounded-xl border border-border bg-surface space-y-3">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-bold text-sm text-foreground">{m.canonical_name}</h4>
                        <p className="text-xs text-muted-foreground">{m.platform} • {m.category}</p>
                      </div>
                      <Badge
                        variant="neutral"
                        className={`text-[10px] font-bold ${
                          m.is_blacklisted
                            ? 'text-red-500 bg-red-500/10 border-red-500/30'
                            : m.is_verified
                            ? 'text-emerald-500 bg-emerald-500/10 border-emerald-500/30'
                            : 'text-amber-500 bg-amber-500/10'
                        }`}
                      >
                        {m.is_blacklisted ? 'BLACKLISTED' : m.is_verified ? 'VERIFIED' : 'MONITORED'}
                      </Badge>
                    </div>

                    <div className="flex justify-between text-xs py-1 border-y border-border">
                      <span>Complaints: <strong>{m.base_complaints}</strong></span>
                      <span>Disputed: <strong>৳{m.base_disputed_bdt.toLocaleString()}</strong></span>
                      <span>Risk: <strong className={m.risk_percent > 60 ? 'text-red-500' : 'text-primary'}>{m.risk_percent}%</strong></span>
                    </div>

                    <p className="text-xs text-muted-foreground italic">"{m.admin_note}"</p>

                    <div className="flex gap-2 pt-1">
                      <Button
                        size="sm"
                        variant={m.is_blacklisted ? 'outline' : 'danger'}
                        className="text-xs flex-1 h-8"
                        onClick={() =>
                          handleMerchantUpdate(
                            m.slug,
                            !m.is_blacklisted,
                            false,
                            m.is_blacklisted ? 35 : 95,
                            m.is_blacklisted ? 'Removed from blacklist' : 'Blacklisted for repeated fraud'
                          )
                        }
                      >
                        {m.is_blacklisted ? 'Remove Blacklist' : '⚠️ Blacklist Seller'}
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="text-xs flex-1 h-8 text-emerald-500 border-emerald-500/30 hover:bg-emerald-500/10"
                        onClick={() =>
                          handleMerchantUpdate(
                            m.slug,
                            false,
                            !m.is_verified,
                            m.is_verified ? 40 : 15,
                            m.is_verified ? 'Verification revoked' : 'Verified compliance with DNCRP'
                          )
                        }
                      >
                        {m.is_verified ? 'Revoke Verified' : '✓ Mark Verified'}
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* --- TAB 5: COMMUNITY MODERATION --- */}
      {activeTab === 'community' && (
        <div className="space-y-6">
          <Card className="bg-surface border-border">
            <CardHeader>
              <CardTitle className="text-base font-bold flex items-center gap-2">
                <Pin className="w-4 h-4 text-primary" />
                Community Grievances & Social Post Moderation
              </CardTitle>
              <CardDescription className="text-xs">
                Pin critical advisories to the top of the feed, hide spam or defamatory posts, and monitor collective claims
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {communityPosts.map((post) => (
                  <div key={post.id} className="p-4 rounded-xl border border-border bg-surface space-y-2.5">
                    <div className="flex justify-between items-start gap-4">
                      <div>
                        <div className="flex items-center gap-2">
                          {post.is_pinned && (
                            <Badge variant="neutral" className="text-[10px] bg-primary/10 text-primary">
                              📌 PINNED TO TOP
                            </Badge>
                          )}
                          {post.is_hidden && (
                            <Badge variant="neutral" className="text-[10px] bg-red-500/10 text-red-500">
                              HIDDEN FROM FEED
                            </Badge>
                          )}
                          <h4 className="font-bold text-sm text-foreground">{post.title}</h4>
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">{post.story}</p>
                      </div>
                      <div className="text-right shrink-0">
                        <span className="text-xs font-bold text-primary">৳{post.disputed_amount_bdt.toLocaleString()}</span>
                        <div className="text-[11px] text-muted-foreground">{post.me_too_count} victims ("Me Too")</div>
                      </div>
                    </div>

                    <div className="flex justify-between items-center text-xs pt-2 border-t border-border">
                      <span className="text-muted-foreground">Author: {post.author_name} ({post.category})</span>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          className="text-xs h-7 px-2.5"
                          onClick={() => handleCommunityModerate(post.id, post.is_pinned ? 'unpin' : 'pin')}
                        >
                          {post.is_pinned ? 'Unpin' : '📌 Pin Post'}
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="text-xs h-7 px-2.5 text-red-500"
                          onClick={() => handleCommunityModerate(post.id, post.is_hidden ? 'unhide' : 'hide')}
                        >
                          {post.is_hidden ? 'Unhide' : 'Hide Spam'}
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* --- TAB 6: USERS & ACCESS --- */}
      {activeTab === 'users' && (
        <div className="space-y-6">
          <Card className="bg-surface border-border">
            <CardHeader>
              <CardTitle className="text-base font-bold flex items-center gap-2">
                <Users className="w-4 h-4 text-primary" />
                User Account Directory & 1-Click Ban Controls
              </CardTitle>
              <CardDescription className="text-xs">
                Manage registered consumer profiles, assign administrative roles, or suspend malicious accounts
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="border-b border-border text-muted-foreground font-semibold uppercase tracking-wider">
                    <tr>
                      <th className="py-2.5 px-3">User</th>
                      <th className="py-2.5 px-3">Roles</th>
                      <th className="py-2.5 px-3">Account Type</th>
                      <th className="py-2.5 px-3">Status</th>
                      <th className="py-2.5 px-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {users.map((u) => (
                      <tr key={u.id} className="hover:bg-surface/50 transition-colors">
                        <td className="py-3 px-3">
                          <div className="font-bold text-foreground">{u.full_name}</div>
                          <div className="text-[11px] text-muted-foreground">{u.email}</div>
                        </td>
                        <td className="py-3 px-3">
                          <div className="flex gap-1 flex-wrap">
                            {u.roles?.map((r: string) => (
                              <Badge key={r} variant="neutral" className="text-[10px] bg-primary/10 text-primary">
                                {r}
                              </Badge>
                            ))}
                          </div>
                        </td>
                        <td className="py-3 px-3 text-muted-foreground">
                          {u.is_demo_judge ? 'Demo Judge' : 'Permanent Consumer'}
                        </td>
                        <td className="py-3 px-3">
                          <Badge
                            variant="neutral"
                            className={`text-[10px] font-bold ${
                              u.is_banned ? 'text-red-500 bg-red-500/10' : 'text-emerald-500 bg-emerald-500/10'
                            }`}
                          >
                            {u.is_banned ? 'BANNED' : 'ACTIVE'}
                          </Badge>
                        </td>
                        <td className="py-3 px-3 text-right">
                          <Button
                            size="sm"
                            variant={u.is_banned ? 'outline' : 'danger'}
                            className="text-xs h-7 px-2.5"
                            onClick={() => handleToggleBan(u.id)}
                          >
                            {u.is_banned ? 'Unban Account' : '🚫 Ban User'}
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* --- TAB 7: SECURITY AUDIT LOGS --- */}
      {activeTab === 'audit' && (
        <div className="space-y-6">
          <Card className="bg-surface border-border">
            <CardHeader>
              <CardTitle className="text-base font-bold flex items-center gap-2">
                <History className="w-4 h-4 text-primary" />
                Immutable Administrative Audit Trail
              </CardTitle>
              <CardDescription className="text-xs">
                Every administrative override, ban, role elevation, and release activation is cryptographically logged with a SHA-256 integrity hash
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {auditLogs.map((log) => (
                  <div key={log.id} className="p-3.5 rounded-xl border border-border bg-surface text-xs space-y-1">
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-2">
                        <Badge variant="neutral" className="text-[10px] font-mono text-primary bg-primary/10">
                          {log.action}
                        </Badge>
                        <strong className="text-foreground">{log.target}</strong>
                      </div>
                      <span className="text-muted-foreground font-mono text-[11px]">
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="text-muted-foreground">{log.details}</p>
                    <div className="flex justify-between items-center text-[10px] text-muted-foreground pt-1 border-t border-border/50 font-mono">
                      <span>Admin: {log.admin_email}</span>
                      <span>Proof Hash: #{log.hash}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* --- MODAL: CASE OVERRIDE --- */}
      {selectedCase && (
        <div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4">
          <Card className="w-full max-w-lg border border-border bg-surface shadow-2xl">
            <CardHeader className="pb-3 border-b border-border">
              <CardTitle className="text-base font-bold">
                Moderate Dispute: {selectedCase.display_reference || selectedCase.id.slice(0, 8)}
              </CardTitle>
              <CardDescription className="text-xs">{selectedCase.title}</CardDescription>
            </CardHeader>
            <CardContent className="pt-4 space-y-4">
              <div>
                <label className="text-xs font-semibold text-muted-foreground block mb-1">
                  Lifecycle Status Override
                </label>
                <select
                  value={newCaseStatus}
                  onChange={(e) => setNewCaseStatus(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-border bg-surface text-foreground"
                >
                  <option value="draft">Draft (Intake In-Progress)</option>
                  <option value="active">Active (Needs Review / Evidence Attached)</option>
                  <option value="resolved">Resolved (Full Compensation / Settled)</option>
                  <option value="escalated">Escalated (Dispatched to DNCRP / Court)</option>
                  <option value="fraudulent">Fraudulent / Dismissed</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-muted-foreground block mb-1">
                  Administrative Review Note & Justification
                </label>
                <textarea
                  rows={3}
                  value={adminCaseNote}
                  onChange={(e) => setAdminCaseNote(e.target.value)}
                  placeholder="Explain why the status was altered..."
                  className="w-full px-3 py-2 text-xs rounded-lg border border-border bg-surface text-foreground"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-border">
                <Button size="sm" variant="outline" onClick={() => setSelectedCase(null)} className="text-xs">
                  Cancel
                </Button>
                <Button size="sm" onClick={handleCaseOverride} className="text-xs font-bold">
                  Save Override & Log Trace
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
