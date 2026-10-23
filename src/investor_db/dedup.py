import re
import unicodedata

import tldextract

from investor_db.schema import Candidate

LEGAL_SUFFIXES = (
    "s.r.o.",
    "spol. s r.o.",
    "a.s.",
    "sicav",
    "investiční fond",
    "investicni fond",
    "investiční společnost",
    "investicni spolecnost",
    "gmbh",
    "ltd",
    "llc",
    "llp",
    "b.v.",
    "s.a.",
    "se",
    "plc",
    "inc",
)

_extract = tldextract.TLDExtract(suffix_list_urls=())


def strip_diacritics(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def normalise_name(name: str) -> str:
    lowered = strip_diacritics(name).casefold().strip()
    changed = True
    while changed:
        changed = False
        for suffix in LEGAL_SUFFIXES:
            plain_suffix = strip_diacritics(suffix)
            if lowered.endswith(" " + plain_suffix) or lowered.endswith("," + plain_suffix):
                lowered = lowered[: -len(plain_suffix)].rstrip(" ,")
                changed = True
    return re.sub(r"[^a-z0-9]+", " ", lowered).strip()


def registrable_domain(url: str) -> str | None:
    parts = _extract(url)
    if not parts.domain or not parts.suffix:
        return None
    return f"{parts.domain}.{parts.suffix}".lower()


def dedup_candidates(candidates: list[Candidate]) -> tuple[list[Candidate], list[Candidate]]:
    parent = list(range(len(candidates)))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    first_index_by_key: dict[str, int] = {}
    for index, candidate in enumerate(candidates):
        keys = [f"name:{normalise_name(candidate.name)}"]
        if candidate.website and (domain := registrable_domain(candidate.website)):
            keys.append(f"domain:{domain}")
        for key in keys:
            if key in first_index_by_key:
                parent[find(index)] = find(first_index_by_key[key])
            else:
                first_index_by_key[key] = index

    kept: list[Candidate] = []
    duplicates: list[Candidate] = []
    seen_roots: set[int] = set()
    for index, candidate in enumerate(candidates):
        root = find(index)
        if root in seen_roots:
            duplicates.append(candidate)
        else:
            seen_roots.add(root)
            kept.append(candidate)
    return kept, duplicates
