"use client";

import React from "react";
import { AlertCircle, RefreshCw, ShieldAlert, FileQuestion } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";

export interface EvidenceRejectionProps {
  rejectionCode?: string | null;
  rejectionReason?: string | null;
  isRetryable?: boolean;
  guidanceEn?: string | null;
  guidanceBn?: string | null;
  locale?: string;
  onRetry?: () => void;
}

export const EvidenceItemRejectionBanner: React.FC<EvidenceRejectionProps> = ({
  rejectionCode = "MALWARE_OR_LIMIT_REJECTION",
  rejectionReason,
  isRetryable = false,
  guidanceEn,
  guidanceBn,
  locale = "en",
  onRetry,
}) => {
  const isBn = locale.startsWith("bn");

  // Determine icon & header based on code
  const getHeader = () => {
    switch (rejectionCode) {
      case "PIXEL_BOMB":
        return isBn ? "ছবিটি অত্যধিক বড় (পিক্সেল বোমা প্রতিরোধ)" : "Image Resolution Exceeds Limit (Pixel Bomb Prevention)";
      case "PDF_PAGE_LIMIT":
        return isBn ? "পিডিএফ পাতার সংখ্যা সীমা অতিক্রম করেছে" : "PDF Page Count Exceeds 50-Page Limit";
      case "PDF_ENCRYPTED":
        return isBn ? "পাসওয়ার্ড-সুরক্ষিত পিডিএফ ফাইল" : "Password-Protected / Encrypted PDF";
      case "ACTIVE_CONTENT_DETECTED":
        return isBn ? "সক্রিয় স্ক্রিপ্ট বা ক্ষতিকর কোড শনাক্ত হয়েছে" : "Active JavaScript / Executable Code Detected";
      case "SCANNER_OUTAGE":
        return isBn ? "স্ক্যানার সাময়িকভাবে অনুপলব্ধ (কোয়ারেন্টাইনে সংরক্ষিত)" : "Scanner Temporarily Unavailable (Safely Quarantined)";
      case "MIME_SPOOF":
        return isBn ? "ফাইলের ধরন অমিল (MIME স্পুফ প্রতিরোধ)" : "MIME Signature Mismatch (Spoof Prevention)";
      default:
        return isBn ? "ফাইলটি যাচাইকরণে বাতিল হয়েছে" : "Evidence Item Verification Failed";
    }
  };

  const guidanceText = isBn
    ? guidanceBn || guidanceEn || "অনুগ্রহ করে ফাইলটির সাইজ পরীক্ষা করুন বা পরিষ্কার ফরম্যাটে পুনরায় আপলোড করুন।"
    : guidanceEn || guidanceBn || "Please inspect your file or re-export to a clean static format before retrying.";

  return (
    <div
      role="alert"
      className={`rounded-lg border p-4 ${
        isRetryable
          ? "border-amber-300 bg-amber-50 dark:border-amber-800 dark:bg-amber-950/30 text-amber-950 dark:text-amber-200"
          : "border-red-300 bg-red-50 dark:border-red-800 dark:bg-red-950/30 text-red-950 dark:text-red-200"
      }`}
    >
      <div className="flex items-start gap-3">
        {isRetryable ? (
          <AlertCircle className="h-5 w-5 shrink-0 text-amber-600 dark:text-amber-400 mt-0.5" />
        ) : (
          <ShieldAlert className="h-5 w-5 shrink-0 text-red-600 dark:text-red-400 mt-0.5" />
        )}

        <div className="flex-1 space-y-1">
          <div className="flex items-center gap-2">
            <h4 className="font-semibold text-sm">{getHeader()}</h4>
            <Badge variant={isRetryable ? "warning" : "danger"}>
              {isRetryable
                ? isBn
                  ? "পুনরায় চেষ্টাযোগ্য"
                  : "Retryable"
                : isBn
                ? "বাতিল (অপরিবর্তনীয়)"
                : "Non-Retryable"}
            </Badge>
          </div>

          <p className="text-xs leading-relaxed opacity-90">{guidanceText}</p>

          {rejectionReason && (
            <p className="text-xs font-mono opacity-75 mt-1 bg-black/5 dark:bg-white/5 px-2 py-1 rounded inline-block">
              {rejectionReason}
            </p>
          )}

          {isRetryable && onRetry && (
            <div className="pt-2">
              <Button size="sm" variant="outline" onClick={onRetry} className="gap-1.5 text-xs">
                <RefreshCw className="h-3.5 w-3.5" />
                {isBn ? "পুনরায় যাচাই করুন" : "Retry Verification"}
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

