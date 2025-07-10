@http_server(host=127.0.0.1,port=8000)
Feature: HTTP server

  Scenario: Basic test
    Given the base url is http://127.0.0.1:8000
    And the HTTP headers
      | header           | value                            |
      | x-correlation_id | "${UUID()}"                      |
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
      | header       | value              |
      | content-type | application/jsonxx |
      | foo          | bar                |

  Scenario: Basic test 2
    Given the base url is http://127.0.0.1:8000
    And the HTTP headers
      | header           | value                            |
      | x-correlation_id | "${UUID()}"                      |
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
