# ADR-109: Privacy, Deletion Suppression and Backup Recovery

## Context
Consumers must have the right to permanently delete their cases, attachments, and transcripts. Standard database backup restores could inadvertently restore previously deleted personal data.

## Decision
1. **Deletion Execution:** Case deletion immediately revokes session access, tombstones database records, deletes private storage objects, and cleans up derived OCR/ASR text.
2. **Deletion Suppression Manifest:** A cryptographic hash of deleted case IDs is retained in a minimal, append-only suppression register outside standard database backups.
3. **Restoration Safety:** Any database backup restoration script must re-apply the deletion suppression manifest before accepting incoming traffic.

