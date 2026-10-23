from investor_db.sampling import stratified_sample

ITEMS = [("a", index) for index in range(20)] + [("b", index) for index in range(10)] + [("c", 0)]


def stratum(item: tuple[str, int]) -> str:
    return item[0]


def test_sample_is_reproducible_with_fixed_seed() -> None:
    assert stratified_sample(ITEMS, stratum, 10) == stratified_sample(ITEMS, stratum, 10)


def test_sample_has_requested_size_and_covers_every_stratum() -> None:
    sample = stratified_sample(ITEMS, stratum, 10)
    assert len(sample) == 10
    assert {item[0] for item in sample} == {"a", "b", "c"}
    assert len(set(sample)) == 10


def test_sample_allocates_proportionally() -> None:
    sample = stratified_sample(ITEMS, stratum, 10)
    counts = {key: sum(1 for item in sample if item[0] == key) for key in "abc"}
    assert counts == {"a": 6, "b": 3, "c": 1}


def test_sample_returns_everything_when_size_exceeds_population() -> None:
    assert stratified_sample(ITEMS, stratum, 100) == ITEMS
