from datetime import date

import pytest
from pydantic import ValidationError

from investor_db.constants import InvestorType, SourceKind
from investor_db.schema import Evidence, Fact


def test_quote_longer_than_30_words_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Evidence(
            source_url="https://example.com",
            source_kind=SourceKind.PRESS,
            retrieved_at=date(2026, 10, 23),
            quote=" ".join(["word"] * 31),
        )


def test_fact_requires_reason_when_null_and_evidence_when_set() -> None:
    with pytest.raises(ValidationError):
        Fact[InvestorType]()
    with pytest.raises(ValidationError):
        Fact[InvestorType](value=InvestorType.VC)
    assert Fact[InvestorType](null_reason="not published").value is None
