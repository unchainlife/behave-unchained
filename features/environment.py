import uuid

def before_feature(context, feature):
    if "skip" in feature.tags:
        feature.skip("Marked with @skip")
    context.functions = {}
    context.functions["UUID"] = uuid.uuid4

def before_scenario(context, scenario):
    if "skip" in scenario.tags:
        scenario.skip("Marked with @skip")
    context.values = {}
    context.results = {}

