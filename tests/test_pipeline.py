from datetime import UTC, date, datetime

from investor_db.constants import (
    ExclusionReason,
    InvestorType,
    L1Failure,
    RecordStatus,
    SourceKind,
)
from investor_db.fetch import Page
from investor_db.pipeline import finalise_record, verify_record
from investor_db.schema import Evidence, Fact, Investment, Investor, Money, TotalCapital

RETRIEVED = date(2026, 10, 23)
PAGES = {
    "https://fund.example/about": "Example Ventures is a seed fund that invests in software.",
    "https://press.example/deal": "Example Ventures led the seed round of Acme in June 2025.",
    "https://press.example/fund": "Example Ventures closed its second fund at EUR 40 million.",
}


def lookup(url: str) -> Page:
    return Page(
        url=url,
        status_code=200 if url in PAGES else 404,
        content_type="text/html",
        text=PAGES.get(url, ""),
        sha256="0" * 64,
        fetched_at=datetime(2026, 10, 23, tzinfo=UTC),
    )


def evidence(url: str, quote: str, source_date: date | None = None) -> Evidence:
    return Evidence(
        source_url=url,
        source_kind=SourceKind.PRESS,
        source_date=source_date,
        retrieved_at=RETRIEVED,
        quote=quote,
    )


def make_investor(deal_date: date, capital_quote: str) -> Investor:
    unknown = "not published"
    return Investor(
        investor_id="example-ventures",
        name="Example Ventures",
        investor_type=Fact[InvestorType](
            value=InvestorType.VC,
            evidence=[evidence("https://fund.example/about", "is a seed fund that invests")],
        ),
        country=Fact[str](null_reason=unknown),
        sectors=Fact(null_reason=unknown),
        stages=Fact(null_reason=unknown),
        ticket_min=Fact[Money](null_reason=unknown),
        ticket_max=Fact[Money](null_reason=unknown),
        total_capital=Fact[TotalCapital](
            value=TotalCapital(amount=40e6, currency="EUR", basis="latest_fund_size"),
            evidence=[evidence("https://press.example/fund", capital_quote)],
        ),
        investments=[
            Investment(
                portfolio_company="Acme",
                deal_date=deal_date,
                evidence=[evidence("https://press.example/deal", "led the seed round of Acme")],
            )
        ],
        status=RecordStatus.INCLUDED,
    )


def test_verified_record_stays_included() -> None:
    record = verify_record(make_investor(date(2025, 6, 1), "second fund at EUR 40 million"), lookup)
    final = finalise_record(record, RETRIEVED)
    assert final.status == RecordStatus.INCLUDED
    assert final.total_capital.value is not None
    assert all(item.verified for item in final.investor_type.evidence)


def test_quote_missing_from_page_nulls_the_field_with_reason() -> None:
    record = verify_record(make_investor(date(2025, 6, 1), "third fund at EUR 40 million"), lookup)
    assert record.total_capital.evidence[0].l1_failure == L1Failure.QUOTE_NOT_FOUND
    final = finalise_record(record, RETRIEVED)
    assert final.total_capital.value is None
    assert "quote_not_found" in (final.total_capital.null_reason or "")


def test_old_investment_marks_record_inactive() -> None:
    record = verify_record(make_investor(date(2022, 1, 1), "second fund at EUR 40 million"), lookup)
    final = finalise_record(record, RETRIEVED)
    assert final.status == RecordStatus.EXCLUDED
    assert final.exclusion_reason == ExclusionReason.INACTIVE


def test_unreachable_source_fails_and_excludes_for_insufficient_evidence() -> None:
    investor = make_investor(date(2025, 6, 1), "second fund at EUR 40 million")
    investor.investments[0].evidence[0].source_url = "https://press.example/missing"
    final = finalise_record(verify_record(investor, lookup), RETRIEVED)
    assert final.status == RecordStatus.EXCLUDED
    assert final.exclusion_reason == ExclusionReason.INSUFFICIENT_EVIDENCE


def test_linkedin_source_is_refused() -> None:
    investor = make_investor(date(2025, 6, 1), "second fund at EUR 40 million")
    investor.investments[0].evidence[0].source_url = "https://www.linkedin.com/posts/x"
    record = verify_record(investor, lookup)
    assert record.investments[0].evidence[0].l1_failure == L1Failure.BLOCKED_DOMAIN
