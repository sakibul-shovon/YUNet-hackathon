/**
 * Auto-generated ClaimCraft BD TypeScript API contracts.
 * DO NOT EDIT MANUALLY. Generated via: python scripts/tasks.py contracts
 */

export interface ApiLiveHealth {
  status: string;
  app: string;
  environment: string;
  version: string;
}

export interface ApiReadyHealth {
  status: string;
  app: string;
  environment: string;
  capabilities: {
    ai_provider: string;
    stt_provider: string;
    storage_backend: string;
  };
}

export interface ApiPing {
  message: string;
}

export interface ErrorResponse {
  error: {
    code: string;
    message: string;
    correlation_id?: string;
    details?: Record<string, unknown>;
  };
}
