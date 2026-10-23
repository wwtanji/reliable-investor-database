from datetime import date

from pydantic import BaseModel, Field, field_validator, model_validator

from investor_db.constants import (
    MAX_QUOTE_WORDS,
    CapitalBasis,
    Confidence,
    ExclusionReason,
    InvestorType,
    L1Failure,
    RecordStatus,
    Sector,
    SourceKind,
    Stage,
    VerifierVerdict,
)


class Evidence(BaseModel):
    source_url: str
    source_kind: SourceKind
    source_date: date | None = None
    retrieved_at: date
    quote: str
    verified: bool = False
    l1_failure: L1Failure | None = None
    content_sha256: str | None = None

    @field_validator("source_url")
    @classmethod
    def require_http_url(cls, url: str) -> str:
        if not url.startswith(("https://", "http://")):
            raise ValueError("source_url must be an http(s) URL")
        return url

    @field_validator("quote")
    @classmethod
    def limit_quote_length(cls, quote: str) -> str:
        if not quote.strip():
            raise ValueError("quote must not be empty")
        if len(quote.split()) > MAX_QUOTE_WORDS:
            raise ValueError(f"quote exceeds {MAX_QUOTE_WORDS} words")
        return quote


class Fact[T](BaseModel):
    value: T | None = None
    evidence: list[Evidence] = Field(default_factory=list)
    null_reason: str | None = None
    confidence: Confidence | None = None
    verifier_verdict: VerifierVerdict | None = None
    verifier_note: str | None = None

    @model_validator(mode="after")
    def require_evidence_or_reason(self) -> "Fact[T]":
        if self.value is None and not self.null_reason:
            raise ValueError("a null value needs a null_reason")
        if self.value is not None and not self.evidence:
            raise ValueError("a value needs at least one evidence item")
        return self

    @property
    def verified_evidence(self) -> list[Evidence]:
        return [item for item in self.evidence if item.verified]


class Money(BaseModel):
    amount: float = Field(gt=0)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    amount_eur: float | None = None
    fx_rate: float | None = None
    fx_date: date | None = None


class TotalCapital(Money):
    basis: CapitalBasis
    as_of: date | None = None


class Fund(BaseModel):
    name: str
    vintage: int | None = None
    size: Fact[Money]


class Investment(BaseModel):
    portfolio_company: str
    deal_date: date | None = None
    evidence: list[Evidence] = Field(min_length=1)


class Candidate(BaseModel):
    name: str
    website: str | None = None
    found_at_url: str
    source_kind: SourceKind
    note: str | None = None


class Investor(BaseModel):
    investor_id: str = Field(pattern=r"^[a-z0-9-]+$")
    name: str
    aliases: list[str] = Field(default_factory=list)
    website: str | None = None
    investor_type: Fact[InvestorType]
    is_cvc: bool = False
    country: Fact[str]
    sectors: Fact[list[Sector]]
    stages: Fact[list[Stage]]
    ticket_min: Fact[Money]
    ticket_max: Fact[Money]
    total_capital: Fact[TotalCapital]
    funds: list[Fund] = Field(default_factory=list)
    investments: list[Investment] = Field(default_factory=list)
    status: RecordStatus
    exclusion_reason: ExclusionReason | None = None
    exclusion_evidence: list[Evidence] = Field(default_factory=list)
    discovered_via: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_reason_when_excluded(self) -> "Investor":
        if (self.status == RecordStatus.EXCLUDED) != (self.exclusion_reason is not None):
            raise ValueError("exclusion_reason is required exactly when status is excluded")
        return self
