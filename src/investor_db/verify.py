import re
import unicodedata
from datetime import date

from investor_db.constants import ACTIVITY_WINDOW_MONTHS, L1Failure
from investor_db.dedup import strip_diacritics
from investor_db.schema import Evidence

CHARACTER_MAP = str.maketrans(
    {
        "\u2018": "'",
        "\u2019": "'",
        "\u201a": "'",
        "\u201b": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u201e": '"',
        "\u00ab": '"',
        "\u00bb": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        "\u00a0": " ",
        "\u202f": " ",
        "\u2009": " ",
        "\u00ad": "",
    }
)

MULTIPLIERS: dict[str, float] = {
    "k": 1e3,
    "thousand": 1e3,
    "tis": 1e3,
    "m": 1e6,
    "mn": 1e6,
    "mil": 1e6,
    "mio": 1e6,
    "million": 1e6,
    "millions": 1e6,
    "milion": 1e6,
    "milionu": 1e6,
    "miliony": 1e6,
    "b": 1e9,
    "bn": 1e9,
    "billion": 1e9,
    "mld": 1e9,
    "miliarda": 1e9,
    "miliardy": 1e9,
    "miliard": 1e9,
}

NUMBER_PATTERN = re.compile(
    r"(?<![\w.])(\d{1,3}(?:[ ,.]\d{3})+|\d+)(?:[.,](\d+))?\s*([a-z]+)?",
)
AMOUNT_TOLERANCE = 0.01


def normalise_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).translate(CHARACTER_MAP).casefold()
    return re.sub(r"\s+", " ", text).strip()


def quote_in_text(quote: str, text: str) -> bool:
    return normalise_text(quote) in normalise_text(text)


def parse_amounts(text: str) -> list[float]:
    plain = strip_diacritics(normalise_text(text))
    amounts: list[float] = []
    for whole, fraction, unit in NUMBER_PATTERN.findall(plain):
        integer_part = re.sub(r"[ ,.]", "", whole)
        value = float(f"{integer_part}.{fraction}" if fraction else integer_part)
        amounts.append(value * MULTIPLIERS.get(unit, 1.0))
    return amounts


def amount_in_quote(amount: float, quote: str) -> bool:
    return any(
        abs(candidate - amount) <= AMOUNT_TOLERANCE * amount for candidate in parse_amounts(quote)
    )


def months_between(earlier: date, later: date) -> int:
    return (later.year - earlier.year) * 12 + later.month - earlier.month


def is_recent(day: date, reference: date, window_months: int = ACTIVITY_WINDOW_MONTHS) -> bool:
    return day <= reference and months_between(day, reference) <= window_months


def check_quote(
    evidence: Evidence,
    page_text: str,
    expected_amount: float | None = None,
) -> L1Failure | None:
    if not quote_in_text(evidence.quote, page_text):
        return L1Failure.QUOTE_NOT_FOUND
    if expected_amount is not None and not amount_in_quote(expected_amount, evidence.quote):
        return L1Failure.NUMBER_NOT_IN_QUOTE
    if evidence.source_date is not None and evidence.source_date > evidence.retrieved_at:
        return L1Failure.DATE_OUT_OF_RANGE
    return None


def apply_check(evidence: Evidence, failure: L1Failure | None, sha256: str | None) -> Evidence:
    return evidence.model_copy(
        update={"verified": failure is None, "l1_failure": failure, "content_sha256": sha256}
    )
