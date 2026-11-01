from enum import Enum
from typing import Any

from pydantic import BaseModel

from app.policy.ast import (
    AllNode,
    AnyNode,
    ConditionNode,
    DateCompareNode,
    EqNode,
    ExistsNode,
    InNode,
    Kleene,
    MoneyCompareNode,
    NotNode,
    PolicyRule,
    ReviewAcceptedNode,
    SourceApprovedNode,
)


class RouteStatus(str, Enum):
    SUPPORTED = "supported"
    EXCLUDED = "excluded"
    NEEDS_FACTS = "needs_facts"
    NEEDS_REVIEW = "needs_review"
    SOURCE_CAUTION = "source_caution"
    NOT_SUPPORTED = "not_supported"


class EvaluationTraceItem(BaseModel):
    node_type: str
    fact: str | None = None
    inspected_value: Any = None
    outcome: Kleene
    details: str | None = None


class RuleEvaluationResult(BaseModel):
    rule_id: str
    status: RouteStatus
    condition_outcome: Kleene
    has_unresolved_exclusion: bool
    reasons: list[str]
    allowed_actions: list[str]
    trace: list[EvaluationTraceItem]


class PolicyEvaluator:
    @classmethod
    def evaluate_node(
        cls,
        node: ConditionNode,
        facts: dict[str, Any],
        approved_sources: list[str] | None = None,
        trace: list[EvaluationTraceItem] | None = None,
    ) -> Kleene:
        """Evaluates a single typed condition node using Kleene three-valued logic."""
        if isinstance(node, EqNode):
            fact_val = facts.get(node.fact)
            if fact_val is None:
                res = Kleene.UNKNOWN
            else:
                res = Kleene.TRUE if fact_val == node.value else Kleene.FALSE
            if trace is not None:
                trace.append(
                    EvaluationTraceItem(
                        node_type="eq",
                        fact=node.fact,
                        inspected_value=fact_val,
                        outcome=res,
                        details=f"expected {node.value}",
                    )
                )
            return res

        elif isinstance(node, InNode):
            fact_val = facts.get(node.fact)
            if fact_val is None:
                res = Kleene.UNKNOWN
            else:
                res = Kleene.TRUE if fact_val in node.values else Kleene.FALSE
            if trace is not None:
                trace.append(
                    EvaluationTraceItem(
                        node_type="in",
                        fact=node.fact,
                        inspected_value=fact_val,
                        outcome=res,
                    )
                )
            return res

        elif isinstance(node, ExistsNode):
            fact_val = facts.get(node.fact)
            res = Kleene.TRUE if fact_val is not None else Kleene.FALSE
            if trace is not None:
                trace.append(
                    EvaluationTraceItem(
                        node_type="exists",
                        fact=node.fact,
                        inspected_value=fact_val,
                        outcome=res,
                    )
                )
            return res

        elif isinstance(node, DateCompareNode):
            fact_val = facts.get(node.fact)
            if not fact_val:
                res = Kleene.UNKNOWN
            else:
                # Lexicographical comparison for ISO date strings YYYY-MM-DD
                v_str = str(fact_val)
                op = node.op
                if op == "<":
                    res = Kleene.TRUE if v_str < node.value else Kleene.FALSE
                elif op == "<=":
                    res = Kleene.TRUE if v_str <= node.value else Kleene.FALSE
                elif op == ">":
                    res = Kleene.TRUE if v_str > node.value else Kleene.FALSE
                elif op == ">=":
                    res = Kleene.TRUE if v_str >= node.value else Kleene.FALSE
                else:
                    res = Kleene.TRUE if v_str == node.value else Kleene.FALSE
            if trace is not None:
                trace.append(
                    EvaluationTraceItem(
                        node_type="date_compare",
                        fact=node.fact,
                        inspected_value=fact_val,
                        outcome=res,
                    )
                )
            return res

        elif isinstance(node, MoneyCompareNode):
            fact_val = facts.get(node.fact)
            if fact_val is None:
                res = Kleene.UNKNOWN
            else:
                # Assume minor_units in fact or dict
                val_units = (
                    fact_val if isinstance(fact_val, int) else fact_val.get("minor_units", 0)
                )
                op = node.op
                if op == "<":
                    res = Kleene.TRUE if val_units < node.minor_units else Kleene.FALSE
                elif op == "<=":
                    res = Kleene.TRUE if val_units <= node.minor_units else Kleene.FALSE
                elif op == ">":
                    res = Kleene.TRUE if val_units > node.minor_units else Kleene.FALSE
                elif op == ">=":
                    res = Kleene.TRUE if val_units >= node.minor_units else Kleene.FALSE
                else:
                    res = Kleene.TRUE if val_units == node.minor_units else Kleene.FALSE
            if trace is not None:
                trace.append(
                    EvaluationTraceItem(
                        node_type="money_compare",
                        fact=node.fact,
                        inspected_value=fact_val,
                        outcome=res,
                    )
                )
            return res

        elif isinstance(node, SourceApprovedNode):
            sources = approved_sources or []
            res = Kleene.TRUE if node.source_id in sources else Kleene.FALSE
            if trace is not None:
                trace.append(
                    EvaluationTraceItem(
                        node_type="source_approved",
                        fact=node.source_id,
                        inspected_value=sources,
                        outcome=res,
                    )
                )
            return res

        elif isinstance(node, ReviewAcceptedNode):
            review_state = facts.get(f"{node.assertion_field}_review_status")
            if not review_state:
                res = Kleene.UNKNOWN
            else:
                res = Kleene.TRUE if review_state == "accepted" else Kleene.FALSE
            if trace is not None:
                trace.append(
                    EvaluationTraceItem(
                        node_type="review_accepted",
                        fact=node.assertion_field,
                        inspected_value=review_state,
                        outcome=res,
                    )
                )
            return res

        elif isinstance(node, NotNode):
            child_res = cls.evaluate_node(node.condition, facts, approved_sources, trace)
            return Kleene.not_val(child_res)

        elif isinstance(node, AllNode):
            child_results = [cls.evaluate_node(c, facts, approved_sources, trace) for c in node.all]
            return Kleene.and_all(child_results)

        elif isinstance(node, AnyNode):
            child_results = [cls.evaluate_node(c, facts, approved_sources, trace) for c in node.any]
            return Kleene.or_any(child_results)

        raise ValueError(f"Unknown condition node type: {type(node)}")

    @classmethod
    def evaluate(
        cls,
        rule: PolicyRule,
        facts: dict[str, Any],
        approved_sources: list[str] | None = None,
        source_health: dict[str, str] | None = None,
        allow_test_only: bool = False,
    ) -> RuleEvaluationResult:
        """Evaluates a policy rule against facts, checking exclusions, 3-valued conditions, and source health."""
        # T18: test_only rules cannot run in live production release
        if rule.status == "test_only" and not allow_test_only:
            raise ValueError(
                f"Rule '{rule.rule_id}' is marked test_only and cannot be activated in live release (T18)."
            )

        trace: list[EvaluationTraceItem] = []
        reasons: list[str] = []

        # 1. Evaluate exclusions first
        has_unresolved_exclusion = False
        for excl in rule.exclusions:
            excl_res = cls.evaluate_node(excl, facts, approved_sources, trace)
            if excl_res == Kleene.TRUE:
                reasons.append(rule.reason_templates.get("excluded", "route_statutorily_excluded"))
                return RuleEvaluationResult(
                    rule_id=rule.rule_id,
                    status=RouteStatus.EXCLUDED,
                    condition_outcome=Kleene.FALSE,
                    has_unresolved_exclusion=False,
                    reasons=reasons,
                    allowed_actions=[],
                    trace=trace,
                )
            elif excl_res == Kleene.UNKNOWN:
                has_unresolved_exclusion = True

        # 2. Evaluate conditions
        cond_res = cls.evaluate_node(rule.conditions, facts, approved_sources, trace)

        if cond_res == Kleene.FALSE:
            reasons.append(rule.reason_templates.get("not_supported", "conditions_not_satisfied"))
            status = RouteStatus.NOT_SUPPORTED
            actions = []

        elif cond_res == Kleene.UNKNOWN:
            reasons.append(rule.reason_templates.get("unknown", "more_facts_required"))
            status = RouteStatus.NEEDS_FACTS
            actions = rule.allowed_actions

        else:  # Kleene.TRUE
            if has_unresolved_exclusion:
                reasons.append(
                    rule.reason_templates.get(
                        "exclusion_uncertain", "unresolved_exclusion_needs_clarification"
                    )
                )
                status = RouteStatus.NEEDS_FACTS
                actions = rule.allowed_actions
            else:
                # Check source health overlay (T17)
                s_health = source_health or {}
                unhealthy = [
                    src
                    for src in rule.source_dependencies
                    if s_health.get(src)
                    in ("temporarily_unavailable", "conflicted", "emergency_disabled")
                ]
                if unhealthy:
                    reasons.append(f"source_health_caution: {', '.join(unhealthy)}")
                    status = RouteStatus.SOURCE_CAUTION
                    actions = rule.allowed_actions
                else:
                    reasons.append(
                        rule.reason_templates.get("supported", "procedural_pathway_supported")
                    )
                    status = RouteStatus.SUPPORTED
                    actions = rule.allowed_actions

        return RuleEvaluationResult(
            rule_id=rule.rule_id,
            status=status,
            condition_outcome=cond_res,
            has_unresolved_exclusion=has_unresolved_exclusion,
            reasons=reasons,
            allowed_actions=actions,
            trace=trace,
        )
