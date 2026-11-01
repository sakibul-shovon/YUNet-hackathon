'use client';

import React, { useEffect, useState } from 'react';
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  ExternalLink,
  Layers,
  Radio,
  RefreshCw,
  Shield,
  ShieldAlert,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { apiFetch } from '@/lib/api';

interface SourceHealthItem {
  source_id: string;
  title_en: string;
  title_bn: string;
  official_url: string;
  document_type: string;
  status: string;
  health_status: string;
  procedural_scope: string;
  is_authoritative_for_penalties: boolean;
  notice?: string;
}

interface SourceHealthData {
  active_release_id: string | null;
  active_release_mode: string | null;
  active_manifest_hash: string | null;
  sources: SourceHealthItem[];
}

export function SourceHealthMonitor({ locale }: { locale: string }) {
  const isBangla = locale === 'bn';
  const [data, setData] = useState<SourceHealthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiFetch('/api/v1/knowledge/source-health');
      if (!res.ok) {
        throw new Error(`Failed to fetch source health: ${res.status}`);
      }
      const json = await res.json();
      setData(json);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  const getStatusBadge = (health: string) => {
    switch (health) {
      case 'current_check_passed':
        return (
          <Badge variant="success" className="flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" />
            <span>{isBangla ? 'যাচাইকৃত সচল' : 'Verified Current'}</span>
          </Badge>
        );
      case 'temporarily_unavailable':
        return (
          <Badge variant="warning" className="flex items-center gap-1">
            <AlertTriangle className="w-3 h-3" />
            <span>{isBangla ? 'সাময়িক অনুপলব্ধ' : 'Temporarily Unavailable'}</span>
          </Badge>
        );
      default:
        return (
          <Badge variant="neutral" className="flex items-center gap-1">
            <Activity className="w-3 h-3" />
            <span>{health}</span>
          </Badge>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner: Active Release Status */}
      <Card className="border-primary/20 bg-primary/5">
        <CardContent className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10 text-primary">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  {isBangla ? 'সক্রিয় আইনি রিলিজ' : 'Active Knowledge Release'}
                </span>
                <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono bg-primary/15 text-primary">
                  {data?.active_release_id || 'INIT-PROCEDURE-V1'}
                </span>
              </div>
              <p className="text-xs text-muted-foreground font-mono mt-0.5 truncate max-w-xs sm:max-w-md">
                SHA-256: {data?.active_manifest_hash ? `${data.active_manifest_hash.substring(0, 16)}...` : 'genesis-canonical-manifest'}
              </p>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchHealth}
            disabled={loading}
            className="self-start sm:self-auto text-xs flex items-center gap-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>{isBangla ? 'পুনরায় যাচাই' : 'Refresh Health'}</span>
          </Button>
        </CardContent>
      </Card>

      {/* Official Watcher Feeds List */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Radio className="w-4 h-4 text-primary animate-pulse" />
            <h3 className="text-sm font-semibold text-foreground">
              {isBangla ? 'স্বয়ংক্রিয় অফিশিয়াল ওয়াচার মনিটরিং' : 'Monitored Official Sources & Watchers'}
            </h3>
          </div>
          <span className="text-xs text-muted-foreground">
            {data?.sources?.length || 6} {isBangla ? 'টি উৎস পর্যবেক্ষণে' : 'sources tracked'}
          </span>
        </div>

        {error && (
          <div className="p-3 bg-destructive/10 border border-destructive/20 text-destructive text-xs rounded-lg flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div className="grid gap-3">
          {(data?.sources || []).map((src) => (
            <Card key={src.source_id} className="hover:border-border transition-colors">
              <CardContent className="p-4 flex flex-col md:flex-row md:items-center justify-between gap-3">
                <div className="space-y-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs font-semibold text-foreground">
                      {isBangla ? src.title_bn : src.title_en}
                    </span>
                    {getStatusBadge(src.health_status)}
                    {src.is_authoritative_for_penalties && (
                      <Badge variant="brand" className="text-[10px] py-0">
                        {isBangla ? 'দণ্ড আরোপে প্রযোজ্য' : 'Authoritative Penalties'}
                      </Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <span className="capitalize">{src.document_type.replace('_', ' ')}</span>
                    <span>•</span>
                    <span className="font-mono">{src.source_id}</span>
                  </div>
                  {src.notice && (
                    <p className="text-xs text-muted-foreground italic mt-1">
                      {src.notice}
                    </p>
                  )}
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <a
                    href={src.official_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-xs text-primary hover:underline font-medium"
                  >
                    <span>{isBangla ? 'অফিশিয়াল পোর্টাল' : 'Official Portal'}</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
