import re
from typing import Any, ClassVar

from app.retrieval.provisions_data import CANONICAL_PROVISIONS
from app.retrieval.schemas import ProvisionLookupResult, ProvisionOut, ProvisionTreeItem

# Bengali numeral mapping
BN_TO_EN_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
EN_TO_BN_DIGITS = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")


class ProvisionService:
    """T24: Governed provision index, exact Bengali/Latin section parser, and qualification preservation."""

    _provisions_by_handle: ClassVar[dict[str, dict[str, Any]]] = {}
    _provisions_by_alias: ClassVar[dict[str, dict[str, Any]]] = {}

    @classmethod
    def _ensure_indexed(cls) -> None:
        if not cls._provisions_by_handle:
            for item in CANONICAL_PROVISIONS:
                handle = item["citation_handle"].lower()
                cls._provisions_by_handle[handle] = item

                # Map path
                path = item["provision_path"].lower()
                cls._provisions_by_alias[path] = item

                # Map all explicit aliases
                for alias in item.get("aliases", []):
                    norm = cls.normalize_lookup_key(alias)
                    cls._provisions_by_alias[norm] = item

    @classmethod
    def normalize_lookup_key(cls, key: str) -> str:
        """Normalizes Latin and Bengali section references into a canonical lookup key."""
        raw = key.strip().lower()
        translated = raw.translate(BN_TO_EN_DIGITS)

        # Stage patterns for BB CIPC ("স্তর ১", "stage:1", "stage:2", "স্তর-২")
        m_stage = re.search(r"(?:stage|স্তর)[\s:-]*([12১২])", raw)
        if m_stage:
            digit = m_stage.group(1).translate(BN_TO_EN_DIGITS)
            return "stage:provider_grievance" if digit == "1" else "stage:cipc_escalation"

        if "provider_grievance" in translated:
            return "stage:provider_grievance"
        if "cipc_escalation" in translated:
            return "stage:cipc_escalation"

        # Remove law name prefixes if present
        clean = re.sub(r"^(?:crpa2009|crpa|bd_crpa_2009|bb_cipc|bb)[:\s]+", "", translated)

        # 1. Section with subsection: "sec:45(2)", "ধারা ৪৫(২)", "ধারা ৪৫ এর ২", "45(2)"
        m_sub = re.search(r"(?:(?:ধারা|sec(?:tion)?)\s*[:\s]*)?(\d+)\s*(?:\((\d+)\)|এর\s*(\d+))", clean)
        if m_sub and (m_sub.group(2) or m_sub.group(3)):
            sec_num = m_sub.group(1)
            sub_num = m_sub.group(2) or m_sub.group(3)
            return f"sec:{sec_num}({sub_num})"

        # 2. Section with prefix: "sec:45", "ধারা ৪৫", "section 45", "ধারা: ৪৫"
        m_sec = re.search(r"(?:ধারা|sec(?:tion)?)\s*[:\s]*(\d+)", clean)
        if m_sec:
            sec_num = m_sec.group(1)
            return f"sec:{sec_num}"

        # 3. Standalone number: "45"
        if clean.isdigit():
            return f"sec:{clean}"

        # Fallback to normalized alphanumeric key
        return re.sub(r"[\s_]+", ":", clean)

    @classmethod
    def lookup_exact_provision(cls, query: str) -> ProvisionLookupResult:
        """T24: Exact Bengali/Latin section lookup.
        
        Guarantees:
        - Preserves subsections, parent context, and long Bengali qualifications/exceptions.
        - Never invents or hallucinates non-existent statutory provisions.
        """
        cls._ensure_indexed()
        norm_key = cls.normalize_lookup_key(query)

        # 1. Direct handle match
        matched_dict = cls._provisions_by_handle.get(query.lower())

        # 2. Alias match
        if not matched_dict:
            matched_dict = cls._provisions_by_alias.get(norm_key)

        # 3. Normalized alias direct comparison
        if not matched_dict:
            for alias, item in cls._provisions_by_alias.items():
                if alias == norm_key:
                    matched_dict = item
                    break

        if not matched_dict:
            # T24 Invariant: Non-existent sections must never be invented
            return ProvisionLookupResult(
                query=query,
                normalized_query=norm_key,
                match_found=False,
                provision=None,
                preserves_qualification=True,
            )

        # Attach parent context if subsection
        parent_dict = None
        if matched_dict.get("parent_path"):
            parent_key = matched_dict["parent_path"].lower()
            parent_raw = cls._provisions_by_alias.get(parent_key)
            if parent_raw:
                parent_dict = {
                    "citation_handle": parent_raw["citation_handle"],
                    "section_number": parent_raw["section_number"],
                    "section_bn": parent_raw["section_bn"],
                    "title_en": parent_raw["title_en"],
                    "title_bn": parent_raw["title_bn"],
                    "canonical_text_bn": parent_raw["canonical_text_bn"][:200] + "...",
                }

        provision_out = ProvisionOut(
            **matched_dict,
            parent_provision=parent_dict,
        )

        return ProvisionLookupResult(
            query=query,
            normalized_query=norm_key,
            match_found=True,
            provision=provision_out,
            preserves_qualification=len(provision_out.qualifications_and_exceptions) > 0,
        )

    @classmethod
    def get_provisions_tree(cls, source_id: str) -> list[ProvisionTreeItem]:
        """Builds a hierarchical tree of provisions for a source family."""
        cls._ensure_indexed()
        items = [p for p in CANONICAL_PROVISIONS if p["source_id"] == source_id]

        roots: list[ProvisionTreeItem] = []
        children_by_parent: dict[str, list[ProvisionTreeItem]] = {}

        for p in items:
            tree_item = ProvisionTreeItem(
                provision_path=p["provision_path"],
                citation_handle=p["citation_handle"],
                title_en=p["title_en"],
                title_bn=p["title_bn"],
                section_number=p["section_number"],
            )
            parent = p.get("parent_path")
            if parent:
                children_by_parent.setdefault(parent, []).append(tree_item)
            else:
                roots.append(tree_item)

        # Attach children
        for root in roots:
            if root.provision_path in children_by_parent:
                root.children = children_by_parent[root.provision_path]

        return roots
