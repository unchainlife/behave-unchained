import pytest
from features.steps.common import get_value, set_value, assert_valid, evaluate

class MockContext:
    pass

def test__set_get_value():
    context = MockContext()
    set_value(context, name="test", value="123")
    actual = get_value(context, name="test")
    assert actual == 123


def test__cannot_set_unknown():
    context = MockContext()
    with pytest.raises(ValueError):
        set_value(context, name="bar", value="${foo}4")


def test__evaluate():
    context = MockContext()
    set_value(context, name="foo", value="123")
    set_value(context, name="bar", value="${foo}4")
    actual = get_value(context, name="bar")
    assert actual == 1234

def test__evaluate_functions():
    context = MockContext()
    context.functions = { }
    context.functions["X"] = lambda: "XYZ"
    actual = evaluate(context, "\"${X()}\"")
    assert actual == "XYZ"