import { FactReview } from '@/features/workspace/Review';
export const metadata = { title: 'Ebarki' };
export default async function Page({params}:{params:Promise<{locale:string}>}){const {locale}=await params;return <FactReview locale={locale} />;}
