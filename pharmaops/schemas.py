"""Validated contracts shared by the simulated API, tools, and UI."""

import hashlib
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Country = Literal["BG", "DE", "RO"]
Category = Literal["damaged_packaging", "missing_items", "discrepancy", "return_request"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Delivery(StrictModel):
    delivery_id: str = Field(pattern=r"^DEL-\d{4}$")
    country: Country
    distribution_center: str
    recipient: str
    packages: int = Field(ge=1)
    status: str


class ComplaintInput(StrictModel):
    delivery_id: str = Field(pattern=r"^DEL-\d{4}$")
    category: Category
    description: str = Field(min_length=10, max_length=1500)
    affected_packages: int = Field(ge=1, le=1000)
    requested_resolution: Literal["investigation", "replacement_review", "return_review"]

    @field_validator("description")
    @classmethod
    def meaningful_description(cls, value):
        if len(value.strip()) < 10:
            raise ValueError("Provide at least 10 characters describing the issue.")
        return value


class Draft(ComplaintInput):
    draft_id: str
    revision: int = Field(ge=1)
    country: Country
    source_ids: list[str] = Field(min_length=1, max_length=5)


def fingerprint(draft: Draft) -> str:
    payload = json.dumps(draft.model_dump(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


class Confirmation(StrictModel):
    draft_id: str
    revision: int
    fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    confirmed: Literal[True]


class Receipt(StrictModel):
    reference: str
    draft_id: str
    duplicate: bool = False


class Claim(StrictModel):
    citation_id: str = Field(max_length=100)
    quote: str = Field(min_length=15, max_length=1600)
    translation_bg: str = Field(default="", max_length=2000)


class GroundedAnswer(StrictModel):
    supported: bool
    claims: list[Claim] = Field(max_length=5)


class ToolDecision(StrictModel):
    tool: Literal["retrieve_procedures", "lookup_delivery", "prepare_draft", "clarify"]
    query: str = Field(default="", max_length=500)
