from behave import given, when, then
import requests
from requests.structures import CaseInsensitiveDict

from features.utils.common import evaluate, write_context, read_context

################################################################################
# Given
################################################################################

HTTP = "http"
HTTP_RESPONSES = "http_responses"

@given("the HTTP headers")
def given_the_http_headers(context):
    headers = {}
    for row in context.table:
        headers[row["header"]] = evaluate(context, '"' + row["value"] + '"')
    write_context(context, HTTP, "headers", headers)

@given("the protocol is {protocol:S}")
def given_the_protocol_is(context, protocol:str):
    write_context(context, HTTP, "protocol", protocol)

@given("the hostname is {hostname:S}")
def given_the_hostname_is(context, hostname:str):
    write_context(context, HTTP, "hostname", hostname)

@given("the port is {port:S}")
def given_the_port_is(context, port:str):
    write_context(context, HTTP, "protocol", port)

@given("the base path is {base_path:S}")
def given_the_base_path_is(context, base_path:str):
    write_context(context, HTTP, "base_path", base_path)

@given("the base url is {base_url:S}")
def given_the_base_url_is(context, base_url:str):
    write_context(context, HTTP, "base_url", base_url)


@given("the querystring parameters")
def given_the_querystring_parameters(context):
    qs = { }
    for row in context.table.rows:
        name = row["parameter"]
        value = row["value"]
        qs[name] = [value] if name not in qs else [ *qs[name], value ]
    write_context(context, HTTP, "querystring", qs)

################################################################################
# When
################################################################################


DEFAULT_RESPONSE_NAME = "default"

@when("I invoke {name:S} as {method:S} {path:S}")
def when_i_invoke_name(context, name, method, path):
    base_url = read_context(context, HTTP, "base_url")
    headers = { **read_context(context, HTTP, "headers", {}) }
    qs = { **read_context(context, HTTP, "querystring", {}) }
    for row in context.table:
        type = row["type"]
        param = row["name"]
        value = evaluate(context, '"' + row["value"] + '"')
        match type:
            case "header":
                headers[param] = str(value)
            case "parameter":
                qs[param] = [value] if param not in qs else [ *qs[param], value ]
            case _:
                raise ValueError(f"Unhandled type: {type}")
    data = None
    if context.text:
        data = context.text.strip()
        headers["Content-Length"] = str(len(data))
    url = base_url + path
    cert = None
    response = requests.request(
        method=method,
        url=url,
        data=data,
        headers=headers,
        params=qs,
        cert=cert,
    )
    write_context(context, HTTP_RESPONSES, name, response)

# ------------------------------------------------------------------------------
# Overloads
# ------------------------------------------------------------------------------

@when("I invoke {method:S} {path:S}")
def when_i_invoke(context, method, path):
    when_i_invoke_name(context, DEFAULT_RESPONSE_NAME, method, path)

################################################################################
# Then
################################################################################

@then("the response {name:S} is OK")
def then_the_response_name_is_ok(context, name):
    response: requests.Response = read_context(context, HTTP_RESPONSES, name)
    assert response.ok, f"got status_code {response.status_code}"

@then("the response {name:S} is not OK")
def then_the_response_name_is_not_ok(context, name):
    response: requests.Response = read_context(context, HTTP_RESPONSES, name)
    assert not response.ok, f"got status_code {response.status_code}"

@then("the response {name:S} status code is {status_code:d}")
def then_the_response_name_status_code_is(context, name, status_code):
    response: requests.Response = read_context(context, HTTP_RESPONSES, name)
    assert response.status_code == int(status_code), f"expected {status_code} got {response.status_code}"

@then("the response {name:S} headers include")
def the_response_name_headers_include(context, name):
    response: requests.Response = read_context(context, HTTP_RESPONSES, name)
    expected = CaseInsensitiveDict()
    for row in context.table:
        expected[row["header"]] = row["value"]
    mismatched = []
    for k, v in expected.items():
        v = evaluate(context, '"' + v + '"')
        if k not in response.headers:
            mismatched.append(f"{k} is missing")
        elif response.headers[k] != v:
            mismatched.append(f"{k} expected '{v}' vs actual '{response.headers[k]}'")
    assert mismatched == [], f"{len(mismatched)} errors: {", ".join(mismatched)}"

# ------------------------------------------------------------------------------
# Overloads
# ------------------------------------------------------------------------------

@then("the response is OK")
def then_the_response_is_ok(context):
    then_the_response_name_is_ok(context, DEFAULT_RESPONSE_NAME)

@then("the response is not OK")
def then_the_response_is_not_ok(context):
    then_the_response_name_is_not_ok(context, DEFAULT_RESPONSE_NAME)

@then("the response status code is {status_code}")
def then_the_response_status_code_is(context, status_code):
    then_the_response_name_status_code_is(context, DEFAULT_RESPONSE_NAME, status_code)

@then("the response headers include")
def the_response_headers_include(context):
    the_response_name_headers_include(context, DEFAULT_RESPONSE_NAME)

