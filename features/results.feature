Feature: The ability to set and validate results

  Scenario Outline: Named results
    Given the result <name> is <value>
    Then the result <name> = <value>

    Examples:
      | name   | value       |
      | bool   | true        |
      | number |     123.456 |
      | str    | "foo"       |
      | obj    | { }         |
      | list   | [ 1, 2, 3 ] |
      | None   | null        |

  Scenario Outline: Unnamed results
    Given the result is <value>
    Then the result = <value>

    Examples:
      | value       |
      | true        |
      |     123.456 |
      | "foo"       |
      | { }         |
      | [ 1, 2, 3 ] |
      | null        |

  Scenario: Results table
    Given the results
      | name | value |
      | A    |   "a" |
      | B    |     1 |
    Then the result A = "a"
     And the result B = 1

  Scenario: Named results text
    Given the result X is
      """
      1
      """
    Then the result X = 1

  Scenario: Unnamed results text
    Given the result is
      """
      1
      """
    Then the result = 1

  Scenario Outline: Operators
    Given the result X is <a>
    Then the result X <op> <b>

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

  Scenario Outline: Operators from text
    Given the result X is <a>
    Then the result X <op>
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
