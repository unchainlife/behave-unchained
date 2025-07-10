@generator
Feature: The ability to set and validate values

  Scenario: Basic values
    Given the value X is 123
    Then the value X is 123

  Scenario: Values in table form
    Given the values
      | name | value |
      | A    | "a"   |
      | B    |     1 |
    Then the value A = "a"
    And the value B = 1

  Scenario: Values as text
    Given the value X is
      """
      1
      """
    Then the value X =
      """
      1
      """

  Scenario Outline: Operators
    Given the value X is <a>
    Then the value X <op> <b>
    And the value X <op>
      """
      <b>
      """

    Examples:
      | a                | op      | b             |
      |                1 | =       |             1 |
      |                1 | <>      |             2 |
      |                1 | >       |             0 |
      |                1 | >=      |             1 |
      |                2 | >=      |             1 |
      |                1 | <       |             2 |
      |                1 | <=      |             1 |
      |                1 | <=      |             2 |
      | "foo"            | ~       | "o"           |
      | "foo"            | !~      | "x"           |
      | { "foo": "bar" } | matches | "foo = 'bar'" |

  Scenario: value subsitutions
    Given the values
      | name | value   |
      | foo  |     123 |
      | bar  | ${foo}4 |
    Then the value foo < ${bar}

  @http_server
  Scenario: functions
    Given the values
      | name           | value       |
      | correlation_id | "${UUID()}" |
    Then the value correlation_id <> ""
