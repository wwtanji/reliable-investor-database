from collections.abc import Callable
from datetime import date

from investor_db.constants import (
    ExclusionReason,
    L1Failure,
    RecordStatus,
)
from investor_db.fetch import FetchRefused, Page, is_blocked
from investor_db.fx import RateTable, to_eur
from investor_db.schema import Evidence, Fact, Fund, Investment, Investor, Money
from investor_db.verify import apply_check, check_quote, is_recent

type PageLookup = Callable[[str], Page]

OK_STATUS = 200


def verify_evidence(
    evidence: Evidence, lookup: PageLookup, expected_amount: float | None = None
) -> Evidence:
    if is_blocked(evidence.source_url):
        return apply_check(evidence, L1Failure.BLOCKED_DOMAIN, None)
    try:
        page = lookup(evidence.source_url)
    except FetchRefused:
        return apply_check(evidence, L1Failure.ROBOTS_DISALLOWED, None)
    except Exception:
        return apply_check(evidence, L1Failure.FETCH_FAILED, None)
    if page.status_code != OK_STATUS:
        return apply_check(evidence, L1Failure.FETCH_FAILED, page.sha256)
    return apply_check(evidence, check_quote(evidence, page.text, expected_amount), page.sha256)


def _expected_amount(value: object) -> float | None:
    return value.amount if isinstance(value, Money) else None


def verify_fact[T](fact: Fact[T], lookup: PageLookup) -> Fact[T]:
    expected = _expected_amount(fact.value)
    checked = [verify_evidence(item, lookup, expected) for item in fact.evidence]
    return fact.model_copy(update={"evidence": checked})


def verify_record(investor: Investor, lookup: PageLookup) -> Investor:
    return investor.model_copy(
        update={
            "investor_type": verify_fact(investor.investor_type, lookup),
            "country": verify_fact(investor.country, lookup),
            "sectors": verify_fact(investor.sectors, lookup),
            "stages": verify_fact(investor.stages, lookup),
            "ticket_min": verify_fact(investor.ticket_min, lookup),
            "ticket_max": verify_fact(investor.ticket_max, lookup),
            "total_capital": verify_fact(investor.total_capital, lookup),
            "funds": [
                fund.model_copy(update={"size": verify_fact(fund.size, lookup)})
                for fund in investor.funds
            ],
            "investments": [
                item.model_copy(
                    update={"evidence": [verify_evidence(e, lookup) for e in item.evidence]}
                )
                for item in investor.investments
            ],
            "exclusion_evidence": [verify_evidence(e, lookup) for e in investor.exclusion_evidence],
        }
    )


def failed_reason(evidence: list[Evidence]) -> str:
    failures = sorted({str(item.l1_failure) for item in evidence if item.l1_failure})
    return "evidence failed code verification: " + ", ".join(failures or ["unverified"])


def finalise_fact[T](fact: Fact[T]) -> Fact[T]:
    if fact.value is None or fact.verified_evidence:
        return fact.model_copy(update={"evidence": fact.verified_evidence})
    return fact.model_copy(
        update={"value": None, "evidence": [], "null_reason": failed_reason(fact.evidence)}
    )


def _verified_investments(investments: list[Investment]) -> list[Investment]:
    kept: list[Investment] = []
    for item in investments:
        verified = [evidence for evidence in item.evidence if evidence.verified]
        if verified:
            kept.append(item.model_copy(update={"evidence": verified}))
    return kept


def investment_day(item: Investment) -> date | None:
    dates = [evidence.source_date for evidence in item.evidence if evidence.source_date]
    return item.deal_date or (min(dates) if dates else None)


def has_recent_investment(investments: list[Investment], reference: date) -> bool:
    return any(
        (day := investment_day(item)) is not None and is_recent(day, reference)
        for item in investments
    )


def finalise_record(investor: Investor, reference: date) -> Investor:
    investments = _verified_investments(investor.investments)
    finalised = investor.model_copy(
        update={
            "investor_type": finalise_fact(investor.investor_type),
            "country": finalise_fact(investor.country),
            "sectors": finalise_fact(investor.sectors),
            "stages": finalise_fact(investor.stages),
            "ticket_min": finalise_fact(investor.ticket_min),
            "ticket_max": finalise_fact(investor.ticket_max),
            "total_capital": finalise_fact(investor.total_capital),
            "funds": [
                fund.model_copy(update={"size": finalise_fact(fund.size)})
                for fund in investor.funds
            ],
            "investments": investments,
            "exclusion_evidence": [e for e in investor.exclusion_evidence if e.verified],
        }
    )
    if finalised.status == RecordStatus.INCLUDED:
        if finalised.investor_type.value is None:
            finalised = _exclude(finalised, ExclusionReason.INSUFFICIENT_EVIDENCE)
        elif not has_recent_investment(investments, reference):
            reason = (
                ExclusionReason.INACTIVE if investments else ExclusionReason.INSUFFICIENT_EVIDENCE
            )
            finalised = _exclude(finalised, reason)
    return Investor.model_validate(finalised.model_dump())


def _exclude(investor: Investor, reason: ExclusionReason) -> Investor:
    return investor.model_copy(update={"status": RecordStatus.EXCLUDED, "exclusion_reason": reason})


def _fact_date(fact: Fact) -> date | None:
    if not fact.evidence:
        return None
    first = fact.evidence[0]
    return first.source_date or first.retrieved_at


def convert_fact[M: Money](fact: Fact[M], table: RateTable) -> Fact[M]:
    day = _fact_date(fact)
    if fact.value is None or day is None:
        return fact
    return fact.model_copy(update={"value": to_eur(fact.value, day, table)})


def convert_record(investor: Investor, table: RateTable) -> Investor:
    return investor.model_copy(
        update={
            "ticket_min": convert_fact(investor.ticket_min, table),
            "ticket_max": convert_fact(investor.ticket_max, table),
            "total_capital": convert_fact(investor.total_capital, table),
            "funds": [
                Fund(name=fund.name, vintage=fund.vintage, size=convert_fact(fund.size, table))
                for fund in investor.funds
            ],
        }
    )
