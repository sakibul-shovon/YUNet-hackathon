'use client';
import { AdminConsole } from '@/features/workspace/Admin';

/** Ebarki compatibility entry: keep one authorization-aware administration UI. */
export function AdminDashboardClient({ locale }: { locale: string }) { return <AdminConsole locale={locale} />; }
