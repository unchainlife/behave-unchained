Feature: The ability to set and validate values

  Scenario Outline: Named values
    Given the value <name> is <value>
    Then the value <name> = <value>

    Examples:
      | name   | value       |
      | bool   | true        |
      | number |     123.456 |
      | str    | "foo"       |
      | obj    | { }         |
      | list   | [ 1, 2, 3 ] |
      | None   | null        |

  Scenario Outline: Unnamed values
    Given the value is <value>
    Then the value = <value>

    Examples:
      | value       |
      | true        |
      |     123.456 |
      | "foo"       |
      | { }         |
      | [ 1, 2, 3 ] |
      | null        |

  Scenario: Results table
    Given the values
      | name | value |
      | A    | "a"   |
      | B    |     1 |
    Then the value A = "a"
    And the value B = 1

  Scenario: Named values text
    Given the value X is
      """
      1
      """
    Then the value X = 1

  Scenario: Unnamed values text
    Given the value is
      """
      1
      """
    Then the value = 1

  Scenario Outline: Operators
    Given the value X is <a>
    Then the value X <op> <b>

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
    Given the value X is <a>
    Then the value X <op>
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

  Scenario: value references
    Given the values
      | name | value   |
      | foo  |     123 |
      | bar  | ${foo}4 |
    Then the value foo < ${bar}

  Scenario: functions
    Given the values
      | name           | value       |
      | correlation_id | "${UUID()}" |
    Then the value correlation_id <> ""