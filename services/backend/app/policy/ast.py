from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class Kleene(str, Enum):
    TRUE = "TRUE"
    FALSE = "FALSE"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_bool(cls, val: bool | None) -> "Kleene":
        if val is None:
            return cls.UNKNOWN
        return cls.TRUE if val else cls.FALSE

    @classmethod
    def and_all(cls, items: list["Kleene"]) -> "Kleene":
        """Three-valued Kleene AND:

        - Any FALSE -> FALSE
        - All TRUE -> TRUE
        - Otherwise (contains UNKNOWN and no FALSE) -> UNKNOWN
        """
        if not items:
            return cls.TRUE
        if any(x == cls.FALSE for x in items):
            return cls.FALSE
        if all(x == cls.TRUE for x in items):
            return cls.TRUE
        return cls.UNKNOWN

    @classmethod
    def or_any(cls, items: list["Kleene"]) -> "Kleene":
        """Three-valued Kleene OR:

        - Any TRUE -> TRUE
        - All FALSE -> FALSE
        - Otherwise -> UNKNOWN
        """
        if not items:
            return cls.FALSE
        if any(x == cls.TRUE for x in items):
            return cls.TRUE
        if all(x == cls.FALSE for x in items):
            return cls.FALSE
        return cls.UNKNOWN

    @classmethod
    def not_val(cls, item: "Kleene") -> "Kleene":
        """Three-valued Kleene NOT:

        - not(TRUE) = FALSE
        - not(FALSE) = TRUE
        - not(UNKNOWN) = UNKNOWN
        """
        if item == cls.TRUE:
            return cls.FALSE
        if item == cls.FALSE:
            return cls.TRUE
        return cls.UNKNOWN


# --- Typed AST Condition Nodes ---


class ASTNode(BaseModel):
    pass


class EqNode(ASTNode):
    fact: str
    value: Any


class InNode(ASTNode):
    fact: str
    values: list[Any]


class ExistsNode(ASTNode):
    fact: str


class DateCompareNode(ASTNode):
    fact: str
    op: str = Field(..., pattern="^(<|<=|>|>=|==)$")
    value: str  # ISO date string YYYY-MM-DD


class MoneyCompareNode(ASTNode):
    fact: str
    op: str = Field(..., pattern="^(<|<=|>|>=|==)$")
    minor_units: int
    currency: str = "BDT"


class SourceApprovedNode(ASTNode):
    source_id: str


class ReviewAcceptedNode(ASTNode):
    assertion_field: str


class HasVerifiedExternalRecordNode(ASTNode):
    record_type: str


def parse_condition_node(v: Any) -> Any:
    """Recursively converts operator-tagged dictionaries (e.g. {'eq': {...}}) into typed AST nodes."""
    if isinstance(v, ASTNode):
        return v
    if isinstance(v, dict):
        if "eq" in v and len(v) == 1:
            return EqNode.model_validate(v["eq"])
        if "in" in v and len(v) == 1:
            return InNode.model_validate(v["in"])
        if "exists" in v and len(v) == 1:
            return ExistsNode.model_validate(v["exists"])
        if "date_compare" in v and len(v) == 1:
            return DateCompareNode.model_validate(v["date_compare"])
        if "money_compare" in v and len(v) == 1:
            return MoneyCompareNode.model_validate(v["money_compare"])
        if "source_approved" in v and len(v) == 1:
            return SourceApprovedNode.model_validate(v["source_approved"])
        if "review_accepted" in v and len(v) == 1:
            return ReviewAcceptedNode.model_validate(v["review_accepted"])
        if "has_verified_record" in v and len(v) == 1:
            return HasVerifiedExternalRecordNode.model_validate(v["has_verified_record"])
        if "not" in v and len(v) == 1:
            return NotNode(condition=parse_condition_node(v["not"]))
        if "all" in v and len(v) == 1:
            return AllNode(all=[parse_condition_node(c) for c in v["all"]])
        if "any" in v and len(v) == 1:
            return AnyNode(any=[parse_condition_node(c) for c in v["any"]])
    return v


class NotNode(ASTNode):
    condition: "ConditionNode"

    @model_validator(mode="before")
    @classmethod
    def normalize_item(cls, data: Any) -> Any:
        if isinstance(data, dict) and "condition" in data:
            data["condition"] = parse_condition_node(data["condition"])
        return data


class AllNode(ASTNode):
    all: list["ConditionNode"]

    @model_validator(mode="before")
    @classmethod
    def normalize_items(cls, data: Any) -> Any:
        if isinstance(data, dict) and "all" in data and isinstance(data["all"], list):
            data["all"] = [parse_condition_node(c) for c in data["all"]]
        return data


class AnyNode(ASTNode):
    any: list["ConditionNode"]

    @model_validator(mode="before")
    @classmethod
    def normalize_items(cls, data: Any) -> Any:
        if isinstance(data, dict) and "any" in data and isinstance(data["any"], list):
            data["any"] = [parse_condition_node(c) for c in data["any"]]
        return data


ConditionNode = (
    AllNode
    | AnyNode
    | NotNode
    | EqNode
    | InNode
    | ExistsNode
    | DateCompareNode
    | MoneyCompareNode
    | SourceApprovedNode
    | ReviewAcceptedNode
    | HasVerifiedExternalRecordNode
)

# Update forward refs
NotNode.model_rebuild()
AllNode.model_rebuild()
AnyNode.model_rebuild()


class PolicyRule(BaseModel):
    schema_version: str = "policy.v1"
    rule_id: str
    status: str = Field("active", pattern="^(active|test_only|draft)$")
    jurisdiction: str = "BD"
    issue_type: str
    date_basis: str = Field(
        "assessment_date", pattern="^(conduct_date|filing_date|assessment_date|review_required)$"
    )
    statutory_citations: list[str] = Field(default_factory=list)
    statutory_limitation_days: int | None = None
    supported_remedies: list[str] = Field(default_factory=list)
    unsupported_remedies: list[str] = Field(default_factory=list)
    source_dependencies: list[str] = Field(default_factory=list)
    conditions: ConditionNode
    exclusions: list[ConditionNode] = Field(default_factory=list)
    unknown_behavior: str = "ask_material_question"
    reason_templates: dict[str, str] = Field(default_factory=dict)
    allowed_actions: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def check_forbidden_constructs(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Enforce that no dangerous executable tags exist in dictionary
            forbidden = {"eval", "exec", "__import__", "subprocess", "os.system", "sh"}
            for k in data:
                if k in forbidden:
                    raise ValueError(f"Dangerous/executable keyword '{k}' forbidden in policy AST.")
            if "conditions" in data:
                data["conditions"] = parse_condition_node(data["conditions"])
            if "exclusions" in data and isinstance(data["exclusions"], list):
                data["exclusions"] = [parse_condition_node(x) for x in data["exclusions"]]
        return data
