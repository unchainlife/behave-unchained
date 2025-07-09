from behave import register_type
import re
import json
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

################################################################################
# Values
################################################################################

DEFAULT_VALUE_NAME = "default"

def assert_valid(context, expr: str):
    references = re.findall(r"\${[a-zA-Z][a-zA-Z0-9_]*}", expr)
    for r in references:
        if not value_exists(context, r[2:-1]):
            raise ValueError(f"Unknown value '${r}'")

def set_value_expr(context, value: str, name: str = DEFAULT_VALUE_NAME):
    assert isinstance(value, str), "Values must be string representations"
    assert re.match(r"^[A-z][A-z0-9_]*$", name), f"Invalid name: {name}"
    assert_valid(context, value)
    if not hasattr(context, "values"):
        context.values = { }
    context.values[name] = value

def get_value(context, name: str = DEFAULT_VALUE_NAME, default: Any = None):
    if not hasattr(context, "values") or name not in context.values:
        return default
    value = context.values[name]
    return evaluate(context, value)

def value_exists(context, name: str) -> bool:
    return hasattr(context, "values") and name in context.values

def evaluate(context, expr: str) -> Any:
    def repl(match):
        name = match.group(0)[2:-1]
        if name.endswith("()"):
            fn = context.functions[name[:-2]]
            return str(fn())
        return str(get_value(context, name=name))
    expr = re.sub(r"\${[A-z][A-z0-9_]*(\(\))?}", repl, expr)
    return json.loads(expr)

################################################################################
# Results
################################################################################

DEFAULT_RESULT_NAME = "default"

def set_result(context, value: Any, name: str):
    if not hasattr(context, "results"):
        context.results = { }
    context.results[name] = value

def get_result(context, name: str, default: Any = None):
    if not hasattr(context, "results") or name not in context.results:
        return default
    return context.results[name]
