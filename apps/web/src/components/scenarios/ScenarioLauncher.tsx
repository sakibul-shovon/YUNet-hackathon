'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Play, Loader2, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/Button';

interface ScenarioLauncherProps {
  scenarioId: string;
  locale: string;
  isBangla: boolean;
}

export function ScenarioLauncher({ scenarioId, locale, isBangla }: ScenarioLauncherProps) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const handleLaunch = async () => {
    try {
      setLoading(true);

      // Authenticate as guest if needed to establish session
      const authRes = await fetch('/api/v1/auth/guest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      const authData = await authRes.json();
      const token = authData.access_token;

      // Launch fresh isolated scenario
      const launchRes = await fetch(`/api/v1/scenarios/${scenarioId}/launch?locale=${locale}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
      });

      if (!launchRes.ok) {
        throw new Error('Failed to launch scenario');
      }

      const launchData = await launchRes.json();
      router.push(`/${locale}/cases/${launchData.case_id}`);
    } catch (err) {
      console.error('Launch failed:', err);
      // Fallback
      router.push(`/${locale}/cases/new`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button
      size="sm"
      variant="primary"
      onClick={handleLaunch}
      disabled={loading}
      className="inline-flex items-center gap-1.5 text-xs font-semibold"
    >
      {loading ? (
        <>
          <Loader2 className="w-3.5 h-3.5 animate-spin" />
          <span>{isBangla ? 'লোড হচ্ছে...' : 'Provisioning...'}</span>
        </>
      ) : (
        <>
          <Play className="w-3.5 h-3.5 fill-current" />
          <span>{isBangla ? 'লাইভ সিনারিও চালান' : 'Launch Live Scenario'}</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </>
      )}
    </Button>
  );
}
