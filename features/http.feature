@http_server(host=127.0.0.1,port=8000)
Feature: HTTP server

  Background:
    Given the values
      | name           | value       |
      | CORRELATION_ID | "${UUID()}" |
      | REQUEST_ID     | "${UUID()}" |

  Scenario: Basic test
    Given the base url is http://127.0.0.1:8000
    And the HTTP headers
      | header           | value                            |
      | x-correlation-id | ${CORRELATION_ID}                |
      | x-request-id     | ${REQUEST_ID}                    |
      | accept           | application/fhir+json; version=1 |
    And the querystring parameters
      | parameter   | value |
      | _revinclude |       |
    When I invoke GET /foo/bar
      | type      | name               | value                                         |
      | parameter | patient:identifier | https://fhir.nhs.uk/Id/nhs-number\|4409815415 |
      | header    | content-type       | application/json                              |
      """
      {
        "message": "Body"
      }
      """
    Then the response is OK
    And the response status code is 200
    And the response headers include
      | header           | value             |
      | Content-Type     | application/json  |
      | X-Correlation-Id | ${CORRELATION_ID} |
      | X-Request-Id     | ${REQUEST_ID}     |
    And the response body matches
      """
      message = "Echo"
      """