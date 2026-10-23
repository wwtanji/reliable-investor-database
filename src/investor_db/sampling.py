import random
from collections.abc import Callable, Hashable, Sequence

from investor_db.constants import RANDOM_SEED


def stratified_sample[T](
    items: Sequence[T],
    stratum_of: Callable[[T], Hashable],
    size: int,
    seed: int = RANDOM_SEED,
) -> list[T]:
    if size >= len(items):
        return list(items)
    strata: dict[Hashable, list[T]] = {}
    for item in items:
        strata.setdefault(stratum_of(item), []).append(item)
    ordered_keys = sorted(strata, key=str)
    quotas = {key: max(1, round(size * len(strata[key]) / len(items))) for key in ordered_keys}
    while sum(quotas.values()) > size:
        largest = max(ordered_keys, key=lambda key: (quotas[key], str(key)))
        quotas[largest] -= 1
    while sum(quotas.values()) < size:
        roomiest = max(ordered_keys, key=lambda key: (len(strata[key]) - quotas[key], str(key)))
        quotas[roomiest] += 1
    rng = random.Random(seed)
    sample: list[T] = []
    for key in ordered_keys:
        sample.extend(rng.sample(strata[key], min(quotas[key], len(strata[key]))))
    return sample
