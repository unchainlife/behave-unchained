import uuid
from behave import fixture, use_fixture

def before_feature(context, feature):
    if "skip" in feature.tags:
        feature.skip("Marked with @skip")
    context.functions = {
        "UUID": uuid.uuid4
    }

def before_scenario(context, scenario):
    if "skip" in scenario.tags:
        scenario.skip("Marked with @skip")
    context.values = {}
    context.results = {}

def before_tag(context, tag):
    if tag == "generator":
        use_fixture(generator, context)

@fixture
def generator(context):
    print (">>> before")
    yield
    print ("<<< after")