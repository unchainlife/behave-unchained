"""
This file contains a series of steps for manipulating and evaluating a generic
'value'.

Use the 'set_value' and 'get_value' to store/retrieve the values and then use
the then steps to evaluate them.
"""

from behave import given, when, then
import json
from features.steps.common import Comparison, compare, get_value, set_value_expr, evaluate, DEFAULT_RESULT_NAME

################################################################################
# Given
################################################################################

@given("the value {name:S} is {value}")
def step__given_value_name_is_value(context, name: str, value: str):
    """Set the value by manually"""
    set_value_expr(context, name=name, value=value)

@given("the value is {value}")
def step__given_value_is_value(context, value: str):
    """Set the value manually"""
    step__given_value_name_is_value(context, name=DEFAULT_RESULT_NAME, value=value)

@given("the value {name:S} is")
def step__given_value_name_is_text(context, name: str):
    step__given_value_name_is_value(context, name, context.text)

@given("the value is")
def step__given_value_is_text(context):
    step__given_value_name_is_value(context, name=DEFAULT_RESULT_NAME, value=context.text)

@given("the values")
def step__given_the_values(context):
    for row in context.table:
        set_value_expr(context, name=row["name"], value=row["value"])

################################################################################
# When
################################################################################


################################################################################
# Then
################################################################################


# ------------------------------------------------------------------------------
# comparisons
# ------------------------------------------------------------------------------

@then("the value {name:S} {op:Comparison}")
def step__then_the_value(context, name: str, op: Comparison):
    step__then_the_value_name_is_value(context, name=name, op=op, expected=context.text)

@then("the value {op:Comparison}")
def step__then_the_value(context, op: Comparison):
    step__then_the_value_name_is_value(context, name=DEFAULT_RESULT_NAME, op=op, expected=context.text)

@then("the value {op:Comparison} {expected}")
def step__then_the_value_is_value(context, op: Comparison, expected: str):
    step__then_the_value_name_is_value(context, name=DEFAULT_RESULT_NAME, op=op, expected=expected)

@then("the value {name:S} {op:Comparison} {expected}")
def step__then_the_value_name_is_value(context, name: str, op:Comparison, expected: str):
    actual = get_value(context, name=name)
    expected = evaluate(context, expected)
    compare(
        actual=actual,
        op=op,
        expected=expected,
    )
