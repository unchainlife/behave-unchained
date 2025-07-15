from behave import given, when, then, register_type
import requests
from requests.structures import CaseInsensitiveDict
import json
from jsonata import Jsonata
import xmltodict
from enum import StrEnum

from features.steps.step_results import RESULTS
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


class HttpPart(StrEnum):
    PROTOCOL = "protocol"
    HOSTNAME = "hostname"
    PORT = "port"
    BASE_PATH = "basepath"
    BASE_URL = "baseurl"


register_type(HttpPart=lambda s: HttpPart(s))


@given("the http {part:HttpPart} is {value:S}")
def given_the_http_part(context, part: HttpPart, value: str):
    write_context(context, HTTP, part, value)


@given("the querystring parameters")
def given_the_querystring_parameters(context):
    qs = {}
    for row in context.table.rows:
        name = row["parameter"]
        value = row["value"]
        qs[name] = [value] if name not in qs else [*qs[name], value]
    write_context(context, HTTP, "querystring", qs)


class MtlsClientPart(StrEnum):
    CERTIFICATE = "certificate"
    KEY = "key"


register_type(MtlsClient=lambda s: MtlsClientPart(s))


@given("the mTLS client {part:MtlsClient} from {filename}")
def given_the_mtls_client_part_file(context, part, filename):
    """
    Configure the HTTP request to submit mTLS certificate and key for
    authentication.
    """
    write_context(context, HTTP, f"mtls_{part}", filename)


################################################################################
# When
################################################################################


DEFAULT_RESPONSE_NAME = "default"


@when("I invoke {name:S} as {method:S} {path:S}")
def when_i_invoke_name(context, name, method, path):
    """Invoke the HTTP request, storing the named response and the response body
    as a named result.

    Args:
        context:        The behave context.
        name (str):     The name under which the response and result
                        (response.text) are to be stored.
        method (str):   The HTTP method to be used when invoking the request.
        path (str):     The path to be used when invoking the request.  This
                        will be appended to the the "base url".

    Raises:
        ValueError

    """
    base_url = read_context(context, HTTP, HttpPart.BASE_URL)
    headers = {**read_context(context, HTTP, "headers", {})}
    qs = {**read_context(context, HTTP, "querystring", {})}
    for row in context.table:
        type = row["type"]
        param = row["name"]
        value = evaluate(context, '"' + row["value"] + '"')
        match type:
            case "header":
                headers[param] = str(value)
            case "parameter":
                qs[param] = [value] if param not in qs else [*qs[param], value]
            case _:
                raise ValueError(f"Unhandled type: {type}")
    data = None
    if context.text:
        data = context.text.strip()
        headers["Content-Length"] = str(len(data))
    url = base_url + path
    cert = (
        read_context(context, HTTP, "mtls_certificate"),
        read_context(context, HTTP, "mtls_key"),
    )
    response = requests.request(
        method=method,
        url=url,
        data=data,
        headers=headers,
        params=qs,
        cert=cert,
    )
    body = response.text
    match response.headers["content-type"]:
        case "application/json" | "application/fhir+json":
            body = json.loads(body)
        case "application/xml" | "application/fhir+xml":
            body = xmltodict.parse(body)
    write_context(context, RESULTS, name, body)
    write_context(context, HTTP_RESPONSES, name, response)


# ------------------------------------------------------------------------------
# Overloads
# ------------------------------------------------------------------------------


@when("I invoke {method:S} {path:S}")
def when_i_invoke(context, method, path):
    """
    Invoke the HTTP request, storing the response and and putting the
    response body as a result

    Args:
        context: The behave context
        method (str): The HTTP method
        path (str): The HTTP path, to be appended to the "base url"
    """
    when_i_invoke_name(context, DEFAULT_RESPONSE_NAME, method, path)


################################################################################
# Then
################################################################################


@then("the response {name:S} is OK")
def then_the_response_name_is_ok(context, name):
    """
    Check that the named response has a 2xx status code

    Args:
        context: The behave context
        name (str): The named response to be evaluated
    """
    response: requests.Response = read_context(context, HTTP_RESPONSES, name)
    assert response.ok, f"got status_code {response.status_code}"


@then("the response {name:S} is not OK")
def then_the_response_name_is_not_ok(context, name):
    """
    Check that the named response has a non-2xx status code

    Args:
        context: The behave context
        name (str): The named response to be evaluated
    """
    response: requests.Response = read_context(context, HTTP_RESPONSES, name)
    assert not response.ok, f"got status_code {response.status_code}"


@then("the response {name:S} status code is {status_code:d}")
def then_the_response_name_status_code_is(context, name, status_code):
    """
    Check that the named response has a specific status code

    Args:
        context: The behave context
        name (str): The named response to be evaluated
        status_code (int): The expected HTTP status code
    """
    response: requests.Response = read_context(context, HTTP_RESPONSES, name)
    assert response.status_code == int(
        status_code
    ), f"expected {status_code} got {response.status_code}"


@then("the response {name:S} headers include")
def the_response_name_headers_include(context, name):
    """
    Check that the named response has all of the stated headers included.
    Note that this does not exclude the presence of other headers.

    Args:
        context: The behave context
        name (str): The named response to be evaluated
    """
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
    """
    Check for a 2xx status code

    Args:
        context: The behave context
    """
    then_the_response_name_is_ok(context, DEFAULT_RESPONSE_NAME)


@then("the response is not OK")
def then_the_response_is_not_ok(context):
    """
    Check for a non 2xx status code

    Args:
        context: The behave context
    """
    then_the_response_name_is_not_ok(context, DEFAULT_RESPONSE_NAME)


@then("the response status code is {status_code}")
def then_the_response_status_code_is(context, status_code):
    """
    Check for a specific status code

    Args:
        context: The behave context
        status_code (int): The HTTP status code expected
    """
    then_the_response_name_status_code_is(context, DEFAULT_RESPONSE_NAME, status_code)


@then("the response headers include")
def the_response_headers_include(context):
    """
    Check that every specified header is included in the response.  This does
    not exclude the presence of headers not named

    Args:
        context: The behave context
    """
    the_response_name_headers_include(context, DEFAULT_RESPONSE_NAME)
