import re
import uuid
from typing import Any, ClassVar

from pydantic import BaseModel, Field

from app.knowledge.models import SourceProvision

# Provision regex patterns for English and Bengali legislative texts
SECTION_REGEX_EN = re.compile(r"(?:Section|Sec\.)\s+(\d+(?:\([0-9a-zA-Z]+\))?)[:.\s]+(.*?)(?=(?:Section|Sec\.)\s+\d+|$)", re.DOTALL | re.IGNORECASE)
SECTION_REGEX_BN = re.compile(r"ধারা\s+([০-৯\d]+(?:\([০-৯a-zA-Z\d]+\))?)[:.\s]+(.*?)(?=ধারা\s+[০-৯\d]+|$)", re.DOTALL)


class ParsedProvision(BaseModel):
    provision_path: str
    title: str
    text_content: str
    normalized_text: str


class ProvisionDiffItem(BaseModel):
    provision_path: str
    title: str
    status: str  # 'added', 'modified', 'repealed', 'unchanged'
    old_text: str | None = None
    new_text: str | None = None
    diff_summary: str | None = None


class CandidateImpactProposal(BaseModel):
    candidate_id: uuid.UUID
    family_slug: str
    is_current_law: bool = False  # Invariant T43: Unapproved change is strictly NOT current law
    publication_date: str | None = None
    commencement_date: str | None = None
    commencement_status: str = "unknown"  # 'commenced', 'deferred_pending_gazette', 'unknown'
    has_transitional_clauses: bool = False
    transitional_notes: list[str] = Field(default_factory=list)
    impacted_rules: list[str] = Field(default_factory=list)
    impacted_domains: list[str] = Field(default_factory=list)
    provision_diffs: list[ProvisionDiffItem] = Field(default_factory=list)
    added_count: int = 0
    modified_count: int = 0
    repealed_count: int = 0
    unchanged_count: int = 0


