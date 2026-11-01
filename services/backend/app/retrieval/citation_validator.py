"""T28, T29: Citation and Statement Validator.

Guarantees:
- Validates that every statutory citation referenced in user drafts, policy assessments,
  or exports corresponds to an existing, verified provision in the canonical corpus.
- Rejects fabricated citations (e.g. 'crpa:sec:999', 'fake_law:12').
- Rejects outdated provisions where the case incident date falls outside [effective_from, effective_to).
- Blocks generation or export if any citation fails reference integrity (T28).
"""

from typing import Any

from app.retrieval.provision_service import ProvisionService


class CitationValidationResult:
    def __init__(self, is_valid: bool, valid_citations: list[str], invalid_citations: list[dict[str, Any]]):
        self.is_valid = is_valid
        self.valid_citations = valid_citations
        self.invalid_citations = invalid_citations


class CitationValidator:
    """T28: Citation integrity enforcement engine."""

    @classmethod
    def validate_citations(
        cls,
        citation_handles: list[str],
        date_context: str | None = None,
        allowed_source_ids: set[str] | None = None,
    ) -> CitationValidationResult:
        valid: list[str] = []
        invalid: list[dict[str, Any]] = []

        for handle in citation_handles:
            # 1. Check existence via ProvisionService
            res = ProvisionService.lookup_exact_provision(handle)
            if not res.match_found or not res.provision:
                invalid.append({
                    "citation": handle,
                    "code": "CITATION_NON_EXISTENT",
                    "reason_en": f"Citation '{handle}' does not exist in governed statutory corpus.",
                    "reason_bn": f"উদ্ধৃতি '{handle}' সরকার-অনুমোদিত বিধিবদ্ধ করপাসে বিদ্যমান নেই।",
                })
                continue

            prov = res.provision

            # 2. Check source scope filter
            if allowed_source_ids and prov.source_id not in allowed_source_ids:
                invalid.append({
                    "citation": handle,
                    "code": "CITATION_OUT_OF_SCOPE",
                    "reason_en": f"Citation '{handle}' is outside the authorized procedural scope.",
                    "reason_bn": f"উদ্ধৃতি '{handle}' অনুমোদিত কার্যপ্রণালী পরিধির বাইরে।",
                })
                continue

            # 3. Check temporal validity interval (T28 Invariant: Outdated laws block output)
            if date_context:
                eff_from = prov.effective_from
                eff_to = prov.effective_to
                if eff_from and date_context < eff_from:
                    invalid.append({
                        "citation": handle,
                        "code": "CITATION_NOT_YET_EFFECTIVE",
                        "reason_en": f"Provision was not yet in force on incident date ({date_context} < {eff_from}).",
                        "reason_bn": f"ঘটনার তারিখে বিধানটি কার্যকর ছিল না ({date_context} < {eff_from})।",
                    })
                    continue
                if eff_to and date_context >= eff_to:
                    invalid.append({
                        "citation": handle,
                        "code": "CITATION_OUTDATED_OR_REPEALED",
                        "reason_en": f"Provision was repealed or superseded before incident date ({date_context} >= {eff_to}).",
                        "reason_bn": f"ঘটনার তারিখের পূর্বেই বিধানটি বাতিল বা প্রতিস্থাপিত হয়েছিল ({date_context} >= {eff_to})।",
                    })
                    continue

            valid.append(handle)

        is_all_valid = (len(invalid) == 0)
        return CitationValidationResult(
            is_valid=is_all_valid,
            valid_citations=valid,
            invalid_citations=invalid,
        )
