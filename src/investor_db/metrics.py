from math import sqrt

from pydantic import BaseModel

Z_95 = 1.959963984540054


class Proportion(BaseModel):
    successes: int
    total: int
    value: float | None
    ci_low: float | None
    ci_high: float | None


def wilson_interval(successes: int, total: int, z: float = Z_95) -> tuple[float, float]:
    if total == 0:
        raise ValueError("total must be positive")
    if not 0 <= successes <= total:
        raise ValueError("successes must be between 0 and total")
    share = successes / total
    denominator = 1 + z**2 / total
    centre = (share + z**2 / (2 * total)) / denominator
    margin = z * sqrt(share * (1 - share) / total + z**2 / (4 * total**2)) / denominator
    return max(0.0, centre - margin), min(1.0, centre + margin)


def proportion(successes: int, total: int) -> Proportion:
    if total == 0:
        return Proportion(successes=0, total=0, value=None, ci_low=None, ci_high=None)
    low, high = wilson_interval(successes, total)
    return Proportion(
        successes=successes, total=total, value=successes / total, ci_low=low, ci_high=high
    )


def format_proportion(result: Proportion) -> str:
    if result.value is None:
        return "n/a (0 checked)"
    return (
        f"{result.value:.1%} ({result.successes}/{result.total}, "
        f"95% CI {result.ci_low:.1%}-{result.ci_high:.1%})"
    )