class SectionAwareDiffService:
    """Performs structured section-aware legal diffs and candidate impact proposals (T43)."""

    # Provision to Policy Rule mapping knowledge base
    PROVISION_RULE_MAP: ClassVar[dict[str, dict[str, Any]]] = {
        "sec:45": {
            "rules": ["R-CRPA-S45-MISLEADING-PRICE", "R-CRPA-S45-OVERCHARGING"],
            "domains": ["consumer_ecommerce", "retail_goods"],
        },
        "sec:60": {
            "rules": ["R-CRPA-S60-LIMITATION-30D"],
            "domains": ["statutory_limitation", "consumer_ecommerce"],
        },
        "sec:76": {
            "rules": ["R-CRPA-S76-COMPLAINT-PROCEDURE", "R-CRPA-S76-REWARD-25PCT"],
            "domains": ["consumer_ecommerce", "retail_goods"],
        },
        "bb_cipc": {
            "rules": ["R-BB-CIPC-STAGE1-MANDATORY"],
            "domains": ["financial_services", "mfs_banking"],
        },
        "btrc_consumer": {
            "rules": ["R-BTRC-STAGE1-MANDATORY"],
            "domains": ["telecom_isp"],
        },
    }

    @classmethod
    def parse_provisions(cls, text: str, default_path_prefix: str = "sec") -> list[ParsedProvision]:
        """Extracts structured provisions from statutory or procedural text."""
        provisions: list[ParsedProvision] = []

        # 1. Try Bengali pattern
        matches_bn = list(SECTION_REGEX_BN.finditer(text))
        if matches_bn:
            for m in matches_bn:
                sec_num = m.group(1).strip()
                body = m.group(2).strip()
                first_line = body.split("\n")[0] if "\n" in body else body
                title = f"ধারা {sec_num}: {first_line[:80]}"
                normalized = " ".join(body.split())
                provisions.append(
                    ParsedProvision(
                        provision_path=f"sec:{sec_num}",
                        title=title,
                        text_content=body,
                        normalized_text=normalized,
                    )
                )
            return provisions

        # 2. Try English pattern
        matches_en = list(SECTION_REGEX_EN.finditer(text))
        if matches_en:
            for m in matches_en:
                sec_num = m.group(1).strip()
                body = m.group(2).strip()
                first_line = body.split("\n")[0] if "\n" in body else body
                title = f"Section {sec_num}: {first_line[:80]}"
                normalized = " ".join(body.split())
                provisions.append(
                    ParsedProvision(
                        provision_path=f"sec:{sec_num}",
                        title=title,
                        text_content=body,
                        normalized_text=normalized,
                    )
                )
            return provisions

        # 3. Fallback: Parse paragraphs / headings or create whole document provision
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        for idx, p in enumerate(paragraphs, start=1):
            first_line = p.split("\n")[0]
            normalized = " ".join(p.split())
            provisions.append(
                ParsedProvision(
                    provision_path=f"{default_path_prefix}:{idx}",
                    title=f"Clause {idx}: {first_line[:60]}",
                    text_content=p,
                    normalized_text=normalized,
                )
            )
        return provisions

    @classmethod
    def compute_diff(
        cls,
        candidate_id: uuid.UUID,
        family_slug: str,
        candidate_provisions: list[ParsedProvision],
        approved_provisions: list[SourceProvision],
        publication_date: str | None = None,
        commencement_date: str | None = None,
        candidate_raw_text: str = "",
    ) -> CandidateImpactProposal:
        """Computes provision-level diff and assesses downstream impact on rules (T43)."""
        approved_map = {p.provision_path: p for p in approved_provisions}
        candidate_map = {p.provision_path: p for p in candidate_provisions}

        diffs: list[ProvisionDiffItem] = []
        impacted_rules: set[str] = set()
        impacted_domains: set[str] = set()

        all_paths = sorted(set(approved_map.keys()) | set(candidate_map.keys()))

        added_cnt = 0
        mod_cnt = 0
        rep_cnt = 0
        unchanged_cnt = 0

        for path in all_paths:
            old_p = approved_map.get(path)
            new_p = candidate_map.get(path)

            if old_p and not new_p:
                # Repealed provision
                rep_cnt += 1
                diff_item = ProvisionDiffItem(
                    provision_path=path,
                    title=old_p.title,
                    status="repealed",
                    old_text=old_p.text_content,
                    diff_summary="Provision repealed or omitted in new candidate.",
                )
                diffs.append(diff_item)
                cls._map_rules_and_domains(path, impacted_rules, impacted_domains)

            elif new_p and not old_p:
                # Newly added provision
                added_cnt += 1
                diff_item = ProvisionDiffItem(
                    provision_path=path,
                    title=new_p.title,
                    status="added",
                    new_text=new_p.text_content,
                    diff_summary="New provision introduced in candidate.",
                )
                diffs.append(diff_item)
                cls._map_rules_and_domains(path, impacted_rules, impacted_domains)

            elif old_p and new_p:
                # Existing provision compared
                if old_p.normalized_text != new_p.normalized_text:
                    mod_cnt += 1
                    diff_summary = f"Text modified: length changed {len(old_p.normalized_text)} -> {len(new_p.normalized_text)} chars"
                    diff_item = ProvisionDiffItem(
                        provision_path=path,
                        title=new_p.title,
                        status="modified",
                        old_text=old_p.text_content,
                        new_text=new_p.text_content,
                        diff_summary=diff_summary,
                    )
                    diffs.append(diff_item)
                    cls._map_rules_and_domains(path, impacted_rules, impacted_domains)
                else:
                    unchanged_cnt += 1
                    diffs.append(
                        ProvisionDiffItem(
                            provision_path=path,
                            title=old_p.title,
                            status="unchanged",
                            old_text=old_p.text_content,
                            new_text=new_p.text_content,
                        )
                    )

        # Invariant T43: Commencement Date vs Enactment / Publication
        # Unknown commencement dates remain unknown and must NOT default to today.
        commencement_status = "unknown"
        if commencement_date:
            commencement_status = "commenced"
        else:
            # Check if candidate mentions deferred commencement
            lowered_text = candidate_raw_text.lower()
            if any(term in lowered_text for term in ["সরকারি গেজেটে প্রজ্ঞাপন দ্বারা", "shall come into force on such date", "appointed day", "notification in the official gazette"]):
                commencement_status = "deferred_pending_gazette"
            else:
                commencement_status = "unknown"

        # Check for savings / transitional clauses
        has_transitional = False
        transitional_notes = []
        lowered_text = candidate_raw_text.lower()
        if any(term in lowered_text for term in ["savings", "repeal and savings", "রহিতকরণ ও হেফাজত", "transitional"]):
            has_transitional = True
            transitional_notes.append("Transitional or savings provisions detected; historical acts remain governed under prior version.")

        return CandidateImpactProposal(
            candidate_id=candidate_id,
            family_slug=family_slug,
            is_current_law=False,  # Invariant T43: strictly false until officially reviewed and approved
            publication_date=publication_date,
            commencement_date=commencement_date,
            commencement_status=commencement_status,
            has_transitional_clauses=has_transitional,
            transitional_notes=transitional_notes,
            impacted_rules=sorted(impacted_rules),
            impacted_domains=sorted(impacted_domains),
            provision_diffs=diffs,
            added_count=added_cnt,
            modified_count=mod_cnt,
            repealed_count=rep_cnt,
            unchanged_count=unchanged_cnt,
        )

    @classmethod
    def _map_rules_and_domains(cls, path: str, rules_out: set[str], domains_out: set[str]) -> None:
        """Finds policy rules and domains bound to the provision path."""
        base_path = path.split("(")[0]  # e.g. sec:45(2) -> sec:45
        mapping = cls.PROVISION_RULE_MAP.get(base_path) or cls.PROVISION_RULE_MAP.get(path)
        if mapping:
            rules_out.update(mapping.get("rules", []))
            domains_out.update(mapping.get("domains", []))
