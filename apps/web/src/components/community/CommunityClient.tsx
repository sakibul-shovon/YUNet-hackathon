'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  MessageSquare,
  Users,
  Sparkles,
  ArrowRight,
  ShieldAlert,
  Send,
  Heart,
  HelpCircle,
  CheckCircle2,
  Filter,
} from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { apiFetch } from '@/lib/api';

interface Comment {
  id: string;
  author_name: string;
  content: string;
  created_at: string;
  is_legal_volunteer: boolean;
}

interface Post {
  id: string;
  title: string;
  story: string;
  category: string;
  merchant_name: string;
  disputed_amount_bdt: number;
  author_name: string;
  me_too_count: number;
  created_at: string;
  has_converted_case: boolean;
  comments_count: number;
  comments: Comment[];
}

interface CommunityClientProps {
  initialPosts: Post[];
  locale: string;
}

export function CommunityClient({ initialPosts, locale }: CommunityClientProps) {
  const isBangla = locale === 'bn';
  const [posts, setPosts] = useState<Post[]>(initialPosts);
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [meTooTrack, setMeTooTrack] = useState<Record<string, boolean>>({});

  // New post modal / state
  const [showNewPost, setShowNewPost] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newStory, setNewStory] = useState('');
  const [newMerchant, setNewMerchant] = useState('');
  const [newAmount, setNewAmount] = useState('');
  const [newCategory, setNewCategory] = useState('E-Commerce');
  const [submitting, setSubmitting] = useState(false);

  // New comment state per post
  const [commentInputs, setCommentInputs] = useState<Record<string, string>>({});

  const categories = ['All', 'E-Commerce', 'MFS / Fintech', 'Retail', 'Telecom / ISP'];

  const handleMeToo = async (postId: string) => {
    if (meTooTrack[postId]) return;
    try {
      const res = await apiFetch(`/api/v1/community/posts/${postId}/me-too`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setPosts((prev) =>
          prev.map((p) => (p.id === postId ? { ...p, me_too_count: data.me_too_count } : p))
        );
        setMeTooTrack((prev) => ({ ...prev, [postId]: true }));
      }
    } catch {}
  };

  const handleAddComment = async (postId: string) => {
    const text = commentInputs[postId]?.trim();
    if (!text) return;

    try {
      const res = await apiFetch(`/api/v1/community/posts/${postId}/comments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          author_name: isBangla ? 'সচেতন ভোক্তা' : 'Concerned Citizen',
          content: text,
        }),
      });

      if (res.ok) {
        const newC = await res.json();
        setPosts((prev) =>
          prev.map((p) =>
            p.id === postId
              ? {
                  ...p,
                  comments_count: p.comments_count + 1,
                  comments: [...p.comments, newC],
                }
              : p
          )
        );
        setCommentInputs((prev) => ({ ...prev, [postId]: '' }));
      }
    } catch {}
  };

  const handleCreatePost = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim() || !newStory.trim()) return;

    setSubmitting(true);
    try {
      const res = await apiFetch('/api/v1/community/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: newTitle,
          story: newStory,
          merchant_name: newMerchant || 'Unknown Merchant',
          category: newCategory,
          disputed_amount_bdt: parseFloat(newAmount) || 0,
        }),
      });

      if (res.ok) {
        const created = await res.json();
        setPosts((prev) => [created, ...prev]);
        setShowNewPost(false);
        setNewTitle('');
        setNewStory('');
        setNewMerchant('');
        setNewAmount('');
      }
    } finally {
      setSubmitting(false);
    }
  };

  const filteredPosts =
    selectedCategory === 'All'
      ? posts
      : posts.filter((p) => p.category.toLowerCase().includes(selectedCategory.toLowerCase()));

  return (
    <div className="space-y-8">
      {/* Top Banner & Post Creator Button */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl bg-surface border border-border shadow-xs">
        <div className="space-y-1">
          <h2 className="text-xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Users className="w-5 h-5 text-primary" />
            <span>{isBangla ? 'ভোক্তা অধিকার সহায়তা ও অভিজ্ঞতা বিনিময়' : 'Consumer Mutual Help & Community Voice'}</span>
          </h2>
          <p className="text-xs text-muted-foreground leading-relaxed">
            {isBangla
              ? 'প্রতারিত হয়েছেন বা কোনো সমাধান খুঁজে পাচ্ছেন না? পোস্ট করে অন্য ভোক্তাদের অভিজ্ঞতা ও পরামর্শ জানুন।'
              : 'Share your dispute, ask for community advice, or connect with other consumers facing the same merchant.'}
          </p>
        </div>

        <Button
          variant="primary"
          className="gap-2 shrink-0 text-xs"
          onClick={() => setShowNewPost(!showNewPost)}
        >
          <MessageSquare className="w-4 h-4" />
          <span>{isBangla ? 'কমিউনিটিতে প্রশ্ন/পোস্ট করুন' : 'Post Your Question / Story'}</span>
        </Button>
      </div>

      {/* New Post Modal / Card */}
      {showNewPost && (
        <form
          onSubmit={handleCreatePost}
          className="p-6 rounded-2xl bg-surface border-2 border-primary/40 shadow-md space-y-4 animate-in fade-in duration-150"
        >
          <div className="flex items-center justify-between pb-3 border-b border-border">
            <h3 className="font-bold text-base text-foreground">
              {isBangla ? 'নতুন অভিযোগ বা প্রশ্ন লিখুন' : 'Ask Community for Advice'}
            </h3>
            <button
              type="button"
              onClick={() => setShowNewPost(false)}
              className="text-xs text-muted-foreground hover:text-foreground"
            >
              ✕ {isBangla ? 'বাতিল' : 'Cancel'}
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            <div>
              <label className="font-semibold text-foreground block mb-1">
                {isBangla ? 'শিরোনাম / মূল সমস্যা:' : 'Title / Main Issue:'}
              </label>
              <input
                type="text"
                required
                placeholder={isBangla ? 'যেমন: দারাজে টাকা কেটেছে কিন্তু পণ্য আসেনি...' : 'e.g., Paid advance on Facebook page but blocked...'}
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                className="w-full p-2.5 rounded-xl border border-border bg-elevated/40 text-foreground"
              />
            </div>

            <div>
              <label className="font-semibold text-foreground block mb-1">
                {isBangla ? 'মার্চেন্ট / প্রতিষ্ঠানের নাম:' : 'Merchant / Shop Name:'}
              </label>
              <input
                type="text"
                placeholder={isBangla ? 'যেমন: Daraz, Gadget Zone BD' : 'e.g., Daraz, Gadget Zone BD'}
                value={newMerchant}
                onChange={(e) => setNewMerchant(e.target.value)}
                className="w-full p-2.5 rounded-xl border border-border bg-elevated/40 text-foreground"
              />
            </div>

            <div>
              <label className="font-semibold text-foreground block mb-1">
                {isBangla ? 'অভিযোগের ক্যাটাগরি:' : 'Category:'}
              </label>
              <select
                value={newCategory}
                onChange={(e) => setNewCategory(e.target.value)}
                className="w-full p-2.5 rounded-xl border border-border bg-elevated/40 text-foreground"
              >
                <option value="E-Commerce">E-Commerce / ফ-কমার্স</option>
                <option value="MFS / Fintech">MFS / Fintech (বিকাশ, নগদ)</option>
                <option value="Retail">Retail Goods / অফলাইন দোকান</option>
                <option value="Telecom / ISP">Telecom / ISP ব্রডব্যান্ড</option>
              </select>
            </div>

            <div>
              <label className="font-semibold text-foreground block mb-1">
                {isBangla ? 'বিরোধের মোট টাকা (টাকায়):' : 'Disputed Amount (BDT):'}
              </label>
              <input
                type="number"
                placeholder="5500"
                value={newAmount}
                onChange={(e) => setNewAmount(e.target.value)}
                className="w-full p-2.5 rounded-xl border border-border bg-elevated/40 text-foreground"
              />
            </div>
          </div>

          <div>
            <label className="font-semibold text-foreground block mb-1 text-xs">
              {isBangla ? 'ঘটনার বিস্তারিত বিবরণ:' : 'Full Story / Details:'}
            </label>
            <textarea
              required
              rows={3}
              placeholder={isBangla ? 'কী ঘটেছে, কত তারিখে অর্ডার করেছিলেন, এবং বিক্রেতা কী প্রতিক্রিয়া জানিয়েছে তা লিখুন...' : 'Describe what happened, dates, and merchant responses...'}
              value={newStory}
              onChange={(e) => setNewStory(e.target.value)}
              className="w-full p-2.5 rounded-xl border border-border bg-elevated/40 text-foreground text-xs"
            />
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <Button
              type="submit"
              variant="primary"
              size="sm"
              disabled={submitting}
              className="gap-2"
            >
              <Send className="w-3.5 h-3.5" />
              <span>{submitting ? (isBangla ? 'পোস্ট হচ্ছে...' : 'Posting...') : (isBangla ? 'পোস্ট প্রকাশ করুন' : 'Publish Post')}</span>
            </Button>
          </div>
        </form>
      )}

      {/* Category Filter Pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
        <span className="font-semibold text-muted-foreground flex items-center gap-1 shrink-0">
          <Filter className="w-3.5 h-3.5" />
          <span>{isBangla ? 'ফিল্টার:' : 'Filter:'}</span>
        </span>
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-3.5 py-1.5 rounded-full font-semibold transition shrink-0 ${
              selectedCategory === cat
                ? 'bg-primary text-primary-foreground shadow-2xs'
                : 'bg-surface border border-border text-muted-foreground hover:text-foreground'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Feed of Posts */}
      <div className="space-y-6">
        {filteredPosts.map((post) => (
          <Card key={post.id} className="border border-border bg-surface shadow-2xs hover:shadow-xs transition">
            <CardHeader className="pb-3">
              <div className="flex flex-wrap items-center justify-between gap-2 mb-1.5">
                <div className="flex items-center gap-2">
                  <Badge variant="brand">{post.category}</Badge>
                  <span className="text-xs text-muted-foreground">· {post.created_at}</span>
                  <span className="text-xs text-muted-foreground font-medium">· {post.author_name}</span>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-foreground bg-elevated/80 px-2.5 py-1 rounded-lg border border-border/60">
                    {post.merchant_name}
                  </span>
                  {post.disputed_amount_bdt > 0 && (
                    <span className="text-xs font-extrabold text-primary bg-[var(--brand-soft)] px-2.5 py-1 rounded-lg">
                      ৳{post.disputed_amount_bdt.toLocaleString(isBangla ? 'bn-BD' : 'en-US')}
                    </span>
                  )}
                </div>
              </div>

              <CardTitle className="text-base sm:text-lg font-bold text-foreground">
                {post.title}
              </CardTitle>
            </CardHeader>

            <CardContent className="space-y-4 text-xs pt-0">
              <p className="text-foreground/90 leading-relaxed text-xs sm:text-sm">
                {post.story}
              </p>

              {/* Action Buttons Row */}
              <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-border">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleMeToo(post.id)}
                    className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs font-semibold transition ${
                      meTooTrack[post.id]
                        ? 'bg-[var(--danger-soft)] text-[var(--danger-ink)] border-[var(--danger-ink)]/30'
                        : 'bg-surface text-muted-foreground border-border hover:text-foreground hover:bg-elevated'
                    }`}
                  >
                    <Heart className={`w-3.5 h-3.5 ${meTooTrack[post.id] ? 'fill-current' : ''}`} />
                    <span>
                      {isBangla ? 'আমার সাথেও হয়েছে' : 'Me Too'} ({post.me_too_count})
                    </span>
                  </button>

                  <span className="text-muted-foreground flex items-center gap-1 text-xs">
                    <MessageSquare className="w-3.5 h-3.5" />
                    <span>
                      {post.comments_count} {isBangla ? 'টি পরামর্শ' : 'Advice'}
                    </span>
                  </span>
                </div>

                {/* 1-Click Convert to Formal ClaimCraft Case */}
                <Link
                  href={`/${locale}/cases/new?prefill_title=${encodeURIComponent(post.title)}&prefill_merchant=${encodeURIComponent(post.merchant_name)}&prefill_story=${encodeURIComponent(post.story)}`}
                  className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-primary text-primary-foreground font-bold text-xs hover:opacity-90 shadow-2xs transition"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>{isBangla ? '🤖 AI দিয়ে এই অভিযোগের কেস খুলুন' : '🤖 Convert into Legal Case'}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>

              {/* Comments Section */}
              {post.comments.length > 0 && (
                <div className="pt-3 border-t border-border/60 space-y-2">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground block">
                    {isBangla ? 'কমিউনিটি ও আইনি ভলান্টিয়ারদের পরামর্শ:' : 'Community & Legal Volunteer Advice:'}
                  </span>
                  <div className="space-y-2">
                    {post.comments.map((c) => (
                      <div
                        key={c.id}
                        className={`p-3 rounded-xl border text-xs leading-relaxed space-y-1 ${
                          c.is_legal_volunteer
                            ? 'bg-[var(--brand-soft)]/60 border-primary/30'
                            : 'bg-elevated/40 border-border/60'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-foreground flex items-center gap-1.5">
                            {c.is_legal_volunteer && (
                              <CheckCircle2 className="w-3.5 h-3.5 text-primary shrink-0" />
                            )}
                            <span>{c.author_name}</span>
                            {c.is_legal_volunteer && (
                              <Badge variant="brand" className="text-[9px] py-0">
                                {isBangla ? 'আইনি ভলান্টিয়ার' : 'Legal Volunteer'}
                              </Badge>
                            )}
                          </span>
                          <span className="text-[10px] text-muted-foreground">{c.created_at}</span>
                        </div>
                        <p className="text-foreground/90">{c.content}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Add Comment Input */}
              <div className="flex items-center gap-2 pt-2">
                <input
                  type="text"
                  placeholder={isBangla ? 'আপনার পরামর্শ বা অভিজ্ঞতা লিখুন...' : 'Write your advice or solution...'}
                  value={commentInputs[post.id] || ''}
                  onChange={(e) => setCommentInputs({ ...commentInputs, [post.id]: e.target.value })}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      handleAddComment(post.id);
                    }
                  }}
                  className="flex-1 p-2 rounded-xl border border-border bg-elevated/40 text-xs text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
                />
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleAddComment(post.id)}
                  className="shrink-0"
                >
                  <Send className="w-3.5 h-3.5" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

