import csv
import io
import zipfile
from bisect import bisect_right
from datetime import date
from pathlib import Path

import httpx

from investor_db.constants import BASE_CURRENCY, ECB_HIST_CSV, ECB_HIST_URL, USER_AGENT
from investor_db.schema import Money

MISSING_RATE = "N/A"

type RateTable = dict[str, list[tuple[date, float]]]


def download_ecb_history(target: Path = ECB_HIST_CSV) -> Path:
    response = httpx.get(ECB_HIST_URL, headers={"User-Agent": USER_AGENT}, timeout=60.0)
    response.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        csv_name = archive.namelist()[0]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(archive.read(csv_name))
    return target


def load_rates(path: Path = ECB_HIST_CSV) -> RateTable:
    table: RateTable = {}
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            day = date.fromisoformat(row["Date"])
            for currency, raw_rate in row.items():
                if currency == "Date" or not currency or not raw_rate:
                    continue
                if raw_rate.strip() == MISSING_RATE:
                    continue
                table.setdefault(currency.strip(), []).append((day, float(raw_rate)))
    for series in table.values():
        series.sort()
    return table


def rate_on(table: RateTable, currency: str, day: date) -> tuple[float, date]:
    series = table.get(currency)
    if not series:
        raise KeyError(f"no ECB rate for {currency}")
    position = bisect_right(series, (day, float("inf")))
    if position == 0:
        raise KeyError(f"no ECB rate for {currency} on or before {day}")
    rate_day, rate = series[position - 1]
    return rate, rate_day


def to_eur[M: Money](money: M, day: date, table: RateTable) -> M:
    if money.currency == BASE_CURRENCY:
        return money.model_copy(update={"amount_eur": money.amount, "fx_rate": 1.0, "fx_date": day})
    rate, rate_day = rate_on(table, money.currency, day)
    return money.model_copy(
        update={"amount_eur": round(money.amount / rate, 2), "fx_rate": rate, "fx_date": rate_day}
    )
