import pytest
from pydantic import ValidationError

from app.policy.ast import (
    AllNode,
    AnyNode,
    EqNode,
    InNode,
    Kleene,
    NotNode,
    PolicyRule,
)
from app.policy.evaluator import PolicyEvaluator, RouteStatus


def test_t17_kleene_three_valued_truth_tables():
    """T17: Strict Kleene 3-valued logic truth tables."""
    # AND / ALL
    assert Kleene.and_all([Kleene.TRUE, Kleene.TRUE]) == Kleene.TRUE
    assert Kleene.and_all([Kleene.FALSE, Kleene.UNKNOWN]) == Kleene.FALSE
    assert Kleene.and_all([Kleene.TRUE, Kleene.UNKNOWN]) == Kleene.UNKNOWN
    assert Kleene.and_all([Kleene.UNKNOWN, Kleene.UNKNOWN]) == Kleene.UNKNOWN
    assert Kleene.and_all([Kleene.FALSE, Kleene.TRUE]) == Kleene.FALSE

    # OR / ANY
    assert Kleene.or_any([Kleene.TRUE, Kleene.FALSE]) == Kleene.TRUE
    assert Kleene.or_any([Kleene.TRUE, Kleene.UNKNOWN]) == Kleene.TRUE
    assert Kleene.or_any([Kleene.FALSE, Kleene.FALSE]) == Kleene.FALSE
    assert Kleene.or_any([Kleene.FALSE, Kleene.UNKNOWN]) == Kleene.UNKNOWN
    assert Kleene.or_any([Kleene.UNKNOWN, Kleene.UNKNOWN]) == Kleene.UNKNOWN

    # NOT
    assert Kleene.not_val(Kleene.TRUE) == Kleene.FALSE
    assert Kleene.not_val(Kleene.FALSE) == Kleene.TRUE
    assert Kleene.not_val(Kleene.UNKNOWN) == Kleene.UNKNOWN


def test_t17_missing_fact_remains_unknown_never_false():
    """T17: Missing fact evaluates strictly to UNKNOWN, never coerced to FALSE."""
    node = EqNode(fact="alleged_defect", value=True)

    # Empty facts dictionary
    res_missing = PolicyEvaluator.evaluate_node(node, facts={})
    assert res_missing == Kleene.UNKNOWN

    # Explicit False
    res_false = PolicyEvaluator.evaluate_node(node, facts={"alleged_defect": False})
    assert res_false == Kleene.FALSE

    # Explicit True
    res_true = PolicyEvaluator.evaluate_node(node, facts={"alleged_defect": True})
    assert res_true == Kleene.TRUE


def test_t17_exclusions_and_source_health_overlay():
    """T17: Exclusions and source-health overlays produce expected states."""
    rule = PolicyRule(
        rule_id="ecommerce.delivery_failure",
        status="active",
        issue_type="delivery_failure",
        source_dependencies=["bd_crpa_2009", "dncrp_ccms_portal"],
        conditions=AllNode(
            all=[
                EqNode(fact="goods_received", value=False),
                EqNode(fact="payment_confirmed", value=True),
            ]
        ),
        exclusions=[
            EqNode(fact="court_pending_litigation", value=True),
        ],
        reason_templates={
            "supported": "eligible_for_dncrp_complaint",
            "excluded": "matter_already_in_civil_court",
            "unknown": "need_delivery_confirmation",
        },
        allowed_actions=["prepare_dncrp_complaint"],
    )

    # Scenario 1: Fully satisfied, healthy sources -> SUPPORTED
    facts_valid = {
        "goods_received": False,
        "payment_confirmed": True,
        "court_pending_litigation": False,
    }
    res1 = PolicyEvaluator.evaluate(rule, facts_valid, source_health={"bd_crpa_2009": "current_check_passed"})
    assert res1.status == RouteStatus.SUPPORTED
    assert "prepare_dncrp_complaint" in res1.allowed_actions

    # Scenario 2: Active exclusion (e.g. pending in court) -> EXCLUDED
    facts_excluded = {
        "goods_received": False,
        "payment_confirmed": True,
        "court_pending_litigation": True,
    }
    res2 = PolicyEvaluator.evaluate(rule, facts_excluded)
    assert res2.status == RouteStatus.EXCLUDED
    assert "matter_already_in_civil_court" in res2.reasons

    # Scenario 3: Missing exclusion fact -> NEEDS_FACTS (unresolved exclusion)
    facts_uncertain_exclusion = {
        "goods_received": False,
        "payment_confirmed": True,
        # court_pending_litigation is missing -> UNKNOWN
    }
    res3 = PolicyEvaluator.evaluate(rule, facts_uncertain_exclusion)
    assert res3.status == RouteStatus.NEEDS_FACTS
    assert res3.has_unresolved_exclusion is True

    # Scenario 4: Dependent source is emergency_disabled -> SOURCE_CAUTION overlay
    res4 = PolicyEvaluator.evaluate(
        rule,
        facts_valid,
        source_health={"bd_crpa_2009": "emergency_disabled"},
    )
    assert res4.status == RouteStatus.SOURCE_CAUTION
    assert any("source_health_caution" in r for r in res4.reasons)


def test_t18_security_injection_and_test_only_rejection():
    """T18: Executable YAML/expression injection and test_only rules rejected."""
    # 1. Dangerous injection keywords rejected in AST
    with pytest.raises(ValidationError):
        PolicyRule.model_validate({
            "rule_id": "malicious_rule",
            "issue_type": "exploit",
            "eval": "os.system('rm -rf /')",
            "conditions": {"all": []},
        })

    with pytest.raises(ValidationError):
        PolicyRule.model_validate({
            "rule_id": "malicious_import",
            "issue_type": "exploit",
            "__import__": "subprocess",
            "conditions": {"all": []},
        })

    # 2. Unknown operator rejected
    with pytest.raises(ValidationError):
        PolicyRule.model_validate({
            "rule_id": "bad_op_rule",
            "issue_type": "unknown_op",
            "conditions": {"unknown_operator": {"fact": "x", "val": 1}},
        })

    # 3. test_only rule rejected in live release evaluation
    test_only_rule = PolicyRule(
        rule_id="experimental.provisional_rule",
        status="test_only",
        issue_type="experimental",
        conditions=EqNode(fact="is_test", value=True),
    )
    with pytest.raises(ValueError, match="marked test_only and cannot be activated"):
        PolicyEvaluator.evaluate(test_only_rule, facts={"is_test": True}, allow_test_only=False)

    # In explicit test mode (allow_test_only=True), evaluation succeeds
    res_test = PolicyEvaluator.evaluate(test_only_rule, facts={"is_test": True}, allow_test_only=True)
    assert res_test.status == RouteStatus.SUPPORTED

