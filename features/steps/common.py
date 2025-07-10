from behave import register_type
import re
import json
import parse
from enum import StrEnum
from typing import Any
from jsonata import Jsonata

ERROR_CONTEXT_NOT_INITIALISED = "context has not been initialised properly.  Check environment.py"

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
            assert type(actual) is type(expected), f"types don't match {type(actual)} vs {type(expected)}"
            assert actual is expected, f"{actual} is {expected}"
        case Comparison.Equals:
            assert type(actual) is type(expected), f"types don't match {type(actual)} vs {type(expected)}"
            assert actual == expected, f"{actual} = {expected}"
        case Comparison.NotEquals:
            assert type(actual) is type(expected), f"types don't match {type(actual)} vs {type(expected)}"
            assert actual != expected, f"{actual} <> {expected}"
        case Comparison.GreaterThan:
            assert type(actual) is type(expected), f"types don't match {type(actual)} vs {type(expected)}"
            assert actual > expected, f"{actual} > {expected}"
        case Comparison.GreaterThenOrEquals:
            assert type(actual) is type(expected), f"types don't match {type(actual)} vs {type(expected)}"
            assert actual >= expected, f"{actual} >= {expected}"
        case Comparison.LessThan:
            assert type(actual) is type(expected), f"types don't match {type(actual)} vs {type(expected)}"
            assert actual < expected, f"{actual} < {expected}"
        case Comparison.LessThanOrEquals:
            assert type(actual) is type(expected), f"types don't match {type(actual)} vs {type(expected)}"
            assert actual <= expected, f"{actual} <= {expected}"
        case Comparison.Contains:
            assert type(actual) is str, f"string expected"
            assert type(expected) is str, f"string expected"
            assert expected in actual, f"{actual} ~ {expected}"
        case Comparison.NotContains:
            assert type(actual) is str, f"string expected"
            assert type(expected) is str, f"string expected"
            assert expected not in actual, f"{actual} !~ {expected}"
        case Comparison.Matches:
            assert type(actual) is dict, f"object expected"
            assert type(expected) is str, f"string expected"
            expr = Jsonata(expected)
            result = expr.evaluate(actual)
            assert result is True, f"{actual} vs {expected}"
        case _:
            raise NotImplementedError(f"Unhandled Operation '{op}'")

register_type(Comparison=parse_comparison)

def read_context(context, collection:str, name:str, default_value:Any = None):
    return default_value if not hasattr(context, collection) else getattr(context, collection).get(name, default_value)

def write_context(context, collection, name, value):
    if not hasattr(context, collection):
        setattr(context, collection, {})
    getattr(context, collection)[name] = value

################################################################################
# Values
################################################################################

def assert_valid(context, expr: str):
    references = re.findall(r"\${[A-z][A-z0-9_]*}", expr)
    for r in references:
        if not value_exists(context, r[2:-1]):
            raise ValueError(f"Unknown value '${r}'")

def set_value(context, value: str, name: str):
    assert hasattr(context, "values") and isinstance(context.values, dict), ERROR_CONTEXT_NOT_INITIALISED
    assert isinstance(value, str), "Values must be string representations"
    assert re.match(r"^[A-z][A-z0-9_]*$", name), f"Invalid name: {name}"
    assert_valid(context, value)
    context.values[name] = value

def get_value(context, name: str, default: Any = None):
    assert hasattr(context, "values") and isinstance(context.values, dict), ERROR_CONTEXT_NOT_INITIALISED
    if name not in context.values:
        return default
    value = context.values[name]
    return evaluate(context, value)

def value_exists(context, name: str) -> bool:
    assert hasattr(context, "values") and isinstance(context.values, dict), ERROR_CONTEXT_NOT_INITIALISED
    return name in context.values

def evaluate(context, expr: str) -> Any:
    """
    This is a really super simple expression evaluation function, which will be
    replaced.
    """
    assert hasattr(context, "functions") and isinstance(context.functions, dict), ERROR_CONTEXT_NOT_INITIALISED
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
    assert hasattr(context, "results") and isinstance(context.results, dict), ERROR_CONTEXT_NOT_INITIALISED
    assert re.match(r"^[A-z][A-z0-9_]*$", name), f"Invalid name: {name}"
    context.results[name] = value

def get_result(context, name: str, default: Any = None):
    assert hasattr(context, "results") and isinstance(context.results, dict), ERROR_CONTEXT_NOT_INITIALISED
    if not hasattr(context, "results") or name not in context.results:
        return default
    return context.results[name]
