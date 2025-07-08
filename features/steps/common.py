from behave import register_type
import parse
from enum import StrEnum
from typing import Any
from jsonata import Jsonata

class Comparison(StrEnum):
    Is = "is"
    Equals = "="
    NotEquals = "<>"
    GreaterThan = ">"
    GreaterThenOrEquals = ">="
    LessThan = "<"
    LessThanOrEquals = "<="
    Contains = "~"
    NotContains = "!~"
    Matches = "matches"

@parse.with_pattern("(" + "|".join([str(e) for e in Comparison]) + ")")
def parse_comparison(s: str) -> Comparison:
    return Comparison(s)

def compare(actual: Any, op: Comparison, expected: Any):
    match (op):
        case Comparison.Is:
            assert actual is expected, f"{actual} is {expected}"
        case Comparison.Equals:
            assert actual == expected, f"{actual} = {expected}"
        case Comparison.NotEquals:
            assert actual != expected, f"{actual} <> {expected}"
        case Comparison.GreaterThan:
            assert actual > expected, f"{actual} > {expected}"
        case Comparison.GreaterThenOrEquals:
            assert actual >= expected, f"{actual} >= {expected}"
        case Comparison.LessThan:
            assert actual < expected, f"{actual} < {expected}"
        case Comparison.LessThanOrEquals:
            assert actual <= expected, f"{actual} <= {expected}"
        case Comparison.Contains:
            assert expected in actual, f"{actual} ~ {expected}"
        case Comparison.NotContains:
            assert expected not in actual, f"{actual} !~ {expected}"
        case Comparison.Matches:
            expr = Jsonata(expected)
            result = expr.evaluate(actual)
            assert result is True, f"{actual} vs {expected}"
        case _:
            raise NotImplementedError(f"Unhandled Operation '{op}'")

register_type(Comparison=parse_comparison)
