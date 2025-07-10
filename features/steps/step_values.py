"""
This file contains a series of steps for manipulating and evaluating a generic
'value'.

Use the 'set_value' and 'get_value' to store/retrieve the values and then use
the then steps to evaluate them.

Given examples:

  Given the value <name> is <value>
  Given the value <name> is
    """"""
    text
    """"""
  Given the values
    | name                 | value                                   |
    | bool_value           | true                                    |
    | number_value         | 123                                     |
    | string_value         | "hello"                                 |
    | array_value          | [ 1, 2, 3 ]                             |
    | object_value         | { "hello": "world" }                    |
    | substitution_value   | "${string_value} world"                 |
    | substitution_complex | { "response": "${substitution_value}" } |
    | messy_array_part     | "[1, 2,"                                |
    | messy_array_value    | ${messy_array_part} 3]                  |
    | function_value       | "${UUID()}"                             |

  Names:
    [A-z][A-z0-9_]*

  Values:
    Values are all parsed into json values from string representations.

    bool   - JSON true/false (e.g. true)
    number - JSON number (e.g. 123.45)
    string - a string value (e.g. "Hello World")
    array  - a list value (e.g. [ 1, 2, 3 ])
    object - a complex object value (e.g. { "hello": "world" })

    substitutions:
      Before the string is parsed as a json value subsitutions with other 
      values or calls to a pre-defined set of functions can be performed.

      values   - ${VAR}.
      function - ${FUNC()}

  Functions:
    UUID()     - generate a v4 UUID

When:

Then:

  Then the value <name> <operator> <value>
  Then the value <name> <operator>
    """"""
    <value>
    """"""

  Operators:
    is      - Standard python 'is' operator
    =       - Equality operator
    <>      - Not-equals operator
    >       - Greater than
    >=      - Greater then or equals
    <       - Less than
    <=      - Less than or equals
    ~       - String contains
    !~      - String does not contain
    matches - JSONata query expected to resolve to True
"""

from behave import given, then
from features.utils.common import Comparison, compare, get_value, set_value, evaluate, DEFAULT_RESULT_NAME

################################################################################
# Given
################################################################################

@given("the value {name:S} is {value}")
def step__given_value_name_is_value(context, name: str, value: str):
    """Set the value by manually"""
    set_value(context, name=name, value=value)

@given("the value {name:S} is")
def step__given_value_name_is_text(context, name: str):
    step__given_value_name_is_value(context, name, context.text)

@given("the values")
def step__given_the_values(context):
    for row in context.table:
        set_value(context, name=row["name"], value=row["value"])

################################################################################
# When
################################################################################


################################################################################
# Then
################################################################################

@then("the value {name:S} {op:Comparison}")
def step__then_the_value(context, name: str, op: Comparison):
    step__then_the_value_name_is_value(context, name=name, op=op, expected=context.text)

@then("the value {name:S} {op:Comparison} {expected}")
def step__then_the_value_name_is_value(context, name: str, op:Comparison, expected: str):
    actual = get_value(context, name=name)
    expected = evaluate(context, expected)
    compare(
        actual=actual,
        op=op,
        expected=expected,
    )
