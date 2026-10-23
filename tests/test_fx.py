from datetime import date
from pathlib import Path

import pytest

from investor_db.fx import load_rates, rate_on, to_eur
from investor_db.schema import Money

ECB_SAMPLE = """Date,USD,CZK,ISK,
2025-01-03,1.0299,25.155,N/A,
2025-01-02,1.0321,25.183,N/A,
2024-12-31,1.0389,25.185,N/A,
"""


@pytest.fixture
def table(tmp_path: Path) -> dict[str, list[tuple[date, float]]]:
    path = tmp_path / "eurofxref-hist.csv"
    path.write_text(ECB_SAMPLE)
    return load_rates(path)


def test_rate_on_uses_closest_earlier_publication_day(table) -> None:
    assert rate_on(table, "CZK", date(2025, 1, 2)) == (25.183, date(2025, 1, 2))
    assert rate_on(table, "CZK", date(2025, 1, 5)) == (25.155, date(2025, 1, 3))


def test_rate_on_rejects_unknown_currency_and_early_dates(table) -> None:
    with pytest.raises(KeyError):
        rate_on(table, "ISK", date(2025, 1, 2))
    with pytest.raises(KeyError):
        rate_on(table, "CZK", date(2024, 1, 1))


def test_to_eur_keeps_original_and_records_rate(table) -> None:
    converted = to_eur(Money(amount=500_000_000, currency="CZK"), date(2025, 1, 1), table)
    assert converted.amount == 500_000_000
    assert converted.currency == "CZK"
    assert converted.fx_rate == 25.185
    assert converted.fx_date == date(2024, 12, 31)
    assert converted.amount_eur == pytest.approx(19_853_087.16, abs=0.01)


def test_to_eur_is_identity_for_euro(table) -> None:
    converted = to_eur(Money(amount=10.0, currency="EUR"), date(2025, 1, 2), table)
    assert converted.amount_eur == 10.0
    assert converted.fx_rate == 1.0
