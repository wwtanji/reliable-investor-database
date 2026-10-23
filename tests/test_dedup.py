from investor_db.constants import SourceKind
from investor_db.dedup import dedup_candidates, normalise_name, registrable_domain
from investor_db.schema import Candidate


def make_candidate(name: str, website: str | None = None) -> Candidate:
    return Candidate(
        name=name,
        website=website,
        found_at_url="https://example.com/list",
        source_kind=SourceKind.ASSOCIATION,
    )


def test_normalise_name_strips_legal_forms_diacritics_and_punctuation() -> None:
    assert normalise_name("Inven Capital, SICAV, a.s.") == "inven capital"
    assert normalise_name("Česká Investiční s.r.o.") == "ceska investicni"


def test_registrable_domain_handles_subdomains_and_multi_part_suffixes() -> None:
    assert registrable_domain("https://www.credoventures.com/portfolio") == "credoventures.com"
    assert registrable_domain("https://fund.example.co.uk") == "example.co.uk"
    assert registrable_domain("not a url") is None


def test_dedup_merges_by_name_or_domain_transitively() -> None:
    candidates = [
        make_candidate("Credo Ventures", "https://credoventures.com"),
        make_candidate("Credo Ventures a.s."),
        make_candidate("Credo Stage 5", "https://www.credoventures.com/stage-5"),
        make_candidate("Presto Ventures", "https://presto.vc"),
    ]
    kept, duplicates = dedup_candidates(candidates)
    assert [item.name for item in kept] == ["Credo Ventures", "Presto Ventures"]
    assert [item.name for item in duplicates] == ["Credo Ventures a.s.", "Credo Stage 5"]


def test_dedup_keeps_each_candidate_exactly_once() -> None:
    candidates = [
        make_candidate("A", "https://a.cz"),
        make_candidate("B", "https://b.cz"),
        make_candidate("B", "https://a.cz"),
        make_candidate("C"),
    ]
    kept, duplicates = dedup_candidates(candidates)
    assert len(kept) + len(duplicates) == len(candidates)
    assert [item.name for item in kept] == ["A", "C"]
