"""
This file contains a series of steps for manipulating and evaluating a generic
'result'.

Use the 'set_result' and 'get_result' to store/retrieve the values and then use
the then steps to evaluate them.
"""

from behave import given, when, then
import json
from typing import Any
from features.steps.common import Comparison, compare

DEFAULT_RESULT_NAME = "(DEFAULT)"

def set_result(context, value, name: str):
    if not hasattr(context, "results"):
        context.results = { }
    context.results[name] = value

def get_result(context, name: str, default: Any = None):
    if not hasattr(context, "results") or name not in context.results:
        return default
    return context.results[name]

################################################################################
# Given
################################################################################

@given("the result {name:S} is {value}")
def step__given_result_name_is_value(context, name: str, value: str):
    """Set the result by manually"""
    set_result(context, name=name, value=json.loads(value))

@given("the result is {value}")
def step__given_result_is_value(context, value: str):
    """Set the result manually"""
    step__given_result_name_is_value(context, name=DEFAULT_RESULT_NAME, value=value)

@given("the result {name:S} is")
def step__given_result_name_is_text(context, name: str):
    step__given_result_name_is_value(context, name, context.text)

@given("the result is")
def step__given_result_is_text(context):
    step__given_result_name_is_value(context, name=DEFAULT_RESULT_NAME, value=context.text)

@given("the results")
def step__given_the_results(context):
    for row in context.table:
        set_result(context, name=row["name"], value=json.loads(row["value"]))

################################################################################
# When
################################################################################


################################################################################
# Then
################################################################################


# ------------------------------------------------------------------------------
# comparisons
# ------------------------------------------------------------------------------

@then("the result {name:S} {op:Comparison}")
def step__then_the_result(context, name: str, op: Comparison):
    step__then_the_result_name_is_value(context, name=name, op=op, expected=context.text)

@then("the result {op:Comparison}")
def step__then_the_result(context, op: Comparison):
    step__then_the_result_name_is_value(context, name=DEFAULT_RESULT_NAME, op=op, expected=context.text)

@then("the result {op:Comparison} {expected}")
def step__then_the_result_is_value(context, op: Comparison, expected: str):
    step__then_the_result_name_is_value(context, name=DEFAULT_RESULT_NAME, op=op, expected=expected)

@then("the result {name:S} {op:Comparison} {expected}")
def step__then_the_result_name_is_value(context, name: str, op:Comparison, expected: str):
    actual = get_result(context, name=name)
    expected = json.loads(expected)
    compare(
        actual=actual,
        op=op,
        expected=expected,
    )
