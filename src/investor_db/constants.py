from enum import StrEnum
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
CACHE_DIR = ROOT / ".cache"
PAGES_CACHE_DIR = CACHE_DIR / "pages"
REVIEW_DIR = ROOT / "review"

INVESTORS_JSONL = DATA_DIR / "investors.jsonl"
INVESTORS_CSV = DATA_DIR / "investors.csv"
EVIDENCE_CSV = DATA_DIR / "evidence.csv"
EXCLUDED_CSV = DATA_DIR / "excluded.csv"
FUNNEL_JSON = DATA_DIR / "funnel.json"
PAGE_HASHES_CSV = DATA_DIR / "page_hashes.csv"
MANUAL_REVIEW_CSV = REVIEW_DIR / "manual_review.csv"

ECB_HIST_URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip"
ECB_HIST_CSV = CACHE_DIR / "eurofxref-hist.csv"

USER_AGENT = "investor-db-research/0.1 (+https://github.com/wwtanji/reliable-investor-database)"
BLOCKED_DOMAINS = frozenset({"linkedin.com"})

MAX_QUOTE_WORDS = 30
ACTIVITY_WINDOW_MONTHS = 36
MONEY_AGREEMENT_TOLERANCE = 0.10
SAMPLE_COUNTRY = "CZ"
RANDOM_SEED = 20261023

BASE_CURRENCY = "EUR"


class InvestorType(StrEnum):
    VC = "vc"
    PE = "pe"
    FAMILY_OFFICE = "family_office"
    ANGEL = "angel"
    PRIVATE_INVESTOR = "private_investor"


class Stage(StrEnum):
    PRE_SEED = "pre_seed"
    SEED = "seed"
    SERIES_A = "series_a"
    SERIES_B_PLUS = "series_b_plus"
    GROWTH = "growth"
    BUYOUT = "buyout"


class Sector(StrEnum):
    SOFTWARE = "software"
    FINTECH = "fintech"
    HEALTH_BIO = "health_bio"
    DEEPTECH_HARDWARE = "deeptech_hardware"
    AI_DATA = "ai_data"
    ENERGY_CLIMATE = "energy_climate"
    MOBILITY = "mobility"
    CONSUMER_ECOMMERCE = "consumer_ecommerce"
    INDUSTRIAL = "industrial"
    AGRIFOOD = "agrifood"
    EDTECH = "edtech"
    CYBERSECURITY = "cybersecurity"
    MEDIA_GAMING = "media_gaming"
    PROPTECH = "proptech"
    GENERALIST = "generalist"


class SourceKind(StrEnum):
    REGULATOR = "regulator"
    ASSOCIATION = "association"
    CO_INVESTOR = "co_investor"
    PRESS = "press"
    OWN_WEBSITE = "own_website"


class ExclusionReason(StrEnum):
    ACCELERATOR_NO_CAPITAL = "accelerator_no_capital"
    ADVISOR = "advisor"
    CROWDFUNDING_PLATFORM = "crowdfunding_platform"
    LENDER = "lender"
    PUBLIC_MARKETS_ONLY = "public_markets_only"
    REAL_ESTATE_ONLY = "real_estate_only"
    FUND_OF_FUNDS_ONLY = "fund_of_funds_only"
    INACTIVE = "inactive"
    CORPORATE_NO_CVC = "corporate_no_cvc"
    DUPLICATE = "duplicate"
    OUT_OF_SCOPE_TYPE = "out_of_scope_type"
    OUT_OF_SCOPE_GEO = "out_of_scope_geo"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class RecordStatus(StrEnum):
    INCLUDED = "included"
    EXCLUDED = "excluded"


class CapitalBasis(StrEnum):
    AUM = "aum"
    SUM_OF_FUND_SIZES = "sum_of_fund_sizes"
    LATEST_FUND_SIZE = "latest_fund_size"


class Confidence(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class VerifierVerdict(StrEnum):
    SUPPORTED = "supported"
    REFUTED = "refuted"
    UNCERTAIN = "uncertain"


class L1Failure(StrEnum):
    BLOCKED_DOMAIN = "blocked_domain"
    ROBOTS_DISALLOWED = "robots_disallowed"
    FETCH_FAILED = "fetch_failed"
    QUOTE_TOO_LONG = "quote_too_long"
    QUOTE_NOT_FOUND = "quote_not_found"
    NUMBER_NOT_IN_QUOTE = "number_not_in_quote"
    DATE_OUT_OF_RANGE = "date_out_of_range"


class ClaimField(StrEnum):
    EXISTENCE = "existence"
    INVESTOR_TYPE = "investor_type"
    COUNTRY = "country"
    WEBSITE = "website"
    SECTORS = "sectors"
    STAGES = "stages"
    TICKET_MIN = "ticket_min"
    TICKET_MAX = "ticket_max"
    TOTAL_CAPITAL = "total_capital"
    INVESTMENT = "investment"
    EXCLUSION = "exclusion"
