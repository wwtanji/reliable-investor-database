import csv
import json
from collections.abc import Iterator
from pathlib import Path

from pydantic import BaseModel

from investor_db.constants import (
    EVIDENCE_CSV,
    EXCLUDED_CSV,
    INVESTORS_CSV,
    INVESTORS_JSONL,
    ClaimField,
    RecordStatus,
)
from investor_db.schema import Evidence, Fact, Investor, Money

LIST_SEPARATOR = "; "


class Claim(BaseModel):
    investor_id: str
    field: ClaimField
    value: str
    evidence: Evidence


def render_value(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, Money):
        return f"{value.amount:g} {value.currency}"
    if isinstance(value, list):
        return LIST_SEPARATOR.join(str(item) for item in value)
    return str(value)


def _fact_claims(investor_id: str, field: ClaimField, fact: Fact) -> Iterator[Claim]:
    for item in fact.evidence:
        yield Claim(
            investor_id=investor_id, field=field, value=render_value(fact.value), evidence=item
        )


def claims(investor: Investor) -> Iterator[Claim]:
    facts: list[tuple[ClaimField, Fact]] = [
        (ClaimField.INVESTOR_TYPE, investor.investor_type),
        (ClaimField.COUNTRY, investor.country),
        (ClaimField.SECTORS, investor.sectors),
        (ClaimField.STAGES, investor.stages),
        (ClaimField.TICKET_MIN, investor.ticket_min),
        (ClaimField.TICKET_MAX, investor.ticket_max),
        (ClaimField.TOTAL_CAPITAL, investor.total_capital),
    ]
    for field, fact in facts:
        yield from _fact_claims(investor.investor_id, field, fact)
    for fund in investor.funds:
        yield from _fact_claims(investor.investor_id, ClaimField.TOTAL_CAPITAL, fund.size)
    for investment in investor.investments:
        value = f"{investment.portfolio_company} ({investment.deal_date or 'date unknown'})"
        for item in investment.evidence:
            yield Claim(
                investor_id=investor.investor_id,
                field=ClaimField.INVESTMENT,
                value=value,
                evidence=item,
            )
    for item in investor.exclusion_evidence:
        yield Claim(
            investor_id=investor.investor_id,
            field=ClaimField.EXCLUSION,
            value=str(investor.exclusion_reason),
            evidence=item,
        )


def load_investors(path: Path = INVESTORS_JSONL) -> list[Investor]:
    if not path.exists():
        return []
    return [Investor.model_validate_json(line) for line in path.read_text().splitlines() if line]


def write_jsonl(investors: list[Investor], path: Path = INVESTORS_JSONL) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [investor.model_dump_json() for investor in investors]
    path.write_text("\n".join(lines) + ("\n" if lines else ""))


def _write_csv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def _money_columns(fact: Fact) -> list[str]:
    money = fact.value
    if money is None:
        return ["", "", "", "", fact.null_reason or ""]
    return [
        f"{money.amount:g}",
        money.currency,
        "" if money.amount_eur is None else f"{money.amount_eur:.0f}",
        "" if money.fx_date is None else money.fx_date.isoformat(),
        "",
    ]


INVESTOR_HEADER = [
    "investor_id",
    "name",
    "aliases",
    "website",
    "investor_type",
    "is_cvc",
    "country",
    "sectors",
    "stages",
    "ticket_min",
    "ticket_min_currency",
    "ticket_min_eur",
    "ticket_min_fx_date",
    "ticket_min_null_reason",
    "ticket_max",
    "ticket_max_currency",
    "ticket_max_eur",
    "ticket_max_fx_date",
    "ticket_max_null_reason",
    "total_capital",
    "total_capital_currency",
    "total_capital_eur",
    "total_capital_fx_date",
    "total_capital_null_reason",
    "total_capital_basis",
    "latest_investment",
    "latest_investment_date",
    "evidence_count",
]


def investor_row(investor: Investor) -> list[str]:
    capital = investor.total_capital.value
    dated = [item for item in investor.investments if item.deal_date]
    latest = max(dated, key=lambda item: item.deal_date) if dated else None
    return [
        investor.investor_id,
        investor.name,
        LIST_SEPARATOR.join(investor.aliases),
        investor.website or "",
        render_value(investor.investor_type.value),
        str(investor.is_cvc).lower(),
        render_value(investor.country.value),
        render_value(investor.sectors.value),
        render_value(investor.stages.value),
        *_money_columns(investor.ticket_min),
        *_money_columns(investor.ticket_max),
        *_money_columns(investor.total_capital),
        "" if capital is None else str(capital.basis),
        latest.portfolio_company if latest else "",
        latest.deal_date.isoformat() if latest and latest.deal_date else "",
        str(sum(1 for _ in claims(investor))),
    ]


EVIDENCE_HEADER = [
    "investor_id",
    "field",
    "value",
    "source_url",
    "source_kind",
    "source_date",
    "retrieved_at",
    "quote",
    "verified",
    "l1_failure",
    "content_sha256",
]


def evidence_row(claim: Claim) -> list[str]:
    item = claim.evidence
    return [
        claim.investor_id,
        str(claim.field),
        claim.value,
        item.source_url,
        str(item.source_kind),
        item.source_date.isoformat() if item.source_date else "",
        item.retrieved_at.isoformat(),
        item.quote,
        str(item.verified).lower(),
        str(item.l1_failure or ""),
        item.content_sha256 or "",
    ]


EXCLUDED_HEADER = ["investor_id", "name", "website", "exclusion_reason", "source_url", "quote"]


def excluded_row(investor: Investor) -> list[str]:
    first = investor.exclusion_evidence[0] if investor.exclusion_evidence else None
    return [
        investor.investor_id,
        investor.name,
        investor.website or "",
        str(investor.exclusion_reason),
        first.source_url if first else "",
        first.quote if first else "",
    ]


def export_all(investors: list[Investor]) -> None:
    included = [item for item in investors if item.status == RecordStatus.INCLUDED]
    excluded = [item for item in investors if item.status == RecordStatus.EXCLUDED]
    write_jsonl(investors)
    _write_csv(INVESTORS_CSV, INVESTOR_HEADER, [investor_row(item) for item in included])
    _write_csv(
        EVIDENCE_CSV,
        EVIDENCE_HEADER,
        [evidence_row(claim) for investor in investors for claim in claims(investor)],
    )
    _write_csv(EXCLUDED_CSV, EXCLUDED_HEADER, [excluded_row(item) for item in excluded])


def write_json(payload: dict[str, object], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n")
