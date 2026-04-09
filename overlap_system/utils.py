from typing import Iterable


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def sorted_list(values: set[str]) -> list[str]:
    return sorted(values)


def set_presence_confidence(pairs: Iterable[tuple[set[str], set[str]]]) -> float:
    pairs_list = list(pairs)
    if not pairs_list:
        return 1.0

    known = 0
    for left, right in pairs_list:
        if left or right:
            known += 1
    return known / len(pairs_list)


def field_known_confidence(values: Iterable[object]) -> float:
    values_list = list(values)
    if not values_list:
        return 1.0
    known = sum(1 for value in values_list if value is not None)
    return known / len(values_list)
