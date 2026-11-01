from pathlib import Path
import yaml
import pytest

from app.knowledge.source_registry import INITIAL_SOURCE_REGISTRY, get_source_by_id
from app.policy.ast import PolicyRule
from app.policy.evaluator import PolicyEvaluator, RouteStatus


def get_repo_root() -> Path:
    # services/backend/tests/unit/file.py -> repo root is 4 parents up
    return Path(__file__).resolve().parents[4]


def test_starter_rules_parse_into_typed_ast():
    root = get_repo_root()
    packs_dir = root / "knowledge" / "packs" / "bd"
    assert packs_dir.exists(), f"Directory {packs_dir} must exist"

    yaml_files = list(packs_dir.rglob("*.yaml"))
    assert len(yaml_files) >= 4, f"Expected at least 4 starter rule files, found {len(yaml_files)}"

    for yf in yaml_files:
        with open(yf, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        rule = PolicyRule.model_validate(data)
        assert rule.schema_version == "policy.v1"
        assert rule.jurisdiction == "BD"
        assert rule.rule_id is not None
        assert rule.issue_type is not None

        # Check source dependencies against registry
        for dep in rule.source_dependencies:
            source = get_source_by_id(dep)
            assert source is not None, f"Dependency '{dep}' in {yf.name} not found in INITIAL_SOURCE_REGISTRY"


def test_shopping_delivery_failure_evaluation():
    root = get_repo_root()
    rule_path = root / "knowledge" / "packs" / "bd" / "shopping" / "ecommerce_delivery_failure.yaml"
    with open(rule_path, "r", encoding="utf-8") as f:
        rule = PolicyRule.model_validate(yaml.safe_load(f))

    # Case 1: Fully eligible (SUPPORTED when conditions are true and exclusions are explicitly false)
    facts_eligible = {
        "purchase_channel": "ecommerce",
        "goods_delivered": False,
        "promised_delivery_date_passed": True,
        "refund_already_issued": False,
        "order_cancelled_by_buyer_before_dispatch": False,
    }
    res = PolicyEvaluator.evaluate(rule, facts_eligible)
    assert res.status == RouteStatus.SUPPORTED
    assert "prepare_merchant_notice" in res.allowed_actions

    # Case 2: Excluded because refund already issued
    facts_excluded = {
        "purchase_channel": "ecommerce",
        "goods_delivered": False,
        "promised_delivery_date_passed": True,
        "refund_already_issued": True,
        "order_cancelled_by_buyer_before_dispatch": False,
    }
    res = PolicyEvaluator.evaluate(rule, facts_excluded)
    assert res.status == RouteStatus.EXCLUDED
    assert "reasons.shopping.delivery_failure_excluded" in res.reasons

    # Case 3: Missing condition fact (promised date passed is unknown)
    facts_missing = {
        "purchase_channel": "ecommerce",
        "goods_delivered": False,
        "refund_already_issued": False,
        "order_cancelled_by_buyer_before_dispatch": False,
    }
    res = PolicyEvaluator.evaluate(rule, facts_missing)
    assert res.status == RouteStatus.NEEDS_FACTS
    assert "reasons.shopping.delivery_failure_needs_facts" in res.reasons

    # Case 4: Unresolved exclusion yields NEEDS_FACTS
    facts_unresolved_exclusion = {
        "purchase_channel": "ecommerce",
        "goods_delivered": False,
        "promised_delivery_date_passed": True,
        # refund_already_issued not provided -> UNKNOWN
    }
    res_excl = PolicyEvaluator.evaluate(rule, facts_unresolved_exclusion)
    assert res_excl.status == RouteStatus.NEEDS_FACTS


def test_finance_mfs_unauthorized_charge_evaluation():
    root = get_repo_root()
    rule_path = root / "knowledge" / "packs" / "bd" / "finance" / "mfs_unauthorized_charge.yaml"
    with open(rule_path, "r", encoding="utf-8") as f:
        rule = PolicyRule.model_validate(yaml.safe_load(f))

    # Case 1: Eligible for escalation (SUPPORTED when conditions are true and exclusions false)
    facts_eligible = {
        "payment_instrument_kind": "mfs_wallet",
        "transaction_unauthorized": True,
        "provider_ticket_filed": True,
        "otp_pin_voluntarily_shared_to_fraudster": False,
    }
    res = PolicyEvaluator.evaluate(rule, facts_eligible)
    assert res.status == RouteStatus.SUPPORTED
    assert "prepare_bb_cipc_escalation" in res.allowed_actions

    # Case 2: Excluded due to voluntary PIN disclosure
    facts_excluded = {
        "payment_instrument_kind": "mfs_wallet",
        "transaction_unauthorized": True,
        "provider_ticket_filed": True,
        "otp_pin_voluntarily_shared_to_fraudster": True,
    }
    res = PolicyEvaluator.evaluate(rule, facts_excluded)
    assert res.status == RouteStatus.EXCLUDED
    assert "reasons.finance.mfs_charge_excluded_pin_sharing" in res.reasons

    # Case 3: Unresolved exclusion yields NEEDS_FACTS
    facts_unresolved = {
        "payment_instrument_kind": "mfs_wallet",
        "transaction_unauthorized": True,
        "provider_ticket_filed": True,
        # otp_pin_voluntarily_shared_to_fraudster missing -> UNKNOWN
    }
    res_unresolved = PolicyEvaluator.evaluate(rule, facts_unresolved)
    assert res_unresolved.status == RouteStatus.NEEDS_FACTS


def test_source_cards_exist_and_contain_required_metadata():
    root = get_repo_root()
    cards_dir = root / "docs" / "knowledge" / "source_cards"
    assert cards_dir.exists()

    expected_cards = [
        "bd_crpa_2009.md",
        "dncrp_ccms.md",
        "bb_cipc.md",
        "bb_mfs_2022.md",
        "dncrp_hotline_16121.md",
    ]

    for card_name in expected_cards:
        card_file = cards_dir / card_name
        assert card_file.exists(), f"Source card {card_name} missing in {cards_dir}"
        content = card_file.read_text(encoding="utf-8")
        assert "## Metadata" in content
        assert "Source ID:" in content
        assert "Official URL:" in content
        assert "Procedural Scope:" in content
