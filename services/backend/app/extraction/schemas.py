from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ALLOWED_DOMAINS = {
    "consumer_ecommerce",
    "retail_goods",
    "financial_services",
    "mfs_banking",
    "telecom_isp",
    "product_safety",
    "insurance",
    "government_grs",
}

ALLOWED_ISSUES = {
    "ecommerce_delivery_failure",
    "defective_goods",
    "mfs_unauthorized_charge",
    "product_safety_hazard",
    "telecom_billing_and_outage",
    "insurance_claim_dispute",
    "public_service_grievance",
    "other_consumer_dispute",
}

ALLOWED_FIELD_TYPES = {"money", "date", "boolean", "string", "select"}

ALLOWED_FIELD_NAMES = {
    "purchase_channel",
    "goods_delivered",
    "promised_delivery_date_passed",
    "refund_already_issued",
    "order_cancelled_by_buyer_before_dispatch",
    "goods_received_defective",
    "seller_notified_within_warranty",
    "user_inflicted_damage",
    "payment_instrument_kind",
    "transaction_unauthorized",
    "provider_ticket_filed",
    "otp_pin_voluntarily_shared_to_fraudster",
    "product_presents_immediate_hazard",
    "amount_paid",
    "incident_date",
    "merchant_name",
    "transaction_id",
    "order_id",
    # Telecom domain facts
    "telecom_provider_ticket_filed",
    "provider_response_overdue_or_unsatisfactory",
    "service_disruption_or_billing_error_documented",
    "issue_is_handset_hardware_only",
    "consumer_has_unpaid_due_prior_to_dispute",
    "provider_ticket_number",
    # Insurance domain facts
    "insurance_policy_documented",
    "formal_claim_submitted_to_insurer",
    "claim_denied_or_settlement_delayed_over_90d",
    "subject_of_ongoing_court_litigation",
    "fraudulent_misrepresentation_admitted",
    "claim_reference",
    # GRS domain facts
    "public_service_request_submitted",
    "citizen_charter_timeline_exceeded",
    "relevant_office_contacted_first",
    "service_cadre_discipline_or_promotion",
    "alternative_statutory_appeal_pending",
}


class TextSpan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    span_id: str = Field(..., pattern=r"^span_\d+$")
    text: str = Field(..., min_length=1, max_length=1000)
    start_offset: int = Field(..., ge=0)
    end_offset: int = Field(..., ge=0)

    @model_validator(mode="after")
    def check_offsets(self) -> "TextSpan":
        if self.end_offset < self.start_offset:
            raise ValueError(
                f"end_offset ({self.end_offset}) cannot be less than start_offset ({self.start_offset})"
            )
        return self


class FactProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field_name: str
    field_type: str
    raw_value: Any
    original_text: str = Field(..., max_length=1000)
    span_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    uncertainty_rationale: str | None = None

    @field_validator("field_name")
    @classmethod
    def validate_field_name(cls, v: str) -> str:
        if v not in ALLOWED_FIELD_NAMES:
            raise ValueError(f"Field name '{v}' is not in allowed schema taxonomy")
        return v

    @field_validator("field_type")
    @classmethod
    def validate_field_type(cls, v: str) -> str:
        if v not in ALLOWED_FIELD_TYPES:
            raise ValueError(
                f"Field type '{v}' is not in allowed field types ({ALLOWED_FIELD_TYPES})"
            )
        return v


class FactProposalSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "extraction.v1"
    detected_domain: str
    detected_issue: str
    spans: list[TextSpan] = Field(default_factory=list)
    proposals: list[FactProposal] = Field(default_factory=list)

    @field_validator("detected_domain")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        if v not in ALLOWED_DOMAINS:
            raise ValueError(f"Domain '{v}' is not in allowed domains ({ALLOWED_DOMAINS})")
        return v

    @field_validator("detected_issue")
    @classmethod
    def validate_issue(cls, v: str) -> str:
        if v not in ALLOWED_ISSUES:
            raise ValueError(f"Issue '{v}' is not in allowed issues ({ALLOWED_ISSUES})")
        return v

    @model_validator(mode="after")
    def validate_span_references(self) -> "FactProposalSet":
        """T08: Ensures all proposed span_ids strictly reference valid spans in the set."""
        valid_span_ids = {s.span_id for s in self.spans}
        for prop in self.proposals:
            for s_id in prop.span_ids:
                if s_id not in valid_span_ids:
                    raise ValueError(
                        f"Foreign or unknown span ID '{s_id}' not found in authorized span set (T08)."
                    )
        return self
