'use client';

import { usePathname } from 'next/navigation';
import { AICopilotDrawer } from '@/components/ai/AICopilotDrawer';
import { AgentCommandPalette } from '@/components/ai/AgentCommandPalette';
import { JudgeQuickStartDrawer } from '@/components/ai/JudgeQuickStartDrawer';

/** Keep the existing workspace tools out of the independent landing review. */
export function AppUtilities({ locale }: { locale: string }) {
  const pathname = usePathname();
  if (pathname === `/${locale}` || pathname === `/${locale}/`) return null;
  return <><AICopilotDrawer locale={locale} /><AgentCommandPalette locale={locale} /><JudgeQuickStartDrawer locale={locale} /></>;
}
