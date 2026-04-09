def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def sorted_list(values: set[str]) -> list[str]:
    return sorted(values)
