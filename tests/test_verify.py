from datetime import date

from investor_db.constants import L1Failure, SourceKind
from investor_db.schema import Evidence
from investor_db.verify import (
    amount_in_quote,
    check_quote,
    is_recent,
    normalise_text,
    parse_amounts,
    quote_in_text,
)

PAGE = "<p>Credo Ventures  announced its “fifth fund” of $88M – the largest yet.</p>"


def make_evidence(quote: str, source_date: date | None = None) -> Evidence:
    return Evidence(
        source_url="https://example.com/news",
        source_kind=SourceKind.PRESS,
        source_date=source_date,
        retrieved_at=date(2026, 10, 23),
        quote=quote,
    )


def test_normalise_unifies_quotes_dashes_spaces_and_case() -> None:
    assert normalise_text("A “B” –  c") == 'a "b" - c'


def test_quote_found_despite_typography_differences() -> None:
    assert quote_in_text('its "fifth fund" of $88M - the largest', PAGE)


def test_quote_not_found_when_words_change() -> None:
    assert not quote_in_text("its sixth fund of $88M", PAGE)


def test_parse_amounts_handles_units_and_separators() -> None:
    assert parse_amounts("$88M") == [88e6]
    assert parse_amounts("fond 1,5 mld. Kč") == [1.5e9]
    assert parse_amounts("EUR 250 000 000") == [250e6]
    assert parse_amounts("75 milionů eur") == [75e6]
    assert parse_amounts("tickets of €500k") == [500e3]


def test_amount_in_quote_tolerates_rounding_only() -> None:
    assert amount_in_quote(88_000_000, "a fund of $88M")
    assert not amount_in_quote(80_000_000, "a fund of $88M")


def test_check_quote_reports_missing_quote() -> None:
    assert check_quote(make_evidence("a fund of $90M"), PAGE) == L1Failure.QUOTE_NOT_FOUND


def test_check_quote_reports_number_mismatch() -> None:
    evidence = make_evidence("fifth fund” of $88M")
    assert check_quote(evidence, PAGE, expected_amount=50e6) == L1Failure.NUMBER_NOT_IN_QUOTE
    assert check_quote(evidence, PAGE, expected_amount=88e6) is None


def test_check_quote_rejects_source_date_after_retrieval() -> None:
    evidence = make_evidence("fifth fund", source_date=date(2027, 1, 1))
    assert check_quote(evidence, PAGE) == L1Failure.DATE_OUT_OF_RANGE


def test_is_recent_uses_36_month_window() -> None:
    reference = date(2026, 10, 23)
    assert is_recent(date(2023, 10, 1), reference)
    assert not is_recent(date(2023, 9, 30), reference)
    assert not is_recent(date(2026, 11, 1), reference)
